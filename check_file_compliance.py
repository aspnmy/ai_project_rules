#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件结构合规性检查工具

该脚本用于对项目根目录递归执行文件结构和路径结构的合规性检查，
识别新增文件类型并生成合规性报告。
"""

import os
import json
import logging
import argparse
from collections import defaultdict
import pathlib
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置为DEBUG以查看详细信息
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("compliance_check.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ComplianceChecker")

class FileComplianceChecker:
    """
    文件合规性检查器类
    """
    
    def __init__(self, root_dir, rules_dir):
        """
        初始化合规性检查器
        
        Args:
            root_dir: 要检查的项目根目录
            rules_dir: 规则文件所在目录
        """
        self.root_dir = root_dir
        self.rules_dir = rules_dir
        self.file_types = defaultdict(list)  # 记录每种文件类型的示例路径
        self.existing_rules = set()  # 现有的规则类型
        self.missing_rules = set()  # 缺少规则的文件类型
        
    def load_existing_rules(self):
        """
        加载现有的合规规则
        
        Returns:
            set: 包含所有已有规则文件类型的集合
        """
        try:
            # 明确指定已支持的文件类型扩展
            self.existing_rules = set([
                '.py', '.js', '.json', '.md', '.sh', '.bat', '.ps1',  # 原有规则
                '.css', '.yml', '.yaml', '.csv', '.txt', '.info', '.log', '.offline', '.example'  # 新增规则
            ])
            
            # 检查规则文件目录，以确认所有规则文件都存在
            required_rules = {
                '.py': 'python_rules.txt',
                '.js': 'js_coding_rules.txt',
                '.json': 'json_rules.txt',
                '.md': 'markdown_rules.txt',
                '.sh': 'bash_rules.txt',
                '.bat': 'batch_rules.txt',
                '.ps1': 'powershell_rules.txt',
                '.css': 'css_rules.txt',
                '.yml': 'yaml_rules.txt',
                '.yaml': 'yaml_rules.txt',
                '.csv': 'csv_rules.txt',
                '.txt': 'text_rules.txt',
                '.info': 'text_rules.txt',
                '.log': 'text_rules.txt',
                '.offline': 'text_rules.txt',
                '.example': 'text_rules.txt'
            }
            
            # 验证规则文件是否存在
            for ext, rule_file in required_rules.items():
                # 正确构建规则文件路径 - 规则文件位于当前目录下的rules子目录
                if 'rules' not in self.rules_dir:
                    rule_path = os.path.join(self.rules_dir, 'rules', rule_file)
                else:
                    rule_path = os.path.join(self.rules_dir, rule_file)
                
                if os.path.exists(rule_path):
                    logger.info(f"找到规则文件 {rule_file} 用于 {ext} 在 {rule_path}")
                else:
                    # 尝试另一种路径组合
                    alt_path = os.path.join(self.rules_dir, 'rules', rule_file)
                    if os.path.exists(alt_path):
                        logger.info(f"找到规则文件 {rule_file} 用于 {ext} 在 {alt_path}")
                    else:
                        logger.warning(f"警告: 规则文件 {rule_file} 不存在，但仍将 {ext} 标记为受支持")
            
            logger.info(f"已加载现有规则: {', '.join(sorted(self.existing_rules))}")
            return self.existing_rules
        except Exception as e:
            logger.error(f"加载规则时出错: {e}")
            return set()
    
    def _is_commented(self, line):
        """
        检查一行文本是否为注释
        
        Args:
            line: 要检查的文本行
            
        Returns:
            bool: 如果是注释返回True，否则返回False
        """
        # 检查是否在注释块中或单行注释
        comment_markers = ['#', '//', '/*', '*/']
        # 简单检查，实际可能需要更复杂的解析
        return any(marker in line and not self._in_string(line, line.find(marker)) for marker in comment_markers)
    
    def _in_string(self, line, pos):
        """
        检查位置是否在字符串内
        
        Args:
            line: 文本行
            pos: 要检查的位置
            
        Returns:
            bool: 如果在字符串内返回True
        """
        in_string = False
        string_char = None
        
        for i in range(pos):
            # 跳过转义字符
            if i > 0 and line[i-1] == '\\':
                continue
            # 检查字符串边界
            if line[i] in ['"', "'"] and (string_char is None or string_char == line[i]):
                in_string = not in_string
                if in_string:
                    string_char = line[i]
                else:
                    string_char = None
        
        return in_string
    
    def scan_directory(self):
        """
        递归扫描目录结构，收集所有文件类型
        
        Returns:
            dict: 文件类型到示例路径的映射
        """
        try:
            logger.info(f"开始扫描目录: {self.root_dir}")
            
            for root, dirs, files in os.walk(self.root_dir):
                # 跳过隐藏目录和临时文件目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    # 跳过隐藏文件
                    if file.startswith('.'):
                        continue
                    
                    # 获取文件扩展名
                    file_ext = pathlib.Path(file).suffix.lower()
                    if not file_ext:
                        file_ext = '[无扩展名]'
                    
                    # 记录文件路径示例
                    file_path = os.path.join(root, file)
                    if len(self.file_types[file_ext]) < 3:  # 只记录前3个示例
                        self.file_types[file_ext].append(file_path)
            
            logger.info(f"扫描完成，共发现 {len(self.file_types)} 种文件类型")
            return self.file_types
        except Exception as e:
            logger.error(f"扫描目录时出错: {e}")
            return {}
    
    def identify_missing_rules(self):
        """
        识别缺少规则的文件类型
        
        Returns:
            set: 缺少规则的文件类型集合
        """
        # 加载现有规则
        self.load_existing_rules()
        
        # 识别缺少规则的文件类型
        for file_ext in self.file_types.keys():
            if file_ext != '[无扩展名]' and file_ext not in self.existing_rules:
                self.missing_rules.add(file_ext)
        
        logger.info(f"发现 {len(self.missing_rules)} 种文件类型缺少合规规则")
        return self.missing_rules
    
    def generate_report(self, output_file="compliance_report.json"):
        """
        生成合规性检查报告
        
        Args:
            output_file: 报告输出文件路径
            
        Returns:
            dict: 包含合规性检查结果的字典
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "root_directory": self.root_dir,
            "total_file_types": len(self.file_types),
            "total_existing_rules": len(self.existing_rules),
            "missing_rules_count": len(self.missing_rules),
            "all_file_types": dict(self.file_types),
            "existing_rules": list(sorted(self.existing_rules)),
            "missing_rules": list(sorted(self.missing_rules)),
            "recommendations": []
        }
        
        # 生成建议
        if self.missing_rules:
            for file_ext in sorted(self.missing_rules):
                report["recommendations"].append({
                    "file_type": file_ext,
                    "action": "创建新的规则文件或在现有规则文件中添加该文件类型的规则",
                    "examples": self.file_types.get(file_ext, [])
                })
        
        # 保存报告
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"合规性检查报告已保存至: {output_file}")
        except Exception as e:
            logger.error(f"保存报告时出错: {e}")
        
        # 同时生成markdown格式报告
        self._generate_markdown_report(report)
        
        return report
    
    def _generate_markdown_report(self, report):
        """
        生成markdown格式的合规性检查报告
        
        Args:
            report: 合规性检查报告数据
        """
        md_report = f"""
# 文件结构合规性检查报告

## 摘要
- **检查时间**: {report['timestamp']}
- **检查目录**: {report['root_directory']}
- **文件类型总数**: {report['total_file_types']}
- **现有规则数量**: {report['total_existing_rules']}
- **缺少规则的文件类型**: {report['missing_rules_count']}

## 现有规则文件类型
```
{', '.join(report['existing_rules'])}
```

## 缺少规则的文件类型
```
{', '.join(report['missing_rules'])}
```

## 文件类型详情
"""
        
        # 添加每个文件类型的详细信息
        for file_ext, examples in sorted(report['all_file_types'].items()):
            status = "✅ 已有规则" if file_ext in report['existing_rules'] else "❌ 缺少规则"
            md_report += f"\n### {file_ext} {status}\n\n**示例文件:**\n"
            for example in examples:
                rel_path = os.path.relpath(example, report['root_directory'])
                md_report += f"- `{rel_path}`\n"
        
        # 保存markdown报告
        try:
            with open("compliance_report.md", 'w', encoding='utf-8') as f:
                f.write(md_report)
            logger.info("合规性检查报告(Markdown格式)已保存至: compliance_report.md")
        except Exception as e:
            logger.error(f"保存Markdown报告时出错: {e}")
    
    def run_full_check(self):
        """
        执行完整的合规性检查流程
        
        Returns:
            dict: 合规性检查报告
        """
        logger.info("开始执行完整的文件结构合规性检查...")
        
        # 1. 扫描目录，收集文件类型
        self.scan_directory()
        
        # 2. 识别缺少规则的文件类型
        self.identify_missing_rules()
        
        # 3. 生成报告
        report = self.generate_report()
        
        logger.info("合规性检查完成！")
        return report

def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='文件结构合规性检查工具')
    parser.add_argument('--root-dir', default=r'u:\git\binwalk\.trae\rules', 
                       help='要检查的项目根目录')
    parser.add_argument('--rules-dir', default=r'u:\git\binwalk\.trae\rules\rules', 
                       help='规则文件所在目录')
    args = parser.parse_args()
    
    # 创建合规性检查器实例
    checker = FileComplianceChecker(args.root_dir, args.rules_dir)
    
    # 执行检查
    report = checker.run_full_check()
    
    # 打印结果摘要
    print(f"\n=== 合规性检查结果摘要 ===")
    print(f"检查目录: {report['root_directory']}")
    print(f"文件类型总数: {report['total_file_types']}")
    print(f"现有规则数量: {report['total_existing_rules']}")
    print(f"缺少规则的文件类型: {report['missing_rules_count']}")
    
    if report['missing_rules']:
        print(f"\n缺少规则的文件类型列表:")
        for file_ext in sorted(report['missing_rules']):
            print(f"- {file_ext}")
    
    print(f"\n详细报告已保存至: compliance_report.json 和 compliance_report.md")

if __name__ == "__main__":
    main()