"""Các hàm tiện ích"""
import json
import os
import hashlib
import time
import shutil
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from flask import redirect, url_for, request, session
import config

def init_directories():
    """Tạo các thư mục cần thiết nếu chưa tồn tại"""
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.QRCODE_DIR, exist_ok=True)
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(config.UPLOAD_DIR, 'production'), exist_ok=True)
    os.makedirs(os.path.join(config.UPLOAD_DIR, 'harvest'), exist_ok=True)

def load_data():
    """Đọc dữ liệu từ data.json, tạo file mới nếu chưa có"""
    if os.path.exists(config.DATA_FILE):
        try:
            with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    else:
        # Tạo file mới với cấu trúc rỗng
        save_data({})
        return {}

def save_data(data):
    """Lưu dữ liệu vào data.json"""
    with open(config.DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    """Đọc dữ liệu user từ users.json"""
    if os.path.exists(config.USERS_FILE):
        try:
            with open(config.USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    else:
        # Tạo file mới với admin user mặc định
        default_users = {
            'users': [
                {
                    'username': 'admin',
                    'password': hash_password('admin123'),  # Mật khẩu: admin123
                    'full_name': 'Quản trị viên',
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            ]
        }
        save_users(default_users)
        return default_users

def save_users(users_data):
    """Lưu dữ liệu user vào users.json"""
    with open(config.USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """Mã hóa mật khẩu (MD5 - đơn giản cho học tập)"""
    return hashlib.md5(password.encode()).hexdigest()

def login_required(f):
    """Decorator để yêu cầu đăng nhập"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Kiểm tra extension file có được phép không"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def is_image_file(filename):
    """Kiểm tra file có phải là hình ảnh không"""
    image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in image_extensions

def is_video_file(filename):
    """Kiểm tra file có phải là video không"""
    video_extensions = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in video_extensions

def save_uploaded_files(files, product_id, upload_type):
    """Lưu các file đã upload và trả về danh sách đường dẫn"""
    saved_files = []
    if not files:
        return saved_files
    
    upload_folder = os.path.join(config.UPLOAD_DIR, upload_type, product_id)
    os.makedirs(upload_folder, exist_ok=True)
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            # Tạo tên file an toàn
            filename = secure_filename(file.filename)
            # Thêm timestamp để tránh trùng tên
            timestamp = str(int(time.time() * 1000))
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_{timestamp}{ext}"
            file_path = os.path.join(upload_folder, new_filename)
            
            try:
                file.save(file_path)
                # Lưu đường dẫn tương đối để hiển thị
                relative_path = f"uploads/{upload_type}/{product_id}/{new_filename}"
                saved_files.append(relative_path)
            except Exception as e:
                print(f"Lỗi khi lưu file {filename}: {str(e)}")
                continue
    
    return saved_files

def generate_qrcode(product_id, base_url):
    """Tạo mã QR cho sản phẩm"""
    import qrcode
    
    # URL của trang sản phẩm (loại bỏ dấu / cuối nếu có)
    base = base_url.rstrip('/')
    url = f"{base}/product/{product_id}"
    
    # Tạo QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Tạo hình ảnh QR
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Lưu vào thư mục static/qrcodes
    qr_path = os.path.join(config.QRCODE_DIR, f'{product_id}.png')
    img.save(qr_path)
    
    return qr_path

def delete_product_files(product_id):
    """Xóa tất cả file liên quan đến sản phẩm (QR code và media)"""
    # Xóa file QR code
    qr_path = os.path.join(config.QRCODE_DIR, f'{product_id}.png')
    if os.path.exists(qr_path):
        try:
            os.remove(qr_path)
        except:
            pass
    
    # Xóa thư mục media của sản phẩm
    production_media_dir = os.path.join(config.UPLOAD_DIR, 'production', product_id)
    harvest_media_dir = os.path.join(config.UPLOAD_DIR, 'harvest', product_id)
    
    for media_dir in [production_media_dir, harvest_media_dir]:
        if os.path.exists(media_dir):
            try:
                shutil.rmtree(media_dir)
            except:
                pass

def get_user_info(session):
    """Lấy thông tin user từ session"""
    if 'user_id' not in session:
        return None
    
    users_data = load_users()
    for user in users_data.get('users', []):
        if user.get('username') == session.get('user_id'):
            return {
                'username': user.get('username'),
                'full_name': user.get('full_name', user.get('username'))
            }
    return None

