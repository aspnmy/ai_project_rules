#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自我进化脚本
功能说明：
1. 监控PG_sub_rulesfiles中的注册规则文件，如果有更新修改，自动对项目文件进行自我检查更新
2. 监控本项目和被开发项目中的文件修改状态，有修改时自动调用脚本进行自我检查和更新
3. 判断PG_ProjectMod模式，确保正确处理不同模式下的规范解释文件
4. 将需要自我进化的文件路径写入到rules/todo_Self-evolution_lists.txt
5. 实现优先级机制：devP模式下自我进化优先级高于人工，proD模式下优先级低于人工

作者：AI Assistant
创建时间：2024年
"""

import os
import sys
import time
import json
import logging
import argparse
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple

# 添加项目路径以便导入rules_loader
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from rules_loader import RulesLoader


class SelfEvolutionMonitor:
    """自我进化监控器类"""
    
    def __init__(self, interval: int = 60):
        """
        初始化自我进化监控器
        
        参数：
            interval: 监控间隔时间（秒）
        """
        # 设置日志
        self.setup_logging()
        
        # 监控间隔
        self.interval = interval
        
        # 项目根目录
        self.project_root = Path(__file__).resolve().parent.parent
        
        # 规则加载器
        self.rules_loader = RulesLoader(str(self.project_root))
        
        # 文件哈希值缓存
        self.rules_hash_cache: Dict[str, str] = {}
        self.project_files_hash_cache: Dict[str, str] = {}
        
        # 自我进化待办文件路径
        self.todo_file_path = self.project_root / 'rules' / 'todo_Self-evolution_lists.txt'
        
        # 人工活动状态文件
        self.user_activity_file = self.project_root / '.trae' / '.user_activity'
        
        # 文件锁定目录
        self.lock_dir = self.project_root / '.trae' / '.locks'
        
        # 冲突日志文件
        self.conflict_log_file = self.project_root / 'Logs' / 'path_conflicts.log'
        
        # 确保目录存在
        self.user_activity_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        
        # 监控线程
        self.monitor_thread = None
        self.running = False
        self.lock = threading.RLock()
        
        self.logger.info("自我进化监控器初始化完成")
    
    def setup_logging(self):
        """
        设置日志配置
        """
        log_dir = Path(__file__).resolve().parent.parent / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'self_evolution.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('SelfEvolution')
    
    def calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """
        计算文件的MD5哈希值
        
        参数：
            file_path: 文件路径
            
        返回：
            Optional[str]: 文件哈希值，如果计算失败返回None
        """
        try:
            if not file_path.exists():
                return None
            
            md5_hash = hashlib.md5()
            with open(file_path, "rb") as f:
                # 分块读取文件
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            
            return md5_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"计算文件哈希值失败 {file_path}: {e}")
            return None
    
    def get_project_mode(self) -> str:
        """
        获取当前项目模式
        
        返回：
            str: 项目模式，默认返回 'devP'
        """
        config = self.rules_loader.get_project_mod_config()
        if config and 'mode' in config:
            return config['mode']
        return 'devP'  # 默认开发模式
    
    def is_user_active(self) -> bool:
        """
        检查用户是否处于活动状态
        
        返回：
            bool: 用户活动状态
        """
        try:
            if not self.user_activity_file.exists():
                return False
            
            # 检查活动文件的时间戳
            modified_time = self.user_activity_file.stat().st_mtime
            current_time = time.time()
            
            # 如果活动文件在过去5分钟内被修改，则认为用户活动
            return (current_time - modified_time) < 300
        except Exception as e:
            self.logger.error(f"检查用户活动状态失败: {e}")
            return False
    
    def should_execute_evolution(self) -> bool:
        """
        判断是否应该执行自我进化
        根据优先级规则：
        - devP模式：自我进化优先级高于人工
        - proD模式：只在用户不活动时执行
        
        返回：
            bool: 是否执行自我进化
        """
        mode = self.get_project_mode()
        user_active = self.is_user_active()
        
        self.logger.debug(f"模式: {mode}, 用户活动状态: {user_active}")
        
        if mode == 'devP':
            return True  # devP模式下总是执行
        else:  # proD模式
            return not user_active  # 只在用户不活动时执行
    
    def get_rule_files_to_monitor(self) -> List[Path]:
        """
        获取需要监控的规则文件列表
        
        返回：
            List[Path]: 规则文件路径列表
        """
        rule_files = []
        
        # 获取主规则文件
        main_rule_path = self.rules_loader.get_active_rule_file_path()
        if main_rule_path:
            rule_files.append(main_rule_path)
        
        # 获取次级规则文件 - 这里已经通过rules_loader处理了路径
        secondary_rules = self.rules_loader.get_secondary_rules_files()
        rule_files.extend(secondary_rules)
        
        # 添加PG_sub_rulesfiles文件本身
        sub_rules_file = self.rules_loader.get_variable('PG_sub_rulesfiles')
        if sub_rules_file:
            # 严格按照规范：处理相对路径前缀
            clean_path = sub_rules_file.lstrip('.\\/')
            
            # 严格按照规范：PG_RuleFileName文件同级目录被视为根目录
            # 直接使用项目根目录构建路径
            sub_rules_path = self.project_root / clean_path
            
            # 确保路径是绝对路径并正确解析
            sub_rules_path = sub_rules_path.resolve()
            
            if sub_rules_path.exists():
                rule_files.append(sub_rules_path)
        
        return rule_files
    
    def scan_project_files(self, extensions: List[str] = None) -> List[Path]:
        """
        扫描项目中的文件
        
        参数：
            extensions: 要扫描的文件扩展名列表，默认扫描常见代码文件
            
        返回：
            List[Path]: 项目文件路径列表
        """
        if extensions is None:
            extensions = ['.py', '.txt', '.md', '.json', '.yaml', '.yml', '.ps1', '.sh']
        
        project_files = []
        
        try:
            # 扫描项目根目录
            for root, dirs, files in os.walk(self.project_root):
                # 跳过.git目录和其他临时目录
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.idea', 'node_modules']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_path = Path(root) / file
                        project_files.append(file_path)
        except Exception as e:
            self.logger.error(f"扫描项目文件失败: {e}")
        
        return project_files
    
    def check_rule_files_changes(self) -> List[Path]:
        """
        检查规则文件是否有变化
        
        返回：
            List[Path]: 有变化的规则文件路径列表
        """
        changed_files = []
        rule_files = self.get_rule_files_to_monitor()
        
        for file_path in rule_files:
            current_hash = self.calculate_file_hash(file_path)
            
            if file_path not in self.rules_hash_cache:
                # 新文件，记录哈希值
                if current_hash:
                    self.rules_hash_cache[file_path] = current_hash
                continue
            
            # 检查是否有变化
            if current_hash != self.rules_hash_cache[file_path]:
                changed_files.append(file_path)
                self.rules_hash_cache[file_path] = current_hash
                self.logger.info(f"检测到规则文件变化: {file_path}")
        
        return changed_files
    
    def check_project_files_changes(self) -> List[Path]:
        """
        检查项目文件是否有变化
        
        返回：
            List[Path]: 有变化的项目文件路径列表
        """
        changed_files = []
        project_files = self.scan_project_files()
        
        for file_path in project_files:
            current_hash = self.calculate_file_hash(file_path)
            
            if file_path not in self.project_files_hash_cache:
                # 新文件，记录哈希值
                if current_hash:
                    self.project_files_hash_cache[file_path] = current_hash
                continue
            
            # 检查是否有变化
            if current_hash != self.project_files_hash_cache[file_path]:
                # 排除自我进化待办文件本身
                if file_path != self.todo_file_path:
                    changed_files.append(file_path)
                    self.logger.info(f"检测到项目文件变化: {file_path}")
                self.project_files_hash_cache[file_path] = current_hash
        
        return changed_files
    
    def add_files_to_todo(self, files: List[Path]):
        """
        将文件添加到自我进化待办列表，考虑路径冲突
        
        参数：
            files: 需要添加的文件路径列表
        """
        if not files:
            return
        
        try:
            # 读取现有待办列表
            existing_files = set()
            if self.todo_file_path.exists():
                with open(self.todo_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 分离文件路径和优先级信息
                            parts = line.split('|', 1)
                            if parts:
                                existing_files.add(parts[0].strip())
            
            # 检查并添加文件，处理冲突
            files_to_add = []
            skipped_files = []
            
            for file_path in files:
                # 检查路径冲突
                has_conflict, conflict_reason = self.check_path_conflicts(file_path)
                
                if str(file_path) in existing_files:
                    continue  # 已经在待办列表中
                
                if has_conflict:
                    # 尝试解决冲突
                    resolution = self.resolve_path_conflict(file_path, conflict_reason)
                    
                    # 根据解决结果决定是否添加
                    if "跳过处理" in resolution:
                        skipped_files.append((file_path, resolution))
                        continue
                
                # 准备添加到待办列表，包含优先级信息
                project_mode = self.get_project_mode()
                priority = "HIGH" if project_mode == 'devP' else "LOW"
                files_to_add.append(f"{file_path}|{priority}|{datetime.now().isoformat()}")
            
            # 写入待办文件
            if files_to_add:
                with open(self.todo_file_path, 'a', encoding='utf-8') as f:
                    f.write("# 待处理文件路径|优先级|添加时间\n")
                    for item in files_to_add:
                        f.write(f"{item}\n")
                        self.logger.info(f"添加到自我进化待办: {item.split('|')[0]}")
            
            # 记录跳过的文件
            for file_path, reason in skipped_files:
                self.logger.info(f"跳过添加到待办: {file_path} - {reason}")
        
        except Exception as e:
            self.logger.error(f"写入自我进化待办文件失败: {e}")
    
    def update_user_activity(self):
        """
        更新用户活动状态文件
        """
        try:
            # 创建或更新活动文件
            with open(self.user_activity_file, 'w', encoding='utf-8') as f:
                f.write(f"Last activity: {datetime.now().isoformat()}")
        except Exception as e:
            self.logger.error(f"更新用户活动文件失败: {e}")
    
    def run_monitor_cycle(self):
        """
        运行一次监控周期
        """
        try:
            with self.lock:
                self.logger.debug("开始监控周期")
                
                # 检查规则文件变化
                changed_rule_files = self.check_rule_files_changes()
                
                # 检查项目文件变化
                changed_project_files = self.check_project_files_changes()
                
                # 合并需要处理的文件
                files_to_process = []
                
                # 如果规则文件变化，需要检查所有项目文件
                if changed_rule_files:
                    self.logger.info(f"规则文件有变化，需要检查所有项目文件")
                    files_to_process = self.scan_project_files()
                elif changed_project_files:
                    # 如果只有项目文件变化，只检查变化的文件
                    files_to_process = changed_project_files
                
                # 如果有需要处理的文件
                if files_to_process and self.should_execute_evolution():
                    # 1. 执行合规性检查和更新
                    self.logger.info(f"开始对 {len(files_to_process)} 个文件进行合规性检查和更新")
                    total_checked, total_updated = self.process_files_for_compliance(files_to_process)
                    
                    # 2. 将未处理的文件添加到待办列表
                    if total_updated < total_checked:
                        self.add_files_to_todo(files_to_process)
                        self.logger.info("传输指令：执行rules/todo_Self-evolution_lists.txt中的todo")
                
                self.logger.debug("监控周期结束")
        
        except Exception as e:
            self.logger.error(f"监控周期执行失败: {e}")
    
    def start_monitoring(self):
        """
        开始持续监控
        """
        self.running = True
        self.logger.info(f"开始持续监控，间隔: {self.interval}秒")
        
        # 初始化哈希缓存
        self.logger.info("初始化文件哈希缓存...")
        for file_path in self.get_rule_files_to_monitor():
            current_hash = self.calculate_file_hash(file_path)
            if current_hash:
                self.rules_hash_cache[file_path] = current_hash
        
        for file_path in self.scan_project_files():
            current_hash = self.calculate_file_hash(file_path)
            if current_hash:
                self.project_files_hash_cache[file_path] = current_hash
        
        # 运行一次初始检查
        self.run_monitor_cycle()
        
        while self.running:
            time.sleep(self.interval)
            self.run_monitor_cycle()
    
    def stop_monitoring(self):
        """
        停止监控
        """
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        self.logger.info("监控已停止")
    
    def start_in_thread(self):
        """
        在单独的线程中启动监控
        """
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.start_monitoring)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("在单独线程中启动监控")
    
    def log_conflict(self, file_path: Path, conflict_reason: str, resolution: str):
        """
        记录路径冲突日志
        
        参数：
            file_path: 冲突的文件路径
            conflict_reason: 冲突原因
            resolution: 解决方式
        """
        try:
            with open(self.conflict_log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                project_mode = self.get_project_mode()
                log_entry = f"[{timestamp}] 文件: {file_path} | 模式: {project_mode} | 原因: {conflict_reason} | 解决: {resolution}\n"
                f.write(log_entry)
            self.logger.info(f"记录冲突日志: {file_path} - {conflict_reason} - {resolution}")
        except Exception as e:
            self.logger.error(f"写入冲突日志失败: {e}")
    
    def get_lock_file_path(self, file_path: Path) -> Path:
        """
        获取文件对应的锁文件路径
        
        参数：
            file_path: 文件路径
            
        返回：
            Path: 锁文件路径
        """
        # 使用文件路径的哈希值作为锁文件名，避免路径分隔符问题
        file_hash = hashlib.md5(str(file_path).encode()).hexdigest()
        return self.lock_dir / f"{file_hash}.lock"
    
    def acquire_file_lock(self, file_path: Path, timeout: int = 5) -> bool:
        """
        获取文件锁
        
        参数：
            file_path: 文件路径
            timeout: 超时时间（秒）
            
        返回：
            bool: 是否成功获取锁
        """
        lock_file = self.get_lock_file_path(file_path)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 尝试创建锁文件
                with open(lock_file, 'x') as f:
                    f.write(f"锁定时间: {datetime.now().isoformat()}\n")
                    f.write(f"进程ID: {os.getpid()}\n")
                return True
            except FileExistsError:
                # 检查锁文件是否过期（超过5分钟）
                try:
                    if lock_file.exists():
                        lock_time = lock_file.stat().st_mtime
                        if time.time() - lock_time > 300:
                            # 锁文件已过期，删除并重试
                            lock_file.unlink()
                            self.logger.warning(f"删除过期的锁文件: {lock_file}")
                except Exception as e:
                    self.logger.error(f"检查锁文件过期状态失败: {e}")
                
                time.sleep(0.1)
        
        return False
    
    def release_file_lock(self, file_path: Path):
        """
        释放文件锁
        
        参数：
            file_path: 文件路径
        """
        lock_file = self.get_lock_file_path(file_path)
        try:
            if lock_file.exists():
                lock_file.unlink()
        except Exception as e:
            self.logger.error(f"释放文件锁失败: {e}")
    
    def is_file_locked(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        检查文件是否被锁定
        
        参数：
            file_path: 文件路径
            
        返回：
            Tuple[bool, Optional[str]]: (是否被锁定, 锁定信息)
        """
        lock_file = self.get_lock_file_path(file_path)
        if not lock_file.exists():
            return False, None
        
        try:
            with open(lock_file, 'r', encoding='utf-8') as f:
                return True, f.read().strip()
        except Exception as e:
            self.logger.error(f"读取锁文件失败: {e}")
            return False, None
    
    def check_path_conflicts(self, file_path: Path) -> Tuple[bool, str]:
        """
        检查文件路径是否与人工编辑冲突，并返回冲突详情
        
        参数：
            file_path: 要检查的文件路径
            
        返回：
            Tuple[bool, str]: (是否存在冲突, 冲突原因)
        """
        project_mode = self.get_project_mode()
        
        # 检查文件是否被锁定
        is_locked, lock_info = self.is_file_locked(file_path)
        if is_locked and lock_info:
            conflict_reason = f"文件被锁定: {lock_info}"
            return True, conflict_reason
        
        # 检查用户活动状态
        user_active = self.is_user_active()
        
        # devP模式下，自我进化优先级高于人工
        if project_mode == 'devP':
            if user_active:
                # 虽然有用户活动，但在devP模式下仍允许自我进化
                return False, "devP模式下自我进化优先级高于人工"
            return False, "无用户活动"
        
        # proD模式下，自我进化优先级低于人工
        if project_mode == 'proD':
            if user_active:
                conflict_reason = "proD模式下用户活动优先级高于自我进化"
                return True, conflict_reason
            return False, "无用户活动"
        
        # 其他模式默认与proD相同
        if user_active:
            conflict_reason = "未知模式下用户活动优先级高于自我进化"
            return True, conflict_reason
        
        return False, "无冲突"
    
    def resolve_path_conflict(self, file_path: Path, conflict_reason: str) -> str:
        """
        根据优先级规则解决路径冲突
        
        参数：
            file_path: 冲突的文件路径
            conflict_reason: 冲突原因
            
        返回：
            str: 解决结果
        """
        project_mode = self.get_project_mode()
        
        # 记录冲突
        self.log_conflict(file_path, conflict_reason, "待处理")
        
        if project_mode == 'devP':
            # devP模式下尝试获取锁并强制处理
            if self.acquire_file_lock(file_path):
                resolution = "devP模式下强制获取锁，执行自我进化"
                self.log_conflict(file_path, conflict_reason, resolution)
                return resolution
            else:
                resolution = "无法获取文件锁，跳过处理"
                self.log_conflict(file_path, conflict_reason, resolution)
                return resolution
        else:
            # proD模式下，尊重用户活动，跳过处理
            resolution = "proD模式下跳过处理，尊重用户活动"
            self.log_conflict(file_path, conflict_reason, resolution)
            return resolution
    
    def check_file_compliance(self, file_path: Path) -> Tuple[bool, List[str], Dict[str, str]]:
        """
        检查单个文件的合规性
        
        参数：
            file_path: 要检查的文件路径
            
        返回：
            Tuple[bool, List[str], Dict[str, str]]: (是否合规, 不合规原因列表, 需要更新的内容字典)
        """
        try:
            if not file_path.exists():
                return False, [f"文件不存在: {file_path}"], {}
            
            # 获取适用的规则
            applicable_rules = self.rules_loader.get_applicable_rules_for_file(str(file_path))
            
            if not applicable_rules:
                self.logger.debug(f"没有适用的规则用于文件: {file_path}")
                return True, [], {}
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
            
            compliance_issues = []
            update_content = {}
            is_compliant = True
            
            # 应用每个规则进行检查
            for rule_name, rule_config in applicable_rules.items():
                # 这里是规则检查的占位符逻辑
                # 实际实现需要根据具体的规则类型和配置进行处理
                self.logger.debug(f"对文件 {file_path} 应用规则 {rule_name}")
                
                # 示例：检查文件头部注释
                if rule_name == 'header_comment':
                    if not file_content.strip().startswith('#') and file_path.suffix in ['.py', '.sh', '.ps1']:
                        compliance_issues.append(f"缺少标准头部注释")
                        update_content['header_comment'] = True
                        is_compliant = False
                
                # 示例：检查编码声明
                if rule_name == 'encoding_declaration' and file_path.suffix == '.py':
                    if '# -*- coding: utf-8 -*-' not in file_content:
                        compliance_issues.append(f"缺少UTF-8编码声明")
                        update_content['encoding_declaration'] = True
                        is_compliant = False
            
            return is_compliant, compliance_issues, update_content
            
        except Exception as e:
            self.logger.error(f"检查文件合规性失败 {file_path}: {e}")
            return False, [f"检查失败: {str(e)}"], {}
    
    def check_project_files_compliance(self, files: List[Path]) -> Dict[str, Tuple[bool, List[str], Dict[str, str]]]:
        """
        批量检查项目文件的合规性
        
        参数：
            files: 要检查的文件路径列表
            
        返回：
            Dict[str, Tuple[bool, List[str], Dict[str, str]]]: 文件路径到检查结果的映射
        """
        results = {}
        
        for file_path in files:
            # 先检查路径冲突
            has_conflict, conflict_reason = self.check_path_conflicts(file_path)
            
            if has_conflict:
                # 尝试解决冲突
                resolution = self.resolve_path_conflict(file_path, conflict_reason)
                
                # 如果冲突解决失败，跳过此文件
                if "跳过处理" in resolution:
                    results[str(file_path)] = (False, [conflict_reason], {})
                    continue
            
            # 进行合规性检查
            is_compliant, issues, update_info = self.check_file_compliance(file_path)
            results[str(file_path)] = (is_compliant, issues, update_info)
        
        return results
    
    def update_file_compliance(self, file_path: Path, update_info: Dict[str, str]) -> bool:
        """
        根据更新信息修复文件合规性问题
        
        参数：
            file_path: 要更新的文件路径
            update_info: 更新信息字典
            
        返回：
            bool: 更新是否成功
        """
        try:
            # 获取文件锁
            if not self.acquire_file_lock(file_path):
                self.logger.error(f"无法获取文件锁，更新失败: {file_path}")
                return False
            
            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                
                # 应用更新
                updated_content = file_content
                
                # 根据更新信息进行相应的修复
                # 添加UTF-8编码声明
                if 'encoding_declaration' in update_info and file_path.suffix == '.py':
                    lines = updated_content.splitlines()
                    if lines:
                        # 检查第一行是否是shebang
                        if lines[0].startswith('#!'):
                            # 在shebang后添加编码声明
                            if len(lines) > 1 and not lines[1].startswith('# -*- coding: utf-8 -*-'):
                                lines.insert(1, '# -*- coding: utf-8 -*-')
                        else:
                            # 在开头添加编码声明
                            lines.insert(0, '# -*- coding: utf-8 -*-')
                        updated_content = '\n'.join(lines)
                
                # 添加头部注释
                if 'header_comment' in update_info:
                    lines = updated_content.splitlines()
                    # 确保有编码声明（如果是Python文件）
                    if file_path.suffix == '.py' and not any('# -*- coding: utf-8 -*-' in line for line in lines[:5]):
                        if lines and lines[0].startswith('#!'):
                            lines.insert(1, '# -*- coding: utf-8 -*-')
                        else:
                            lines.insert(0, '# -*- coding: utf-8 -*-')
                    
                    # 检查是否已有头部注释
                    has_header_comment = False
                    for i, line in enumerate(lines[:10]):
                        if line.strip().startswith('"""') or line.strip().startswith("'''"):
                            has_header_comment = True
                            break
                    
                    # 如果没有头部注释，添加标准头部注释
                    if not has_header_comment:
                        # 找出应该插入注释的位置
                        insert_pos = 0
                        if lines and lines[0].startswith('#!'):
                            insert_pos = 1
                        if insert_pos < len(lines) and lines[insert_pos].startswith('# -*- coding: utf-8 -*-'):
                            insert_pos += 1
                        
                        # 添加头部注释模板
                        header_comment = [
                            '"""',
                            f"{file_path.name}",
                            "功能说明：",
                            "",
                            "作者：自我进化系统",
                            f"更新时间：{datetime.now().strftime('%Y-%m-%d')}",
                            '"""'
                        ]
                        
                        # 插入头部注释
                        for i, line in enumerate(header_comment):
                            lines.insert(insert_pos + i, line)
                        
                        updated_content = '\n'.join(lines)
                
                # 写入更新后的内容
                if updated_content != file_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    self.logger.info(f"成功更新文件: {file_path}")
                    return True
                else:
                    self.logger.debug(f"文件内容未改变，无需更新: {file_path}")
                    return True
                    
            finally:
                # 释放文件锁
                self.release_file_lock(file_path)
                
        except Exception as e:
            self.logger.error(f"更新文件失败 {file_path}: {e}")
            # 确保释放锁
            self.release_file_lock(file_path)
            return False
    
    def process_files_for_compliance(self, files: List[Path]) -> Tuple[int, int]:
        """
        处理文件合规性：检查并更新不合规的文件
        
        参数：
            files: 要处理的文件路径列表
            
        返回：
            Tuple[int, int]: (检查的文件数, 成功更新的文件数)
        """
        # 检查文件合规性
        compliance_results = self.check_project_files_compliance(files)
        
        total_files = len(compliance_results)
        updated_files = 0
        
        # 处理不合规的文件
        for file_path_str, (is_compliant, issues, update_info) in compliance_results.items():
            if not is_compliant and issues and update_info:
                self.logger.warning(f"文件不合规: {file_path_str}")
                for issue in issues:
                    self.logger.warning(f"  - {issue}")
                
                # 尝试更新文件
                file_path = Path(file_path_str)
                if self.update_file_compliance(file_path, update_info):
                    updated_files += 1
                    
                    # 更新哈希缓存
                    new_hash = self.calculate_file_hash(file_path)
                    if new_hash:
                        self.project_files_hash_cache[file_path] = new_hash
        
        self.logger.info(f"合规性检查完成：检查了 {total_files} 个文件，成功更新了 {updated_files} 个文件")
        return total_files, updated_files


def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description='自我进化监控脚本')
    parser.add_argument('--interval', type=int, default=60, help='监控间隔时间（秒）')
    parser.add_argument('--once', action='store_true', help='只运行一次监控周期')
    parser.add_argument('--debug', action='store_true', help='启用调试日志')
    return parser.parse_args()


def main():
    """
    主函数
    """
    args = parse_args()
    
    # 创建监控器
    monitor = SelfEvolutionMonitor(interval=args.interval)
    
    # 如果启用调试模式
    if args.debug:
        logging.getLogger('SelfEvolution').setLevel(logging.DEBUG)
    
    try:
        if args.once:
            # 只运行一次
            monitor.logger.info("运行单次监控")
            monitor.run_monitor_cycle()
        else:
            # 持续运行
            monitor.start_in_thread()
            
            # 等待用户输入以停止
            print("自我进化监控已启动。按Ctrl+C停止...")
            while True:
                time.sleep(1)
    
    except KeyboardInterrupt:
        monitor.logger.info("接收到停止信号")
    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    main()