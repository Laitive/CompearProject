from flask import Flask, render_template, jsonify
import os

# 创建Flask应用
app = Flask(__name__, 
            static_folder='../../staic', 
            static_url_path='/staic',
            template_folder='../../templates/htmls')

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

# 启动服务器
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)