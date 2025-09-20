import os
from flask import Flask, render_template, jsonify, request

# 创建Flask应用
app = Flask(__name__, 
            static_folder='../../staic', 
            static_url_path='/staic',
            template_folder='../../templates/htmls')

# 导入消息管理器
from messages import message_manager

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 获取网站配置
@app.route('/api/config')
def get_config():
    config_path = os.path.join('../../staic', 'KEY', 'json', 'website_config.json')
    try:
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 消息管理路由

# 获取所有消息
@app.route('/api/messages')
def get_messages():
    try:
        messages = message_manager.get_all_messages()
        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 添加新消息
@app.route('/api/messages', methods=['POST'])
def add_message():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message_text = data.get('message')
        
        if not all([name, email, message_text]):
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        success = message_manager.add_message(name, email, subject, message_text)
        if success:
            return jsonify({'success': True, 'message': '消息发送成功'})
        else:
            return jsonify({'success': False, 'error': '消息发送失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 标记消息为已读
@app.route('/api/messages/<int:message_id>/read', methods=['POST'])
def mark_message_as_read(message_id):
    try:
        success = message_manager.mark_as_read(message_id)
        if success:
            return jsonify({'success': True, 'message': '标记成功'})
        else:
            return jsonify({'success': False, 'error': '标记失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 删除消息
@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    try:
        success = message_manager.delete_message(message_id)
        if success:
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'error': '删除失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 消息管理页面
@app.route('/message-management')
def message_management():
    return render_template('message_management.html')

# 启动服务器
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)