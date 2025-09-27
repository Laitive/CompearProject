#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置接口模块
使用Python引用JavaScript配置读取器并提供更丰富的接口
"""

import os
import sys
import json
import logging
import threading
import importlib.util
from typing import Any, Dict, Optional, Union, Callable

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ConfigInterface')

class ConfigInterfaceError(Exception):
    """配置接口异常类"""
    pass

class ConfigInterface:
    """配置接口类，用于引用JavaScript配置读取器并提供更丰富的接口"""
    
    _instance = None
    _lock = threading.RLock()  # 使用可重入锁
    
    def __new__(cls):
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigInterface, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置接口"""
        with self._lock:
            # 确保初始化只执行一次
            if not hasattr(self, '_initialized'):
                self._initialized = False
                
                # 获取JavaScript文件路径
                self.js_file_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'config_reader.js'
                )
                
                # 检查JavaScript文件是否存在
                if not os.path.exists(self.js_file_path):
                    raise ConfigInterfaceError(f'JavaScript配置读取器文件不存在: {self.js_file_path}')
                
                # 初始化JS执行环境
                self._init_js_environment()
                
                # 配置缓存
                self._config_cache = {}
                self._cache_enabled = True
                self._cache_ttl = 10  # 缓存过期时间（秒）
                self._last_cache_update = 0
                
                # 事件监听器
                self._event_listeners = {}
                
                # 初始化完成
                self._initialized = True
                logger.info('配置接口初始化成功')
    
    def _init_js_environment(self):
        """初始化JavaScript执行环境"""
        try:
            # 尝试导入PyExecJS库（推荐）
            try:
                import execjs
                self.js_engine = 'execjs'
                self.js_context = execjs.compile(open(self.js_file_path, 'r', encoding='utf-8').read())
                logger.info('使用PyExecJS执行JavaScript')
            except ImportError:
                # 尝试导入js2py库
                try:
                    import js2py
                    self.js_engine = 'js2py'
                    self.js_context = js2py.EvalJs()
                    self.js_context.execute(open(self.js_file_path, 'r', encoding='utf-8').read())
                    logger.info('使用js2py执行JavaScript')
                except ImportError:
                    # 尝试使用简单的JSON解析作为备选方案
                    self.js_engine = 'fallback'
                    self._js_fallback()
                    logger.warning('使用备选方案（直接解析JSON配置文件）')
        except Exception as e:
            raise ConfigInterfaceError(f'初始化JavaScript执行环境失败: {str(e)}')
    
    def _js_fallback(self):
        """备选方案：直接解析JSON配置文件"""
        self._fallback_configs = {}
        self._config_dir = "c:/Users/Administrator/Documents/GitHub/CompearProject/ConfigDir"
        
        # 尝试加载set.config（简化版本）
        set_config_path = os.path.join(self._config_dir, 'set.config')
        if os.path.exists(set_config_path):
            try:
                with open(set_config_path, 'r', encoding='utf-8') as f:
                    self._fallback_global = self._parse_ini(f.read())
            except Exception as e:
                logger.error(f'解析set.config文件失败: {str(e)}')
                self._fallback_global = {}
        else:
            self._fallback_global = {}
    
    def _parse_ini(self, content: str) -> Dict[str, Dict[str, Any]]:
        """简单的INI文件解析器"""
        result = {}
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # 跳过注释和空行
            if line.startswith(';') or line == '':
                continue
            
            # 检查是否是section
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                result[current_section] = {}
            elif current_section and '=' in line:
                # 解析键值对
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 尝试转换值的类型
                if value.lower() == 'true':
                    result[current_section][key] = True
                elif value.lower() == 'false':
                    result[current_section][key] = False
                elif value.isdigit():
                    result[current_section][key] = int(value)
                elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                    result[current_section][key] = float(value)
                else:
                    result[current_section][key] = value
        
        return result
    
    def init(self, config_dir: Optional[str] = None) -> None:
        """
        初始化配置读取器
        
        Args:
            config_dir: 配置目录路径，如果为None则使用默认路径
        """
        try:
            if self.js_engine == 'fallback':
                # 备选方案下的初始化
                if config_dir:
                    self._config_dir = config_dir
                
                # 尝试加载所有已知的配置文件
                for module_name in ['aipart', 'hardware', 'maincode', 'web']:
                    file_path = os.path.join(self._config_dir, f'{module_name}.dir')
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                self._fallback_configs[module_name] = json.load(f)
                        except Exception as e:
                            logger.error(f'解析{file_path}文件失败: {str(e)}')
            else:
                # 使用JavaScript引擎初始化
                if config_dir:
                    self.js_context.call('ConfigReader.init', config_dir)
                else:
                    self.js_context.call('ConfigReader.init')
                
            # 清除缓存
            self.clear_cache()
            
            # 触发初始化事件
            self._trigger_event('init')
            
        except Exception as e:
            raise ConfigInterfaceError(f'配置读取器初始化失败: {str(e)}')
    
    def get_global_config(self) -> Dict[str, Any]:
        """
        获取全局配置
        
        Returns:
            全局配置对象
        """
        try:
            if self.js_engine == 'fallback':
                return self._fallback_global
            else:
                return self.js_context.call('ConfigReader.getGlobalConfig')
        except Exception as e:
            logger.error(f'获取全局配置失败: {str(e)}')
            return {}
    
    def get_module_config(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模块的配置
        
        Args:
            module_name: 模块名称（小写）
        
        Returns:
            模块配置对象或None
        """
        cache_key = f'module_{module_name}'
        
        # 检查缓存
        if self._cache_enabled and cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            if self.js_engine == 'fallback':
                config = self._fallback_configs.get(module_name.lower(), None)
            else:
                config = self.js_context.call('ConfigReader.getModuleConfig', module_name)
            
            # 更新缓存
            if self._cache_enabled:
                self._config_cache[cache_key] = config
            
            return config
        except Exception as e:
            logger.error(f'获取{module_name}模块配置失败: {str(e)}')
            return None
    
    def get_ai_config(self) -> Optional[Dict[str, Any]]:
        """
        获取AI模块配置
        
        Returns:
            AI模块配置对象或None
        """
        return self.get_module_config('aipart')
    
    def get_hardware_config(self) -> Optional[Dict[str, Any]]:
        """
        获取硬件模块配置
        
        Returns:
            硬件模块配置对象或None
        """
        return self.get_module_config('hardware')
    
    def get_main_code_config(self) -> Optional[Dict[str, Any]]:
        """
        获取主程序代码模块配置
        
        Returns:
            主程序代码模块配置对象或None
        """
        return self.get_module_config('maincode')
    
    def get_web_config(self) -> Optional[Dict[str, Any]]:
        """
        获取Web模块配置
        
        Returns:
            Web模块配置对象或None
        """
        return self.get_module_config('web')
    
    def reload(self) -> None:
        """重新加载所有配置"""
        try:
            if self.js_engine != 'fallback':
                self.js_context.call('ConfigReader.reload')
            else:
                # 备选方案下的重新加载
                self._js_fallback()
                for module_name in self._fallback_configs:
                    file_path = os.path.join(self._config_dir, f'{module_name}.dir')
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                self._fallback_configs[module_name] = json.load(f)
                        except Exception as e:
                            logger.error(f'重新加载{file_path}文件失败: {str(e)}')
            
            # 清除缓存
            self.clear_cache()
            
            # 触发重新加载事件
            self._trigger_event('reload')
            
            logger.info('所有配置重新加载完成')
        except Exception as e:
            raise ConfigInterfaceError(f'重新加载配置失败: {str(e)}')
    
    def get_value(self, module_name: str, key_path: str, default_value: Any = None) -> Any:
        """
        获取配置中的特定值
        
        Args:
            module_name: 模块名称
            key_path: 键路径，使用点分隔，例如："server.port"
            default_value: 默认值
        
        Returns:
            配置值或默认值
        """
        cache_key = f'{module_name}_{key_path}'
        
        # 检查缓存
        if self._cache_enabled and cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            if self.js_engine == 'fallback':
                # 备选方案下的实现
                module_config = self.get_module_config(module_name)
                if not module_config:
                    return default_value
                
                keys = key_path.split('.')
                value = module_config
                
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return default_value
                
                config_value = value
            else:
                config_value = self.js_context.call('ConfigReader.getValue', module_name, key_path, default_value)
            
            # 更新缓存
            if self._cache_enabled:
                self._config_cache[cache_key] = config_value
            
            return config_value
        except Exception as e:
            logger.error(f'获取{module_name}.{key_path}配置值失败: {str(e)}')
            return default_value
    
    def set_cache_enabled(self, enabled: bool) -> None:
        """
        设置是否启用缓存
        
        Args:
            enabled: 是否启用缓存
        """
        self._cache_enabled = enabled
        if not enabled:
            self.clear_cache()
    
    def set_cache_ttl(self, ttl: int) -> None:
        """
        设置缓存过期时间
        
        Args:
            ttl: 缓存过期时间（秒）
        """
        self._cache_ttl = max(0, ttl)
    
    def clear_cache(self) -> None:
        """清除配置缓存"""
        self._config_cache = {}
        self._last_cache_update = 0
        logger.debug('配置缓存已清除')
    
    def register_event_listener(self, event_name: str, callback: Callable) -> None:
        """
        注册事件监听器
        
        Args:
            event_name: 事件名称
            callback: 回调函数
        """
        if event_name not in self._event_listeners:
            self._event_listeners[event_name] = []
        
        if callback not in self._event_listeners[event_name]:
            self._event_listeners[event_name].append(callback)
            logger.debug(f'已注册{event_name}事件监听器')
    
    def unregister_event_listener(self, event_name: str, callback: Callable) -> None:
        """
        注销事件监听器
        
        Args:
            event_name: 事件名称
            callback: 回调函数
        """
        if event_name in self._event_listeners and callback in self._event_listeners[event_name]:
            self._event_listeners[event_name].remove(callback)
            logger.debug(f'已注销{event_name}事件监听器')
    
    def _trigger_event(self, event_name: str, *args, **kwargs) -> None:
        """
        触发事件
        
        Args:
            event_name: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if event_name in self._event_listeners:
            for callback in self._event_listeners[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f'执行{event_name}事件监听器失败: {str(e)}')
    
    def validate_config(self, module_name: str, schema: Dict[str, Any]) -> Dict[str, str]:
        """
        验证配置是否符合指定的模式
        
        Args:
            module_name: 模块名称
            schema: 验证模式
        
        Returns:
            验证错误字典，键为配置项路径，值为错误信息
        """
        errors = {}
        config = self.get_module_config(module_name)
        
        if not config:
            errors['__module__'] = f'模块{module_name}的配置不存在'
            return errors
        
        # 这里可以实现复杂的配置验证逻辑
        # 简单实现：检查必要的配置项是否存在
        for key, value_type in schema.items():
            if key not in config:
                errors[key] = f'缺少必要的配置项: {key}'
            elif not isinstance(config[key], value_type):
                errors[key] = f'配置项{key}的类型错误，期望{value_type.__name__}，实际是{type(config[key]).__name__}'
        
        return errors
    
    def to_json(self, module_name: Optional[str] = None, indent: int = 2) -> str:
        """
        将配置转换为JSON字符串
        
        Args:
            module_name: 模块名称，如果为None则输出所有配置
            indent: 缩进空格数
        
        Returns:
            JSON字符串
        """
        try:
            if module_name:
                config = self.get_module_config(module_name)
            else:
                # 获取所有配置
                config = {
                    'global': self.get_global_config(),
                    'modules': {
                        'aipart': self.get_ai_config(),
                        'hardware': self.get_hardware_config(),
                        'maincode': self.get_main_code_config(),
                        'web': self.get_web_config()
                    }
                }
            
            return json.dumps(config, ensure_ascii=False, indent=indent)
        except Exception as e:
            logger.error(f'转换配置为JSON字符串失败: {str(e)}')
            return '{}'

# 创建配置接口单例实例
config_interface = ConfigInterface()

# 示例使用
if __name__ == '__main__':
    try:
        # 初始化配置接口
        config_interface.init()
        
        # 注册事件监听器
        def on_config_reload():
            print('配置已重新加载!')
        
        config_interface.register_event_listener('reload', on_config_reload)
        
        # 获取全局配置
        global_config = config_interface.get_global_config()
        print('全局配置:')
        print(json.dumps(global_config, ensure_ascii=False, indent=2))
        
        # 获取AI模块配置
        ai_config = config_interface.get_ai_config()
        print('\nAI模块配置:')
        if ai_config:
            print(json.dumps(ai_config, ensure_ascii=False, indent=2))
        
        # 获取Web模块配置中的服务器端口
        web_port = config_interface.get_value('web', 'server.port', 8080)
        print(f'\nWeb服务器端口: {web_port}')
        
        # 验证配置
        ai_schema = {
            'version': str,
            'ai_provider': str,
            'api_key': str
        }
        
        validation_errors = config_interface.validate_config('aipart', ai_schema)
        if validation_errors:
            print('\n配置验证错误:')
            for key, error in validation_errors.items():
                print(f'  {key}: {error}')
        else:
            print('\n配置验证通过')
        
        # 生成JSON格式的所有配置
        print('\n所有配置(JSON格式):')
        print(config_interface.to_json())
        
    except ConfigInterfaceError as e:
        print(f'错误: {e}')
        sys.exit(1)