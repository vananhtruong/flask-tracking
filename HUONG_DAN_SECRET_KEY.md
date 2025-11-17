# 🔐 Hướng dẫn chi tiết: Tạo và thêm SECRET_KEY

## 📖 Environment Variable là gì?

**Environment Variable (Biến môi trường)** là các giá trị cấu hình được lưu trữ bên ngoài code, giúp:
- Bảo mật thông tin nhạy cảm (không commit vào Git)
- Dễ dàng thay đổi cấu hình mà không cần sửa code
- Mỗi môi trường (local, production) có thể có giá trị khác nhau

## 🔑 SECRET_KEY là gì và tại sao cần?

**SECRET_KEY** là một chuỗi bí mật dùng để:
- Mã hóa session cookies (đăng nhập, đăng xuất)
- Bảo vệ dữ liệu người dùng
- Ngăn chặn tấn công CSRF

⚠️ **QUAN TRỌNG:** Nếu không có SECRET_KEY hoặc dùng key yếu, website của bạn sẽ không an toàn!

## 📝 Cách tạo SECRET_KEY

### Cách 1: Dùng Python (Khuyến nghị)

Mở Terminal/Command Prompt và chạy:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Hoặc nếu dùng Python 3:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Kết quả sẽ là một chuỗi dài như:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**Lưu ý:** Mỗi lần chạy sẽ tạo một key khác nhau, chỉ cần copy một lần và dùng mãi mãi.

### Cách 2: Dùng online generator

Truy cập: https://randomkeygen.com/
- Chọn "CodeIgniter Encryption Keys"
- Copy một trong các key được tạo

### Cách 3: Tạo thủ công (không khuyến nghị)

Tạo một chuỗi ngẫu nhiên dài ít nhất 32 ký tự, ví dụ:
```
my-super-secret-key-2024-change-this-now-123456789
```

## 🚀 Cách thêm SECRET_KEY vào Render.com

### Bước 1: Vào trang quản lý Service

1. Đăng nhập vào https://render.com
2. Click vào service `flask-tracking` của bạn (hoặc service bạn vừa tạo)

### Bước 2: Vào phần Environment

1. Trong menu bên trái, tìm và click **"Environment"**
2. Hoặc scroll xuống phần **"Environment Variables"**

### Bước 3: Thêm biến mới

1. Click nút **"Add Environment Variable"** hoặc **"+ Add"**
2. Điền thông tin:
   - **Key:** `SECRET_KEY`
   - **Value:** (paste chuỗi SECRET_KEY bạn đã tạo)
   
   Ví dụ:
   ```
   Key: SECRET_KEY
   Value: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
   ```

3. Click **"Save Changes"** hoặc **"Add"**

### Bước 4: Redeploy (Quan trọng!)

Sau khi thêm Environment Variable:
1. Render sẽ tự động detect thay đổi
2. Hoặc bạn có thể click **"Manual Deploy"** → **"Deploy latest commit"**
3. Chờ deploy xong (2-5 phút)

## ✅ Cách kiểm tra SECRET_KEY đã hoạt động

1. Truy cập website của bạn
2. Thử đăng ký/đăng nhập
3. Nếu hoạt động bình thường = SECRET_KEY đã OK ✅
4. Nếu có lỗi session = kiểm tra lại SECRET_KEY

## 🔍 Xem code đã sử dụng SECRET_KEY chưa?

Mở file `app.py`, dòng 12:

```python
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production-2024')
```

**Giải thích:**
- `os.environ.get('SECRET_KEY', ...)` = Lấy SECRET_KEY từ Environment Variable
- Nếu không tìm thấy, sẽ dùng giá trị mặc định (chỉ dùng khi test local)

## 📸 Hình ảnh minh họa (Render.com)

```
┌─────────────────────────────────────┐
│  flask-tracking                    │
├─────────────────────────────────────┤
│  Overview  │  Logs  │  Environment │ ← Click vào đây
│            │        │              │
│  [Add Environment Variable]        │ ← Click nút này
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Key:   SECRET_KEY           │   │
│  │ Value: [paste your key]     │   │
│  │        [Save Changes]       │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

## ⚠️ Lưu ý quan trọng

1. **KHÔNG BAO GIỜ** commit SECRET_KEY vào Git
2. **KHÔNG BAO GIỜ** chia sẻ SECRET_KEY công khai
3. Mỗi môi trường (local, production) nên có SECRET_KEY khác nhau
4. Nếu bị lộ SECRET_KEY, hãy tạo key mới ngay lập tức

## 🆘 Troubleshooting

**Lỗi: "Session không hoạt động"**
- Kiểm tra SECRET_KEY đã được thêm chưa
- Kiểm tra đã redeploy chưa
- Kiểm tra key có đủ dài không (ít nhất 32 ký tự)

**Lỗi: "Invalid secret key"**
- Tạo lại SECRET_KEY mới
- Đảm bảo không có khoảng trắng thừa
- Copy/paste cẩn thận

## 📚 Tóm tắt nhanh

1. Tạo SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Vào Render.com → Service → Environment
3. Add: Key=`SECRET_KEY`, Value=`[paste key]`
4. Save và Redeploy
5. Xong! ✅

Chúc bạn thành công! 🎉

