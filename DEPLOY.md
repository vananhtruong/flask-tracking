# 🚀 Hướng dẫn Deploy lên Render.com (Miễn phí)

## Bước 1: Chuẩn bị code trên GitHub

1. **Tạo repository trên GitHub:**
   - Đăng nhập GitHub
   - Tạo repository mới (ví dụ: `flask-tracking`)
   - Không tích "Initialize with README" nếu đã có code

2. **Push code lên GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/flask-tracking.git
   git push -u origin main
   ```

## Bước 2: Deploy lên Render.com

1. **Đăng ký tài khoản Render:**
   - Truy cập: https://render.com
   - Đăng ký bằng GitHub (dễ nhất)

2. **Tạo Web Service:**
   - Click "New +" → "Web Service"
   - Connect repository của bạn
   - Chọn repository `flask-tracking`

3. **Cấu hình:**
   - **Name:** `flask-tracking` (hoặc tên bạn muốn)
   - **Region:** Singapore (gần Việt Nam nhất)
   - **Branch:** `main`
   - **Root Directory:** (để trống)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

4. **Environment Variables (Tùy chọn):**
   - `FLASK_ENV=production`
   - `PYTHON_VERSION=3.11.0`

5. **Click "Create Web Service"**

## Bước 3: Chờ Deploy

- Render sẽ tự động build và deploy
- Mất khoảng 5-10 phút lần đầu
- Bạn sẽ có URL dạng: `https://flask-tracking.onrender.com`

## Bước 4: Cập nhật Secret Key (Quan trọng!)

### Tại sao cần SECRET_KEY?
SECRET_KEY dùng để mã hóa session cookies (đăng nhập, đăng xuất). Không có nó, website sẽ không bảo mật!

### Cách tạo SECRET_KEY:

**Mở Terminal/Command Prompt và chạy:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Kết quả sẽ là một chuỗi dài như:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**Copy chuỗi này lại!**

### Cách thêm vào Render:

1. Vào trang quản lý service trên Render.com
2. Click vào tab **"Environment"** (ở menu bên trái)
3. Click nút **"Add Environment Variable"**
4. Điền:
   - **Key:** `SECRET_KEY` (viết hoa, có dấu gạch dưới)
   - **Value:** (paste chuỗi SECRET_KEY bạn vừa tạo)
5. Click **"Save Changes"**
6. **Quan trọng:** Click **"Manual Deploy"** → **"Deploy latest commit"** để áp dụng thay đổi

### Kiểm tra:
- Code đã được cập nhật sẵn trong `app.py` (dòng 12)
- Sau khi deploy, thử đăng nhập/đăng ký, nếu hoạt động = OK ✅

**📖 Xem hướng dẫn chi tiết hơn trong file `HUONG_DAN_SECRET_KEY.md`**

## ⚠️ Lưu ý quan trọng:

1. **Free tier có giới hạn:**
   - Service sẽ "ngủ" sau 15 phút không có request
   - Lần đầu truy cập sau khi ngủ sẽ mất ~30 giây để khởi động
   - Có thể upgrade lên paid để không bị ngủ

2. **Dữ liệu:**
   - File JSON sẽ được lưu trên server
   - Nếu service bị xóa, dữ liệu sẽ mất
   - Nên backup định kỳ hoặc dùng database (PostgreSQL free trên Render)

3. **QR Codes:**
   - File QR sẽ được lưu trong `static/qrcodes/`
   - Sẽ mất nếu service bị rebuild

## 🔄 Cập nhật code:

Mỗi khi push code lên GitHub, Render sẽ tự động deploy lại!

```bash
git add .
git commit -m "Update code"
git push
```

## 📝 Các platform miễn phí khác:

1. **Railway.app** - https://railway.app
   - Free tier tốt, không bị ngủ
   - Dễ deploy

2. **PythonAnywhere** - https://www.pythonanywhere.com
   - Free tier cho Python apps
   - Có giới hạn request/ngày

3. **Fly.io** - https://fly.io
   - Free tier, cần thẻ tín dụng
   - Performance tốt

4. **Replit** - https://replit.com
   - Có thể deploy trực tiếp
   - Free tier có giới hạn

## 🎯 Khuyến nghị:

**Render.com** là lựa chọn tốt nhất vì:
- ✅ Hoàn toàn miễn phí
- ✅ Dễ deploy
- ✅ Tự động deploy từ GitHub
- ✅ SSL miễn phí
- ✅ Hỗ trợ Flask tốt

Chúc bạn deploy thành công! 🎉

