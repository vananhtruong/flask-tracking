from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from functools import wraps
from werkzeug.utils import secure_filename
import json
import os
import qrcode
from datetime import datetime
import time
import hashlib
import shutil

app = Flask(__name__)
# Sử dụng biến môi trường cho secret key khi deploy
app.secret_key = os.environ.get('SECRET_KEY', '0deab411eb2ed51a3a625a05ce9602c521d54ad4c3ceab1d3af2d35978b9ca15')

# Đường dẫn file data
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'data.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
QRCODE_DIR = 'static/qrcodes'
UPLOAD_DIR = 'static/uploads'

# Cấu hình upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mkv', 'webm'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Tạo thư mục data và qrcodes nếu chưa tồn tại
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(QRCODE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'production'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'harvest'), exist_ok=True)

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

def allowed_file(filename):
    """Kiểm tra extension file có được phép không"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    
    upload_folder = os.path.join(UPLOAD_DIR, upload_type, product_id)
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
    
    # Xử lý tìm kiếm
    search_query = request.args.get('search', '').strip()
    if search_query:
        # Lọc sản phẩm theo từ khóa tìm kiếm
        search_lower = search_query.lower()
        filtered_products = []
        for product in products:
            # Tìm trong tên sản phẩm, tên người sản xuất, khu vực
            product_name = product.get('product_name', '').lower()
            farmer_name = product.get('farmer_name', '').lower()
            production_area = product.get('production_area', '').lower()
            
            if (search_lower in product_name or 
                search_lower in farmer_name or 
                search_lower in production_area):
                filtered_products.append(product)
        
        products = filtered_products
    
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
    
    return render_template('index.html', products=products, user=user_info, search_query=search_query)

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
        
        # Lấy thông tin liên hệ
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        
        # Tạo user mới
        new_user = {
            'username': username,
            'password': hash_password(password),
            'full_name': full_name,
            'phone': phone,
            'email': email,
            'address': address,
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

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Trang thông tin cá nhân - xem và sửa"""
    current_username = session.get('user_id')
    users_data = load_users()
    
    # Tìm user hiện tại
    current_user = None
    user_index = -1
    for i, user in enumerate(users_data.get('users', [])):
        if user.get('username') == current_username:
            current_user = user
            user_index = i
            break
    
    if not current_user:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Cập nhật thông tin
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        
        if not full_name:
            user_info = {
                'username': current_user.get('username'),
                'full_name': current_user.get('full_name', ''),
                'phone': current_user.get('phone', ''),
                'email': current_user.get('email', ''),
                'address': current_user.get('address', ''),
                'created_at': current_user.get('created_at', ''),
                'updated_at': current_user.get('updated_at', '')
            }
            return render_template('profile.html', user=user_info, error='Vui lòng điền họ và tên!')
        
        # Cập nhật thông tin user
        current_user['full_name'] = full_name
        current_user['phone'] = phone
        current_user['email'] = email
        current_user['address'] = address
        current_user['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Cập nhật session
        session['user_name'] = full_name
        
        # Lưu lại
        users_data['users'][user_index] = current_user
        save_users(users_data)
        
        # Chuẩn bị user_info để render
        user_info = {
            'username': current_user.get('username'),
            'full_name': current_user.get('full_name', ''),
            'phone': current_user.get('phone', ''),
            'email': current_user.get('email', ''),
            'address': current_user.get('address', ''),
            'created_at': current_user.get('created_at', ''),
            'updated_at': current_user.get('updated_at', '')
        }
        
        return render_template('profile.html', user=user_info, success='Cập nhật thông tin thành công!')
    
    # Chuẩn bị user_info để render
    user_info = {
        'username': current_user.get('username'),
        'full_name': current_user.get('full_name', ''),
        'phone': current_user.get('phone', ''),
        'email': current_user.get('email', ''),
        'address': current_user.get('address', ''),
        'created_at': current_user.get('created_at', ''),
        'updated_at': current_user.get('updated_at', '')
    }
    
    return render_template('profile.html', user=user_info)

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
        
        # Xử lý upload file cho quá trình sản xuất
        production_files = request.files.getlist('production_files')
        production_media = save_uploaded_files(production_files, product_id, 'production')
        
        # Xử lý upload file cho quá trình thu hoạch
        harvest_files = request.files.getlist('harvest_files')
        harvest_media = save_uploaded_files(harvest_files, product_id, 'harvest')
        
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
            'production_media': production_media,  # Danh sách file media quá trình sản xuất
            'harvest_media': harvest_media,  # Danh sách file media quá trình thu hoạch
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
        
        # Chuyển đến trang chi tiết sản phẩm của người tạo
        return redirect(url_for('view_product', product_id=product_id))
    
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
        
        # Xóa thư mục media của sản phẩm
        production_media_dir = os.path.join(UPLOAD_DIR, 'production', product_id)
        harvest_media_dir = os.path.join(UPLOAD_DIR, 'harvest', product_id)
        
        import shutil
        for media_dir in [production_media_dir, harvest_media_dir]:
            if os.path.exists(media_dir):
                try:
                    shutil.rmtree(media_dir)
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
        
        # Xử lý upload file mới cho quá trình sản xuất
        production_files = request.files.getlist('production_files')
        new_production_media = save_uploaded_files(production_files, product_id, 'production')
        if new_production_media:
            if 'production_media' not in product:
                product['production_media'] = []
            product['production_media'].extend(new_production_media)
        
        # Xử lý upload file mới cho quá trình thu hoạch
        harvest_files = request.files.getlist('harvest_files')
        new_harvest_media = save_uploaded_files(harvest_files, product_id, 'harvest')
        if new_harvest_media:
            if 'harvest_media' not in product:
                product['harvest_media'] = []
            product['harvest_media'].extend(new_harvest_media)
        
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
    product_index = -1
    for i, p in enumerate(products):
        if p.get('id') == product_id:
            product = p
            product_index = i
            break
    
    if not product:
        return render_template('product.html', error='Không tìm thấy sản phẩm!', product=None, farmer_contact=None)
    
    # Tăng số lượt quét QR
    if 'scan_count' not in product:
        product['scan_count'] = 0
    product['scan_count'] = product.get('scan_count', 0) + 1
    product['last_scan'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Lưu lại
    products[product_index] = product
    data['products'] = products
    save_data(data)
    
    # Lấy thông tin liên hệ của người sản xuất
    farmer_contact = None
    created_by = product.get('created_by')
    if created_by:
        users_data = load_users()
        for user in users_data.get('users', []):
            if user.get('username') == created_by:
                farmer_contact = {
                    'full_name': user.get('full_name', ''),
                    'phone': user.get('phone', ''),
                    'email': user.get('email', ''),
                    'address': user.get('address', '')
                }
                break
    
    return render_template('product.html', product=product, error=None, farmer_contact=farmer_contact)

@app.route('/view/<product_id>')
@login_required
def view_product(product_id):
    """Trang chi tiết sản phẩm cho người tạo - có nút sửa/xóa"""
    current_user = session.get('user_id')
    data = load_data()
    products = data.get('products', [])
    
    # Tìm sản phẩm theo ID
    product = None
    for p in products:
        if p.get('id') == product_id:
            product = p
            break
    
    if not product:
        return render_template('view_product.html', error='Không tìm thấy sản phẩm!', product=None)
    
    # Kiểm tra quyền sở hữu
    if product.get('created_by') != current_user:
        return redirect(url_for('manage'))
    
    # Lấy thông tin user
    user_info = {
        'username': session.get('user_id'),
        'full_name': session.get('user_name', session.get('user_id'))
    }
    
    return render_template('view_product.html', product=product, error=None, user=user_info)

def analyze_product_ai(product):
    """Phân tích sản phẩm bằng AI - phân tích mùa vụ, đánh giá tiêu chuẩn, gợi ý thị trường"""
    analysis = {
        'transparency': {},
        'recommendations': [],
        'score': 0,
        'stats': {},
        'season_analysis': {},
        'standards_compliance': {},
        'market_suggestions': []
    }
    
    # Đánh giá tính minh bạch
    has_basic_info = bool(product.get('product_name') and product.get('farmer_name') and product.get('production_area'))
    has_production_process = bool(product.get('production_process') and len(product.get('production_process', '')) > 10)
    has_harvest_process = bool(product.get('harvest_process') and len(product.get('harvest_process', '')) > 10)
    has_storage_method = bool(product.get('storage_method') and len(product.get('storage_method', '')) > 10)
    has_production_media = bool(product.get('production_media') and len(product.get('production_media', [])) > 0)
    has_harvest_media = bool(product.get('harvest_media') and len(product.get('harvest_media', [])) > 0)
    has_dates = bool(product.get('planting_date') and product.get('harvest_date'))
    
    analysis['transparency'] = {
        'basic_info': has_basic_info,
        'production_process': has_production_process,
        'harvest_process': has_harvest_process,
        'storage_method': has_storage_method,
        'production_media': has_production_media,
        'harvest_media': has_harvest_media,
        'dates': has_dates
    }
    
    # Tính điểm minh bạch
    score = 0
    if has_basic_info: score += 15
    if has_production_process: score += 15
    if has_harvest_process: score += 15
    if has_storage_method: score += 10
    if has_production_media: score += 15
    if has_harvest_media: score += 15
    if has_dates: score += 15
    
    analysis['score'] = score
    
    # Phân tích mùa vụ và năng suất dự kiến
    planting_date = product.get('planting_date')
    harvest_date = product.get('harvest_date')
    production_area = product.get('production_area', '')
    
    season_info = {
        'season': 'Không xác định',
        'growth_period': None,
        'yield_prediction': 'Trung bình',
        'harvest_timing': 'Phù hợp'
    }
    
    if planting_date and harvest_date:
        try:
            from datetime import datetime as dt
            plant = dt.strptime(planting_date, '%Y-%m-%d')
            harvest = dt.strptime(harvest_date, '%Y-%m-%d')
            growth_days = (harvest - plant).days
            
            # Xác định mùa vụ
            month = plant.month
            if month in [1, 2, 3]:
                season_info['season'] = 'Đông Xuân'
            elif month in [4, 5, 6]:
                season_info['season'] = 'Xuân Hè'
            elif month in [7, 8, 9]:
                season_info['season'] = 'Hè Thu'
            else:
                season_info['season'] = 'Thu Đông'
            
            season_info['growth_period'] = f"{growth_days} ngày"
            
            # Phân tích theo loại sản phẩm để đánh giá thời gian sinh trưởng
            product_name_lower = product.get('product_name', '').lower()
            
            # Xác định loại sản phẩm và đánh giá phù hợp
            if any(x in product_name_lower for x in ['lúa', 'rice', 'gạo']):
                # Lúa: 90-120 ngày là bình thường
                if growth_days < 80:
                    season_info['yield_prediction'] = 'Ngắn ngày (có thể ảnh hưởng năng suất)'
                elif growth_days > 150:
                    season_info['yield_prediction'] = 'Dài ngày (năng suất cao)'
                else:
                    season_info['yield_prediction'] = 'Phù hợp (90-120 ngày)'
            elif any(x in product_name_lower for x in ['rau', 'vegetable', 'cải', 'xà lách', 'cà chua', 'ớt', 'dưa']):
                # Rau củ: 30-90 ngày
                if growth_days < 20:
                    season_info['yield_prediction'] = 'Quá ngắn (có thể chưa đủ thời gian)'
                elif growth_days > 120:
                    season_info['yield_prediction'] = 'Dài ngày (có thể là cây lâu năm)'
                else:
                    season_info['yield_prediction'] = 'Phù hợp với rau củ (30-90 ngày)'
            elif any(x in product_name_lower for x in ['trái cây', 'fruit', 'nho', 'táo', 'cam', 'chuối', 'xoài', 'bòn bon']):
                # Trái cây: 60-180 ngày hoặc lâu hơn
                if growth_days < 40:
                    season_info['yield_prediction'] = 'Ngắn ngày (có thể là cây non)'
                elif growth_days > 200:
                    season_info['yield_prediction'] = 'Cây lâu năm (năng suất ổn định)'
                else:
                    season_info['yield_prediction'] = 'Phù hợp với cây ăn trái'
            elif any(x in product_name_lower for x in ['cà phê', 'coffee', 'hồ tiêu', 'pepper', 'quế', 'cinnamon']):
                # Cây công nghiệp: thường > 180 ngày
                if growth_days < 100:
                    season_info['yield_prediction'] = 'Ngắn ngày (có thể là giai đoạn đầu)'
                else:
                    season_info['yield_prediction'] = 'Phù hợp với cây công nghiệp'
            else:
                # Nông sản khác: đánh giá chung
                if growth_days < 60:
                    season_info['yield_prediction'] = 'Thời gian sinh trưởng ngắn'
                elif growth_days > 180:
                    season_info['yield_prediction'] = 'Thời gian sinh trưởng dài'
                else:
                    season_info['yield_prediction'] = 'Thời gian sinh trưởng trung bình'
            
            # Đánh giá thời điểm thu hoạch
            current_date = dt.now()
            if harvest < current_date:
                days_since_harvest = (current_date - harvest).days
                if days_since_harvest > 30:
                    season_info['harvest_timing'] = f'Đã thu hoạch {days_since_harvest} ngày trước'
                else:
                    season_info['harvest_timing'] = 'Vừa thu hoạch'
            else:
                days_to_harvest = (harvest - current_date).days
                if days_to_harvest < 7:
                    season_info['harvest_timing'] = f'Gần đến ngày thu hoạch (còn {days_to_harvest} ngày)'
                else:
                    season_info['harvest_timing'] = f'Còn {days_to_harvest} ngày đến ngày thu hoạch'
        except:
            pass
    
    analysis['season_analysis'] = season_info
    
    # Đánh giá tuân thủ tiêu chuẩn số hóa
    standards = {
        'has_digital_records': has_dates and has_production_process,
        'has_media_evidence': has_production_media or has_harvest_media,
        'has_complete_info': has_basic_info and has_production_process and has_harvest_process,
        'has_storage_info': has_storage_method,
        'compliance_level': 'Cơ bản'
    }
    
    compliance_score = 0
    if standards['has_digital_records']: compliance_score += 25
    if standards['has_media_evidence']: compliance_score += 25
    if standards['has_complete_info']: compliance_score += 30
    if standards['has_storage_info']: compliance_score += 20
    
    if compliance_score >= 80:
        standards['compliance_level'] = 'Xuất sắc'
    elif compliance_score >= 60:
        standards['compliance_level'] = 'Tốt'
    elif compliance_score >= 40:
        standards['compliance_level'] = 'Trung bình'
    else:
        standards['compliance_level'] = 'Cần cải thiện'
    
    standards['compliance_score'] = compliance_score
    analysis['standards_compliance'] = standards
    
    # Gợi ý thị trường và giá cả - phân tích theo nhiều loại nông sản
    market_suggestions = []
    product_name_lower = product.get('product_name', '').lower()
    
    # Phân tích theo loại sản phẩm
    if any(x in product_name_lower for x in ['lúa', 'rice', 'gạo']):
        market_suggestions.append({
            'type': 'Thị trường',
            'suggestion': 'Giá lúa gạo hiện tại ổn định. Nên bán vào thời điểm sau thu hoạch để đạt giá tốt nhất. Thị trường nội địa ổn định. Có thể mở rộng xuất khẩu nếu đạt tiêu chuẩn chất lượng.'
        })
    elif any(x in product_name_lower for x in ['rau', 'vegetable', 'cải', 'xà lách', 'cà chua', 'ớt', 'dưa chuột', 'bắp cải']):
        market_suggestions.append({
            'type': 'Thị trường',
            'suggestion': 'Rau củ tươi có giá trị cao, đặc biệt là rau sạch có truy xuất nguồn gốc. Nên bán tại chợ, siêu thị hoặc kênh online. Thị trường rau sạch đang phát triển mạnh. Người tiêu dùng sẵn sàng trả giá cao cho rau có nguồn gốc rõ ràng.'
        })
    elif any(x in product_name_lower for x in ['trái cây', 'fruit', 'nho', 'táo', 'cam', 'chuối', 'xoài', 'bòn bon', 'mít', 'sầu riêng']):
        market_suggestions.append({
            'type': 'Thị trường',
            'suggestion': 'Trái cây tươi có giá trị cao, đặc biệt là trái cây đặc sản địa phương. Nên bán trực tiếp hoặc qua kênh online để tăng lợi nhuận. Tập trung vào chất lượng và truy xuất nguồn gốc để xây dựng thương hiệu.'
        })
    elif any(x in product_name_lower for x in ['cà phê', 'coffee']):
        market_suggestions.append({
            'type': 'Thị trường',
            'suggestion': 'Cà phê có giá trị xuất khẩu cao. Nên chú trọng chất lượng và chứng nhận để đạt giá tốt nhất. Thị trường cà phê trong nước và xuất khẩu đều phát triển. Có thể kết nối với các nhà rang xay và xuất khẩu.'
        })
    elif any(x in product_name_lower for x in ['hồ tiêu', 'pepper', 'tiêu']):
        market_suggestions.append({
            'type': 'Thị trường',
            'suggestion': 'Hồ tiêu có giá trị xuất khẩu cao. Chất lượng và truy xuất nguồn gốc là yếu tố quan trọng. Thị trường hồ tiêu chủ yếu là xuất khẩu. Nên đảm bảo chất lượng và tiêu chuẩn để đạt giá tốt.'
        })
    elif any(x in product_name_lower for x in ['quế', 'cinnamon']):
        market_suggestions.append({
            'type': 'Thị trường',
            'suggestion': 'Quế là đặc sản địa phương có giá trị cao. Quế Tiên Phước nổi tiếng, nên quảng bá thương hiệu địa phương. Quế có thể tiêu thụ trong nước và xuất khẩu. Tập trung vào chất lượng và quảng bá thương hiệu địa phương.'
        })
    elif any(x in product_name_lower for x in ['bòn bon', 'langsat']):
        market_suggestions.append({
            'type': 'Thị trường',
            'suggestion': 'Bòn bon Tiên Châu là đặc sản nổi tiếng. Nên quảng bá thương hiệu địa phương để tăng giá trị. Bòn bon Tiên Châu có thể tiêu thụ tại địa phương và các thành phố lớn. Truy xuất nguồn gốc giúp tăng niềm tin.'
        })
    else:
        # Nông sản khác
        market_suggestions.append({
            'type': 'Thị trường',
            'suggestion': 'Nông sản có truy xuất nguồn gốc thường có giá cao hơn 15-30% so với sản phẩm thông thường. Hãy tận dụng điều này. Người tiêu dùng ngày càng quan tâm đến nguồn gốc sản phẩm. Hãy tận dụng mã QR để quảng bá và kết nối trực tiếp với người tiêu dùng.'
        })
    
    # Gợi ý theo khu vực
    if production_area:
        area_lower = production_area.lower()
        if any(x in area_lower for x in ['long an', 'đồng bằng sông cửu long', 'miền tây']):
            market_suggestions.append({
                'type': 'Khu vực',
                'suggestion': 'Khu vực Đồng bằng sông Cửu Long có thị trường tiêu thụ lớn. Nên kết nối với các siêu thị và cửa hàng thực phẩm sạch.'
            })
        elif any(x in area_lower for x in ['quảng nam', 'tiên phước', 'tiên châu']):
            market_suggestions.append({
                'type': 'Khu vực',
                'suggestion': 'Khu vực Quảng Nam có nhiều đặc sản địa phương. Hãy quảng bá thương hiệu địa phương như bòn bon Tiên Châu, quế Tiên Phước.'
            })
    
    analysis['market_suggestions'] = market_suggestions
    
    # Thống kê
    analysis['stats'] = {
        'scan_count': product.get('scan_count', 0),
        'production_media_count': len(product.get('production_media', [])),
        'harvest_media_count': len(product.get('harvest_media', [])),
        'has_contact_info': False
    }
    
    # Tạo khuyến nghị cải thiện
    if not has_production_process or len(product.get('production_process', '')) < 50:
        analysis['recommendations'].append(
            "Nên bổ sung thêm thông tin chi tiết về quy trình sản xuất, phân bón, thuốc bảo vệ thực vật để tăng tính minh bạch và niềm tin của người tiêu dùng"
        )
    
    if not has_harvest_process or len(product.get('harvest_process', '')) < 50:
        analysis['recommendations'].append(
            "Nên mô tả rõ ràng quá trình thu hoạch, phương pháp và thời điểm thu hoạch để người tiêu dùng hiểu rõ hơn về chất lượng sản phẩm"
        )
    
    if not has_production_media:
        analysis['recommendations'].append(
            "Nên thêm video hoặc hình ảnh về quá trình sản xuất để tăng độ tin cậy và minh bạch, giúp người tiêu dùng tin tưởng hơn"
        )
    
    if not has_harvest_media:
        analysis['recommendations'].append(
            "Nên thêm video hoặc hình ảnh về quá trình thu hoạch để người tiêu dùng có thể xem trực quan quy trình sản xuất"
        )
    
    if not has_storage_method or len(product.get('storage_method', '')) < 30:
        analysis['recommendations'].append(
            "Nên cung cấp thông tin chi tiết về cách bảo quản sản phẩm, nhiệt độ, độ ẩm để đảm bảo chất lượng và an toàn thực phẩm"
        )
    
    if analysis['stats']['scan_count'] == 0:
        analysis['recommendations'].append(
            "Sản phẩm chưa có lượt quét QR nào. Hãy chia sẻ mã QR trên bao bì, mạng xã hội để tăng độ nhận diện và tin cậy của sản phẩm"
        )
    elif analysis['stats']['scan_count'] < 5:
        analysis['recommendations'].append(
            f"Sản phẩm đã có {analysis['stats']['scan_count']} lượt quét. Hãy tiếp tục quảng bá để tăng mức độ quan tâm và kết nối với người tiêu dùng"
        )
    
    if compliance_score < 60:
        analysis['recommendations'].append(
            "Cần cải thiện mức độ tuân thủ tiêu chuẩn số hóa. Hãy bổ sung đầy đủ thông tin, media và quy trình để đạt tiêu chuẩn cao hơn"
        )
    
    if not analysis['recommendations']:
        analysis['recommendations'].append(
            "Sản phẩm của bạn đã có đầy đủ thông tin minh bạch. Tiếp tục duy trì và cập nhật thông tin định kỳ để giữ được niềm tin của người tiêu dùng."
        )
    
    return analysis

@app.route('/ai-report/<product_id>')
@login_required
def ai_report(product_id):
    """Trang báo cáo AI phân tích sản phẩm - phân tích mùa vụ, đánh giá tiêu chuẩn, gợi ý thị trường"""
    current_user = session.get('user_id')
    data = load_data()
    products = data.get('products', [])
    
    # Tìm sản phẩm theo ID
    product = None
    for p in products:
        if p.get('id') == product_id:
            product = p
            break
    
    if not product:
        return redirect(url_for('manage'))
    
    # Kiểm tra quyền sở hữu
    if product.get('created_by') != current_user:
        return redirect(url_for('manage'))
    
    # Phân tích AI
    analysis = analyze_product_ai(product)
    
    # Lấy thông tin user
    user_info = {
        'username': session.get('user_id'),
        'full_name': session.get('user_name', session.get('user_id'))
    }
    
    return render_template('ai_report.html', product=product, analysis=analysis, user=user_info)

if __name__ == '__main__':
    # Đảm bảo file data.json và users.json tồn tại
    load_data()
    load_users()
    # Chỉ chạy debug mode khi chạy local
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

