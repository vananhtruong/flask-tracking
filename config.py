"""Cấu hình ứng dụng"""
import os

# Đường dẫn file data
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'data.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
QRCODE_DIR = 'static/qrcodes'
UPLOAD_DIR = 'static/uploads'

# Cấu hình upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mkv', 'webm'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Secret key - Nên đặt trong biến môi trường cho production
# Cảnh báo: Không commit secret key thật vào git!
SECRET_KEY = os.environ.get('SECRET_KEY', '0deab411eb2ed51a3a625a05ce9602c521d54ad4c3ceab1d3af2d35978b9ca15')

# CSRF Protection
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 3600  # 1 giờ

