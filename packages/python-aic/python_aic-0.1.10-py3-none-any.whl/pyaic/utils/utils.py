
import os 

import random
import string

__all__ = [
    "add_execute_permission",
    "get_random_str",
    "get_folder_size"
]


def add_execute_permission(file_path):
    # 获取当前文件的权限
    current_permissions = os.stat(file_path).st_mode
    # 添加执行权限
    new_permissions = current_permissions | 0o111  # 添加执行权限
    # 修改文件权限
    os.chmod(file_path, new_permissions)



def get_random_str(n):
    # Define the characters to choose from
    # characters = string.ascii_letters + string.digits + string.punctuation
    characters = string.ascii_letters + string.digits
    # Generate a random string
    random_str = ''.join(random.choice(characters) for _ in range(n))
    return random_str



def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):  # 确保是文件而不是目录
                total_size += os.path.getsize(file_path)
    return total_size