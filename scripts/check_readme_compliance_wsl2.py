#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README文件规范检查工具
用于检查项目中所有目录是否都符合递归README.md规范要求
"""

import os
import sys


def check_readme_files(root_dir):
    """
    递归检查目录中的README.md和README_En.md文件
    
    参数:
        root_dir: 要检查的根目录路径
    
    返回值:
        tuple: (是否全部符合规范, 缺失的文件列表)
    """
    missing_files = []
    all_compliant = True
    
    # 递归遍历所有目录
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 跳过.git目录
        if '.git' in dirpath:
            continue
        
        # 检查当前目录是否有README.md和README_En.md文件
        readme_md_path = os.path.join(dirpath, 'README.md')
        readme_en_path = os.path.join(dirpath, 'README_En.md')
        
        if not os.path.exists(readme_md_path):
            missing_files.append((dirpath, 'README.md'))
            all_compliant = False
        
        if not os.path.exists(readme_en_path):
            missing_files.append((dirpath, 'README_En.md'))
            all_compliant = False
    
    return all_compliant, missing_files


def main():
    """
    主函数，执行README文件规范检查
    """
    # 使用当前脚本所在目录作为根目录
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"开始检查目录: {root_dir}")
    print("="*60)
    
    compliant, missing_files = check_readme_files(root_dir)
    
    if compliant:
        print("✅ 所有目录都符合README文件规范要求！")
    else:
        print(f"❌ 发现 {len(missing_files)} 个缺失的README文件:")
        for dirpath, filename in missing_files:
            print(f"  - {os.path.join(dirpath, filename)}")
        
    print("="*60)
    print(f"检查完成，{'全部符合' if compliant else '存在问题'}")
    
    # 如果有缺失文件，返回非零退出码
    return 0 if compliant else 1


if __name__ == "__main__":
    sys.exit(main())