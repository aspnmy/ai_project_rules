# 项目规则使用指南

## 📋 文档说明

本文档详细介绍了AI项目规则管理系统的使用方法，包括规则文件的更新、管理和应用。

## 🔍 规则文件概述

### 核心文件
- **project_rules.md**: 项目全局规则配置文档
- **rules_manager.py**: 规则管理器工具
- **rule_puller.py**: 规则拉取工具

## 🚀 规则更新流程

### 1. 手动更新规则

```bash
# 运行规则拉取器更新规则
python rule_puller.py update

# 查看当前规则状态
python rule_puller.py status
```

### 2. 设置自动同步

```bash
# 运行自动同步设置脚本
setup_auto_sync.bat
```

## ⚙️ 规则模式切换

### 在线模式
```bash
# 创建在线模式标识文件
New-Item -ItemType File rules.online
```

### 离线模式
```bash
# 创建离线模式标识文件
New-Item -ItemType File rules.offline
```

### 锁定模式
```bash
# 创建锁定模式标识文件
New-Item -ItemType File rules.lock
```

## 📝 规则文件变量管理

所有项目变量在`project_vars.txt`中定义，包括：

- 系统路径变量（system_path_var）
- 调试变量（debug_var）
- 项目变量（project_var）

## 🔒 注意事项

- 请确保规则文件的备份版本与主版本保持一致
- 规则更新时会自动检查冲突
- 重要规则变更需要记录变更历史
- 请不要直接修改规则文件，应通过规则管理器进行更新