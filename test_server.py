from app import create_app
from app.api import rag

# 创建app实例
app = create_app('default')

# 只保留rag蓝图，移除其他蓝图
app.blueprints.clear()
app.register_blueprint(rag)

if __name__ == '__main__':
    app.run(debug=True, port=5001)