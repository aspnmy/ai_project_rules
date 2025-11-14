#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_lists.txt 解析器
用于解析和处理db_lists.txt文件中的MCP服务器配置

参数:
    无
    
返回:
    无
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DBListsParser:
    """
    db_lists.txt 文件解析器
    支持解析MCP服务器配置和环境变量引用
    """
    
    def __init__(self, db_lists_path: str = "db_lists.txt"):
        """
        初始化解析器
        
        参数:
            db_lists_path (str): db_lists.txt文件路径，默认为"db_lists.txt"
        """
        self.db_lists_path = Path(db_lists_path)
        self.configs = []
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        设置日志记录器
        
        参数:
            无
            
        返回:
            logging.Logger: 日志记录器实例
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def parse_file(self) -> List[Dict[str, str]]:
        """
        解析db_lists.txt文件
        
        参数:
            无
            
        返回:
            List[Dict[str, str]]: 配置列表，每个配置包含mcp_server和system_path_var
        """
        if not self.db_lists_path.exists():
            self.logger.error(f"文件 {self.db_lists_path} 不存在")
            return []
        
        configs = []
        
        try:
            with open(self.db_lists_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                # 解析配置行
                config = self._parse_line(line, line_num)
                if config:
                    configs.append(config)
            
            self.configs = configs
            self.logger.info(f"成功解析 {len(configs)} 个配置")
            return configs
            
        except Exception as e:
            self.logger.error(f"解析文件失败: {e}")
            return []
    
    def _parse_line(self, line: str, line_num: int) -> Optional[Dict[str, str]]:
        """
        解析单行配置
        
        参数:
            line (str): 配置行内容
            line_num (int): 行号
            
        返回:
            Optional[Dict[str, str]]: 解析结果，失败返回None
        """
        # 匹配格式: mcp_server:${mcp_server_name}|${system_path_var}
        pattern = r'mcp_server:([^|]+)\|(.+)'
        match = re.match(pattern, line)
        
        if not match:
            self.logger.warning(f"第{line_num}行格式无效: {line}")
            return None
        
        mcp_server = match.group(1).strip()
        system_path_var = match.group(2).strip()
        
        # 验证环境变量格式
        if not self._validate_env_var_name(system_path_var):
            self.logger.warning(f"第{line_num}行环境变量名无效: {system_path_var}")
            return None
        
        config = {
            'mcp_server': mcp_server,
            'system_path_var': system_path_var,
            'line_num': line_num,
            'raw_line': line
        }
        
        self.logger.debug(f"解析配置: {mcp_server} -> {system_path_var}")
        return config
    
    def _validate_env_var_name(self, var_name: str) -> bool:
        """
        验证环境变量名称格式
        
        参数:
            var_name (str): 环境变量名称
            
        返回:
            bool: 是否有效
        """
        # 环境变量名称规则：字母、数字、下划线，不能以数字开头
        pattern = r'^[A-Za-z_][A-Za-z0-9_]*$'
        return bool(re.match(pattern, var_name))
    
    def resolve_paths(self) -> List[Dict[str, str]]:
        """
        解析环境变量引用的实际路径
        
        参数:
            无
            
        返回:
            List[Dict[str, str]]: 包含实际路径的配置列表
        """
        if not self.configs:
            self.parse_file()
        
        resolved_configs = []
        
        for config in self.configs:
            mcp_server = config['mcp_server']
            system_path_var = config['system_path_var']
            
            # 获取环境变量值
            actual_path = self._get_env_var_value(system_path_var)
            
            resolved_config = {
                'mcp_server': mcp_server,
                'system_path_var': system_path_var,
                'actual_path': actual_path,
                'path_exists': Path(actual_path).exists() if actual_path else False,
                'line_num': config['line_num']
            }
            
            resolved_configs.append(resolved_config)
            
            if actual_path:
                self.logger.info(f"{mcp_server}: {system_path_var} -> {actual_path}")
            else:
                self.logger.warning(f"{mcp_server}: 环境变量 {system_path_var} 未设置")
        
        return resolved_configs
    
    def _get_env_var_value(self, var_name: str) -> Optional[str]:
        """
        获取环境变量值
        
        参数:
            var_name (str): 环境变量名称
            
        返回:
            Optional[str]: 环境变量值，不存在返回None
        """
        return os.environ.get(var_name)
    
    def validate_configs(self) -> Tuple[List[Dict], List[Dict]]:
        """
        验证配置的有效性
        
        参数:
            无
            
        返回:
            Tuple[List[Dict], List[Dict]]: (有效配置列表, 无效配置列表)
        """
        resolved_configs = self.resolve_paths()
        
        valid_configs = []
        invalid_configs = []
        
        for config in resolved_configs:
            issues = []
            
            # 检查环境变量是否设置
            if not config['actual_path']:
                issues.append(f"环境变量 {config['system_path_var']} 未设置")
            else:
                # 检查路径是否存在
                if not config['path_exists']:
                    issues.append(f"路径 {config['actual_path']} 不存在")
                else:
                    # 检查是否为文件
                    path = Path(config['actual_path'])
                    if path.is_file():
                        # 检查文件扩展名
                        if not self._is_valid_db_file(path):
                            issues.append(f"文件类型不支持: {path.suffix}")
                    elif path.is_dir():
                        # 检查目录是否包含数据库文件
                        if not self._contains_db_files(path):
                            issues.append("目录中未找到数据库文件")
            
            if issues:
                config['issues'] = issues
                invalid_configs.append(config)
            else:
                valid_configs.append(config)
        
        return valid_configs, invalid_configs
    
    def _is_valid_db_file(self, file_path: Path) -> bool:
        """
        检查是否为有效的数据库文件
        
        参数:
            file_path (Path): 文件路径
            
        返回:
            bool: 是否有效
        """
        valid_extensions = {'.mdb', '.accdb', '.db', '.sqlite', '.sqlite3', 
                           '.db3', '.dbf', '.csv', '.json', '.xml'}
        return file_path.suffix.lower() in valid_extensions
    
    def _contains_db_files(self, dir_path: Path) -> bool:
        """
        检查目录是否包含数据库文件
        
        参数:
            dir_path (Path): 目录路径
            
        返回:
            bool: 是否包含数据库文件
        """
        try:
            for file_path in dir_path.iterdir():
                if file_path.is_file() and self._is_valid_db_file(file_path):
                    return True
            return False
        except Exception:
            return False
    
    def generate_mcp_configs(self) -> List[Dict[str, str]]:
        """
        生成MCP服务器配置
        
        参数:
            无
            
        返回:
            List[Dict[str, str]]: MCP配置列表
        """
        valid_configs, _ = self.validate_configs()
        mcp_configs = []
        
        for config in valid_configs:
            mcp_server = config['mcp_server']
            actual_path = config['actual_path']
            
            # 生成MCP配置
            mcp_config = self._generate_mcp_config(mcp_server, actual_path)
            if mcp_config:
                mcp_configs.append({
                    'mcp_server': mcp_server,
                    'config': mcp_config,
                    'path': actual_path
                })
        
        return mcp_configs
    
    def _generate_mcp_config(self, mcp_server: str, path: str) -> Optional[Dict]:
        """
        生成单个MCP服务器配置
        
        参数:
            mcp_server (str): MCP服务器名称
            path (str): 实际路径
            
        返回:
            Optional[Dict]: MCP配置，失败返回None
        """
        if mcp_server == "filesystem":
            return {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", path]
            }
        elif mcp_server == "sqlite":
            return {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", path]
            }
        elif mcp_server == "postgres":
            return {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres", path]
            }
        else:
            # 通用配置模板
            return {
                "command": "npx",
                "args": ["-y", f"@modelcontextprotocol/server-{mcp_server}", path]
            }
    
    def export_config(self, output_file: str = "mcp_configs.json") -> bool:
        """
        导出配置到文件
        
        参数:
            output_file (str): 输出文件路径，默认为"mcp_configs.json"
            
        返回:
            bool: 是否成功导出
        """
        try:
            valid_configs, invalid_configs = self.validate_configs()
            mcp_configs = self.generate_mcp_configs()
            
            export_data = {
                "valid_configs": valid_configs,
                "invalid_configs": invalid_configs,
                "mcp_configs": mcp_configs,
                "summary": {
                    "total_configs": len(self.configs),
                    "valid_configs": len(valid_configs),
                    "invalid_configs": len(invalid_configs),
                    "mcp_configs": len(mcp_configs)
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"配置已导出到 {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出配置失败: {e}")
            return False
    
    def print_summary(self):
        """
        打印配置摘要
        
        参数:
            无
            
        返回:
            无
        """
        if not self.configs:
            self.parse_file()
        
        valid_configs, invalid_configs = self.validate_configs()
        
        print("\n" + "=" * 60)
        print("db_lists.txt 配置摘要")
        print("=" * 60)
        print(f"总配置数: {len(self.configs)}")
        print(f"有效配置: {len(valid_configs)}")
        print(f"无效配置: {len(invalid_configs)}")
        
        if valid_configs:
            print("\n有效配置:")
            for config in valid_configs:
                print(f"  ✓ {config['mcp_server']}: {config['actual_path']}")
        
        if invalid_configs:
            print("\n无效配置:")
            for config in invalid_configs:
                print(f"  ✗ {config['mcp_server']}: {config['system_path_var']}")
                for issue in config.get('issues', []):
                    print(f"    - {issue}")
        
        print("=" * 60)


def main():
    """
    主函数
    
    参数:
        无
        
    返回:
        无
    """
    parser = DBListsParser()
    
    # 解析文件
    configs = parser.parse_file()
    if not configs:
        print("未找到有效配置")
        return
    
    # 打印摘要
    parser.print_summary()
    
    # 导出配置
    if parser.export_config():
        print("配置已导出到 mcp_configs.json")
    
    # 生成MCP配置
    mcp_configs = parser.generate_mcp_configs()
    if mcp_configs:
        print(f"\n生成了 {len(mcp_configs)} 个MCP配置")
        for config in mcp_configs:
            print(f"  - {config['mcp_server']}: {config['path']}")


if __name__ == "__main__":
    main()