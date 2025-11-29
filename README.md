# 🌾 Hệ thống Truy xuất Nguồn gốc Nông sản

Website quản lý và truy xuất nguồn gốc nông sản cho nông dân nhỏ lẻ, được xây dựng bằng Python Flask.

## 📋 Tính năng

### Tính năng cơ bản
- ✅ Trang chủ liệt kê tất cả sản phẩm với tìm kiếm
- ✅ Tạo, sửa, xóa sản phẩm (yêu cầu đăng nhập)
- ✅ Tự động tạo mã QR cho mỗi sản phẩm
- ✅ Trang chi tiết sản phẩm khi quét QR code (không cần đăng nhập)
- ✅ Upload hình ảnh/video cho quá trình sản xuất và thu hoạch
- ✅ Lưu trữ dữ liệu bằng file JSON (đơn giản, dễ hiểu)

### Tính năng nâng cao
- ✅ Hệ thống đăng nhập/đăng ký với bảo mật bcrypt
- ✅ Quản lý sản phẩm cá nhân (chỉ xem/sửa sản phẩm của mình)
- ✅ Phân tích AI tự động: đánh giá mùa vụ, tiêu chuẩn, gợi ý thị trường
- ✅ Thống kê lượt quét QR code
- ✅ Bảo vệ CSRF cho tất cả form
- ✅ Validation file upload (kích thước, định dạng)

## 🚀 Cài đặt và Chạy

### Bước 1: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

Hoặc cài đặt thủ công:

```bash
pip install flask qrcode pillow bcrypt flask-wtf werkzeug
```

### Bước 2: Chạy ứng dụng

```bash
python app.py
```

### Bước 3: Truy cập website

Mở trình duyệt và truy cập: `http://localhost:5000`

## 📁 Cấu trúc thư mục

```
flask-tracking/
│
├── app.py                 # File chính chứa Flask application
├── config.py             # Cấu hình ứng dụng
├── utils.py              # Các hàm tiện ích
├── ai_analysis.py        # Logic phân tích AI
├── requirements.txt      # Danh sách thư viện cần thiết
├── README.md            # File hướng dẫn
├── Procfile             # Cấu hình cho Heroku
├── render.yaml          # Cấu hình cho Render.com
│
├── data/                # Thư mục lưu trữ dữ liệu
│   ├── data.json        # Dữ liệu sản phẩm (tự động tạo)
│   └── users.json       # Dữ liệu người dùng (tự động tạo)
│
├── routes/              # Blueprints cho các routes
│   ├── __init__.py
│   ├── main.py          # Routes trang chủ
│   ├── auth.py          # Routes đăng nhập/đăng ký
│   └── products.py      # Routes quản lý sản phẩm
│
├── static/              # Thư mục chứa file tĩnh
│   ├── style.css        # File CSS
│   ├── qrcodes/         # Thư mục chứa mã QR (tự động tạo)
│   └── uploads/         # Thư mục chứa file upload
│       ├── production/  # Media quá trình sản xuất
│       └── harvest/     # Media quá trình thu hoạch
│
└── templates/           # Thư mục chứa template HTML
    ├── index.html       # Trang chủ
    ├── login.html       # Trang đăng nhập
    ├── register.html    # Trang đăng ký
    ├── profile.html     # Trang thông tin cá nhân
    ├── create.html      # Trang tạo sản phẩm
    ├── edit.html        # Trang sửa sản phẩm
    ├── manage.html      # Trang quản lý sản phẩm
    ├── product.html     # Trang chi tiết sản phẩm (public)
    ├── view_product.html # Trang chi tiết sản phẩm (owner)
    └── ai_report.html   # Trang báo cáo AI
```

## 🎯 Hướng dẫn sử dụng

### Cho người dùng mới

1. **Đăng ký tài khoản**:
   - Click nút "Đăng ký" ở góc trên bên phải
   - Điền thông tin: tên đăng nhập, mật khẩu (tối thiểu 6 ký tự), họ tên, email, số điện thoại
   - Sau khi đăng ký sẽ tự động đăng nhập

2. **Đăng nhập** (nếu đã có tài khoản):
   - Click "Đăng nhập"
   - Nhập tên đăng nhập và mật khẩu
   - Tài khoản mặc định: `admin` / `admin123`

### Quản lý sản phẩm

3. **Xem danh sách sản phẩm**:
   - Trang chủ hiển thị tất cả sản phẩm
   - Có thể tìm kiếm theo tên sản phẩm, tên nông dân, khu vực

4. **Thêm sản phẩm mới** (cần đăng nhập):
   - Click nút "Thêm sản phẩm mới"
   - Điền thông tin: tên sản phẩm (bắt buộc), ngày trồng, ngày thu hoạch, khu vực, quy trình sản xuất, quy trình thu hoạch, phương pháp bảo quản
   - Upload hình ảnh/video cho quá trình sản xuất và thu hoạch (tùy chọn)
   - Click "Tạo mã QR và Lưu sản phẩm"
   - Hệ thống tự động tạo mã QR và chuyển đến trang chi tiết

5. **Quản lý sản phẩm của mình**:
   - Click "Quản lý" để xem tất cả sản phẩm bạn đã tạo
   - Có thể sửa hoặc xóa sản phẩm
   - Xem báo cáo AI phân tích

6. **Xem chi tiết sản phẩm**:
   - Click "Xem chi tiết" trên card sản phẩm
   - Hoặc quét mã QR đã được tạo (không cần đăng nhập)
   - Xem đầy đủ thông tin, media, và thông tin liên hệ của nông dân

7. **Phân tích AI**:
   - Vào trang quản lý sản phẩm
   - Click "Xem báo cáo AI" trên sản phẩm
   - Xem phân tích về mùa vụ, tiêu chuẩn, gợi ý thị trường

## 🛠️ Công nghệ sử dụng

### Backend
- **Python 3**: Ngôn ngữ lập trình
- **Flask**: Framework web
- **Flask-WTF**: Bảo vệ CSRF và form handling
- **bcrypt**: Mã hóa mật khẩu an toàn
- **QRCode**: Thư viện tạo mã QR
- **Pillow**: Xử lý hình ảnh
- **Werkzeug**: Utilities cho Flask

### Frontend
- **HTML5/CSS3**: Giao diện người dùng
- **Responsive Design**: Tương thích mobile

### Storage
- **JSON Files**: Lưu trữ dữ liệu (phù hợp cho prototype/học tập)

## 📝 Lưu ý

### Lưu trữ dữ liệu
- Dữ liệu sản phẩm: `data/data.json` (tự động tạo khi chạy lần đầu)
- Dữ liệu người dùng: `data/users.json` (tự động tạo với admin mặc định)
- Mã QR: `static/qrcodes/` (tự động tạo)
- File upload: `static/uploads/` (tự động tạo)

### Bảo mật
- Mật khẩu được mã hóa bằng bcrypt (an toàn)
- CSRF protection cho tất cả form
- File upload được validate (kích thước tối đa 100MB, định dạng cho phép)
- Secret key nên đặt trong biến môi trường `SECRET_KEY` cho production

### Cấu hình
- ID sản phẩm được tạo tự động bằng timestamp
- Website chạy ở chế độ debug khi `FLASK_ENV != 'production'`
- Port mặc định: 5000 (có thể thay đổi qua biến môi trường `PORT`)

### Tài khoản mặc định
- Username: `admin`
- Password: `admin123`
- ⚠️ **Lưu ý**: Nên đổi mật khẩu ngay sau lần đăng nhập đầu tiên!

## 👨‍💻 Phù hợp cho

- Học sinh/sinh viên học lập trình web
- Người mới bắt đầu với Flask
- Dự án prototype cần giải pháp đơn giản
- Nông dân nhỏ lẻ muốn số hóa sản phẩm

## 🚀 Deploy

### Heroku
```bash
git push heroku main
```

### Render.com
- Tự động deploy từ GitHub
- Cấu hình trong `render.yaml`

## 🔒 Bảo mật

Dự án đã được cải thiện với:
- ✅ Mã hóa mật khẩu bằng bcrypt
- ✅ CSRF protection
- ✅ File upload validation
- ✅ Error handling cải thiện

Xem chi tiết trong `ANALYSIS_REPORT.md`

## 📈 Tính năng sắp tới

- [ ] Pagination cho danh sách sản phẩm
- [ ] API endpoints cho mobile app
- [ ] Dashboard & Statistics
- [ ] Export/Import dữ liệu
- [ ] Chuyển sang database (SQLite/PostgreSQL)

## 🛠️ Setup Project

### Checklist Ngắn Gọn
👉 Xem file **[CHECKLIST_SETUP.md](CHECKLIST_SETUP.md)** - Thứ tự tạo folder và file một cách ngắn gọn, dễ theo dõi.

### Hướng Dẫn Chi Tiết
👉 Xem file **[HUONG_DAN_SETUP.md](HUONG_DAN_SETUP.md)** với:
- ✅ Hướng dẫn cài đặt môi trường
- ✅ Cách clone từ GitHub
- ✅ Cách tự code lại từ đầu
- ✅ Giải thích từng file
- ✅ Troubleshooting các lỗi thường gặp

## 📚 Hướng Dẫn Học Tập

Nếu bạn muốn **học cách làm project này từ đầu**, xem file **[HOC_TAP_HUONG_DAN.md](HOC_TAP_HUONG_DAN.md)** với:
- ✅ Kiến thức cần biết trước
- ✅ Lộ trình học tập chi tiết
- ✅ Hướng dẫn từng bước
- ✅ Tips cho học sinh cấp 3

## 📄 License

Dự án mã nguồn mở, tự do sử dụng và chỉnh sửa.

