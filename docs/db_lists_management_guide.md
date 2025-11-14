# 数据库配置管理工具使用指南

## 概述

本工具集用于基于 `db_lists.txt` 文件管理数据库配置，支持通过环境变量安全引用数据库路径，并生成相应的 MCP (Model Context Protocol) 服务器配置。

## 文件结构

```
.trae/rules/
├── db_lists.txt                    # 数据库配置列表文件
├── set_SystemPathVar.py            # 系统环境变量设置工具
├── db_lists_parser.py              # db_lists.txt 文件解析器
├── check_project_config.py         # 项目配置检查工具
├── db_filesystem_manager.py        # MCP 配置生成工具
├── test_db_tools.py                # 工具测试脚本
├── db_config/                      # 生成的配置文件目录
│   ├── mcp_config.json            # MCP 服务器配置
│   ├── backup_strategy.json       # 备份策略配置
│   ├── file_operations.json       # 文件操作配置
│   └── maintenance_plan.json      # 维护计划配置
└── db_lists_management_guide.md   # 本使用指南
```

## 配置格式

### db_lists.txt 格式

每行格式：`mcp_server:${mcp_server_name}|${system_path_var}`

示例：
```
mcp_server:filesystem|DB_PATH_CONFIG
mcp_server:sqlite|TEST_SQLITE_DB
mcp_server:postgres|PG_DB_PATH
```

### 环境变量要求

- `system_path_var` 必须是有效的环境变量名称（字母、数字、下划线，不能以数字开头）
- 环境变量值必须指向实际存在的数据库文件或目录
- 禁止使用硬编码的绝对路径，必须通过环境变量引用

## 使用流程

### 1. 设置数据库路径环境变量

使用 `set_SystemPathVar.py` 工具安全设置环境变量：

```bash
python set_SystemPathVar.py
```

交互式界面将引导您：
- 添加新的数据库路径配置
- 查看现有配置
- 测试环境变量
- 删除配置

### 2. 编辑 db_lists.txt 文件

添加您的数据库配置，格式如下：
```
mcp_server:filesystem|您的环境变量名
```

### 3. 验证配置格式

使用 `db_lists_parser.py` 验证配置文件格式：

```bash
python db_lists_parser.py
```

输出示例：
```
==========================================================
db_lists.txt 配置摘要
==========================================================
总配置数: 1
有效配置: 1
无效配置: 0

有效配置:
  ✓ filesystem: D://你的机密项目文件路径//文件名
```

### 4. 生成 MCP 配置

使用 `db_filesystem_manager.py` 生成 MCP 服务器配置：

```bash
python db_filesystem_manager.py
```

生成的配置文件将保存在 `db_config/` 目录中。

### 5. 检查项目配置

使用 `check_project_config.py` 验证项目配置完整性：

```bash
python check_project_config.py
```

输出示例：
```
==========================================================
项目配置检查报告
==========================================================
总体状态: ✓ PASSED

✓ db_lists.txt 文件
✓ 环境变量设置
✓ 路径存在性
✓ MCP配置
✓ 项目结构

改进建议:
----------------------------------------
1. 定期备份数据库文件
2. 确保环境变量名称足够复杂以避免冲突
3. 使用强密码保护数据库文件
==========================================================
```

### 6. 运行测试

使用 `test_db_tools.py` 测试所有工具功能：

```bash
python test_db_tools.py
```

## 工具详细说明

### set_SystemPathVar.py

**功能**：安全设置和管理系统环境变量

**特点**：
- 生成随机的环境变量名称
- 支持 Windows 和 Unix/Linux 系统
- 保存配置到本地文件
- 提供交互式管理界面

**主要方法**：
- `generate_random_var_name()`: 生成随机环境变量名
- `set_env_var()`: 设置系统环境变量（跨平台）
- `save_config()`: 保存配置到文件
- `load_existing_config()`: 加载现有配置

### db_lists_parser.py

**功能**：解析 db_lists.txt 文件并验证配置

**特点**：
- 支持多种 MCP 服务器类型
- 环境变量引用解析
- 配置有效性验证
- 生成 MCP 服务器配置

**主要方法**：
- `parse_file()`: 解析 db_lists.txt 文件
- `resolve_paths()`: 解析环境变量引用的实际路径
- `validate_configs()`: 验证配置的有效性
- `generate_mcp_configs()`: 生成 MCP 服务器配置

### check_project_config.py

**功能**：检查项目配置是否满足 db_lists.txt 中的要求

**检查项目**：
- db_lists.txt 文件存在性和格式
- 环境变量设置状态
- 路径存在性
- MCP 配置有效性
- 项目结构完整性

**输出**：详细的检查报告，包含问题和改进建议

### db_filesystem_manager.py

**功能**：生成 MCP 服务器配置和管理数据库文件

**功能模块**：
- MCP 配置生成
- 备份策略创建
- 文件操作命令生成
- 维护计划制定
- 配置文件导出

## 安全注意事项

1. **环境变量安全**：
   - 使用复杂的环境变量名称，避免与其他系统变量冲突
   - 不要在代码中硬编码敏感路径
   - 定期检查和更新环境变量设置

2. **文件权限**：
   - 确保数据库文件具有适当的访问权限
   - 限制对配置文件的访问权限
   - 定期备份重要的数据库文件

3. **配置验证**：
   - 在使用前务必运行配置检查
   - 及时修复检查工具发现的问题
   - 保持配置文件的最新状态

## 故障排除

### 常见问题

1. **环境变量未设置**
   ```
   错误: 环境变量 XXX 未设置
   解决: 使用 set_SystemPathVar.py 工具设置环境变量
   ```

2. **路径不存在**
   ```
   错误: 路径 XXX 不存在
   解决: 创建路径或检查环境变量设置
   ```

3. **配置格式错误**
   ```
   错误: db_lists.txt 格式无效
   解决: 检查文件格式，确保使用正确的格式: mcp_server:server_name|env_var_name
   ```

4. **MCP 配置生成失败**
   ```
   错误: 无法生成 MCP 配置
   解决: 确保所有环境变量都已正确设置，路径存在
   ```

### 调试步骤

1. 运行 `python check_project_config.py` 获取详细的错误信息
2. 根据错误提示修复相应的问题
3. 重新运行检查工具验证修复结果
4. 如果问题仍然存在，查看工具生成的日志文件

## 最佳实践

1. **命名规范**：
   - 使用描述性的配置名称
   - 环境变量名称包含项目标识
   - 保持命名的一致性

2. **配置管理**：
   - 定期备份配置文件
   - 使用版本控制管理配置变更
   - 记录配置的用途和设置时间

3. **安全实践**：
   - 定期更新环境变量名称
   - 监控配置的访问和使用情况
   - 实施最小权限原则

4. **维护策略**：
   - 定期运行配置检查
   - 及时更新工具版本
   - 保持文档的同步更新

## 更新日志

- 2025-01-14: 初始版本，包含基本的数据库配置管理功能
- 2025-01-14: 添加完整的工具测试套件
- 2025-01-14: 完善安全检查和验证机制