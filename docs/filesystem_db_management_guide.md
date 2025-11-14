# 使用Filesystem MCP Server管理数据库指南

基于db_lists.txt中的配置信息 `mcp_server:filesystem "D://你的机密项目文件路径//文件名"`，以下是详细的使用配置和管理方法。

## 配置文件设置

### 1. NPX方式配置（推荐）
在您的MCP配置文件中添加：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y", 
        "@modelcontextprotocol/server-filesystem",
        "D://你的机密项目文件路径//文件名"
      ]
    }
  }
}
```

### 2. Docker方式配置
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--mount", "type=bind,src=D://你的机密项目文件路径//文件名,dst=/projects/db",
        "mcp/filesystem",
        "/projects/db"
      ]
    }
  }
}
```

## 数据库文件管理操作

### 文件信息获取
```bash
# 获取数据库文件信息
tool: get_file_info
path: "D://你的机密项目文件路径//文件名"
```

### 数据库备份
```bash
# 创建备份目录
tool: create_directory  
path: "D://你的机密项目文件路径//backup"

# 复制数据库文件进行备份
tool: move_file
source: "D://你的机密项目文件路径//文件名"
destination: "D://你的机密项目文件路径//backup/文件名_$(date)"
```

### 数据库文件搜索
```bash
# 在数据库目录中搜索相关文件
tool: search_files
path: "D://你的机密项目文件路径//文件名"
pattern: "*.mdb"
excludePatterns: ["*.log", "*.tmp"]
```

### 目录管理
```bash
# 列出数据库目录内容
tool: list_directory
path: "D://你的机密项目文件路径//文件名"

# 创建新的数据库子目录
tool: create_directory
path: "D://你的机密项目文件路径//archive"
```

## 数据库维护操作

### 1. 文件大小监控
```bash
# 定期检查数据库文件大小
info = get_file_info("D://你的机密项目文件路径//文件名")
if info.size > 1000000000:  # 1GB
    print("数据库文件过大，建议进行维护")
```

### 2. 备份管理
```bash
# 创建带时间戳的备份
backup_dir = "D://你的机密项目文件路径//backup"
create_directory(backup_dir)
backup_file = f"{backup_dir}/数据库备份_{timestamp}.mdb"
# 执行备份操作
```

### 3. 日志文件管理
```bash
# 清理旧的日志文件
log_files = search_files("D://你的机密项目文件路径//文件名", "*.log")
for log_file in log_files:
    if is_older_than_30_days(log_file):
        # 删除或归档旧日志
```

## 安全注意事项

1. **访问权限控制**
   - 确保数据库目录有适当的访问权限
   - 使用只读挂载进行查询操作

2. **备份策略**
   - 定期创建数据库备份
   - 将备份存储在单独的目录中
   - 保留多个历史版本

3. **文件锁定**
   - 在数据库使用时避免直接文件操作
   - 确保数据库连接关闭后再进行文件管理

## 故障排除

### 常见问题

**1. 文件访问权限错误**
```
错误: 无法访问文件 D://你的机密项目文件路径//文件名
解决: 检查文件权限，确保运行用户有访问权限
```

**2. 文件被占用**
```
错误: 文件正在被其他进程使用
解决: 关闭数据库连接后再执行文件操作
```

**3. 路径不存在**
```
错误: 指定的路径不存在
解决: 使用create_directory创建必要的目录结构
```

## 最佳实践

1. **定期备份**: 设置自动备份计划
2. **版本控制**: 保留数据库文件的历史版本
3. **监控文件大小**: 定期检查数据库文件增长情况
4. **安全权限**: 限制对数据库文件的直接访问
5. **操作日志**: 记录所有文件管理操作

## 扩展配置

### 多数据库管理
```json
{
  "mcpServers": {
    "filesystem_db1": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "D://你的机密项目文件路径//文件名"]
    },
    "filesystem_db2": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "F:/DB/production"]
    }
  }
}
```

### 带权限控制的配置
```json
{
  "mcpServers": {
    "filesystem_readonly": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--mount", "type=bind,src=D://你的机密项目文件路径//文件名,dst=/projects/db,ro",
        "mcp/filesystem", "/projects/db"
      ]
    }
  }
}
```