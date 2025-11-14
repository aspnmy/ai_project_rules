#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理todo_Self-evolution_lists.txt文件的脚本
功能：
1. 读取todo列表中的文件路径
2. 对每个文件进行合规性检查
3. 删除检查通过的路径
4. 保存更新后的todo列表

作者：AI Assistant
创建时间：2025-11-15
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 添加rules_loader的导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Util.rules_loader import RulesLoader

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("process_todo_list.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ProcessTodoList")

class TodoListProcessor:
    """todo列表处理器"""
    
    def __init__(self, todo_file_path: str):
        """
        初始化处理器
        
        参数：
            todo_file_path: todo列表文件路径
        """
        self.todo_file_path = Path(todo_file_path)
        self.comment_lines = []  # 存储注释行
        self.todo_entries = []   # 存储todo条目 (path, priority, timestamp)
        # 初始化规则加载器
        self.rules_loader = RulesLoader()
        self.rules_loader.load_rules()
    
    def read_todo_file(self) -> bool:
        """
        读取todo列表文件
        
        返回：
            bool: 是否成功读取
        """
        try:
            if not self.todo_file_path.exists():
                logger.error(f"文件不存在: {self.todo_file_path}")
                return False
            
            with open(self.todo_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('#'):
                    # 这是注释行
                    self.comment_lines.append(line)
                else:
                    # 这是数据行，格式: path|priority|timestamp
                    parts = line.split('|')
                    if len(parts) >= 3:
                        file_path = parts[0].strip()
                        priority = parts[1].strip() if len(parts) > 1 else 'UNKNOWN'
                        timestamp = parts[2].strip() if len(parts) > 2 else ''
                        self.todo_entries.append((file_path, priority, timestamp))
                    else:
                        logger.warning(f"无效的数据行格式: {line}")
            
            logger.info(f"成功读取todo列表，包含 {len(self.todo_entries)} 个条目")
            return True
            
        except Exception as e:
            logger.error(f"读取todo文件失败: {e}")
            return False
    
    def check_file_compliance(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        检查文件的合规性
        
        参数：
            file_path: 要检查的文件路径
            
        返回：
            Tuple[bool, List[str]]: (是否合规, 问题列表)
        """
        issues = []
        path = Path(file_path)
        
        # 1. 检查文件是否存在
        if not path.exists():
            issues.append(f"文件不存在: {file_path}")
            return False, issues
        
        # 2. 检查文件是否为常规文件（非目录）
        if not path.is_file():
            issues.append(f"路径不是文件: {file_path}")
            return False, issues
        
        # 3. 检查文件可读性
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)  # 只读取前1024字节以检查可读性
        except Exception as e:
            issues.append(f"文件读取失败: {file_path}, 错误: {e}")
            return False, issues
        
        # 4. 根据文件类型进行不同的合规性检查
        suffix = path.suffix.lower()
        
        if suffix == '.py':
            # Python文件的检查
            lines = content.splitlines()
            
            # 检查是否有shebang或编码声明
            has_shebang = any(line.startswith('#!') for line in lines[:3])
            has_encoding = any('# -*- coding: utf-8 -*-' in line for line in lines[:5])
            
            if not has_encoding and not has_shebang:
                issues.append(f"Python文件缺少编码声明: {file_path}")
            
            # 检查是否有头部注释
            has_docstring = any(line.strip().startswith('"""') or line.strip().startswith("'''") for line in lines[:10])
            if not has_docstring:
                issues.append(f"Python文件缺少头部文档字符串: {file_path}")
        
        elif suffix in ['.md', '.txt']:
            # Markdown或文本文件的基本检查
            if len(content.strip()) == 0:
                issues.append(f"文件内容为空: {file_path}")
        
        elif suffix == '.json':
            # JSON文件的检查
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError:
                issues.append(f"JSON文件格式错误: {file_path}")
        
        # 如果没有发现问题，则文件合规
        is_compliant = len(issues) == 0
        
        if is_compliant:
            logger.info(f"文件合规: {file_path}")
        else:
            for issue in issues:
                logger.warning(issue)
        
        return is_compliant, issues
    
    def process_todo_entries(self) -> Dict[str, bool]:
        """
        处理所有todo条目
        
        返回：
            Dict[str, bool]: 文件路径到处理结果的映射
        """
        results = {}
        compliant_files = []
        non_compliant_files = []
        
        for file_path, priority, timestamp in self.todo_entries:
            logger.info(f"检查文件: {file_path} (优先级: {priority})")
            is_compliant, issues = self.check_file_compliance(file_path)
            results[file_path] = is_compliant
            
            if is_compliant:
                compliant_files.append((file_path, priority, timestamp))
            else:
                non_compliant_files.append((file_path, priority, timestamp, issues))
        
        # 更新todo条目列表，只保留不合规的文件
        self.todo_entries = non_compliant_files
        
        logger.info(f"处理完成: {len(compliant_files)} 个文件合规，{len(non_compliant_files)} 个文件不合规")
        return results
    
    def save_todo_file(self) -> bool:
        """
        保存更新后的todo列表文件
        
        返回：
            bool: 是否成功保存
        """
        try:
            with open(self.todo_file_path, 'w', encoding='utf-8') as f:
                # 写入注释行
                for comment_line in self.comment_lines:
                    f.write(f"{comment_line}\n")
                
                # 确保有一个空行分隔注释和数据
                if self.todo_entries and not self.comment_lines[-1].startswith('# 待处理文件路径'):
                    f.write("\n")
                
                # 写入不合规的文件条目
                for entry in self.todo_entries:
                    file_path, priority, timestamp, _ = entry  # 第四个元素是issues，不需要写入
                    f.write(f"{file_path}|{priority}|{timestamp}\n")
            
            logger.info(f"成功保存更新后的todo列表到: {self.todo_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存todo文件失败: {e}")
            return False
    
    def run(self) -> bool:
        """
        运行完整的处理流程
        
        返回：
            bool: 是否成功完成处理
        """
        logger.info("开始处理todo列表...")
        
        # 读取todo文件
        if not self.read_todo_file():
            return False
        
        # 处理todo条目
        self.process_todo_entries()
        
        # 保存更新后的文件
        if not self.save_todo_file():
            return False
        
        logger.info("todo列表处理完成")
        return True


def main():
    """主函数"""
    # 默认的todo文件路径
    default_todo_path = "u:\\git\\binwalk\\.trae\\rules\\rules\\todo_Self-evolution_lists.txt"
    
    # 解析命令行参数（可选）
    import argparse
    parser = argparse.ArgumentParser(description='处理todo_Self-evolution_lists.txt文件')
    parser.add_argument('--todo-file', default=default_todo_path, help='todo列表文件路径')
    args = parser.parse_args()
    
    # 创建并运行处理器
    processor = TodoListProcessor(args.todo_file)
    success = processor.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())