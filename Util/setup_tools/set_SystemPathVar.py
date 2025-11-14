#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统环境变量设置工具
用于安全地设置数据库路径等敏感信息到系统环境变量

参数:
    无
    
返回:
    无
"""

import os
import sys
import json
import secrets
import string
from pathlib import Path


class SystemPathVarManager:
    """
    系统环境变量管理器
    用于安全地管理数据库路径等敏感信息
    """
    
    def __init__(self):
        """
        初始化系统环境变量管理器
        
        参数:
            无
        """
        self.config_file = Path("db_path_config.json")
        self.env_vars = {}
    
    def generate_random_var_name(self, length=8):
        """
        生成随机环境变量名称
        
        参数:
            length (int): 随机字符串长度，默认为8
            
        返回:
            str: 随机环境变量名称
        """
        alphabet = string.ascii_letters + string.digits
        random_part = ''.join(secrets.choice(alphabet) for _ in range(length))
        return f"DB_PATH_{random_part}"
    
    def load_existing_config(self):
        """
        加载现有配置文件
        
        参数:
            无
            
        返回:
            dict: 配置字典
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return {}
        return {}
    
    def save_config(self, config):
        """
        保存配置文件
        
        参数:
            config (dict): 配置字典
            
        返回:
            bool: 保存是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def set_windows_env_var(self, var_name, var_value):
        """
        设置Windows系统环境变量
        
        参数:
            var_name (str): 环境变量名称
            var_value (str): 环境变量值
            
        返回:
            bool: 设置是否成功
        """
        try:
            import winreg
            
            # 设置用户环境变量
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Environment", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, var_name, 0, winreg.REG_SZ, var_value)
            winreg.CloseKey(key)
            
            # 广播环境变量变更消息
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            SMTO_ABORTIFHUNG = 0x0002
            
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, 
                "Environment", SMTO_ABORTIFHUNG, 5000, 0)
            
            return True
        except Exception as e:
            print(f"设置Windows环境变量失败: {e}")
            return False
    
    def set_unix_env_var(self, var_name, var_value):
        """
        设置Unix/Linux系统环境变量
        
        参数:
            var_name (str): 环境变量名称
            var_value (str): 环境变量值
            
        返回:
            bool: 设置是否成功
        """
        try:
            shell_config = Path.home() / ".bashrc"
            if not shell_config.exists():
                shell_config = Path.home() / ".profile"
            
            # 读取现有配置
            existing_lines = []
            if shell_config.exists():
                with open(shell_config, 'r', encoding='utf-8') as f:
                    existing_lines = f.readlines()
            
            # 移除旧的环境变量定义
            new_lines = []
            export_line = f"export {var_name}=\"{var_value}\"\n"
            
            for line in existing_lines:
                if not line.strip().startswith(f"export {var_name}="):
                    new_lines.append(line)
            
            # 添加新的环境变量定义
            new_lines.append(f"\n# Database path configuration\n")
            new_lines.append(export_line)
            
            # 写回文件
            with open(shell_config, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            return True
        except Exception as e:
            print(f"设置Unix环境变量失败: {e}")
            return False
    
    def set_env_var(self, var_name, var_value):
        """
        设置系统环境变量（跨平台）
        
        参数:
            var_name (str): 环境变量名称
            var_value (str): 环境变量值
            
        返回:
            bool: 设置是否成功
        """
        if sys.platform == "win32":
            return self.set_windows_env_var(var_name, var_value)
        else:
            return self.set_unix_env_var(var_name, var_value)
    
    def get_env_var(self, var_name):
        """
        获取环境变量值
        
        参数:
            var_name (str): 环境变量名称
            
        返回:
            str: 环境变量值，如果不存在则返回None
        """
        return os.environ.get(var_name)
    
    def interactive_setup(self):
        """
        交互式设置环境变量
        
        参数:
            无
            
        返回:
            无
        """
        print("=" * 60)
        print("系统环境变量设置工具")
        print("=" * 60)
        print("本工具用于安全地设置数据库路径等敏感信息")
        print("将实际路径存储在系统环境变量中，避免在代码中硬编码")
        print()
        
        # 加载现有配置
        config = self.load_existing_config()
        
        while True:
            print("\n选项:")
            print("1. 添加新的数据库路径")
            print("2. 查看现有配置")
            print("3. 测试环境变量")
            print("4. 删除配置")
            print("5. 退出")
            
            choice = input("\n请选择操作 (1-5): ").strip()
            
            if choice == "1":
                self.add_new_config(config)
            elif choice == "2":
                self.view_config(config)
            elif choice == "3":
                self.test_env_vars(config)
            elif choice == "4":
                self.delete_config(config)
            elif choice == "5":
                print("感谢使用！")
                break
            else:
                print("无效选择，请重新输入")
    
    def add_new_config(self, config):
        """
        添加新的配置
        
        参数:
            config (dict): 现有配置字典
            
        返回:
            无
        """
        print("\n添加新的数据库路径配置")
        print("-" * 40)
        
        # 获取配置名称
        name = input("请输入配置名称 (如: koala_db): ").strip()
        if not name:
            print("配置名称不能为空")
            return
        
        # 获取数据库文件路径
        db_path = input("请输入数据库文件完整路径 (如: D://你的机密项目文件路径//文件名): ").strip()
        if not db_path:
            print("数据库路径不能为空")
            return
        
        # 检查文件是否存在
        if not Path(db_path).exists():
            print(f"警告: 文件 {db_path} 不存在")
            confirm = input("是否继续? (y/n): ").strip().lower()
            if confirm != 'y':
                return
        
        # 生成随机环境变量名称
        var_name = self.generate_random_var_name()
        
        # 设置环境变量
        if self.set_env_var(var_name, db_path):
            print(f"✓ 环境变量 {var_name} 设置成功")
            
            # 保存配置
            config[name] = {
                "var_name": var_name,
                "db_path": db_path,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            if self.save_config(config):
                print(f"✓ 配置 {name} 保存成功")
                print(f"环境变量名: {var_name}")
                print(f"数据库路径: {db_path}")
            else:
                print("✗ 配置保存失败")
        else:
            print("✗ 环境变量设置失败")
    
    def view_config(self, config):
        """
        查看现有配置
        
        参数:
            config (dict): 配置字典
            
        返回:
            无
        """
        if not config:
            print("当前没有配置")
            return
        
        print("\n现有配置:")
        print("-" * 60)
        for name, info in config.items():
            print(f"配置名称: {name}")
            print(f"环境变量: {info['var_name']}")
            print(f"数据库路径: {info['db_path']}")
            print(f"创建时间: {info['created_at']}")
            print("-" * 40)
    
    def test_env_vars(self, config):
        """
        测试环境变量
        
        参数:
            config (dict): 配置字典
            
        返回:
            无
        """
        if not config:
            print("当前没有配置可测试")
            return
        
        print("\n测试环境变量:")
        print("-" * 40)
        
        for name, info in config.items():
            var_name = info['var_name']
            expected_path = info['db_path']
            
            actual_value = self.get_env_var(var_name)
            
            print(f"配置: {name}")
            print(f"环境变量: {var_name}")
            print(f"期望值: {expected_path}")
            print(f"实际值: {actual_value}")
            
            if actual_value == expected_path:
                print("✓ 测试通过")
            else:
                print("✗ 测试失败")
                print(f"文件存在: {Path(actual_value).exists() if actual_value else 'N/A'}")
            
            print("-" * 40)
    
    def delete_config(self, config):
        """
        删除配置
        
        参数:
            config (dict): 配置字典
            
        返回:
            无
        """
        if not config:
            print("当前没有配置可删除")
            return
        
        print("\n现有配置:")
        for i, name in enumerate(config.keys(), 1):
            print(f"{i}. {name}")
        
        choice = input("请输入要删除的配置编号 (或输入名称): ").strip()
        
        # 处理数字输入
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(config):
                name = list(config.keys())[idx]
            else:
                print("无效编号")
                return
        else:
            name = choice
        
        if name in config:
            confirm = input(f"确认删除配置 {name}? (y/n): ").strip().lower()
            if confirm == 'y':
                del config[name]
                if self.save_config(config):
                    print(f"✓ 配置 {name} 删除成功")
                else:
                    print("✗ 配置删除失败")
        else:
            print(f"配置 {name} 不存在")


def main():
    """
    主函数
    
    参数:
        无
        
    返回:
        无
    """
    manager = SystemPathVarManager()
    manager.interactive_setup()


if __name__ == "__main__":
    main()