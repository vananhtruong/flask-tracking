"""Routes cho quản lý sản phẩm"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
import time
import utils
import ai_analysis

products_bp = Blueprint('products', __name__)

@products_bp.route('/create', methods=['GET', 'POST'])
@utils.login_required
def create():
    """Trang tạo sản phẩm mới (yêu cầu đăng nhập)"""
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        product_name = request.form.get('product_name', '').strip()
        # Lấy tên người đăng nhập từ session
        farmer_name = session.get('user_name', session.get('user_id', '')).strip()
        plant_type = request.form.get('plant_type', 'seasonal').strip()  # seasonal hoặc perennial
        planting_date = request.form.get('planting_date', '').strip()
        harvest_date = request.form.get('harvest_date', '').strip()
        production_area = request.form.get('production_area', '').strip()
        production_process = request.form.get('production_process', '').strip()
        harvest_process = request.form.get('harvest_process', '').strip()
        storage_method = request.form.get('storage_method', '').strip()
        
        # Kiểm tra dữ liệu
        if not product_name:
            # Lấy thông tin user để hiển thị lại form
            user_info = utils.get_user_info(session)
            return render_template('create.html', error='Vui lòng điền tên sản phẩm!', user=user_info)
        
        # Tạo ID sản phẩm bằng timestamp
        product_id = str(int(time.time() * 1000))
        
        # Xử lý upload file cho quá trình sản xuất
        production_files = request.files.getlist('production_files')
        production_media = utils.save_uploaded_files(production_files, product_id, 'production')
        
        # Xử lý upload file cho quá trình thu hoạch
        harvest_files = request.files.getlist('harvest_files')
        harvest_media = utils.save_uploaded_files(harvest_files, product_id, 'harvest')
        
        # Tạo mã QR
        qr_path = utils.generate_qrcode(product_id, request.url_root)
        
        # Tạo đối tượng sản phẩm
        product = {
            'id': product_id,
            'product_name': product_name,
            'farmer_name': farmer_name,
            'plant_type': plant_type,  # 'seasonal' (cây thời vụ) hoặc 'perennial' (cây lâu năm)
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
        data = utils.load_data()
        if 'products' not in data:
            data['products'] = []
        data['products'].append(product)
        utils.save_data(data)
        
        # Chuyển đến trang chi tiết sản phẩm của người tạo
        return redirect(url_for('products.view_product', product_id=product_id))
    
    # Lấy thông tin user
    user_info = utils.get_user_info(session)
    return render_template('create.html', user=user_info)

@products_bp.route('/manage')
@utils.login_required
def manage():
    """Trang quản lý sản phẩm - chỉ hiển thị sản phẩm của user đăng nhập"""
    current_user = session.get('user_id')
    data = utils.load_data()
    products = data.get('products', [])
    
    # Lọc chỉ sản phẩm của user hiện tại
    my_products = [p for p in products if p.get('created_by') == current_user]
    my_products.sort(key=lambda x: x.get('id', 0), reverse=True)
    
    # Lấy thông tin user
    user_info = utils.get_user_info(session)
    
    return render_template('manage.html', products=my_products, user=user_info)

@products_bp.route('/delete/<product_id>')
@utils.login_required
def delete_product(product_id):
    """Xóa sản phẩm (chỉ xóa được sản phẩm của mình)"""
    current_user = session.get('user_id')
    data = utils.load_data()
    products = data.get('products', [])
    
    # Tìm và xóa sản phẩm
    product_found = False
    for i, p in enumerate(products):
        if p.get('id') == product_id:
            # Kiểm tra quyền sở hữu
            if p.get('created_by') != current_user:
                return redirect(url_for('products.manage'))
            # Xóa sản phẩm
            products.pop(i)
            product_found = True
            break
    
    if product_found:
        data['products'] = products
        utils.save_data(data)
        
        # Xóa file QR code và media
        utils.delete_product_files(product_id)
        
        return redirect(url_for('products.manage'))
    
    return redirect(url_for('products.manage'))

@products_bp.route('/edit/<product_id>', methods=['GET', 'POST'])
@utils.login_required
def edit_product(product_id):
    """Sửa sản phẩm (chỉ sửa được sản phẩm của mình)"""
    current_user = session.get('user_id')
    data = utils.load_data()
    products = data.get('products', [])
    
    # Tìm sản phẩm
    product = None
    product_index = -1
    for i, p in enumerate(products):
        if p.get('id') == product_id:
            # Kiểm tra quyền sở hữu
            if p.get('created_by') != current_user:
                return redirect(url_for('products.manage'))
            product = p
            product_index = i
            break
    
    if not product:
        return redirect(url_for('products.manage'))
    
    if request.method == 'POST':
        # Cập nhật thông tin sản phẩm
        product['product_name'] = request.form.get('product_name', '').strip()
        # farmer_name không đổi vì đã được set khi tạo
        product['plant_type'] = request.form.get('plant_type', 'seasonal').strip()  # seasonal hoặc perennial
        product['planting_date'] = request.form.get('planting_date', '').strip()
        product['harvest_date'] = request.form.get('harvest_date', '').strip()
        product['production_area'] = request.form.get('production_area', '').strip()
        product['production_process'] = request.form.get('production_process', '').strip()
        product['harvest_process'] = request.form.get('harvest_process', '').strip()
        product['storage_method'] = request.form.get('storage_method', '').strip()
        product['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Xử lý upload file mới cho quá trình sản xuất
        production_files = request.files.getlist('production_files')
        new_production_media = utils.save_uploaded_files(production_files, product_id, 'production')
        if new_production_media:
            if 'production_media' not in product:
                product['production_media'] = []
            product['production_media'].extend(new_production_media)
        
        # Xử lý upload file mới cho quá trình thu hoạch
        harvest_files = request.files.getlist('harvest_files')
        new_harvest_media = utils.save_uploaded_files(harvest_files, product_id, 'harvest')
        if new_harvest_media:
            if 'harvest_media' not in product:
                product['harvest_media'] = []
            product['harvest_media'].extend(new_harvest_media)
        
        # Kiểm tra dữ liệu
        if not product['product_name']:
            user_info = utils.get_user_info(session)
            return render_template('edit.html', product=product, error='Vui lòng điền tên sản phẩm!', user=user_info)
        
        # Lưu lại
        products[product_index] = product
        data['products'] = products
        utils.save_data(data)
        
        return redirect(url_for('products.manage'))
    
    # Lấy thông tin user
    user_info = utils.get_user_info(session)
    return render_template('edit.html', product=product, user=user_info)

@products_bp.route('/product/<product_id>')
def product(product_id):
    """Trang chi tiết sản phẩm - hiển thị khi quét QR"""
    data = utils.load_data()
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
    utils.save_data(data)
    
    # Lấy thông tin liên hệ của người sản xuất
    farmer_contact = None
    created_by = product.get('created_by')
    if created_by:
        users_data = utils.load_users()
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

@products_bp.route('/view/<product_id>')
@utils.login_required
def view_product(product_id):
    """Trang chi tiết sản phẩm cho người tạo - có nút sửa/xóa"""
    current_user = session.get('user_id')
    data = utils.load_data()
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
        return redirect(url_for('products.manage'))
    
    # Lấy thông tin user
    user_info = utils.get_user_info(session)
    
    return render_template('view_product.html', product=product, error=None, user=user_info)

@products_bp.route('/ai-report/<product_id>')
@utils.login_required
def ai_report(product_id):
    """Trang báo cáo AI phân tích sản phẩm - phân tích mùa vụ, đánh giá tiêu chuẩn, gợi ý thị trường"""
    current_user = session.get('user_id')
    data = utils.load_data()
    products = data.get('products', [])
    
    # Tìm sản phẩm theo ID
    product = None
    for p in products:
        if p.get('id') == product_id:
            product = p
            break
    
    if not product:
        return redirect(url_for('products.manage'))
    
    # Kiểm tra quyền sở hữu
    if product.get('created_by') != current_user:
        return redirect(url_for('products.manage'))
    
    # Phân tích AI
    analysis = ai_analysis.analyze_product_ai(product)
    
    # Lấy thông tin user
    user_info = utils.get_user_info(session)
    
    return render_template('ai_report.html', product=product, analysis=analysis, user=user_info)

