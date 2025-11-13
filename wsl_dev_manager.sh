#!/bin/bash
# WSL2开发环境管理脚本
# 用于管理Win11 WSL2开发环境的创建、使用、销毁等操作

set -e

# 配置文件路径
CONFIG_FILE="wsl_config.json"
BACKUP_DIR="wsl_backups"

# 默认配置
WSL_DEVPATH="win11"
WSL_USR="devman"
WSL_PWD="devman"
WSL_DISTRO="Ubuntu-22.04"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查WSL是否已安装
check_wsl_installed() {
    if wsl --status >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 检查发行版是否已安装
check_distro_installed() {
    local distro=$1
    if wsl --list --quiet | grep -q "^${distro}$"; then
        return 0
    else
        return 1
    fi
}

# 创建WSL开发环境
create_wsl_env() {
    log_info "正在创建WSL2开发环境：${WSL_DEVPATH}"
    
    # 检查WSL是否已安装
    if ! check_wsl_installed; then
        log_error "WSL未安装，请先安装WSL2"
        exit 1
    fi
    
    # 安装WSL发行版
    if ! check_distro_installed "${WSL_DISTRO}"; then
        log_info "正在安装 ${WSL_DISTRO}..."
        if ! wsl --install -d "${WSL_DISTRO}"; then
            log_error "安装发行版失败"
            exit 1
        fi
    fi
    
    # 设置开发环境目录
    local wsl_path="/home/${WSL_USR}/dev"
    local setup_cmd="wsl -d ${WSL_DISTRO} bash -c \""
    setup_cmd+="sudo useradd -m -s /bin/bash ${WSL_USR} && "
    setup_cmd+="echo '${WSL_USR}:${WSL_PWD}' | sudo chpasswd && "
    setup_cmd+="sudo mkdir -p ${wsl_path} && "
    setup_cmd+="sudo chown ${WSL_USR}:${WSL_USR} ${wsl_path}"
    setup_cmd+="\""
    
    log_info "正在配置开发环境..."
    if ! eval "${setup_cmd}"; then
        log_warn "环境配置可能失败"
    fi
    
    log_info "WSL2开发环境创建成功：${WSL_DEVPATH}"
}

# 复制文件到WSL环境
copy_file_to_wsl() {
    local filename=$1
    
    if [[ ! -f "${filename}" ]]; then
        log_error "文件 ${filename} 不存在"
        exit 1
    fi
    
    local wsl_path="/home/${WSL_USR}/dev"
    local dest_path="\\\\wsl$\\${WSL_DISTRO}${wsl_path}"
    
    # 确保WSL路径存在
    mkdir -p "${dest_path}"
    
    if cp "${filename}" "${dest_path}/$(basename "${filename}")"; then
        log_info "文件 ${filename} 已复制到WSL环境"
    else
        log_error "文件复制失败"
        exit 1
    fi
}

# 计算文件MD5
calculate_md5() {
    local filepath=$1
    if command -v md5sum >/dev/null 2>&1; then
        md5sum "${filepath}" | cut -d' ' -f1
    elif command -v md5 >/dev/null 2>&1; then
        md5 "${filepath}" | cut -d' ' -f4
    else
        log_error "未找到MD5计算工具"
        exit 1
    fi
}

# 比较文件是否一致
compare_files() {
    local local_file=$1
    local wsl_file=$2
    
    local wsl_path="\\\\wsl$\\${WSL_DISTRO}${wsl_file}"
    
    if [[ ! -f "${local_file}" ]] || [[ ! -f "${wsl_path}" ]]; then
        return 1
    fi
    
    local local_md5=$(calculate_md5 "${local_file}")
    local wsl_md5=$(calculate_md5 "${wsl_path}")
    
    if [[ "${local_md5}" == "${wsl_md5}" ]]; then
        return 0
    else
        return 1
    fi
}

# 备份WSL文件到项目
backup_wsl_file() {
    local filename=$1
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local base_name=$(basename "${filename}")
    local backup_name="**-${base_name}-d${timestamp}"
    
    local wsl_path="\\\\wsl$\\${WSL_DISTRO}/home/${WSL_USR}/dev/${base_name}"
    local backup_path="${BACKUP_DIR}/${backup_name}"
    
    # 确保备份目录存在
    mkdir -p "$(dirname "${backup_path}")"
    
    if cp "${wsl_path}" "${backup_path}"; then
        log_info "WSL文件已备份为：${backup_name}"
        echo "${backup_path}"
    else
        log_error "文件备份失败"
        exit 1
    fi
}

# 销毁WSL开发环境
destroy_wsl_env() {
    log_info "正在销毁WSL开发环境：${WSL_DEVPATH}"
    
    # 检查WSL环境中的文件
    local wsl_dev_path="/home/${WSL_USR}/dev"
    local check_cmd="wsl -d ${WSL_DISTRO} bash -c 'ls -la ${wsl_dev_path} 2>/dev/null'"
    
    if files=$(eval "${check_cmd}"); then
        log_info "发现WSL环境中的文件："
        echo "${files}"
        
        # 备份重要文件
        echo "${files}" | tail -n +4 | while read -r file_info; do
            if [[ -n "${file_info}" ]]; then
                local filename=$(echo "${file_info}" | awk '{print $9}')
                if [[ -n "${filename}" ]] && [[ ! "${filename}" =~ ^\. ]]; then
                    log_info "正在备份文件：${filename}"
                    backup_wsl_file "${filename}"
                fi
            fi
        done
    fi
    
    # 删除用户
    local delete_cmd="wsl -d ${WSL_DISTRO} bash -c 'sudo userdel -r ${WSL_USR} 2>/dev/null'"
    if eval "${delete_cmd}"; then
        log_info "WSL开发环境已销毁：${WSL_DEVPATH}"
    else
        log_warn "环境销毁可能不完全"
    fi
}

# 重启WSL开发环境
restart_wsl_env() {
    log_info "正在重启WSL开发环境：${WSL_DEVPATH}"
    
    # 停止WSL
    if wsl --shutdown; then
        # 重新启动并检查环境
        local check_cmd="wsl -d ${WSL_DISTRO} bash -c 'ls -la /home/${WSL_USR}/dev 2>/dev/null'"
        if eval "${check_cmd}"; then
            log_info "WSL开发环境已重启：${WSL_DEVPATH}"
        else
            log_warn "环境检查失败"
        fi
    else
        log_error "WSL停止失败"
        exit 1
    fi
}

# 停用WSL开发环境
stop_wsl_env() {
    log_info "正在停用WSL开发环境：${WSL_DEVPATH}"
    
    if wsl --shutdown; then
        log_info "WSL开发环境已停用：${WSL_DEVPATH}"
    else
        log_error "WSL停用失败"
        exit 1
    fi
}

# 显示环境状态
show_status() {
    echo "=== WSL2开发环境状态 ==="
    echo "环境名称: ${WSL_DEVPATH}"
    echo "用户名: ${WSL_USR}"
    echo "发行版: ${WSL_DISTRO}"
    echo "项目路径: $(pwd)"
    
    # 检查WSL状态
    if check_wsl_installed; then
        echo "WSL状态: 已安装 ✓"
        
        if check_distro_installed "${WSL_DISTRO}"; then
            echo "发行版状态: 已安装 ✓"
            
            # 检查开发环境目录
            local check_cmd="wsl -d ${WSL_DISTRO} bash -c 'ls -la /home/${WSL_USR}/dev 2>/dev/null'"
            if result=$(eval "${check_cmd}" 2>/dev/null); then
                echo "开发环境: 已就绪 ✓"
                echo "环境文件:"
                echo "${result}"
            else
                echo "开发环境: 未创建 ✗"
            fi
        else
            echo "发行版状态: 未安装 ✗"
        fi
    else
        echo "WSL状态: 未安装 ✗"
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  create          - 创建WSL开发环境"
    echo "  copy <file>     - 复制文件到WSL环境"
    echo "  destroy         - 销毁WSL开发环境"
    echo "  restart         - 重启WSL开发环境"
    echo "  stop            - 停用WSL开发环境"
    echo "  status          - 显示环境状态"
    echo "  help            - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 create"
    echo "  $0 copy main.py"
    echo "  $0 destroy"
    echo "  $0 status"
}

# 主函数
main() {
    case "${1:-}" in
        create)
            create_wsl_env
            ;;
        copy)
            if [[ -z "${2:-}" ]]; then
                log_error "请指定要复制的文件"
                exit 1
            fi
            copy_file_to_wsl "${2}"
            ;;
        destroy)
            destroy_wsl_env
            ;;
        restart)
            restart_wsl_env
            ;;
        stop)
            stop_wsl_env
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: ${1:-}"
            show_help
            exit 1
            ;;
    esac
}

# 如果直接运行脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi