"""Routes chính - trang chủ"""
from flask import Blueprint, render_template, request, session, Response, url_for, send_from_directory
from datetime import datetime
import os
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

@main_bp.route('/sitemap.xml')
def sitemap():
    """Tạo sitemap.xml cho Google Search Console"""
    base_url = request.url_root.rstrip('/')
    data = utils.load_data()
    products = data.get('products', [])
    
    # Tạo XML sitemap
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Trang chủ
    sitemap_xml += '  <url>\n'
    sitemap_xml += f'    <loc>{base_url}/</loc>\n'
    sitemap_xml += '    <changefreq>daily</changefreq>\n'
    sitemap_xml += '    <priority>1.0</priority>\n'
    sitemap_xml += '  </url>\n'
    
    # Các trang sản phẩm
    for product in products:
        product_id = product.get('id')
        if product_id:
            sitemap_xml += '  <url>\n'
            sitemap_xml += f'    <loc>{base_url}/product/{product_id}</loc>\n'
            # Lấy ngày cập nhật cuối cùng
            updated_date = product.get('updated_at') or product.get('created_at', '')
            if updated_date:
                try:
                    # Chuyển đổi format ngày nếu cần
                    dt = datetime.strptime(updated_date, '%Y-%m-%d %H:%M:%S')
                    sitemap_xml += f'    <lastmod>{dt.strftime("%Y-%m-%d")}</lastmod>\n'
                except:
                    pass
            sitemap_xml += '    <changefreq>weekly</changefreq>\n'
            sitemap_xml += '    <priority>0.8</priority>\n'
            sitemap_xml += '  </url>\n'
    
    sitemap_xml += '</urlset>'
    
    return Response(sitemap_xml, mimetype='application/xml')

@main_bp.route('/robots.txt')
def robots():
    """Tạo robots.txt để hướng dẫn Google bot"""
    base_url = request.url_root.rstrip('/')
    robots_txt = f"""User-agent: *
Allow: /
Allow: /product/
Disallow: /login
Disallow: /register
Disallow: /create
Disallow: /edit/
Disallow: /delete/
Disallow: /manage
Disallow: /view/
Disallow: /ai-report/
Disallow: /static/uploads/

Sitemap: {base_url}/sitemap.xml
"""
    return Response(robots_txt, mimetype='text/plain')

@main_bp.route('/googleb17c430127147f34.html')
def google_verification():
    """Route để Google Search Console verify website"""
    return send_from_directory('static', 'googleb17c430127147f34.html')

