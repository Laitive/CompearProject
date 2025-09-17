import json
import os

# 文件路径
# 使用绝对路径指向正确的位置
PASSWORD_FILE = os.path.join(os.path.dirname(__file__), 'password.json')

# 读取所有配置函数
def read_all_config():
    try:
        with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 检查JSON格式
            if isinstance(data, list) and len(data) > 0:
                # 如果是数组，返回第一个对象
                return data[0]
            elif isinstance(data, dict):
                # 如果是对象，直接返回
                return data
            else:
                # 格式不正确，返回默认配置
                return {"password": "123456"}
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或解析错误，返回默认配置
        return {"password": "123456"}

# 读取密码函数
def read_password(config=None):
    # 如果没有提供配置，从文件读取
    if config is None:
        config = read_all_config()
    # 获取password字段，如果不存在则返回默认值
    return config.get('password', '123456')

# 保存所有配置函数
def save_all_config(config):
    try:
        # 保持原有的格式（数组中包含对象）
        data = [config]
        with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存配置失败: {e}")

# 保存密码函数（保留向后兼容性）
def save_password(password, config=None):
    # 如果没有提供配置，从文件读取
    if config is None:
        config = read_all_config()
    # 更新password字段
    config['password'] = password
    # 保存所有配置
    save_all_config(config)

# 处理密码修改的函数
def change_password(old_password, new_password):
    """修改密码的处理函数
    
    Args:
        old_password: 旧密码
        new_password: 新密码
        
    Returns:
        tuple: (是否成功, 消息)
    """
    # 在函数开始处声明所有需要使用的全局变量
    global password, config
    
    # 验证旧密码
    if old_password != password:
        return False, "旧密码错误"
    
    # 更新密码
    password = new_password
    config['password'] = new_password
    
    # 保存所有配置
    save_all_config(config)
    
    return True, "密码修改成功"

# 初始化变量
config = read_all_config()  # 读取所有配置
tag = bool(1)  # 初始为root模式
password = read_password(config)  # 从配置中获取密码
umv = 1