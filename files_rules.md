# 文件路径规则记录

## 📋 兼容性说明
为了处理不同开发环境下的命名习惯差异，以下命名视为等效：
- `test-***` ≡ `test_***` (测试文件)
- `temp-***` ≡ `temp_***` (临时文件)
- `true-***` ≡ `true_***` (正式文件)

**搜索结果统计：**
- 发现 `test_*.py` 文件：0个（原test文件已重命名为check_前缀）
- 未发现 `test-*.py` 文件：0个
- 未发现 `temp-*` 文件：0个（代码中有temp_file变量引用）
- 未发现 `true-*` 文件：0个
- 发现 `check_*.py` 文件：3个（网关域名检查、规则管理器检查、WSL2规则检查）

实际文件命名以当前目录为准，规则文件会相应更新记录。

## 生产代码
- project_rules.md
- register-docker-login
- build-image-tools
- portainerEE-Compose
- registerConfig.json.example
- rules_manager.py
- wsl2_dev_environment_guide.md
- wsl2_quick_reference.md
- wsl_dev_manager.py
- wsl_ide_integrator.py
- wsl_config.json
- wsl-distro.info
- download-gateway
- dockerimage-gateway
- files_rules.md
- check_gateway_domains.py (网关域名检查工具)
- check_rules_manager.py (规则管理器检查工具)
- check_wsl2_rules.py (WSL2规则检查工具)

## 临时生成
# 当前无临时文件

## 测试代码
# 当前无测试文件

## 文件说明

### 容器仓库配置相关
- **register-docker-login**: 容器仓库配置模式选择文件
- **registerConfig.json.example**: 容器仓库配置模板文件
- **registerConfig.json**: 实际的容器仓库配置文件（git排除）

### 开发工具相关
- **build-image-tools**: 开发容器初始化工具列表文件
- **portainerEE-Compose**: PortainerEE容器部署配置文件

### 规则管理相关
- **project_rules.md**: 项目全局规则配置文档
- **rules_manager.py**: 全局规则配置管理器
- **files_rules.md**: 文件路径规则记录文件（本文件）

### WSL2开发环境相关
- **wsl2_dev_environment_guide.md**: WSL2开发环境详细指南
- **wsl2_quick_reference.md**: WSL2开发环境快速参考卡
- **wsl_dev_manager.py**: WSL开发环境管理器
- **wsl_ide_integrator.py**: WSL IDE集成工具
- **wsl_config.json**: WSL环境配置
- **wsl-distro.info**: WSL发行版选择配置

### 其他工具文件
- **auto_sync.py**: 自动同步工具
- **docs.md**: 文档说明
- **install_podman_windows.py**: Windows Podman安装脚本
- **install_podman_windows.sh**: Windows Podman安装脚本(shell版本)
- **podman-win-wsl2**: Podman WSL2配置
- **podman-win-wsl2-compose.yml**: Podman WSL2组合配置
- **rule_puller.py**: 规则拉取工具
- **setup_auto_sync.bat**: 自动同步设置脚本
- **sync_config.json**: 同步配置
- **wsl_dev_manager.sh**: WSL开发环境管理器(shell版本)
- **wsl_dev_manager_readme.md**: WSL开发环境管理器说明
- **wsl_dev_path_manager.py**: WSL开发路径管理器
- **使用说明.md**: 使用说明文档

### 网关配置相关
- **download-gateway**: 下载文件跳转域名配置文件
- **dockerimage-gateway**: Docker镜像跳转域名配置文件