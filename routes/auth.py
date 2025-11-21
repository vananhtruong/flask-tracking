"""Routes cho authentication"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
import utils

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error='Vui lòng điền đầy đủ thông tin!')
        
        users_data = utils.load_users()
        hashed_password = utils.hash_password(password)
        
        # Tìm user
        for user in users_data.get('users', []):
            if user.get('username') == username and user.get('password') == hashed_password:
                # Đăng nhập thành công
                session['user_id'] = username
                session['user_name'] = user.get('full_name', username)
                
                # Chuyển đến trang được yêu cầu hoặc trang chủ
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
        
        return render_template('login.html', error='Tên đăng nhập hoặc mật khẩu không đúng!')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
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
        
        users_data = utils.load_users()
        
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
            'password': utils.hash_password(password),
            'full_name': full_name,
            'phone': phone,
            'email': email,
            'address': address,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if 'users' not in users_data:
            users_data['users'] = []
        users_data['users'].append(new_user)
        utils.save_users(users_data)
        
        # Tự động đăng nhập sau khi đăng ký
        session['user_id'] = username
        session['user_name'] = full_name
        
        return redirect(url_for('main.index'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Đăng xuất"""
    session.clear()
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@utils.login_required
def profile():
    """Trang thông tin cá nhân - xem và sửa"""
    current_username = session.get('user_id')
    users_data = utils.load_users()
    
    # Tìm user hiện tại
    current_user = None
    user_index = -1
    for i, user in enumerate(users_data.get('users', [])):
        if user.get('username') == current_username:
            current_user = user
            user_index = i
            break
    
    if not current_user:
        return redirect(url_for('main.index'))
    
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
        utils.save_users(users_data)
        
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

