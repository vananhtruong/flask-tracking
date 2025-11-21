"""Routes chính - trang chủ"""
from flask import Blueprint, render_template, request, session
import utils

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Trang chính - hiển thị danh sách sản phẩm"""
    data = utils.load_data()
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
    user_info = utils.get_user_info(session)
    
    return render_template('index.html', products=products, user=user_info, search_query=search_query)

