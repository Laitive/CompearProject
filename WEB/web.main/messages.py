import json
import os
import sys
import datetime

# 获取当前脚本的绝对路径，并构建messages.json的绝对路径
def get_absolute_path():
    # 获取当前脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建messages.json的绝对路径
    return os.path.join(script_dir, 'messages.json')

# 定义messages.json文件的绝对路径
MESSAGES_FILE = get_absolute_path()

# 调试：打印文件路径以便确认
print(f"Messages file path: {MESSAGES_FILE}")

class MessageManager:
    def __init__(self):
        # 确保messages.json文件存在
        if not os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
                json.dump({'messages': []}, f, ensure_ascii=False, indent=2)
    
    def get_all_messages(self):
        """获取所有消息"""
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('messages', [])
        except Exception as e:
            print(f"读取消息时出错: {e}")
            return []
    
    def add_message(self, name, email, subject, message):
        """添加一条新消息"""
        try:
            messages = self.get_all_messages()
            
            new_message = {
                'id': len(messages) + 1,
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'timestamp': datetime.datetime.now().isoformat(),
                'read': False
            }
            
            messages.append(new_message)
            
            with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
                json.dump({'messages': messages}, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"添加消息时出错: {e}")
            return False
    
    def mark_as_read(self, message_id):
        """将指定消息标记为已读"""
        try:
            messages = self.get_all_messages()
            
            for message in messages:
                if message['id'] == message_id:
                    message['read'] = True
                    break
            
            with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
                json.dump({'messages': messages}, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"标记消息为已读时出错: {e}")
            return False
    
    def delete_message(self, message_id):
        """删除指定消息"""
        try:
            messages = self.get_all_messages()
            
            # 过滤掉要删除的消息
            filtered_messages = [msg for msg in messages if msg['id'] != message_id]
            
            # 重新编号
            for i, msg in enumerate(filtered_messages):
                msg['id'] = i + 1
            
            with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
                json.dump({'messages': filtered_messages}, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"删除消息时出错: {e}")
            return False
    
    def get_unread_count(self):
        """获取未读消息数量"""
        try:
            messages = self.get_all_messages()
            return sum(1 for msg in messages if not msg['read'])
        except Exception as e:
            print(f"获取未读消息数量时出错: {e}")
            return 0

# 创建全局实例供app.py使用
message_manager = MessageManager()