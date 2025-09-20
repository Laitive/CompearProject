import os
import json
import subprocess
import sys
import time
import signal

# 获取当前脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建password.json文件的绝对路径
PASSWORD_FILE = os.path.join(script_dir, 'password.json')
# 构建website_config.json文件的绝对路径
WEBSITE_CONFIG_FILE = os.path.join(script_dir, '../../staic/KEY/json/website_config.json')

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

# 定义PID文件路径
PID_FILE = os.path.join(script_dir, 'website.pid')
LOCK_FILE = os.path.join(script_dir, 'website.lock')
# 初始化变量
config = read_all_config()  # 读取所有配置
tag = bool(1)  # 初始为root模式
admin=False
password = read_password(config)  # 从配置中获取密码
umv = 1

# 读取网站配置函数
def read_website_config():
    try:
        with open(WEBSITE_CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"读取网站配置失败: {e}")
        # 返回默认配置
        return {
            "site": {
                "title": "项目介绍网站",
                "description": "一个现代化、美观且功能丰富的项目介绍网站",
                "keywords": "项目介绍,现代化设计,精美UI,动画效果"
            }
        }

# 保存网站配置函数
def save_website_config(config_data):
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(WEBSITE_CONFIG_FILE), exist_ok=True)
        with open(WEBSITE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True, "网站配置保存成功"
    except Exception as e:
        print(f"保存网站配置失败: {e}")
        return False, f"网站配置保存失败: {str(e)}"

# 修改网站配置项函数
def update_website_config_section(section, key, value):
    """修改网站配置的特定部分
    
    Args:
        section: 配置部分名称（如'site', 'hero'等）
        key: 配置项名称
        value: 新的配置值
        
    Returns:
        tuple: (是否成功, 消息)
    """
    # 读取当前配置
    config_data = read_website_config()
    
    # 检查并更新配置
    if section in config_data:
        if isinstance(config_data[section], dict):
            config_data[section][key] = value
        else:
            return False, f"配置部分 '{section}' 不是对象类型"
    else:
        # 如果部分不存在，创建新部分
        config_data[section] = {key: value}
    
    # 保存更新后的配置
    return save_website_config(config_data)

# 查看网站配置函数
def show_website_config_section(section=None):
    """查看网站配置的特定部分或全部配置
    
    Args:
        section: 可选，配置部分名称（如'site', 'hero'等），如果为None则显示全部配置
        
    Returns:
        tuple: (是否成功, 数据/消息)
    """
    config_data = read_website_config()
    
    if section:
        if section in config_data:
            return True, config_data[section]
        else:
            return False, f"配置部分 '{section}' 不存在"
    else:
            return True, config_data

# 启动网站函数
def start_website():
    """使用文件锁和PID文件启动网站服务
    
    Returns:
        tuple: (是否成功, 消息)
    """
    try:
        # 检查网站是否已经在运行
        status, _ = check_website_status()
        if status:
            return False, "网站已经在运行中"
        
        # 构建app.py的路径
        app_path = os.path.join(script_dir, '../../WEB/web.main/app.py')
        
        # 检查app.py文件是否存在
        if not os.path.exists(app_path):
            return False, f"未找到app.py文件: {app_path}"
        
        # 获取项目根目录
        project_root = os.path.abspath(os.path.join(script_dir, '../../'))
        
        # 创建文件锁
        try:
            lock_fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(lock_fd)
        except FileExistsError:
            return False, "网站锁定文件已存在，可能有其他实例正在运行"
        
        # 启动网站进程
        print(f"正在启动网站服务...")
        if sys.platform == 'win32':
            # Windows平台
            process = subprocess.Popen(
                [sys.executable, app_path],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # 非Windows平台
            process = subprocess.Popen(
                [sys.executable, app_path],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
        
        # 等待短暂时间，确保进程启动
        time.sleep(1)
        
        # 检查进程是否仍在运行
        if process.poll() is None:
            # 保存PID到文件
            with open(PID_FILE, 'w') as f:
                f.write(str(process.pid))
            return True, f"网站服务已成功启动（进程PID: {process.pid}）"
        else:
            # 读取错误输出
            stderr = process.stderr.read().decode('utf-8')
            # 清理锁定文件
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
            return False, f"网站启动失败: {stderr}"
            
    except Exception as e:
        # 清理锁定文件
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        return False, f"启动网站时发生错误: {str(e)}"

# 关闭网站函数
def stop_website():
    """使用PID文件关闭网站服务
    
    Returns:
        tuple: (是否成功, 消息)
    """
    try:
        # 检查网站是否正在运行
        status, message = check_website_status()
        if not status:
            return False, "网站未在运行"
        
        # 尝试从PID文件获取进程ID
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid_str = f.read().strip()
            
            if pid_str.isdigit():
                pid = int(pid_str)
                
                # 根据平台选择终止进程的方法
                if sys.platform == 'win32':
                    # Windows平台
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
                else:
                    # 非Windows平台
                    os.kill(pid, signal.SIGTERM)
                
                # 清理PID文件和锁定文件
                if os.path.exists(PID_FILE):
                    os.remove(PID_FILE)
                if os.path.exists(LOCK_FILE):
                    os.remove(LOCK_FILE)
                
                return True, f"网站服务已成功关闭（进程PID: {pid}）"
        
        # 如果没有PID文件，使用平台特定的方法查找并关闭进程
        if sys.platform == 'win32':
            # Windows平台：使用tasklist和taskkill
            proc = subprocess.Popen(
                ['tasklist', '/fi', 'IMAGENAME eq python.exe', '/fo', 'csv', '/v'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, _ = proc.communicate()
            
            # 解析输出，查找包含app.py的进程
            for line in output.splitlines():
                if 'app.py' in line and 'web.main' in line:
                    # 提取PID
                    parts = line.split(',')[1].strip().strip('"')
                    if parts.isdigit():
                        pid = int(parts)
                        # 强制终止进程
                        subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
                        # 清理锁定文件
                        if os.path.exists(LOCK_FILE):
                            os.remove(LOCK_FILE)
                        return True, f"网站服务已成功关闭（进程PID: {pid}）"
        else:
            # 非Windows平台：使用pgrep和pkill
            proc = subprocess.Popen(
                ['pgrep', '-f', 'python.*app\.py.*web\.main'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            output, _ = proc.communicate()
            
            if output:
                pids = output.decode('utf-8').strip().split('\n')
                for pid in pids:
                    if pid.isdigit():
                        os.kill(int(pid), signal.SIGTERM)
                        # 清理锁定文件
                        if os.path.exists(LOCK_FILE):
                            os.remove(LOCK_FILE)
                        return True, f"网站服务已成功关闭（进程PID: {pid}）"
        
        return False, "未能找到并关闭网站进程"
        
    except Exception as e:
        return False, f"关闭网站时发生错误: {str(e)}"

# 检查网站状态函数
def check_website_status():
    """使用文件锁和PID文件检查网站服务状态
    
    Returns:
        tuple: (是否运行中, 消息)
    """
    # 检查锁定文件是否存在
    if not os.path.exists(LOCK_FILE):
        return False, "网站未在运行（未检测到锁定文件）"
    
    # 检查PID文件是否存在
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid_str = f.read().strip()
            
            if pid_str.isdigit():
                pid = int(pid_str)
                
                # 检查进程是否存在
                if sys.platform == 'win32':
                    # Windows平台
                    proc = subprocess.Popen(
                        ['tasklist', '/fi', f'PID eq {pid}'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    output, _ = proc.communicate()
                    
                    if f' {pid} ' in output:
                        return True, f"网站正在运行中（进程PID: {pid}）"
                else:
                    # 非Windows平台
                    try:
                        os.kill(pid, 0)  # 发送0信号检查进程是否存在
                        return True, f"网站正在运行中（进程PID: {pid}）"
                    except OSError:
                        pass
        except Exception:
            pass
    
    # 尝试使用平台特定的方法查找进程
    if sys.platform == 'win32':
        # Windows平台
        try:
            proc = subprocess.Popen(
                ['tasklist', '/fi', 'IMAGENAME eq python.exe', '/fo', 'csv', '/v'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, _ = proc.communicate()
            
            if 'app.py' in output and 'web.main' in output:
                return True, "网站正在运行中（检测到相关进程）"
        except Exception:
            pass
    else:
        # 非Windows平台
        try:
            proc = subprocess.Popen(
                ['pgrep', '-f', 'python.*app\.py.*web\.main'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            output, _ = proc.communicate()
            
            if output:
                return True, "网站正在运行中（检测到相关进程）"
        except Exception:
            pass
    
    # 如果锁定文件存在但进程不存在，清理锁定文件
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    
    return False, "网站未在运行"