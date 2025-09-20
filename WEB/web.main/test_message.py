# 测试消息保存功能的脚本

# 导入消息管理器
from messages import message_manager

# 尝试添加一条测试消息
success = message_manager.add_message(
    name="测试用户",
    email="test@example.com",
    subject="测试消息",
    message="这是一条测试消息，用于验证消息保存功能是否正常工作。"
)

# 输出结果
if success:
    print("测试消息添加成功！")
    # 读取并显示当前所有消息
    messages = message_manager.get_all_messages()
    print(f"当前共有 {len(messages)} 条消息。")
    print("最后一条消息内容:")
    if messages:
        last_message = messages[-1]
        print(f"ID: {last_message['id']}")
        print(f"姓名: {last_message['name']}")
        print(f"邮箱: {last_message['email']}")
        print(f"主题: {last_message['subject']}")
        print(f"内容: {last_message['message']}")
        print(f"时间戳: {last_message['timestamp']}")
else:
    print("测试消息添加失败！")