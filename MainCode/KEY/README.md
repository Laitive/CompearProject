# 配置读取组件使用指南

## 项目介绍

本目录包含了使用JavaSpirit进行主要配置读取操作，并使用Python提供更丰富接口的组件。这些组件用于读取ConfigDir中的配置文件（.dir文件），实现配置的集中管理和读取。

## 文件说明

- **config_reader.js**: JavaSpirit配置文件读取器，负责主要的配置读取操作
- **config_interface.py**: Python接口模块，引用JavaScript配置读取器并提供更丰富的接口
- **config_reader.py**: 原有的Python配置读取器（保留）

## 前提条件

### 对于JavaScript组件
- 需要Java环境支持JavaSpirit运行

### 对于Python组件
- Python 3.6或更高版本
- 推荐安装以下依赖库：
  - `PyExecJS`: 用于执行JavaScript代码（推荐）
  - `js2py`: 另一个JavaScript执行引擎（备选）

## 安装依赖

```bash
pip install PyExecJS js2py
```

## 使用方法

### 1. JavaSpirit配置读取器使用

可以在JavaSpirit环境中直接使用`config_reader.js`：

```javascript
// 引入配置读取器
// 注意：在JavaSpirit环境中，需要根据实际情况引入文件

// 初始化配置读取器
ConfigReader.init();

// 获取全局配置
var globalConfig = ConfigReader.getGlobalConfig();

// 获取AI模块配置
var aiConfig = ConfigReader.getAIConfig();

// 获取Web模块配置中的服务器端口
var webPort = ConfigReader.getValue('web', 'server.port', 8080);

// 重新加载所有配置
ConfigReader.reload();
```

### 2. Python配置接口使用

`config_interface.py`提供了更丰富的Python接口，可以直接在Python代码中使用：

```python
from config_interface import config_interface

# 初始化配置接口
config_interface.init()

# 获取全局配置
global_config = config_interface.get_global_config()

# 获取AI模块配置
ai_config = config_interface.get_ai_config()

# 获取Web模块配置中的服务器端口
web_port = config_interface.get_value('web', 'server.port', 8080)

# 重新加载所有配置
config_interface.reload()

# 注册事件监听器
def on_config_reload():
    print('配置已重新加载!')
    
config_interface.register_event_listener('reload', on_config_reload)

# 验证配置
ai_schema = {
    'version': str,
    'ai_provider': str,
    'api_key': str
}

validation_errors = config_interface.validate_config('aipart', ai_schema)

# 生成JSON格式的所有配置
all_config_json = config_interface.to_json()
```

## 高级功能

### 缓存功能

Python配置接口提供了配置缓存功能，可以提高性能：

```python
# 启用/禁用缓存
config_interface.set_cache_enabled(True)  # 默认为True

# 设置缓存过期时间（秒）
config_interface.set_cache_ttl(30)  # 默认10秒

# 手动清除缓存
config_interface.clear_cache()
```

### 事件监听

Python配置接口支持事件监听，可以在配置初始化或重新加载时执行自定义操作：

```python
# 注册初始化事件监听器
def on_init():
    print('配置已初始化!')
    
config_interface.register_event_listener('init', on_init)

# 注册重新加载事件监听器
def on_reload():
    print('配置已重新加载!')
    
config_interface.register_event_listener('reload', on_reload)

# 注销事件监听器
config_interface.unregister_event_listener('reload', on_reload)
```

### 配置验证

Python配置接口提供了配置验证功能，可以验证配置是否符合指定的模式：

```python
# 定义验证模式
web_schema = {
    'version': str,
    'server': dict,
    'paths': dict
}

# 验证配置
validation_errors = config_interface.validate_config('web', web_schema)

# 检查验证结果
if validation_errors:
    print('配置验证错误:')
    for key, error in validation_errors.items():
        print(f'  {key}: {error}')
else:
    print('配置验证通过')
```

### 备选执行引擎

Python配置接口会尝试按以下顺序使用JavaScript执行引擎：

1. PyExecJS（推荐）
2. js2py（备选）
3. 直接解析JSON配置文件（最后备选方案）

如果没有安装PyExecJS和js2py，接口会自动切换到备选方案。

## 配置文件结构

### set.config

全局配置文件，采用INI格式，包含模块配置文件的路径等信息：

```ini
; 全局配置文件
; 指定各模块配置文件的路径
[Paths]
AIPart.dir = AIPart.dir
Hardwaer.dir = Hardwaer.dir
MainCode.dir = MainCode.dir
Web.dir = Web.dir

; 全局设置
[Global]
config_format = json
reload_on_change = false
log_level = info
```

### .dir文件

各模块的配置文件，采用JSON格式，例如AIPart.dir：

```json
{
  "version": "1.0.0",
  "ai_provider": "volcano",
  "api_key": "your_api_key_here",
  "model": "doubao-1-5-pro-32k-250115",
  "base_url": "https://ark.cn-beijing.volces.com/api/v3",
  "timeout": 30,
  "retry_count": 3,
  "modules": {
    "chat": {
      "enabled": true,
      "max_tokens": 8000
    },
    "text_generation": {
      "enabled": true
    },
    "embedding": {
      "enabled": true
    }
  },
  "log": {
    "level": "info",
    "file": "ai_part.log"
  }
}
```

## 注意事项

1. 确保配置文件的路径正确，尤其是在不同环境中使用时
2. 保护好包含API密钥等敏感信息的配置文件
3. 在生产环境中，建议禁用配置热重载功能，以提高安全性
4. 如果遇到JavaScript执行环境问题，可以尝试安装推荐的依赖库

## 故障排除

### JavaScript执行环境问题

如果遇到"初始化JavaScript执行环境失败"的错误：

1. 确保已安装PyExecJS或js2py：`pip install PyExecJS js2py`
2. 对于PyExecJS，确保系统中已安装Node.js或其他JavaScript引擎
3. 如果仍然无法解决，可以依赖备选方案（直接解析JSON文件）

### 配置文件读取问题

如果遇到配置文件读取失败的错误：

1. 检查配置文件是否存在
2. 检查配置文件的格式是否正确
3. 检查文件权限是否正确

## 示例程序

请查看`config_interface.py`中的示例代码，或创建自己的示例程序来测试配置读取功能。