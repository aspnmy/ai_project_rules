#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动同步脚本
每72小时自动同步规则文件到GitHub
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import schedule

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class AutoSyncManager:
    """自动同步管理器"""
    
    def __init__(self, repo_path, sync_interval_hours=72):
        """
        初始化同步管理器
        
        参数：
            repo_path: Git仓库路径
            sync_interval_hours: 同步间隔时间（小时）
        """
        self.repo_path = Path(repo_path)
        self.sync_interval = sync_interval_hours
        self.config_file = self.repo_path / 'sync_config.json'
        self.pid_file = self.repo_path / 'auto_sync.pid'
        
    def load_config(self):
        """加载同步配置"""
        if not self.config_file.exists():
            default_config = {
                "last_sync": None,
                "sync_count": 0,
                "auto_sync_enabled": True,
                "sync_interval_hours": self.sync_interval,
                "retry_count": 3,
                "retry_delay_seconds": 300
            }
            self.save_config(default_config)
            return default_config
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"加载配置失败: {e}")
            return self.load_config()  # 返回默认配置
            
    def save_config(self, config):
        """保存同步配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
            
    def is_sync_due(self, config):
        """检查是否需要同步"""
        if not config.get("auto_sync_enabled", True):
            return False
            
        last_sync = config.get("last_sync")
        if not last_sync:
            return True
            
        try:
            last_time = datetime.fromisoformat(last_sync)
            interval = timedelta(hours=config.get("sync_interval_hours", self.sync_interval))
            return datetime.now() - last_time >= interval
        except:
            return True
            
    def check_git_status(self):
        """检查Git状态"""
        try:
            # 检查是否有未提交的更改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                logging.info("发现未提交的更改")
                return True
            else:
                logging.info("工作区干净，无未提交更改")
                return False
                
        except subprocess.CalledProcessError as e:
            logging.error(f"检查Git状态失败: {e}")
            return False
            
    def commit_changes(self, message=None):
        """提交更改"""
        if not message:
            message = f"Auto sync: Update rules - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
        try:
            # 添加所有更改
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True)
            
            # 提交更改
            subprocess.run(['git', 'commit', '-m', message], cwd=self.repo_path, check=True)
            
            logging.info("更改已提交")
            return True
            
        except subprocess.CalledProcessError as e:
            logging.error(f"提交更改失败: {e}")
            return False
            
    def push_to_remote(self, retry_count=3):
        """推送到远程仓库"""
        for attempt in range(retry_count):
            try:
                logging.info(f"推送到远程仓库 (尝试 {attempt + 1}/{retry_count})")
                
                # 先拉取最新更改
                subprocess.run(['git', 'pull', 'origin', 'master'], cwd=self.repo_path, check=True)
                
                # 推送到远程
                result = subprocess.run(
                    ['git', 'push', 'origin', 'master'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                logging.info("成功推送到远程仓库")
                return True
                
            except subprocess.CalledProcessError as e:
                logging.error(f"推送失败 (尝试 {attempt + 1}): {e}")
                
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 300  # 递增等待时间
                    logging.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logging.error("所有重试尝试均失败")
                    return False
                    
        return False
        
    def sync_to_github(self):
        """同步到GitHub"""
        logging.info("开始同步到GitHub...")
        
        # 检查Git状态
        has_changes = self.check_git_status()
        
        if has_changes:
            # 提交更改
            if not self.commit_changes():
                return False
        else:
            logging.info("无更改需要提交")
            
        # 推送到远程
        return self.push_to_remote()
        
    def perform_sync(self):
        """执行同步操作"""
        config = self.load_config()
        
        if not self.is_sync_due(config):
            logging.info("未到同步时间，跳过本次同步")
            return True
            
        logging.info("开始执行自动同步...")
        
        # 执行同步
        success = self.sync_to_github()
        
        # 更新配置
        if success:
            config["last_sync"] = datetime.now().isoformat()
            config["sync_count"] = config.get("sync_count", 0) + 1
            self.save_config(config)
            logging.info("同步完成")
        else:
            logging.error("同步失败")
            
        return success
        
    def run_scheduler(self):
        """运行定时调度器"""
        # 创建PID文件
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
        except Exception as e:
            logging.error(f"创建PID文件失败: {e}")
            return
            
        logging.info(f"启动自动同步调度器，每{self.sync_interval}小时同步一次")
        
        # 立即执行一次同步
        self.perform_sync()
        
        # 设置定时任务
        schedule.every(self.sync_interval).hours.do(self.perform_sync)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(3600)  # 每小时检查一次
                
        except KeyboardInterrupt:
            logging.info("用户中断，停止调度器")
        except Exception as e:
            logging.error(f"调度器运行错误: {e}")
        finally:
            # 清理PID文件
            try:
                self.pid_file.unlink()
            except:
                pass
                
    def stop_scheduler(self):
        """停止调度器"""
        if not self.pid_file.exists():
            logging.info("调度器未运行")
            return
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                
            # 终止进程
            os.kill(pid, 9)
            logging.info(f"已停止调度器进程 {pid}")
            
            # 清理PID文件
            self.pid_file.unlink()
            
        except Exception as e:
            logging.error(f"停止调度器失败: {e}")
            
    def show_status(self):
        """显示同步状态"""
        config = self.load_config()
        
        print("\n" + "="*60)
        print("自动同步管理器状态")
        print("="*60)
        
        print(f"仓库路径: {self.repo_path}")
        print(f"同步间隔: {config.get('sync_interval_hours', self.sync_interval)} 小时")
        print(f"自动同步: {'开启' if config.get('auto_sync_enabled') else '关闭'}")
        print(f"同步次数: {config.get('sync_count', 0)}")
        
        if config.get("last_sync"):
            print(f"最后同步: {config.get('last_sync')}")
            
        # 检查调度器状态
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                    
                # 检查进程是否存在
                os.kill(pid, 0)
                print(f"调度器状态: 运行中 (PID: {pid})")
            except:
                print("调度器状态: PID文件存在但进程未运行")
        else:
            print("调度器状态: 未运行")
            
        print("="*60)

def main():
    """主函数"""
    repo_path = Path(__file__).parent
    sync_manager = AutoSyncManager(repo_path)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            sync_manager.run_scheduler()
        elif sys.argv[1] == "stop":
            sync_manager.stop_scheduler()
        elif sys.argv[1] == "status":
            sync_manager.show_status()
        elif sys.argv[1] == "sync":
            success = sync_manager.perform_sync()
            sys.exit(0 if success else 1)
        else:
            print("用法: python auto_sync.py [start|stop|status|sync]")
            print("  start  - 启动自动同步调度器")
            print("  stop   - 停止自动同步调度器")
            print("  status - 显示同步状态")
            print("  sync   - 立即执行一次同步")
            sys.exit(1)
    else:
        # 默认行为：执行一次同步
        success = sync_manager.perform_sync()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()