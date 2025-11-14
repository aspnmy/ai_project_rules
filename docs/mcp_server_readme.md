# MCP服务器清单管理工具

本工具用于管理和自动安装常用的MCP（Model Context Protocol）服务器。

## 文件说明

### 1. mcp_server_lists.txt
- **功能**: 记录常用需要装载的MCP服务器清单
- **格式**: 每行一个服务器名称，支持#注释
- **内容**: 包含基础工具、开发工具、数据库、API集成、云服务、消息队列、监控日志等各类MCP服务器

### 2. install_mcp_servers.py
- **功能**: Python脚本，自动安装清单中的MCP服务器
- **依赖**: Python 3.x, npm
- **特点**: 
  - 自动检测npm环境
  - 逐个安装并验证
  - 提供详细的安装报告
  - 支持超时控制

### 3. install_mcp_servers.bat
- **功能**: Windows批处理脚本，自动安装清单中的MCP服务器
- **依赖**: Node.js, npm
- **特点**:
  - 无需Python环境
  - 支持UTF-8编码
  - 简单的错误处理

## 使用方法

### 方法1: 使用Python脚本（推荐）
```bash
python install_mcp_servers.py
```

### 方法2: 使用Windows批处理
```cmd
install_mcp_servers.bat
```

### 方法3: 手动安装
```bash
# 查看清单文件
cat mcp_server_lists.txt

# 手动安装指定服务器
npm install -g mcp-server-filesystem
npm install -g mcp-server-github
# ... 其他服务器
```

## 自定义清单

编辑 `mcp_server_lists.txt` 文件，添加或删除需要的MCP服务器：

```
# 添加自定义服务器
my-custom-mcp-server
another-mcp-server
```

## 注意事项

1. 确保已安装Node.js和npm
2. 需要管理员权限安装全局包
3. 安装过程可能需要网络连接
4. 某些服务器可能需要额外的配置

## 故障排除

### npm未找到
- 安装Node.js: https://nodejs.org/
- 确保npm在系统PATH中

### 安装失败
- 检查网络连接
- 尝试使用管理员权限运行
- 检查npm配置: `npm config list`

### 权限问题
- Windows: 以管理员身份运行命令提示符
- Linux/Mac: 使用sudo或在npm配置中设置权限

## 支持的MCP服务器类型

- **基础工具**: filesystem, fetch, github, git
- **开发工具**: python, nodejs, docker, kubernetes  
- **数据库**: postgresql, mongodb, redis, mysql
- **API集成**: openapi, graphql, rest
- **云服务**: aws, azure, gcp
- **消息队列**: rabbitmq, kafka, activemq
- **监控日志**: prometheus, grafana, elasticsearch
- **通讯工具**: slack, discord, telegram, email