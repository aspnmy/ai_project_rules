# rules_management 目录说明

## 目录功能
此目录包含规则管理相关的工具脚本，主要用于规则的拉取、管理和更新等功能。

## 工具列表
- **rule_puller.py**: 规则拉取工具
- **rules_manager.py**: 规则管理器
- **rules_manager_updated.py**: 更新版本的规则管理器

## 功能说明
- 从远程仓库拉取最新规则
- 管理项目中的规则文件
- 处理规则的更新和同步
- 确保规则文件的一致性和完整性

## 使用方法
- 使用rule_puller.py拉取最新规则
- 通过rules_manager.py管理现有规则
- 对于特殊需求，可以使用更新版本的rules_manager_updated.py
- 定期运行以保持规则的最新状态