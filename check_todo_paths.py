import os
import sys

# 读取todo文件并检查路径是否存在
def check_todo_paths(todo_file_path):
    """
    检查todo文件中所有路径是否存在
    
    参数:
    todo_file_path: str - todo文件的路径
    
    返回:
    list - 不存在的文件路径列表
    """
    non_existent_paths = []
    
    try:
        with open(todo_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                # 跳过注释行和空行
                if line.startswith('#') or not line:
                    continue
                
                # 解析文件路径
                parts = line.split('|')
                if len(parts) >= 1:
                    file_path = parts[0].strip()
                    # 检查文件是否存在
                    if not os.path.exists(file_path):
                        non_existent_paths.append(file_path)
    
    except Exception as e:
        print(f"读取文件时出错: {e}")
        sys.exit(1)
    
    return non_existent_paths

if __name__ == "__main__":
    todo_file = "rules/todo_Self-evolution_lists.txt"
    print(f"正在检查 {todo_file} 中的文件路径...")
    
    non_existent = check_todo_paths(todo_file)
    
    if non_existent:
        print(f"发现 {len(non_existent)} 个不存在的文件路径:")
        for path in non_existent:
            print(f"  - {path}")
    else:
        print("所有文件路径都存在")