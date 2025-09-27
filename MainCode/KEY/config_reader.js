/**
 * JavaSpirit配置文件读取器
 * 用于读取ConfigDir中的配置文件
 * 支持读取set.config和各个.dir文件
 */

var ConfigReader = {
    // 配置目录路径
    configDir: "c:/Users/Administrator/Documents/GitHub/CompearProject/ConfigDir",
    
    // set.config文件路径
    setConfigPath: "c:/Users/Administrator/Documents/GitHub/CompearProject/ConfigDir/set.config",
    
    // 全局配置
    globalConfig: {},
    
    // 模块配置
    moduleConfigs: {},
    
    /**
     * 初始化配置读取器
     * @param {string} configDir 配置目录路径
     */
    init: function(configDir) {
        // 如果提供了配置目录，则使用提供的目录
        if (configDir) {
            this.configDir = configDir;
            this.setConfigPath = configDir + '/set.config';
        }
        
        // 检查配置目录是否存在
        if (!this._fileExists(this.setConfigPath)) {
            throw new Error('配置文件不存在: ' + this.setConfigPath);
        }
        
        // 加载全局配置
        this.globalConfig = this._loadSetConfig();
        
        // 加载所有模块配置
        this._loadAllModuleConfigs();
        
        console.log('配置读取器初始化成功');
    },
    
    /**
     * 检查文件是否存在
     * @param {string} filePath 文件路径
     * @returns {boolean} 文件是否存在
     */
    _fileExists: function(filePath) {
        // 在JavaSpirit环境中，可能需要使用Java的文件操作API
        // 这里使用try-catch模拟文件存在检查
        try {
            var file = new java.io.File(filePath);
            return file.exists();
        } catch (e) {
            // 如果没有Java环境，返回true（模拟）
            return true;
        }
    },
    
    /**
     * 读取文件内容
     * @param {string} filePath 文件路径
     * @returns {string} 文件内容
     */
    _readFile: function(filePath) {
        try {
            var file = new java.io.File(filePath);
            var reader = new java.io.BufferedReader(new java.io.FileReader(file));
            var content = '';
            var line;
            while ((line = reader.readLine()) !== null) {
                content += line + '\n';
            }
            reader.close();
            return content;
        } catch (e) {
            // 如果没有Java环境，返回空字符串（模拟）
            console.error('读取文件失败: ' + filePath + ', 错误: ' + e);
            return '';
        }
    },
    
    /**
     * 加载set.config文件
     * @returns {object} 配置对象
     */
    _loadSetConfig: function() {
        try {
            var content = this._readFile(this.setConfigPath);
            var config = {};
            var currentSection = null;
            
            // 解析ini格式
            var lines = content.split('\n');
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i].trim();
                
                // 跳过注释和空行
                if (line.startsWith(';') || line === '') {
                    continue;
                }
                
                // 检查是否是section
                if (line.startsWith('[') && line.endsWith(']')) {
                    currentSection = line.substring(1, line.length - 1).trim();
                    config[currentSection] = {};
                } else if (currentSection && line.includes('=')) {
                    // 解析键值对
                    var parts = line.split('=');
                    var key = parts[0].trim();
                    var value = parts.slice(1).join('=').trim();
                    
                    // 尝试转换值的类型
                    if (value.toLowerCase() === 'true') {
                        config[currentSection][key] = true;
                    } else if (value.toLowerCase() === 'false') {
                        config[currentSection][key] = false;
                    } else if (!isNaN(value)) {
                        config[currentSection][key] = Number(value);
                    } else {
                        config[currentSection][key] = value;
                    }
                }
            }
            
            console.log('成功加载set.config文件');
            return config;
        } catch (e) {
            console.error('加载set.config文件失败: ' + e);
            throw e;
        }
    },
    
    /**
     * 加载.dir文件（JSON格式）
     * @param {string} filePath 文件路径
     * @returns {object} 配置对象
     */
    _loadDirFile: function(filePath) {
        try {
            if (!this._fileExists(filePath)) {
                throw new Error('配置文件不存在: ' + filePath);
            }
            
            var content = this._readFile(filePath);
            var config = JSON.parse(content);
            
            console.log('成功加载配置文件: ' + filePath);
            return config;
        } catch (e) {
            console.error('加载配置文件失败: ' + filePath + ', 错误: ' + e);
            throw e;
        }
    },
    
    /**
     * 加载所有模块的配置文件
     */
    _loadAllModuleConfigs: function() {
        if (this.globalConfig.Paths) {
            for (var moduleName in this.globalConfig.Paths) {
                if (this.globalConfig.Paths.hasOwnProperty(moduleName)) {
                    try {
                        var filePath = this.globalConfig.Paths[moduleName];
                        
                        // 确保路径是绝对路径
                        if (!filePath.startsWith('/') && !filePath.includes(':')) {
                            filePath = this.configDir + '/' + filePath;
                        }
                        
                        // 加载模块配置
                        this.moduleConfigs[moduleName.toLowerCase()] = this._loadDirFile(filePath);
                    } catch (e) {
                        console.warn('加载' + moduleName + '模块配置失败: ' + e);
                        // 继续加载其他模块配置
                    }
                }
            }
        }
    },
    
    /**
     * 获取全局配置
     * @returns {object} 全局配置
     */
    getGlobalConfig: function() {
        return this.globalConfig;
    },
    
    /**
     * 获取指定模块的配置
     * @param {string} moduleName 模块名称（小写）
     * @returns {object} 模块配置
     */
    getModuleConfig: function(moduleName) {
        return this.moduleConfigs[moduleName.toLowerCase()] || null;
    },
    
    /**
     * 获取AI模块配置
     * @returns {object} AI模块配置
     */
    getAIConfig: function() {
        return this.getModuleConfig('aipart');
    },
    
    /**
     * 获取硬件模块配置
     * @returns {object} 硬件模块配置
     */
    getHardwareConfig: function() {
        return this.getModuleConfig('hardware');
    },
    
    /**
     * 获取主程序代码模块配置
     * @returns {object} 主程序代码模块配置
     */
    getMainCodeConfig: function() {
        return this.getModuleConfig('maincode');
    },
    
    /**
     * 获取Web模块配置
     * @returns {object} Web模块配置
     */
    getWebConfig: function() {
        return this.getModuleConfig('web');
    },
    
    /**
     * 重新加载所有配置
     */
    reload: function() {
        console.log('开始重新加载所有配置');
        this.globalConfig = this._loadSetConfig();
        this.moduleConfigs = {};
        this._loadAllModuleConfigs();
        console.log('所有配置重新加载完成');
    },
    
    /**
     * 获取配置中的特定值
     * @param {string} moduleName 模块名称
     * @param {string} keyPath 键路径，使用点分隔，例如："server.port"
     * @param {*} defaultValue 默认值
     * @returns {*} 配置值或默认值
     */
    getValue: function(moduleName, keyPath, defaultValue) {
        var moduleConfig = this.getModuleConfig(moduleName);
        if (!moduleConfig) {
            return defaultValue;
        }
        
        var keys = keyPath.split('.');
        var value = moduleConfig;
        
        try {
            for (var i = 0; i < keys.length; i++) {
                if (value && typeof value === 'object' && keys[i] in value) {
                    value = value[keys[i]];
                } else {
                    return defaultValue;
                }
            }
            return value;
        } catch (e) {
            return defaultValue;
        }
    },
    
    /**
     * 将配置对象转换为字符串
     * @param {object} config 配置对象
     * @returns {string} 格式化的字符串
     */
    toString: function(config) {
        return JSON.stringify(config, null, 2);
    }
};

// 导出配置读取器
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConfigReader;
}

// 示例使用（如果直接运行此脚本）
if (typeof runExample !== 'undefined' && runExample) {
    try {
        // 初始化配置读取器
        ConfigReader.init();
        
        // 获取全局配置
        var globalConfig = ConfigReader.getGlobalConfig();
        console.log('全局配置:');
        console.log(ConfigReader.toString(globalConfig));
        
        // 获取AI模块配置
        var aiConfig = ConfigReader.getAIConfig();
        console.log('\nAI模块配置:');
        if (aiConfig) {
            console.log(ConfigReader.toString(aiConfig));
        }
        
        // 获取Web模块配置中的服务器端口
        var webPort = ConfigReader.getValue('web', 'server.port');
        console.log('\nWeb服务器端口: ' + webPort);
        
    } catch (e) {
        console.error('错误: ' + e);
    }
}