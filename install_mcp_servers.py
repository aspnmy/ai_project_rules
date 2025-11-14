#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务器安装脚本
用于自动安装mcp_server_lists.txt中列出的MCP服务器

参数:
    无
    
返回:
    无
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def read_mcp_server_list():
    """
    读取MCP服务器清单文件
    
    参数:
        无
        
    返回:
        list: MCP服务器名称列表
    """
    list_file = Path(__file__).parent / "mcp_server_lists.txt"
    
    if not list_file.exists():
        print(f"错误: 清单文件 {list_file} 不存在")
        return []
    
    servers = []
    try:
        with open(list_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释行
                if line and not line.startswith('#'):
                    servers.append(line)
    except Exception as e:
        print(f"读取清单文件失败: {e}")
        return []
    
    return servers


def check_npm_installed():
    """
    检查npm是否已安装
    
    参数:
        无
        
    返回:
        bool: npm是否可用
    """
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_mcp_server(server_name):
    """
    安装指定的MCP服务器
    
    参数:
        server_name (str): MCP服务器名称
        
    返回:
        bool: 安装是否成功
    """
    print(f"正在安装 {server_name}...")
    
    try:
        # 使用npm全局安装
        result = subprocess.run(
            ["npm", "install", "-g", server_name],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"✓ {server_name} 安装成功")
            return True
        else:
            print(f"✗ {server_name} 安装失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {server_name} 安装超时")
        return False
    except Exception as e:
        print(f"✗ {server_name} 安装出错: {e}")
        return False


def verify_installation(server_name):
    """
    验证MCP服务器是否安装成功
    
    参数:
        server_name (str): MCP服务器名称
        
    返回:
        bool: 验证是否通过
    """
    try:
        # 检查是否可以在命令行中运行
        result = subprocess.run(
            [server_name, "--help"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False


def main():
    """
    主函数
    
    参数:
        无
        
    返回:
        无
    """
    print("MCP服务器自动安装工具")
    print("=" * 50)
    
    # 检查npm是否安装
    if not check_npm_installed():
        print("错误: 未检测到npm，请先安装Node.js和npm")
        print("访问 https://nodejs.org/ 下载并安装Node.js")
        sys.exit(1)
    
    # 读取服务器清单
    servers = read_mcp_server_list()
    if not servers:
        print("未找到需要安装的MCP服务器")
        sys.exit(0)
    
    print(f"发现 {len(servers)} 个MCP服务器需要安装")
    print()
    
    # 安装统计
    success_count = 0
    fail_count = 0
    
    # 逐个安装服务器
    for i, server in enumerate(servers, 1):
        print(f"[{i}/{len(servers)}] ", end="")
        
        if install_mcp_server(server):
            # 验证安装
            if verify_installation(server):
                print(f"✓ {server} 验证通过")
                success_count += 1
            else:
                print(f"⚠ {server} 安装完成但验证失败")
                fail_count += 1
        else:
            fail_count += 1
        
        print()
    
    # 输出安装报告
    print("\n" + "=" * 50)
    print("安装完成报告:")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"总计: {len(servers)} 个")
    
    if fail_count > 0:
        print(f"\n有 {fail_count} 个服务器安装失败，请检查网络连接和npm配置")
        sys.exit(1)
    else:
        print("\n所有MCP服务器安装成功！")


if __name__ == "__main__":
    main()