#!/usr/bin/env python3
"""
测试网关域名功能
验证下载网关和Docker镜像网关域名的读取和设置
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_gateway_domains():
    """测试网关域名功能"""
    print("=== 测试网关域名功能 ===")
    
    # 测试文件路径
    download_gateway_file = Path("download-gateway")
    dockerimage_gateway_file = Path("dockerimage-gateway")
    
    print(f"下载网关文件: {download_gateway_file}")
    print(f"Docker镜像网关文件: {dockerimage_gateway_file}")
    
    # 检查文件是否存在
    if download_gateway_file.exists():
        with open(download_gateway_file, 'r', encoding='utf-8') as f:
            download_gateway = f.read().strip().split('\n')[0].strip()
        print(f"✓ 下载网关域名: {download_gateway}")
    else:
        print("✗ 下载网关文件不存在")
    
    if dockerimage_gateway_file.exists():
        with open(dockerimage_gateway_file, 'r', encoding='utf-8') as f:
            dockerimage_gateway = f.read().strip().split('\n')[0].strip()
        print(f"✓ Docker镜像网关域名: {dockerimage_gateway}")
    else:
        print("✗ Docker镜像网关文件不存在")
    
    # 测试环境变量
    download_env = os.environ.get('DOWNLOAD_GATEWAY', '未设置')
    docker_env = os.environ.get('DOCKERIMAGE_GATEWAY', '未设置')
    
    print(f"环境变量 DOWNLOAD_GATEWAY: {download_env}")
    print(f"环境变量 DOCKERIMAGE_GATEWAY: {docker_env}")
    
    # 测试URL构建
    test_download_url = f"https://{download_gateway}/files/test.zip"
    test_docker_url = f"{dockerimage_gateway}/windows:latest"
    
    print(f"测试下载URL: {test_download_url}")
    print(f"测试Docker镜像: {test_docker_url}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_gateway_domains()