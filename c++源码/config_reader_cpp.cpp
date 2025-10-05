#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <regex>
#include <sstream>

// 配置读取器类，用于辅助Python读取配置文件
class ConfigReaderCPP {
private:
    std::string configDirPath;
    std::map<std::string, std::string> setConfig;
    std::map<std::string, std::map<std::string, std::string>> moduleConfigs;

public:
    ConfigReaderCPP(const std::string& configDir = "") {
        if (!configDir.empty()) {
            configDirPath = configDir;
        } else {
            // 默认配置目录路径
            configDirPath = "c:/Users/Administrator/Documents/GitHub/CompearProject/ConfigDir";
        }
    }

    // 初始化配置读取器
    bool init() {
        try {
            // 加载set.config文件
            if (!loadSetConfig()) {
                std::cerr << "加载set.config失败" << std::endl;
                return false;
            }

            // 加载所有模块配置
            if (!loadAllModuleConfigs()) {
                std::cerr << "加载模块配置失败" << std::endl;
                return false;
            }

            return true;
        } catch (const std::exception& e) {
            std::cerr << "初始化配置读取器时出错: " << e.what() << std::endl;
            return false;
        }
    }

    // 加载set.config文件
    bool loadSetConfig() {
        std::string setConfigPath = configDirPath + "/set.config";
        std::ifstream file(setConfigPath);

        if (!file.is_open()) {
            std::cerr << "无法打开文件: " << setConfigPath << std::endl;
            return false;
        }

        std::string line;
        std::string currentSection;

        while (std::getline(file, line)) {
            // 去除首尾空格
            line = trim(line);

            // 跳过注释和空行
            if (line.empty() || line[0] == ';') {
                continue;
            }

            // 检查是否是section
            if (line[0] == '[' && line.back() == ']') {
                currentSection = line.substr(1, line.size() - 2);
                currentSection = trim(currentSection);
            } else if (!currentSection.empty()) {
                // 解析键值对
                size_t pos = line.find('=');
                if (pos != std::string::npos) {
                    std::string key = trim(line.substr(0, pos));
                    std::string value = trim(line.substr(pos + 1));
                    setConfig[currentSection + "." + key] = value;
                }
            }
        }

        file.close();
        return true;
    }

    // 加载所有模块配置
    bool loadAllModuleConfigs() {
        // 从set.config中获取模块配置文件路径
        for (const auto& pair : setConfig) {
            // 检查是否是Paths部分的配置
            if (pair.first.find("Paths.") == 0) {
                std::string moduleName = pair.first.substr(6); // 去除"Paths."前缀
                // 处理特殊情况：Hardware vs Hardwaer
                if (moduleName == "Hardware") {
                    moduleName = "Hardwaer"; // 保持与现有代码一致
                }
                std::string filePath = pair.second;

                // 确保路径是绝对路径
                if (filePath.find(":") == std::string::npos && filePath[0] != '/') {
                    filePath = configDirPath + "/" + filePath;
                }

                // 加载模块配置
                std::map<std::string, std::string> config;
                if (loadModuleConfig(filePath, config)) {
                    moduleConfigs[moduleName] = config;
                }
            }
        }

        return true;
    }

    // 加载单个模块配置文件（简化版，仅支持基本的JSON结构）
    bool loadModuleConfig(const std::string& filePath, std::map<std::string, std::string>& config) {
        std::ifstream file(filePath);

        if (!file.is_open()) {
            std::cerr << "无法打开模块配置文件: " << filePath << std::endl;
            return false;
        }

        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        file.close();

        // 简化的JSON解析，实际应用中应使用成熟的JSON库
        // 这里仅处理一级键值对
        std::regex keyValueRegex(R"("(\w+)":\s*"([^"]*)"|\'([^\']*)\')");
        std::smatch match;

        std::string::const_iterator searchStart(content.cbegin());
        while (std::regex_search(searchStart, content.cend(), match, keyValueRegex)) {
            if (match.size() >= 2 && !match[1].str().empty()) {
                std::string key = match[1].str();
                std::string value = match[2].str().empty() ? match[3].str() : match[2].str();
                config[key] = value;
            }
            searchStart = match.suffix().first;
        }

        return !config.empty();
    }

    // 获取全局配置
    std::string getGlobalConfig(const std::string& key, const std::string& defaultValue = "") {
        auto it = setConfig.find(key);
        if (it != setConfig.end()) {
            return it->second;
        }
        return defaultValue;
    }

    // 获取模块配置
    std::string getModuleConfig(const std::string& moduleName, const std::string& key, const std::string& defaultValue = "") {
        auto moduleIt = moduleConfigs.find(moduleName);
        if (moduleIt != moduleConfigs.end()) {
            auto keyIt = moduleIt->second.find(key);
            if (keyIt != moduleIt->second.end()) {
                return keyIt->second;
            }
        }
        return defaultValue;
    }

    // 将所有配置转换为可被Python读取的字符串
    std::string toPythonString() {
        std::stringstream ss;
        ss << "{";

        // 添加全局配置
        ss << "\"global\": {";
        bool firstGlobal = true;
        for (const auto& pair : setConfig) {
            if (!firstGlobal) ss << ",";
            ss << "\"" << pair.first << "\": \"" << escapeString(pair.second) << "\"";
            firstGlobal = false;
        }
        ss << "}";

        // 添加模块配置
        ss << ", \"modules\": {";
        bool firstModule = true;
        for (const auto& modulePair : moduleConfigs) {
            if (!firstModule) ss << ",";
            ss << "\"" << modulePair.first << "\": {";
            bool firstKey = true;
            for (const auto& keyPair : modulePair.second) {
                if (!firstKey) ss << ",";
                ss << "\"" << keyPair.first << "\": \"" << escapeString(keyPair.second) << "\"";
                firstKey = false;
            }
            ss << "}";
            firstModule = false;
        }
        ss << "}";

        ss << "}";
        return ss.str();
    }

    // 获取所有配置文件的路径
    std::vector<std::string> getAllConfigPaths() {
        std::vector<std::string> paths;

        // 添加set.config路径
        paths.push_back(configDirPath + "/set.config");

        // 添加模块配置文件路径
        for (const auto& pair : setConfig) {
            if (pair.first.find("Paths.") == 0) {
                std::string filePath = pair.second;
                if (filePath.find(":") == std::string::npos && filePath[0] != '/') {
                    filePath = configDirPath + "/" + filePath;
                }
                paths.push_back(filePath);
            }
        }

        return paths;
    }

private:
    // 去除字符串首尾空格
    std::string trim(const std::string& str) {
        size_t first = str.find_first_not_of(" \t\n\r");
        if (first == std::string::npos) {
            return "";
        }
        size_t last = str.find_last_not_of(" \t\n\r");
        return str.substr(first, last - first + 1);
    }

    // 转义字符串中的特殊字符，以便在JSON中使用
    std::string escapeString(const std::string& str) {
        std::string result;
        for (char c : str) {
            switch (c) {
                case '\\': result += "\\\\";
                    break;
                case '"': result += "\\\"";
                    break;
                case '\n': result += "\\n";
                    break;
                case '\r': result += "\\r";
                    break;
                case '\t': result += "\\t";
                    break;
                default: result += c;
                    break;
            }
        }
        return result;
    }
};

// 主函数，用于测试和作为Python调用的入口
int main(int argc, char* argv[]) {
    try {
        // 创建配置读取器实例
        ConfigReaderCPP reader;

        // 初始化
        if (!reader.init()) {
            std::cerr << "配置读取器初始化失败" << std::endl;
            return 1;
        }

        // 如果提供了参数，根据参数执行不同的操作
        if (argc > 1) {
            std::string command = argv[1];

            if (command == "get_global") {
                if (argc > 2) {
                    std::string key = argv[2];
                    std::string defaultValue = argc > 3 ? argv[3] : "";
                    std::cout << reader.getGlobalConfig(key, defaultValue) << std::endl;
                }
            } else if (command == "get_module") {
                if (argc > 3) {
                    std::string moduleName = argv[2];
                    std::string key = argv[3];
                    std::string defaultValue = argc > 4 ? argv[4] : "";
                    std::cout << reader.getModuleConfig(moduleName, key, defaultValue) << std::endl;
                }
            } else if (command == "to_python") {
                // 输出可被Python读取的JSON格式字符串
                std::cout << reader.toPythonString() << std::endl;
            } else if (command == "get_paths") {
                // 输出所有配置文件的路径
                auto paths = reader.getAllConfigPaths();
                for (const auto& path : paths) {
                    std::cout << path << std::endl;
                }
            } else {
                std::cerr << "未知命令: " << command << std::endl;
                return 1;
            }
        } else {
            // 没有参数时，输出帮助信息
            std::cout << "配置读取器使用帮助:" << std::endl;
            std::cout << "  get_global <key> [default]: 获取全局配置" << std::endl;
            std::cout << "  get_module <module> <key> [default]: 获取模块配置" << std::endl;
            std::cout << "  to_python: 输出可被Python读取的配置字符串" << std::endl;
            std::cout << "  get_paths: 获取所有配置文件的路径" << std::endl;
        }

        return 0;
    } catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
        return 1;
    }
}