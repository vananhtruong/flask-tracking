"""Logic phân tích AI cho sản phẩm"""
from datetime import datetime as dt

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

