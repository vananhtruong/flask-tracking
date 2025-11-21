"""Flask Application - Truy xuất nguồn gốc nông sản"""
from flask import Flask
import os
import config
import utils
from routes.main import main_bp
from routes.auth import auth_bp
from routes.products import products_bp

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Đăng ký blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)

# Khởi tạo thư mục và dữ liệu
utils.init_directories()
utils.load_data()
utils.load_users()

if __name__ == '__main__':
    # Chỉ chạy debug mode khi chạy local
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
