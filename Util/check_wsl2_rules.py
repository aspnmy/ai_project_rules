#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSL2开发环境规则验证测试脚本

测试内容：
1. WSL2配置文件完整性检查
2. 环境变量设置验证
3. 路径配置正确性检查
4. 工具配置文件验证
5. 网关配置文件检查

测试日志：test_wsl2_rules.log
"""

import os
import sys
import json
import logging
from pathlib import Path

# 设置日志
log_file = 'test_wsl2_rules.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class Colors:
    """终端颜色输出"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test_header(test_name):
    """打印测试头部"""
    logging.info(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    logging.info(f"{Colors.BLUE}开始测试: {test_name}{Colors.RESET}")
    logging.info(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_test_result(test_name, passed, message=""):
    """打印测试结果"""
    status = f"{Colors.GREEN}✓ 通过{Colors.RESET}" if passed else f"{Colors.RED}✗ 失败{Colors.RESET}"
    logging.info(f"{test_name}: {status}")
    if message:
        logging.info(f"  说明: {message}")
    return passed

def test_wsl_config_files():
    """测试WSL配置文件完整性"""
    print_test_header("WSL配置文件完整性检查")
    
    base_path = Path("builder/devWinWsl2")
    required_files = [
        ".wsl-distro.info",
        "wsl_config.json", 
        "build-image-tools",
        "wsl_dev_manager.py",
        "wsl_ide_integrator.py",
        "wsl_dev_path_manager.py"
    ]
    
    all_passed = True
    
    for file_name in required_files:
        file_path = base_path / file_name
        exists = file_path.exists()
        all_passed &= print_test_result(f"文件 {file_name}", exists, 
                                      f"路径: {file_path}" if exists else "文件缺失")
    
    return all_passed

def test_environment_variables():
    """测试环境变量配置"""
    print_test_header("环境变量配置验证")
    
    # 检查wsl_config.json中的环境变量配置
    config_path = Path("builder/devWinWsl2/wsl_config.json")
    
    if not config_path.exists():
        return print_test_result("配置文件存在", False, "wsl_config.json 文件不存在")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查必需的环境变量
        required_vars = ['wsl-usr', 'wsl-pwd', 'wsl-devpath']
        all_passed = True
        
        for var in required_vars:
            exists = var in config
            all_passed &= print_test_result(f"环境变量 {var}", exists,
                                          f"值: {config.get(var, 'N/A')}" if exists else "变量缺失")
        
        return all_passed
        
    except json.JSONDecodeError as e:
        return print_test_result("JSON格式验证", False, f"JSON解析错误: {e}")
    except Exception as e:
        return print_test_result("配置文件读取", False, f"读取错误: {e}")

def test_path_configurations():
    """测试路径配置正确性"""
    print_test_header("路径配置正确性检查")
    
    all_passed = True
    
    # 检查相对路径使用
    python_files = list(Path(".trae/rules").glob("*.py"))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否使用相对路径
            has_abs_path = "/" in content and "C:" not in content  # 简化的绝对路径检测
            if has_abs_path:
                # 更详细的检查
                lines = content.split('\n')
                abs_path_found = False
                for i, line in enumerate(lines, 1):
                    if ('open(' in line or 'Path(' in line) and ('/' in line and not line.strip().startswith('#')):
                        if 'os.path' not in line and 'Path(__file__)' not in line:
                            abs_path_found = True
                            logging.warning(f"  文件 {py_file.name} 第{i}行可能使用绝对路径: {line.strip()}")
                
                if not abs_path_found:
                    all_passed &= print_test_result(f"文件 {py_file.name} 路径使用", True, "使用相对路径")
                else:
                    all_passed &= print_test_result(f"文件 {py_file.name} 路径使用", False, "发现绝对路径使用")
            else:
                all_passed &= print_test_result(f"文件 {py_file.name} 路径使用", True, "使用相对路径")
                
        except Exception as e:
            all_passed &= print_test_result(f"文件 {py_file.name} 读取", False, f"读取错误: {e}")
    
    return all_passed

def test_tool_configurations():
    """测试工具配置文件"""
    print_test_header("工具配置文件验证")
    
    tools_file = Path("builder/devWinWsl2/build-image-tools")
    
    if not tools_file.exists():
        return print_test_result("工具配置文件存在", False, "build-image-tools 文件不存在")
    
    try:
        with open(tools_file, 'r', encoding='utf-8') as f:
            tools_content = f.read().strip()
        
        # 检查必需的工具
        required_tools = ['git', 'curl', 'wget']
        all_passed = True
        
        for tool in required_tools:
            exists = tool in tools_content
            all_passed &= print_test_result(f"工具 {tool}", exists, 
                                          "已配置" if exists else "缺失")
        
        # 检查PortainerEE配置
        has_portainer = 'portainerEE' in tools_content
        print_test_result("PortainerEE配置", True, 
                         "已配置" if has_portainer else "未配置，可选")
        
        return all_passed
        
    except Exception as e:
        return print_test_result("工具配置文件读取", False, f"读取错误: {e}")

def test_gateway_configurations():
    """测试网关配置文件"""
    print_test_header("网关配置文件检查")
    
    gateway_files = [
        ("download-gateway", "gateway.cf.shdrr.org"),
        ("dockerimage-gateway", "drrpull.shdrr.org")
    ]
    
    all_passed = True
    
    for file_name, default_domain in gateway_files:
        file_path = Path(f"builder/devWinWsl2/{file_name}")
        
        if not file_path.exists():
            all_passed &= print_test_result(f"网关文件 {file_name}", False, "文件不存在")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if content:
                # 检查域名格式
                lines = content.split('\n')
                first_line = lines[0].strip()
                
                if '.' in first_line and not first_line.startswith('http'):
                    all_passed &= print_test_result(f"网关文件 {file_name}", True, 
                                                 f"域名: {first_line}")
                else:
                    all_passed &= print_test_result(f"网关文件 {file_name}", False, 
                                                 "域名格式不正确")
            else:
                all_passed &= print_test_result(f"网关文件 {file_name}", True, 
                                             f"使用默认域名: {default_domain}")
                
        except Exception as e:
            all_passed &= print_test_result(f"网关文件 {file_name} 读取", False, 
                                         f"读取错误: {e}")
    
    return all_passed

def test_documentation_files():
    """测试文档文件完整性"""
    print_test_header("文档文件完整性检查")
    
    doc_files = [
        "wsl2_dev_environment_guide.md",
        "wsl2_quick_reference.md",
        "wsl_dev_manager_readme.md"
    ]
    
    all_passed = True
    
    for doc_file in doc_files:
        file_path = Path(f"builder/devWinWsl2/{doc_file}")
        exists = file_path.exists()
        
        if exists:
            # 检查文件内容是否为空
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if len(content) > 100:  # 简单检查是否有实质内容
                    all_passed &= print_test_result(f"文档 {doc_file}", True, "内容完整")
                else:
                    all_passed &= print_test_result(f"文档 {doc_file}", False, "内容过少")
                    
            except Exception as e:
                all_passed &= print_test_result(f"文档 {doc_file} 读取", False, f"读取错误: {e}")
        else:
            all_passed &= print_test_result(f"文档 {doc_file}", False, "文件不存在")
    
    return all_passed

def main():
    """主测试函数"""
    logging.info(f"{Colors.BLUE}开始WSL2开发环境规则验证测试{Colors.RESET}")
    logging.info(f"测试日志文件: {log_file}")
    
    # 运行所有测试
    tests = [
        ("WSL配置文件完整性", test_wsl_config_files),
        ("环境变量配置", test_environment_variables),
        ("路径配置正确性", test_path_configurations),
        ("工具配置文件", test_tool_configurations),
        ("网关配置文件", test_gateway_configurations),
        ("文档文件完整性", test_documentation_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logging.error(f"测试 {test_name} 执行失败: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    logging.info(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    logging.info(f"{Colors.BLUE}测试汇总结果{Colors.RESET}")
    logging.info(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    for test_name, passed in results:
        status = f"{Colors.GREEN}✓ 通过{Colors.RESET}" if passed else f"{Colors.RED}✗ 失败{Colors.RESET}"
        logging.info(f"{test_name}: {status}")
    
    logging.info(f"\n总计: {passed_tests}/{total_tests} 项测试通过")
    
    if passed_tests == total_tests:
        logging.info(f"{Colors.GREEN}🎉 所有测试通过！WSL2开发环境规则配置完整。{Colors.RESET}")
        return 0
    else:
        logging.error(f"{Colors.RED}❌ 部分测试失败，请检查相关配置。{Colors.RESET}")
        return 1

if __name__ == "__main__":
    # 获取脚本所在目录
    script_dir = Path(__file__).resolve().parent
    # 切换到项目根目录（.trae的上一级）
    project_root = script_dir.parent
    os.chdir(project_root)
    
    sys.exit(main())