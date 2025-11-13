#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI项目规则文件拉取脚本
用于自动更新项目规则文件，确保使用最新的规范
"""

import os
import sys
import json
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rule_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class RulePuller:
    """规则文件拉取器"""
    
    def __init__(self, repo_url, local_path):
        """
        初始化拉取器
        
        参数：
            repo_url: GitHub仓库URL
            local_path: 本地规则文件路径
        """
        self.repo_url = repo_url
        self.local_path = Path(local_path)
        self.config_file = self.local_path.parent / 'rule_config.json'
        self.backup_dir = self.local_path.parent / 'backups'
        
        # 确保目录存在
        self.backup_dir.mkdir(exist_ok=True)
        
    def get_github_raw_url(self, filename):
        """获取GitHub原始文件URL"""
        base_url = self.repo_url.replace('github.com', 'raw.githubusercontent.com')
        return f"{base_url}/master/{filename}"
        
    def download_file(self, url, local_file):
        """下载文件"""
        try:
            logging.info(f"正在下载: {url}")
            urllib.request.urlretrieve(url, local_file)
            return True
        except urllib.error.URLError as e:
            logging.error(f"下载失败: {e}")
            return False
            
    def calculate_md5(self, filepath):
        """计算文件MD5"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def backup_current_rules(self):
        """备份当前规则文件"""
        if not self.local_path.exists():
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"project_rules_backup_{timestamp}.md"
        
        try:
            import shutil
            shutil.copy2(self.local_path, backup_file)
            logging.info(f"已备份当前规则到: {backup_file}")
            return backup_file
        except Exception as e:
            logging.error(f"备份失败: {e}")
            return None
            
    def load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            return {
                "last_update": None,
                "current_version": None,
                "auto_sync": True,
                "sync_interval_hours": 72
            }
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"加载配置失败: {e}")
            return self.load_config()  # 返回默认配置
            
    def save_config(self, config):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
            
    def should_update(self, config):
        """判断是否需要更新"""
        if not config.get("auto_sync", True):
            return False
            
        last_update = config.get("last_update")
        if not last_update:
            return True
            
        try:
            last_time = datetime.fromisoformat(last_update)
            interval = timedelta(hours=config.get("sync_interval_hours", 72))
            return datetime.now() - last_time >= interval
        except:
            return True
            
    def update_rules(self):
        """更新规则文件"""
        logging.info("开始检查规则文件更新...")
        
        config = self.load_config()
        
        if not self.should_update(config):
            logging.info("无需更新（未到同步时间）")
            return True
            
        # 备份当前文件
        backup_file = self.backup_current_rules()
        
        # 下载新规则文件
        temp_file = self.local_path.with_suffix('.md.tmp')
        raw_url = self.get_github_raw_url('project_rules.md')
        
        if not self.download_file(raw_url, temp_file):
            logging.error("下载新规则文件失败")
            if backup_file:
                temp_file.unlink(missing_ok=True)
            return False
            
        # 验证文件完整性
        if not temp_file.exists() or temp_file.stat().st_size == 0:
            logging.error("下载的文件为空或不存在")
            temp_file.unlink(missing_ok=True)
            return False
            
        # 比较文件内容
        current_hash = None
        if self.local_path.exists():
            current_hash = self.calculate_md5(self.local_path)
            new_hash = self.calculate_md5(temp_file)
            
            if current_hash == new_hash:
                logging.info("规则文件内容相同，无需更新")
                temp_file.unlink()
                return True
                
        # 替换文件
        try:
            if self.local_path.exists():
                self.local_path.unlink()
            temp_file.rename(self.local_path)
            
            # 更新配置
            config["last_update"] = datetime.now().isoformat()
            config["current_version"] = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.save_config(config)
            
            logging.info("规则文件更新成功")
            return True
            
        except Exception as e:
            logging.error(f"替换文件失败: {e}")
            if backup_file:
                # 恢复备份
                import shutil
                shutil.copy2(backup_file, self.local_path)
            temp_file.unlink(missing_ok=True)
            return False
            
    def show_status(self):
        """显示当前状态"""
        config = self.load_config()
        
        print("\n" + "="*50)
        print("AI项目规则文件状态")
        print("="*50)
        
        if self.local_path.exists():
            file_size = self.local_path.stat().st_size
            modify_time = datetime.fromtimestamp(self.local_path.stat().st_mtime)
            print(f"规则文件: {self.local_path}")
            print(f"文件大小: {file_size} 字节")
            print(f"修改时间: {modify_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("规则文件: 不存在")
            
        print(f"自动同步: {'开启' if config.get('auto_sync') else '关闭'}")
        print(f"同步间隔: {config.get('sync_interval_hours', 72)} 小时")
        
        if config.get("last_update"):
            print(f"最后更新: {config.get('last_update')}")
        if config.get("current_version"):
            print(f"当前版本: {config.get('current_version')}")
            
        print("="*50)
        
def main():
    """主函数"""
    # GitHub仓库地址
    repo_url = "https://github.com/aspnmy/ai_project_rules"
    
    # 本地规则文件路径
    script_dir = Path(__file__).parent
    local_path = script_dir / "project_rules.md"
    
    # 创建拉取器
    puller = RulePuller(repo_url, local_path)
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            puller.show_status()
        elif sys.argv[1] == "update":
            success = puller.update_rules()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "force":
            # 强制更新，忽略时间间隔
            config = puller.load_config()
            config["last_update"] = None
            puller.save_config(config)
            success = puller.update_rules()
            sys.exit(0 if success else 1)
        else:
            print("用法: python rule_puller.py [status|update|force]")
            print("  status - 显示当前状态")
            print("  update - 检查并更新规则文件")
            print("  force  - 强制更新规则文件")
            sys.exit(1)
    else:
        # 默认行为：检查并更新
        success = puller.update_rules()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()