# WSL2开发环境管理器使用说明

## 概述

WSL2开发环境管理器为IDE提供了完整的WSL2纯净开发环境管理功能，支持在Win11系统上创建隔离的开发环境，确保编译和调试过程不受宿主机环境配置污染。

## 环境配置规则

### 基础配置
- **开发环境系统版本**: `${wsl-distro} .\wsl-distro.info`
- **用户名配置**: `${wsl-usr} devman`
- **密码配置**: `${wsl-pwd} devman`

### 环境管理命令

#### 1. 创建WSL开发环境
```bash
# 使用Python管理器
python wsl_dev_manager.py create

# 使用Shell管理器
bash wsl_dev_manager.sh create
```

#### 2. 复制文件到WSL环境
```bash
# 复制单个文件
python wsl_dev_manager.py copy <filename>
bash wsl_dev_manager.sh copy <filename>

# IDE集成自动复制
python wsl_ide_integrator.py copy <filename>
```

#### 3. 编译和调试
```bash
# 在WSL环境中编译文件
python wsl_ide_integrator.py compile <filename>

# 在WSL环境中调试文件
python wsl_ide_integrator.py debug <filename>
```

#### 4. 环境管理
```bash
# 重启WSL开发环境
python wsl_dev_manager.py restart

# 停用WSL开发环境
python wsl_dev_manager.py stop

# 显示环境状态
python wsl_dev_manager.py status
```

#### 5. 销毁环境（del-${wsl-distro}）
```bash
# 执行环境销毁流程
python wsl_ide_integrator.py del
```

**销毁流程说明**:
1. 比较WSL环境中代码与项目中同名代码内容
2. 如果不一致，按照文本版本控制规则创建版本化备份
3. 将备份文件复制到项目中
4. 销毁WSL开发环境

## 配置文件

### wsl_config.json
```json
{
  "wsl_devpath": "win11",
  "wsl_usr": "devman",
  "wsl_pwd": "devman",
  "wsl_distro": "Ubuntu-22.04",
  "auto_copy": true,
  "auto_compile": false,
  "sync_extensions": [".py", ".js", ".ts", ".cpp", ".c", ".h", ".rs", ".go", ".java"],
  "compile_commands": {
    ".py": "python3 -m py_compile {file}",
    ".c": "gcc -o {output} {file}",
    ".cpp": "g++ -o {output} {file}",
    ".rs": "rustc -o {output} {file}",
    ".go": "go build -o {output} {file}"
  }
}
```

##### 支持的文件类型

### Podman配置文件优先级

系统支持两种Podman配置文件，按以下优先级使用：

1. **主配置文件**: `podman-win-wsl2` - 使用 dockurr/windows 镜像，功能完整
2. **备用配置文件**: `podman-win-wsl2-compose.yml` - 使用标准 Windows Server Core 镜像

如果主配置文件不完整（缺少YAML必要结构），系统会自动生成完整的compose文件。

### 编程语言支持
- **Python**: `.py` - 使用 `python3 -m py_compile` 编译
- **C/C++**: `.c`, `.cpp` - 使用 `gcc/g++` 编译
- **Rust**: `.rs` - 使用 `rustc` 编译
- **Go**: `.go` - 使用 `go build` 编译
- **Java**: `.java` - 使用 `javac` 编译

### 调试器支持
- **Python**: `pdb` 调试器
- **C/C++**: `gdb` 调试器
- **Rust**: `rust-gdb` 调试器
- **Go**: `delve` 调试器

## IDE集成示例

### VS Code集成
在 `.vscode/tasks.json` 中添加任务：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Copy to WSL",
      "type": "shell",
      "command": "python",
      "args": ["${workspaceFolder}/.trae/rules/wsl_ide_integrator.py", "copy", "${file}"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "Compile in WSL",
      "type": "shell", 
      "command": "python",
      "args": ["${workspaceFolder}/.trae/rules/wsl_ide_integrator.py", "compile", "${file}"],
      "group": "build",
      "dependsOn": "Copy to WSL"
    },
    {
      "label": "Debug in WSL",
      "type": "shell",
      "command": "python", 
      "args": ["${workspaceFolder}/.trae/rules/wsl_ide_integrator.py", "debug", "${file}"],
      "group": "test",
      "dependsOn": "Copy to WSL"
    }
  ]
}
```

### 快捷键绑定
在 `.vscode/keybindings.json` 中添加：

```json
[
  {
    "key": "ctrl+shift+w",
    "command": "workbench.action.tasks.runTask",
    "args": "Copy to WSL"
  },
  {
    "key": "ctrl+shift+c", 
    "command": "workbench.action.tasks.runTask",
    "args": "Compile in WSL"
  },
  {
    "key": "ctrl+shift+d",
    "command": "workbench.action.tasks.runTask", 
    "args": "Debug in WSL"
  }
]
```

## 环境隔离优势

1. **纯净环境**: WSL2环境独立于宿主机，不受本地环境配置影响
2. **版本控制**: 支持多版本并行开发，通过文本版本控制规则管理
3. **快速重置**: 可以快速销毁和重建开发环境
4. **跨平台**: 支持多种编程语言和开发工具
5. **安全隔离**: 开发环境与生产环境完全隔离

## 常见问题

### Q: WSL2未安装怎么办？
A: 需要先启用WSL2功能并安装Linux发行版：
```powershell
wsl --install
```

### Q: 如何修改用户名和密码？
A: 编辑 `wsl_config.json` 文件，修改 `wsl_usr` 和 `wsl_pwd` 字段

### Q: 支持哪些Linux发行版？
A: 默认使用 Ubuntu-22.04，可以在配置文件中修改为其他支持的发行版

### Q: 文件同步慢怎么办？
A: 建议只同步必要的源文件，避免同步大型二进制文件或node_modules等目录

## 版本历史

- **v1.0.0**: 基础WSL2环境管理功能
- **v1.1.0**: 增加IDE集成功能
- **v1.2.0**: 支持多种编程语言编译调试
- **v1.3.0**: 完善环境销毁和版本控制功能