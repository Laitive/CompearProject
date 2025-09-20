# 测试脚本：验证消息保存功能

# 导入消息管理器
from messages import message_manager

# 添加一条测试消息
success = message_manager.add_message(
    name="网站用户",
    email="user@example.com",
    subject="网站测试消息",
    message="这是一条通过网站发送的测试消息，用于验证修复后的功能是否正常工作。"
)

# 验证结果
if success:
    print("✅ 测试消息添加成功！")
    # 读取所有消息以确认保存
    messages = message_manager.get_all_messages()
    print(f"📧 当前共有 {len(messages)} 条消息")
    if messages:
        print(f"🔍 最后一条消息内容: {messages[-1]['message'][:50]}...")
else:
    print("❌ 测试消息添加失败！")

print("\n测试完成。")