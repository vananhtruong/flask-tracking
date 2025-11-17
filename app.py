from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from functools import wraps
import json
import os
import qrcode
from datetime import datetime
import time
import hashlib

app = Flask(__name__)
# Sử dụng biến môi trường cho secret key khi deploy
app.secret_key = os.environ.get('SECRET_KEY', '0deab411eb2ed51a3a625a05ce9602c521d54ad4c3ceab1d3af2d35978b9ca15')

# Đường dẫn file data
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'data.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
QRCODE_DIR = 'static/qrcodes'

# Tạo thư mục data và qrcodes nếu chưa tồn tại
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(QRCODE_DIR, exist_ok=True)

def load_data():
    """Đọc dữ liệu từ data.json, tạo file mới nếu chưa có"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    else:
        # Tạo file mới với cấu trúc rỗng
        save_data({})
        return {}

def save_data(data):
    """Lưu dữ liệu vào data.json"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    """Đọc dữ liệu user từ users.json"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    else:
        # Tạo file mới với admin user mặc định
        default_users = {
            'users': [
                {
                    'username': 'admin',
                    'password': hashlib.md5('admin123'.encode()).hexdigest(),  # Mật khẩu: admin123
                    'full_name': 'Quản trị viên',
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            ]
        }
        save_users(default_users)
        return default_users

def save_users(users_data):
    """Lưu dữ liệu user vào users.json"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
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

def generate_qrcode(product_id, base_url):
    """Tạo mã QR cho sản phẩm"""
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
    qr_path = os.path.join(QRCODE_DIR, f'{product_id}.png')
    img.save(qr_path)
    
    return qr_path

@app.route('/')
def index():
    """Trang chính - hiển thị danh sách sản phẩm"""
    data = load_data()
    products = data.get('products', [])
    # Sắp xếp theo thời gian tạo mới nhất
    products.sort(key=lambda x: x.get('id', 0), reverse=True)
    
    # Lấy thông tin user nếu đã đăng nhập
    user_info = None
    if 'user_id' in session:
        users_data = load_users()
        for user in users_data.get('users', []):
            if user.get('username') == session.get('user_id'):
                user_info = {
                    'username': user.get('username'),
                    'full_name': user.get('full_name', user.get('username'))
                }
                break
    
    return render_template('index.html', products=products, user=user_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error='Vui lòng điền đầy đủ thông tin!')
        
        users_data = load_users()
        hashed_password = hash_password(password)
        
        # Tìm user
        for user in users_data.get('users', []):
            if user.get('username') == username and user.get('password') == hashed_password:
                # Đăng nhập thành công
                session['user_id'] = username
                session['user_name'] = user.get('full_name', username)
                
                # Chuyển đến trang được yêu cầu hoặc trang chủ
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
        
        return render_template('login.html', error='Tên đăng nhập hoặc mật khẩu không đúng!')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Trang đăng ký tài khoản mới"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        
        # Kiểm tra dữ liệu
        if not username or not password or not full_name:
            return render_template('register.html', error='Vui lòng điền đầy đủ thông tin!')
        
        if password != confirm_password:
            return render_template('register.html', error='Mật khẩu xác nhận không khớp!')
        
        if len(password) < 6:
            return render_template('register.html', error='Mật khẩu phải có ít nhất 6 ký tự!')
        
        users_data = load_users()
        
        # Kiểm tra username đã tồn tại chưa
        for user in users_data.get('users', []):
            if user.get('username') == username:
                return render_template('register.html', error='Tên đăng nhập đã tồn tại!')
        
        # Tạo user mới
        new_user = {
            'username': username,
            'password': hash_password(password),
            'full_name': full_name,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if 'users' not in users_data:
            users_data['users'] = []
        users_data['users'].append(new_user)
        save_users(users_data)
        
        # Tự động đăng nhập sau khi đăng ký
        session['user_id'] = username
        session['user_name'] = full_name
        
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Đăng xuất"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Trang tạo sản phẩm mới (yêu cầu đăng nhập)"""
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        product_name = request.form.get('product_name', '').strip()
        # Lấy tên người đăng nhập từ session
        farmer_name = session.get('user_name', session.get('user_id', '')).strip()
        planting_date = request.form.get('planting_date', '').strip()
        harvest_date = request.form.get('harvest_date', '').strip()
        production_area = request.form.get('production_area', '').strip()
        production_process = request.form.get('production_process', '').strip()
        harvest_process = request.form.get('harvest_process', '').strip()
        storage_method = request.form.get('storage_method', '').strip()
        
        # Kiểm tra dữ liệu
        if not product_name:
            # Lấy thông tin user để hiển thị lại form
            user_info = {
                'username': session.get('user_id'),
                'full_name': session.get('user_name', session.get('user_id'))
            }
            return render_template('create.html', error='Vui lòng điền tên sản phẩm!', user=user_info)
        
        # Tạo ID sản phẩm bằng timestamp
        product_id = str(int(time.time() * 1000))
        
        # Tạo mã QR
        qr_path = generate_qrcode(product_id, request.url_root)
        
        # Tạo đối tượng sản phẩm
        product = {
            'id': product_id,
            'product_name': product_name,
            'farmer_name': farmer_name,
            'planting_date': planting_date,
            'harvest_date': harvest_date,
            'production_area': production_area,
            'production_process': production_process,
            'harvest_process': harvest_process,
            'storage_method': storage_method,
            'qr_code': f'qrcodes/{product_id}.png',
            'created_by': session.get('user_id'),  # Lưu username của người tạo
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Lưu vào data.json
        data = load_data()
        if 'products' not in data:
            data['products'] = []
        data['products'].append(product)
        save_data(data)
        
        # Chuyển đến trang chi tiết sản phẩm
        return redirect(url_for('product', product_id=product_id))
    
    # Lấy thông tin user
    user_info = {
        'username': session.get('user_id'),
        'full_name': session.get('user_name', session.get('user_id'))
    }
    return render_template('create.html', user=user_info)

@app.route('/manage')
@login_required
def manage():
    """Trang quản lý sản phẩm - chỉ hiển thị sản phẩm của user đăng nhập"""
    current_user = session.get('user_id')
    data = load_data()
    products = data.get('products', [])
    
    # Lọc chỉ sản phẩm của user hiện tại
    my_products = [p for p in products if p.get('created_by') == current_user]
    my_products.sort(key=lambda x: x.get('id', 0), reverse=True)
    
    # Lấy thông tin user
    user_info = {
        'username': session.get('user_id'),
        'full_name': session.get('user_name', session.get('user_id'))
    }
    
    return render_template('manage.html', products=my_products, user=user_info)

@app.route('/delete/<product_id>')
@login_required
def delete_product(product_id):
    """Xóa sản phẩm (chỉ xóa được sản phẩm của mình)"""
    current_user = session.get('user_id')
    data = load_data()
    products = data.get('products', [])
    
    # Tìm và xóa sản phẩm
    product_found = False
    for i, p in enumerate(products):
        if p.get('id') == product_id:
            # Kiểm tra quyền sở hữu
            if p.get('created_by') != current_user:
                return redirect(url_for('manage'))
            # Xóa sản phẩm
            products.pop(i)
            product_found = True
            break
    
    if product_found:
        data['products'] = products
        save_data(data)
        
        # Xóa file QR code
        qr_path = os.path.join(QRCODE_DIR, f'{product_id}.png')
        if os.path.exists(qr_path):
            try:
                os.remove(qr_path)
            except:
                pass
    
    return redirect(url_for('manage'))

@app.route('/edit/<product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Sửa sản phẩm (chỉ sửa được sản phẩm của mình)"""
    current_user = session.get('user_id')
    data = load_data()
    products = data.get('products', [])
    
    # Tìm sản phẩm
    product = None
    product_index = -1
    for i, p in enumerate(products):
        if p.get('id') == product_id:
            # Kiểm tra quyền sở hữu
            if p.get('created_by') != current_user:
                return redirect(url_for('manage'))
            product = p
            product_index = i
            break
    
    if not product:
        return redirect(url_for('manage'))
    
    if request.method == 'POST':
        # Cập nhật thông tin sản phẩm
        product['product_name'] = request.form.get('product_name', '').strip()
        # farmer_name không đổi vì đã được set khi tạo
        product['planting_date'] = request.form.get('planting_date', '').strip()
        product['harvest_date'] = request.form.get('harvest_date', '').strip()
        product['production_area'] = request.form.get('production_area', '').strip()
        product['production_process'] = request.form.get('production_process', '').strip()
        product['harvest_process'] = request.form.get('harvest_process', '').strip()
        product['storage_method'] = request.form.get('storage_method', '').strip()
        product['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Kiểm tra dữ liệu
        if not product['product_name']:
            user_info = {
                'username': session.get('user_id'),
                'full_name': session.get('user_name', session.get('user_id'))
            }
            return render_template('edit.html', product=product, error='Vui lòng điền tên sản phẩm!', user=user_info)
        
        # Lưu lại
        products[product_index] = product
        data['products'] = products
        save_data(data)
        
        return redirect(url_for('manage'))
    
    # Lấy thông tin user
    user_info = {
        'username': session.get('user_id'),
        'full_name': session.get('user_name', session.get('user_id'))
    }
    return render_template('edit.html', product=product, user=user_info)

@app.route('/product/<product_id>')
def product(product_id):
    """Trang chi tiết sản phẩm - hiển thị khi quét QR"""
    data = load_data()
    products = data.get('products', [])
    
    # Tìm sản phẩm theo ID
    product = None
    for p in products:
        if p.get('id') == product_id:
            product = p
            break
    
    if not product:
        return render_template('product.html', error='Không tìm thấy sản phẩm!', product=None)
    
    return render_template('product.html', product=product, error=None)

if __name__ == '__main__':
    # Đảm bảo file data.json và users.json tồn tại
    load_data()
    load_users()
    # Chỉ chạy debug mode khi chạy local
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

