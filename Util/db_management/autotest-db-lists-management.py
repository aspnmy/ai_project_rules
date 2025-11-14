#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_lists.txt 管理工具自动化测试脚本
用于验证数据库配置管理工具的完整功能

参数:
    无
    
返回:
    无
"""

import os
import sys
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime


class DBListsManagementTester:
    """
    db_lists.txt 管理工具测试器
    """
    
    def __init__(self):
        """
        初始化测试器
        
        参数:
            无
        """
        self.test_dir = Path("test_workspace")
        self.log_file = f"autotest-db-lists-{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.test_results = []
        
        # 创建测试目录
        self.test_dir.mkdir(exist_ok=True)
        
        # 设置日志
        self.setup_logging()
    
    def setup_logging(self):
        """
        设置日志记录
        
        参数:
            无
        """
        import logging
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_test_start(self, test_name):
        """
        记录测试开始
        
        参数:
            test_name (str): 测试名称
        """
        self.logger.info(f"=" * 60)
        self.logger.info(f"开始测试: {test_name}")
        self.logger.info(f"=" * 60)
    
    def log_test_result(self, test_name, success, message=""):
        """
        记录测试结果
        
        参数:
            test_name (str): 测试名称
            success (bool): 是否成功
            message (str): 附加消息
        """
        status = "✓ 通过" if success else "✗ 失败"
        self.logger.info(f"{test_name}: {status}")
        if message:
            self.logger.info(f"  详情: {message}")
        
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_db_lists_parser_basic(self):
        """
        测试 db_lists_parser.py 基本功能
        
        参数:
            无
            
        返回:
            无
        """
        self.log_test_start("db_lists_parser 基本功能测试")
        
        try:
            # 创建测试用的 db_lists.txt
            test_file = self.test_dir / "test_db_lists.txt"
            test_content = """# 测试配置
mcp_server:filesystem|TEST_FILESYSTEM_PATH
mcp_server:sqlite|TEST_SQLITE_PATH
# 注释行
mcp_server:postgres|TEST_POSTGRES_PATH
"""
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # 导入并测试解析器
            from db_lists_parser import DBListsParser
            
            parser = DBListsParser(str(test_file))
            configs = parser.parse_file()
            
            if len(configs) == 3:
                self.log_test_result("解析配置数量", True, f"解析到 {len(configs)} 个配置")
            else:
                self.log_test_result("解析配置数量", False, f"期望 3 个，实际 {len(configs)} 个")
            
            # 测试环境变量解析
            os.environ["TEST_FILESYSTEM_PATH"] = "/tmp/test.db"
            resolved_configs = parser.resolve_paths()
            
            filesystem_config = next((c for c in resolved_configs if c['mcp_server'] == 'filesystem'), None)
            if filesystem_config and filesystem_config.get('actual_path') == '/tmp/test.db':
                self.log_test_result("环境变量解析", True)
            else:
                self.log_test_result("环境变量解析", False)
            
            # 测试验证功能
            valid_configs, invalid_configs = parser.validate_configs()
            
            # 应该有一个有效配置（filesystem），两个无效配置（环境变量未设置）
            if len(valid_configs) >= 1 and len(invalid_configs) >= 2:
                self.log_test_result("配置验证", True, f"有效: {len(valid_configs)}, 无效: {len(invalid_configs)}")
            else:
                self.log_test_result("配置验证", False)
            
            # 清理环境变量
            if "TEST_FILESYSTEM_PATH" in os.environ:
                del os.environ["TEST_FILESYSTEM_PATH"]
            
        except Exception as e:
            self.log_test_result("db_lists_parser 基本功能", False, str(e))
    
    def test_set_system_path_var(self):
        """
        测试 set_SystemPathVar.py 功能
        
        参数:
            无
            
        返回:
            无
        """
        self.log_test_start("set_SystemPathVar 功能测试")
        
        try:
            from set_SystemPathVar import SystemPathVarManager
            
            manager = SystemPathVarManager()
            
            # 测试随机变量名生成
            var_name = manager.generate_random_var_name()
            if len(var_name) == 8 and var_name.startswith("DB_PATH_"):
                self.log_test_result("随机变量名生成", True, f"生成: {var_name}")
            else:
                self.log_test_result("随机变量名生成", False, f"生成: {var_name}")
            
            # 测试环境变量获取
            test_var = "TEST_VAR_FOR_CHECK"
            test_value = "/tmp/test/path"
            os.environ[test_var] = test_value
            
            retrieved_value = manager.get_env_var(test_var)
            if retrieved_value == test_value:
                self.log_test_result("环境变量获取", True)
            else:
                self.log_test_result("环境变量获取", False)
            
            # 测试配置保存和加载
            test_config = {
                "test_integration": {
                    "var_name": test_var,
                    "db_path": test_value,
                    "created_at": "2025-01-01T00:00:00"
                }
            }
            
            success = manager.save_config(test_config)
            loaded_config = manager.load_existing_config()
            
            if success and loaded_config.get("test_integration", {}).get("var_name") == test_var:
                self.log_test_result("配置保存加载", True)
            else:
                self.log_test_result("配置保存加载", False)
            
            # 清理
            if "TEST_VAR_FOR_CHECK" in os.environ:
                del os.environ["TEST_VAR_FOR_CHECK"]
            if os.path.exists("db_path_config.json"):
                os.remove("db_path_config.json")
            
        except Exception as e:
            self.log_test_result("set_SystemPathVar 功能", False, str(e))
    
    def test_check_project_config(self):
        """
        测试 check_project_config.py 功能
        
        参数:
            无
            
        返回:
            无
        """
        self.log_test_start("check_project_config 功能测试")
        
        try:
            from check_project_config import ProjectConfigChecker
            
            checker = ProjectConfigChecker()
            results = checker.check_all_requirements()
            
            # 检查基本结构
            required_keys = [
                "db_lists_valid", "env_vars_set", "paths_exist", 
                "mcp_configs_valid", "project_structure_ok", 
                "overall_status", "issues", "recommendations"
            ]
            
            all_keys_present = all(key in results for key in required_keys)
            self.log_test_result("检查结果结构", all_keys_present)
            
            # 检查项目结构（应该通过）
            if results.get("project_structure_ok"):
                self.log_test_result("项目结构检查", True)
            else:
                self.log_test_result("项目结构检查", False, "项目结构检查失败")
            
            # 检查建议生成
            recommendations = checker.generate_recommendations()
            if len(recommendations) > 0:
                self.log_test_result("建议生成", True, f"生成 {len(recommendations)} 条建议")
            else:
                self.log_test_result("建议生成", False, "未生成建议")
            
        except Exception as e:
            self.log_test_result("check_project_config 功能", False, str(e))
    
    def test_integration_workflow(self):
        """
        测试完整工作流程
        
        参数:
            无
            
        返回:
            无
        """
        self.log_test_start("完整工作流程测试")
        
        try:
            # 1. 创建测试用的 db_lists.txt
            test_db_path = str(self.test_dir / "test_integration.db")
            test_db_lists = self.test_dir / "test_integration_db_lists.txt"
            
            test_content = f"mcp_server:filesystem|TEST_INTEGRATION_DB\n"
            with open(test_db_lists, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # 2. 设置环境变量
            os.environ["TEST_INTEGRATION_DB"] = test_db_path
            
            # 3. 使用解析器解析
            from db_lists_parser import DBListsParser
            parser = DBListsParser(str(test_db_lists))
            configs = parser.parse_file()
            
            if configs:
                self.log_test_result("配置解析", True, f"解析到 {len(configs)} 个配置")
                
                # 4. 验证配置
                resolved_configs = parser.resolve_paths()
                filesystem_config = next((c for c in resolved_configs if c['mcp_server'] == 'filesystem'), None)
                
                if filesystem_config and filesystem_config.get('actual_path') == test_db_path:
                    self.log_test_result("环境变量解析", True)
                    
                    # 5. 生成MCP配置
                    mcp_configs = parser.generate_mcp_configs()
                    if mcp_configs:
                        self.log_test_result("MCP配置生成", True, f"生成 {len(mcp_configs)} 个配置")
                        
                        # 验证MCP配置结构
                        mcp_config = mcp_configs[0]['config']
                        if 'command' in mcp_config and 'args' in mcp_config:
                            self.log_test_result("MCP配置结构", True)
                        else:
                            self.log_test_result("MCP配置结构", False)
                    else:
                        self.log_test_result("MCP配置生成", False)
                else:
                    self.log_test_result("环境变量解析", False)
            else:
                self.log_test_result("配置解析", False)
            
            # 清理
            if "TEST_INTEGRATION_DB" in os.environ:
                del os.environ["TEST_INTEGRATION_DB"]
            
        except Exception as e:
            self.log_test_result("完整工作流程", False, str(e))
    
    def test_error_handling(self):
        """
        测试错误处理
        
        参数:
            无
            
        返回:
            无
        """
        self.log_test_start("错误处理测试")
        
        try:
            from db_lists_parser import DBListsParser
            
            # 测试无效文件格式
            invalid_file = self.test_dir / "invalid_format.txt"
            with open(invalid_file, 'w', encoding='utf-8') as f:
                f.write("invalid line format\n")
                f.write("another invalid line\n")
            
            parser = DBListsParser(str(invalid_file))
            configs = parser.parse_file()
            
            if len(configs) == 0:
                self.log_test_result("无效格式处理", True, "正确处理了无效格式")
            else:
                self.log_test_result("无效格式处理", False)
            
            # 测试不存在的文件
            nonexistent_file = self.test_dir / "nonexistent.txt"
            parser = DBListsParser(str(nonexistent_file))
            configs = parser.parse_file()
            
            if len(configs) == 0:
                self.log_test_result("不存在文件处理", True, "正确处理了不存在的文件")
            else:
                self.log_test_result("不存在文件处理", False)
            
            # 测试无效环境变量名
            invalid_env_file = self.test_dir / "invalid_env.txt"
            with open(invalid_env_file, 'w', encoding='utf-8') as f:
                f.write("mcp_server:filesystem|123invalid\n")  # 以数字开头
            
            parser = DBListsParser(str(invalid_env_file))
            configs = parser.parse_file()
            
            if len(configs) == 0:
                self.log_test_result("无效环境变量名处理", True, "正确处理了无效环境变量名")
            else:
                self.log_test_result("无效环境变量名处理", False)
            
        except Exception as e:
            self.log_test_result("错误处理", False, str(e))
    
    def generate_test_report(self):
        """
        生成测试报告
        
        参数:
            无
            
        返回:
            无
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("测试报告")
        self.logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        self.logger.info(f"总测试数: {total_tests}")
        self.logger.info(f"通过: {passed_tests}")
        self.logger.info(f"失败: {failed_tests}")
        self.logger.info(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            self.logger.info("\n失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    self.logger.info(f"  - {result['test_name']}: {result['message']}")
        
        # 保存测试结果到文件
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": passed_tests/total_tests*100
            },
            "details": self.test_results
        }
        
        report_file = self.test_dir / "test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"\n详细报告已保存到: {report_file}")
        self.logger.info(f"日志文件: {self.log_file}")
    
    def cleanup(self):
        """
        清理测试文件
        
        参数:
            无
            
        返回:
            无
        """
        try:
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
            self.logger.info("测试环境已清理")
        except Exception as e:
            self.logger.error(f"清理测试环境失败: {e}")
    
    def run_all_tests(self):
        """
        运行所有测试
        
        参数:
            无
            
        返回:
            无
        """
        self.logger.info("开始 db_lists.txt 管理工具自动化测试")
        self.logger.info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 运行所有测试
        self.test_db_lists_parser_basic()
        self.test_set_system_path_var()
        self.test_check_project_config()
        self.test_integration_workflow()
        self.test_error_handling()
        
        # 生成报告
        self.generate_test_report()
        
        # 清理
        self.cleanup()
        
        self.logger.info("\n测试完成")


def main():
    """
    主函数
    
    参数:
        无
        
    返回:
        无
    """
    tester = DBListsManagementTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()