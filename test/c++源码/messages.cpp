#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <chrono>
#include <sstream>

// 简单的JSON解析和生成类
class SimpleJSON {
public:
    // 从文件读取JSON数据
    static std::map<std::string, std::vector<std::map<std::string, std::string>>> readJSON(const std::string& filePath) {
        std::map<std::string, std::vector<std::map<std::string, std::string>>> result;
        std::ifstream file(filePath);
        if (!file.is_open()) {
            std::cerr << "无法打开文件: " << filePath << std::endl;
            return result;
        }

        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        file.close();

        // 注意：这是一个简化的JSON解析器，实际应用中应该使用成熟的JSON库
        // 这里仅作为示例，假设messages.json格式简单且规范
        
        // 查找messages数组
        size_t messagesStart = content.find("\"messages\":[");
        if (messagesStart == std::string::npos) {
            return result;
        }
        
        messagesStart += 12; // "messages":[ 的长度
        size_t messagesEnd = content.rfind("]");
        if (messagesEnd == std::string::npos || messagesEnd < messagesStart) {
            return result;
        }
        
        std::string messagesContent = content.substr(messagesStart, messagesEnd - messagesStart);
        std::vector<std::map<std::string, std::string>> messages;
        
        // 简化的解析逻辑，实际应用中应使用JSON库
        // 这里仅处理格式规范的简单情况
        
        result["messages"] = messages;
        return result;
    }
    
    // 写入JSON数据到文件
    static bool writeJSON(const std::string& filePath, const std::map<std::string, std::vector<std::map<std::string, std::string>>>& data) {
        std::ofstream file(filePath);
        if (!file.is_open()) {
            std::cerr << "无法打开文件进行写入: " << filePath << std::endl;
            return false;
        }
        
        file << "{" << std::endl;
        file << "  \"messages\": [" << std::endl;
        
        auto it = data.find("messages");
        if (it != data.end()) {
            const auto& messages = it->second;
            for (size_t i = 0; i < messages.size(); ++i) {
                file << "    {" << std::endl;
                size_t fieldCount = 0;
                for (const auto& field : messages[i]) {
                    file << "      \"" << field.first << "\": \"" << field.second << "\"";
                    if (++fieldCount < messages[i].size()) {
                        file << ",";
                    }
                    file << std::endl;
                }
                file << "    }";
                if (i < messages.size() - 1) {
                    file << ",";
                }
                file << std::endl;
            }
        }
        
        file << "  ]" << std::endl;
        file << "}" << std::endl;
        
        file.close();
        return true;
    }
};

class MessageManager {
private:
    std::string messagesFilePath;
    
public:
    MessageManager(const std::string& filePath) : messagesFilePath(filePath) {
        // 确保文件存在
        std::ifstream file(messagesFilePath);
        if (!file.is_open()) {
            file.close();
            std::ofstream newFile(messagesFilePath);
            newFile << "{\"messages\": []}";
            newFile.close();
        } else {
            file.close();
        }
    }
    
    // 获取所有消息
    std::vector<std::map<std::string, std::string>> getAllMessages() {
        auto data = SimpleJSON::readJSON(messagesFilePath);
        auto it = data.find("messages");
        if (it != data.end()) {
            return it->second;
        }
        return {};
    }
    
    // 添加新消息
    bool addMessage(const std::string& name, const std::string& email, 
                   const std::string& subject, const std::string& message) {
        try {
            auto data = SimpleJSON::readJSON(messagesFilePath);
            auto& messages = data["messages"];
            
            // 生成ID
            int id = messages.size() + 1;
            
            // 获取当前时间
            auto now = std::chrono::system_clock::now();
            auto now_c = std::chrono::system_clock::to_time_t(now);
            std::stringstream timeStream;
            timeStream << std::put_time(std::localtime(&now_c), "%Y-%m-%dT%H:%M:%S");
            std::string timestamp = timeStream.str();
            
            // 创建新消息
            std::map<std::string, std::string> newMessage;
            newMessage["id"] = std::to_string(id);
            newMessage["name"] = name;
            newMessage["email"] = email;
            newMessage["subject"] = subject;
            newMessage["message"] = message;
            newMessage["timestamp"] = timestamp;
            newMessage["read"] = "false";
            
            messages.push_back(newMessage);
            
            return SimpleJSON::writeJSON(messagesFilePath, data);
        } catch (const std::exception& e) {
            std::cerr << "添加消息时出错: " << e.what() << std::endl;
            return false;
        }
    }
    
    // 将消息标记为已读
    bool markAsRead(int messageId) {
        try {
            auto data = SimpleJSON::readJSON(messagesFilePath);
            auto& messages = data["messages"];
            
            bool found = false;
            for (auto& message : messages) {
                if (message["id"] == std::to_string(messageId)) {
                    message["read"] = "true";
                    found = true;
                    break;
                }
            }
            
            if (!found) {
                std::cerr << "未找到ID为 " << messageId << " 的消息" << std::endl;
                return false;
            }
            
            return SimpleJSON::writeJSON(messagesFilePath, data);
        } catch (const std::exception& e) {
            std::cerr << "标记消息为已读时出错: " << e.what() << std::endl;
            return false;
        }
    }
    
    // 删除消息
    bool deleteMessage(int messageId) {
        try {
            auto data = SimpleJSON::readJSON(messagesFilePath);
            auto& messages = data["messages"];
            
            // 过滤掉要删除的消息
            std::vector<std::map<std::string, std::string>> filteredMessages;
            for (const auto& message : messages) {
                if (message["id"] != std::to_string(messageId)) {
                    filteredMessages.push_back(message);
                }
            }
            
            // 重新编号
            for (size_t i = 0; i < filteredMessages.size(); ++i) {
                filteredMessages[i]["id"] = std::to_string(i + 1);
            }
            
            data["messages"] = filteredMessages;
            
            return SimpleJSON::writeJSON(messagesFilePath, data);
        } catch (const std::exception& e) {
            std::cerr << "删除消息时出错: " << e.what() << std::endl;
            return false;
        }
    }
    
    // 获取未读消息数量
    int getUnreadCount() {
        try {
            auto data = SimpleJSON::readJSON(messagesFilePath);
            auto& messages = data["messages"];
            
            int count = 0;
            for (const auto& message : messages) {
                if (message["read"] == "false") {
                    ++count;
                }
            }
            
            return count;
        } catch (const std::exception& e) {
            std::cerr << "获取未读消息数量时出错: " << e.what() << std::endl;
            return 0;
        }
    }
};

// 示例用法
int main() {
    // 注意：在实际应用中，应从配置文件或命令行参数获取正确的文件路径
    std::string filePath = "../../WEB/web.main/messages.json";
    
    MessageManager manager(filePath);
    
    // 示例：添加一条测试消息
    // manager.addMessage("测试用户", "test@example.com", "测试主题", "这是一条测试消息");
    
    // 示例：获取所有消息
    // auto messages = manager.getAllMessages();
    // std::cout << "共有 " << messages.size() << " 条消息" << std::endl;
    
    // 示例：获取未读消息数量
    // std::cout << "未读消息数量: " << manager.getUnreadCount() << std::endl;
    
    return 0;
}