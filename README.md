# 🌾 Hệ thống Truy xuất Nguồn gốc Nông sản

Website quản lý và truy xuất nguồn gốc nông sản cho nông dân nhỏ lẻ, được xây dựng bằng Python Flask.

## 📋 Tính năng

- ✅ Trang chủ liệt kê tất cả sản phẩm
- ✅ Tạo sản phẩm mới với form nhập thông tin đầy đủ
- ✅ Tự động tạo mã QR cho mỗi sản phẩm
- ✅ Trang chi tiết sản phẩm khi quét QR code
- ✅ Lưu trữ dữ liệu bằng file JSON (đơn giản, dễ hiểu)

## 🚀 Cài đặt và Chạy

### Bước 1: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

Hoặc cài đặt thủ công:

```bash
pip install flask qrcode pillow
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
├── data.json             # File lưu trữ dữ liệu sản phẩm (tự động tạo)
├── requirements.txt      # Danh sách thư viện cần thiết
├── README.md            # File hướng dẫn
│
├── static/              # Thư mục chứa file tĩnh
│   ├── style.css        # File CSS
│   └── qrcodes/         # Thư mục chứa mã QR (tự động tạo)
│
└── templates/           # Thư mục chứa template HTML
    ├── index.html       # Trang chủ
    ├── create.html      # Trang tạo sản phẩm
    └── product.html     # Trang chi tiết sản phẩm
```

## 🎯 Hướng dẫn sử dụng

1. **Xem danh sách sản phẩm**: Truy cập trang chủ để xem tất cả sản phẩm đã được thêm vào hệ thống.

2. **Thêm sản phẩm mới**: 
   - Click nút "Thêm sản phẩm mới"
   - Điền đầy đủ thông tin (tên sản phẩm và hộ sản xuất là bắt buộc)
   - Click "Tạo mã QR và Lưu sản phẩm"
   - Hệ thống sẽ tự động tạo mã QR và chuyển đến trang chi tiết

3. **Xem chi tiết sản phẩm**:
   - Click "Xem chi tiết" trên card sản phẩm
   - Hoặc quét mã QR đã được tạo
   - Xem đầy đủ thông tin và mã QR của sản phẩm

## 🛠️ Công nghệ sử dụng

- **Python 3**: Ngôn ngữ lập trình
- **Flask**: Framework web
- **QRCode**: Thư viện tạo mã QR
- **Pillow**: Xử lý hình ảnh
- **HTML/CSS**: Giao diện người dùng

## 📝 Lưu ý

- Dữ liệu được lưu trong file `data.json` (tự động tạo khi chạy lần đầu)
- Mã QR được lưu trong thư mục `static/qrcodes/`
- ID sản phẩm được tạo tự động bằng timestamp
- Website chạy ở chế độ debug (phù hợp cho phát triển)

## 👨‍💻 Phù hợp cho

- Học sinh THPT học lập trình web
- Người mới bắt đầu với Flask
- Dự án nhỏ cần giải pháp đơn giản

## 📄 License

Dự án mã nguồn mở, tự do sử dụng và chỉnh sửa.

