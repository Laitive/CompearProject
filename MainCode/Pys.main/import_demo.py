# Python模块导入路径指定演示

# 方法1: 基本导入 - 模块必须在当前目录或Python路径中
# 这是最简单的导入方式，但只能导入当前目录或Python环境变量中存在的模块
print("方法1: 基本导入")
import password
print(f"成功导入password模块，可用函数: {dir(password)}")

# 方法2: 使用sys.path.append添加自定义路径
# 这种方法可以临时将任何目录添加到Python的搜索路径中
print("\n方法2: 使用sys.path.append添加自定义路径")
import sys
import os

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"当前目录: {current_dir}")

# 添加自定义路径（假设我们想从另一个目录导入模块）
# 这里我们只是演示，实际上我们已经在当前目录
# sys.path.append("C:\\path\\to\\your\\module")

# 导入成功后，可以导入指定路径下的模块
# import custom_module

# 方法3: 使用importlib动态导入
print("\n方法3: 使用importlib动态导入")
import importlib

# 动态导入password模块
password_module = importlib.import_module('password')
print(f"成功使用importlib导入模块，可用函数: {[func for func in dir(password_module) if not func.startswith('__')]}")

# 方法4: 使用__import__函数导入
print("\n方法4: 使用__import__函数导入")
# __import__是Python的内置函数，import语句实际上就是调用这个函数
password_module2 = __import__('password')
print(f"成功使用__import__导入模块")

# 方法5: 从父目录或子目录导入
print("\n方法5: 从父目录或子目录导入")
# 从父目录导入
# parent_dir = os.path.dirname(current_dir)
# sys.path.append(parent_dir)
# from parent_module import something

# 从子目录导入（子目录必须包含__init__.py文件）
# from subdirectory import module

# 实际应用示例：修改CMD.py中的导入方式
print("\n实际应用示例:")
# 假设我们想从不同路径导入password模块
# 1. 添加模块所在目录到sys.path
# 2. 使用importlib动态导入
# 3. 调用模块中的函数

demo_password = "test123"
new_pwd = password.change_password("123456", "newpassword", demo_password)
print(f"使用password模块中的函数: 尝试更改密码，结果: {'成功' if new_pwd == 'newpassword' else '失败'}")

print("\n所有导入方法演示完成!")