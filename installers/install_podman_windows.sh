#!/bin/bash
# Podman Windows容器环境安装脚本
# 用于在WSL2环境中安装和配置Windows开发容器

set -e

# 颜色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置文件路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/wsl-distro.info"
PODMAN_COMPOSE_FILE="${SCRIPT_DIR}/podman-win-wsl2"
CONTAINER_UUID_FILE="${SCRIPT_DIR}/.container_uuid"
COMPOSE_FILE_PATH="${SCRIPT_DIR}/.compose_file"
DOWNLOAD_GATEWAY_FILE="${SCRIPT_DIR}/download-gateway"
DOCKERIMAGE_GATEWAY_FILE="${SCRIPT_DIR}/dockerimage-gateway"

# 生成完整的compose文件
generate_compose_file() {
    local source_file="$1"
    local output_file="$2"
    
    echo "正在生成完整的podman-compose文件..."
    
    cat > "$output_file" << EOF
# 自动生成的Podman Compose文件
# 基于: $source_file
# 生成时间: $(date)

version: '3.8'

services:
$(cat "$source_file")

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  \${uuid}-storage-\${wsl-distro}:
  \${uuid}-data-\${wsl-distro}:
EOF
    
    echo "已生成完整的compose文件: $output_file"
}

# 默认配置
WSL_DISTRO="Debian"
WSL_USR="devman"
WSL_PWD="devman"
UUID=""
DOWNLOAD_GATEWAY="gateway.cf.shdrr.org"
DOCKERIMAGE_GATEWAY="drrpull.shdrr.org"

# 读取网关域名配置
load_gateway_domains() {
    # 读取下载网关域名
    if [[ -f "$DOWNLOAD_GATEWAY_FILE" ]]; then
        gateway=$(head -n 1 "$DOWNLOAD_GATEWAY_FILE" | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [[ -n "$gateway" ]]; then
            DOWNLOAD_GATEWAY="$gateway"
            echo -e "${GREEN}下载网关域名: $DOWNLOAD_GATEWAY${NC}"
        fi
    else
        echo -e "${BLUE}使用默认下载网关域名: $DOWNLOAD_GATEWAY${NC}"
    fi
    
    # 读取Docker镜像网关域名
    if [[ -f "$DOCKERIMAGE_GATEWAY_FILE" ]]; then
        gateway=$(head -n 1 "$DOCKERIMAGE_GATEWAY_FILE" | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [[ -n "$gateway" ]]; then
            DOCKERIMAGE_GATEWAY="$gateway"
            echo -e "${GREEN}Docker镜像网关域名: $DOCKERIMAGE_GATEWAY${NC}"
        fi
    else
        echo -e "${BLUE}使用默认Docker镜像网关域名: $DOCKERIMAGE_GATEWAY${NC}"
    fi
    
    # 导出环境变量
    export DOWNLOAD_GATEWAY="$DOWNLOAD_GATEWAY"
    export DOCKERIMAGE_GATEWAY="$DOCKERIMAGE_GATEWAY"
}

# 读取配置文件
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        echo -e "${BLUE}正在读取配置文件: $CONFIG_FILE${NC}"
        
        # 直接读取第一行非空内容
        WSL_DISTRO=$(head -n 1 "$CONFIG_FILE" | tr -d '\r\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        if [[ -n "$WSL_DISTRO" ]]; then
            echo -e "${GREEN}配置的系统版本: $WSL_DISTRO${NC}"
        else
            echo -e "${YELLOW}配置文件内容为空，使用默认值: $WSL_DISTRO${NC}"
        fi
    else
        echo -e "${YELLOW}配置文件不存在，使用默认值: $WSL_DISTRO${NC}"
    fi
}

# 检查是否为Windows容器版本
check_windows_distro() {
    case "$WSL_DISTRO" in
        win11|win11l|win7u|win2025)
            return 0  # 是Windows容器
            ;;
        *)
            return 1  # 不是Windows容器
            ;;
    esac
}

# 生成UUID
generate_uuid() {
    UUID=$(date '+%Y-%m-%d_%H-%M')-$(uuidgen 2>/dev/null || echo "$(date '+%s')" | md5sum | cut -c1-8)
    echo -e "${BLUE}生成的容器UUID: $UUID${NC}"
}

# 安装Podman和必要工具
install_podman() {
    echo -e "${BLUE}正在检查Podman安装...${NC}"
    
    if ! command -v podman &> /dev/null; then
        echo -e "${YELLOW}Podman未安装，正在安装...${NC}"
        
        # 检测Linux发行版
        if [[ -f /etc/debian_version ]]; then
            sudo apt update
            sudo apt install -y podman podman-compose
        elif [[ -f /etc/redhat-release ]]; then
            sudo dnf install -y podman podman-compose
        elif [[ -f /etc/arch-release ]]; then
            sudo pacman -S --noconfirm podman podman-compose
        else
            echo -e "${RED}不支持的Linux发行版${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}Podman已安装: $(podman --version)${NC}"
    fi
    
    # 检查并优先使用 podman-win-wsl2 配置文件
    local primary_compose="${SCRIPT_DIR}/podman-win-wsl2"
    local fallback_compose="${SCRIPT_DIR}/podman-win-wsl2-compose.yml"
    
    if [[ -f "$primary_compose" ]]; then
        PODMAN_COMPOSE_FILE="$primary_compose"
        echo -e "${GREEN}使用主配置文件: $PODMAN_COMPOSE_FILE${NC}"
    elif [[ -f "$fallback_compose" ]]; then
        PODMAN_COMPOSE_FILE="$fallback_compose"
        echo -e "${YELLOW}主配置文件不存在，使用备用配置文件: $PODMAN_COMPOSE_FILE${NC}"
    else
        echo -e "${RED}错误: 未找到任何有效的 podman-compose 配置文件${NC}"
        echo -e "${YELLOW}请确保 $primary_compose 或 $fallback_compose 存在${NC}"
        exit 1
    fi
}

# 配置Podman Windows容器
setup_windows_container() {
    if ! check_windows_distro; then
        echo -e "${YELLOW}当前配置不是Windows容器版本，跳过容器配置${NC}"
        return 0
    fi
    
    echo -e "${BLUE}正在配置Windows容器环境...${NC}"
    
    # 检查podman-compose文件是否存在
    if [[ ! -f "$PODMAN_COMPOSE_FILE" ]]; then
        echo -e "${RED}错误: podman-compose文件不存在: $PODMAN_COMPOSE_FILE${NC}"
        return 1
    fi
    
    # 生成UUID
    generate_uuid
    
    # 创建临时docker-compose文件
    local compose_file="${SCRIPT_DIR}/docker-compose-${UUID}.yml"
    
    # 替换变量并生成compose文件
    sed -e "s/\${uuid}/$UUID/g" \
        -e "s/\${wsl-distro}/$WSL_DISTRO/g" \
        -e "s/\${wsl-usr}/$WSL_USR/g" \
        -e "s/\${wsl-pwd}/$WSL_PWD/g" \
        "$PODMAN_COMPOSE_FILE" > "$compose_file"
    
    echo -e "${GREEN}已生成docker-compose文件: $compose_file${NC}"
    
    # 启动容器
    echo -e "${BLUE}正在启动Windows容器...${NC}"
    
    # 优先使用 podman-win-wsl2 配置文件
    local compose_file="${SCRIPT_DIR}/podman-win-wsl2"
    local fallback_compose="${SCRIPT_DIR}/podman-win-wsl2-compose.yml"
    local final_compose=""
    
    if [[ -f "$compose_file" ]]; then
        # 检查 podman-win-wsl2 是否为完整的YAML文件
        if grep -q "version:" "$compose_file" && grep -q "services:" "$compose_file"; then
            final_compose="$compose_file"
            echo -e "${GREEN}使用主配置文件: $final_compose${NC}"
        else
            # podman-win-wsl2 是不完整的YAML片段，需要生成完整的compose文件
            echo -e "${YELLOW}主配置文件不完整，生成完整的compose文件${NC}"
            final_compose="${SCRIPT_DIR}/podman-win-wsl2-generated.yml"
            generate_compose_file "$compose_file" "$final_compose"
        fi
    elif [[ -f "$fallback_compose" ]]; then
        final_compose="$fallback_compose"
        echo -e "${YELLOW}主配置文件不存在，使用备用配置文件: $final_compose${NC}"
    else
        echo -e "${RED}错误: 未找到任何有效的 podman-compose 配置文件${NC}"
        return 1
    fi
    
    podman-compose -f "$final_compose" up -d
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Windows容器启动成功!${NC}"
        echo -e "${GREEN}容器名称: ${UUID}-windows-${WSL_DISTRO}${NC}"
        echo -e "${GREEN}RDP端口: 4489${NC}"
        echo -e "${GREEN}HTTP端口: 4818${NC}"
        echo -e "${GREEN}VNC端口: 4777${NC}"
        echo -e "${GREEN}用户名: $WSL_USR${NC}"
        echo -e "${GREEN}密码: $WSL_PWD${NC}"
        
        # 保存容器信息
        echo "$UUID" > "${SCRIPT_DIR}/.container_uuid"
        echo "$compose_file" > "${SCRIPT_DIR}/.compose_file"
    else
        echo -e "${RED}Windows容器启动失败!${NC}"
        rm -f "$compose_file"
        return 1
    fi
}

# 停止并清理容器
cleanup_container() {
    local uuid_file="${SCRIPT_DIR}/.container_uuid"
    local compose_file="${SCRIPT_DIR}/.compose_file"
    
    if [[ -f "$uuid_file" ]]; then
        local container_uuid=$(cat "$uuid_file")
        echo -e "${BLUE}正在停止容器: ${container_uuid}-windows-${WSL_DISTRO}${NC}"
        
        if [[ -f "$compose_file" ]]; then
            local compose_path=$(cat "$compose_file")
            podman-compose -f "$compose_path" down
            rm -f "$compose_path"
        fi
        
        # 清理容器和卷
        podman rm -f "${container_uuid}-windows-${WSL_DISTRO}" 2>/dev/null || true
        podman volume rm "${container_uuid}-storage-${WSL_DISTRO}" 2>/dev/null || true
        podman volume rm "${container_uuid}-data-${WSL_DISTRO}" 2>/dev/null || true
        
        rm -f "$uuid_file" "$compose_file"
        echo -e "${GREEN}容器清理完成${NC}"
    else
        echo -e "${YELLOW}没有找到运行的容器${NC}"
    fi
}

# 显示容器状态
show_status() {
    echo -e "${BLUE}=== Podman Windows容器状态 ===${NC}"
    echo -e "配置的系统版本: ${GREEN}$WSL_DISTRO${NC}"
    
    if check_windows_distro; then
        echo -e "容器类型: ${GREEN}Windows容器${NC}"
        
        local uuid_file="${SCRIPT_DIR}/.container_uuid"
        if [[ -f "$uuid_file" ]]; then
            local container_uuid=$(cat "$uuid_file")
            echo -e "容器状态: ${GREEN}正在运行${NC}"
            echo -e "容器名称: ${container_uuid}-windows-${WSL_DISTRO}"
            echo -e "RDP端口: 4489"
            echo -e "HTTP端口: 4818"
            echo -e "VNC端口: 4777"
            
            # 显示容器详细信息
            podman ps --filter "name=${container_uuid}-windows-${WSL_DISTRO}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            echo -e "容器状态: ${YELLOW}未运行${NC}"
        fi
    else
        echo -e "容器类型: ${YELLOW}Linux开发环境${NC}"
        echo -e "使用标准的WSL2环境，无需Podman容器"
    fi
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}=== Podman Windows容器安装脚本 ===${NC}"
    echo -e "${GREEN}用法: $0 [命令]${NC}"
    echo
    echo -e "${YELLOW}命令选项:${NC}"
    echo -e "  install    - 安装Podman并配置Windows容器环境"
    echo -e "  start      - 启动Windows容器"
    echo -e "  stop       - 停止并清理容器"
    echo -e "  status     - 显示容器状态"
    echo -e "  cleanup    - 清理所有容器和配置"
    echo -e "  help       - 显示此帮助信息"
    echo
    echo -e "${YELLOW}配置文件:${NC}"
    echo -e "  wsl-distro.info - 系统版本配置文件"
    echo -e "  podman-win-wsl2 - Podman compose配置文件"
    echo
    echo -e "${YELLOW}支持的系统版本:${NC}"
    echo -e "  win11   - Windows 11 专业版"
    echo -e "  win11l  - Windows 11 LTS版本"
    echo -e "  win7u   - Windows 7 专业版"
    echo -e "  win2025 - Windows Server 2025 专业版"
    echo -e "  Debian  - Debian Linux (默认)"
    echo -e "  Ubuntu  - Ubuntu Linux"
}

# 主函数
main() {
    # 读取配置
    load_config
    load_gateway_domains  # 加载网关域名配置
    
    case "${1:-help}" in
        install)
            install_podman
            setup_windows_container
            ;;
        start)
            setup_windows_container
            ;;
        stop)
            cleanup_container
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup_container
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}错误: 未知命令 '$1'${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"