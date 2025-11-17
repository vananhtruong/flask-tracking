# 📤 Hướng dẫn Push Code lên GitHub (Để Deploy)

## ❌ Lỗi hiện tại:
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

**Nguyên nhân:** Code chưa được push lên GitHub, nên Render không tìm thấy file!

## ✅ Giải pháp: Push code lên GitHub

### Bước 1: Tạo Repository trên GitHub

1. Truy cập: https://github.com
2. Đăng nhập vào tài khoản
3. Click nút **"+"** ở góc trên bên phải → **"New repository"**
4. Điền thông tin:
   - **Repository name:** `flask-tracking` (hoặc tên bạn muốn)
   - **Description:** (tùy chọn) "Hệ thống truy xuất nguồn gốc nông sản"
   - **Public** hoặc **Private** (tùy bạn)
   - **KHÔNG** tích "Initialize with README" (vì đã có code rồi)
5. Click **"Create repository"**

### Bước 2: Khởi tạo Git trong project

Mở **Terminal/Command Prompt** trong thư mục project và chạy:

```bash
# Khởi tạo git repository
git init

# Thêm tất cả file vào staging
git add .

# Commit lần đầu
git commit -m "Initial commit: Flask tracking system"

# Đổi tên branch thành main
git branch -M main

# Thêm remote repository (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/flask-tracking.git

# Push code lên GitHub
git push -u origin main
```

**Lưu ý:** 
- Thay `YOUR_USERNAME` bằng username GitHub thực tế của bạn
- Nếu GitHub yêu cầu đăng nhập, bạn sẽ cần nhập username và password (hoặc Personal Access Token)

### Bước 3: Kiểm tra trên GitHub

1. Vào repository vừa tạo trên GitHub
2. Kiểm tra xem các file đã có chưa:
   - ✅ `app.py`
   - ✅ `requirements.txt`
   - ✅ `templates/`
   - ✅ `static/`
   - ✅ Các file khác

### Bước 4: Cấu hình lại trên Render

1. Vào https://render.com
2. Vào service của bạn (hoặc tạo mới nếu chưa có)
3. Vào **Settings**
4. Kiểm tra:
   - **Repository:** Đảm bảo đã chọn đúng repo
   - **Branch:** `main`
   - **Root Directory:** (để trống)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

5. Click **"Save Changes"**

### Bước 5: Deploy lại

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Chờ build (5-10 phút)
3. Kiểm tra logs để xem có lỗi không

## 🔍 Kiểm tra file requirements.txt

Đảm bảo file `requirements.txt` có nội dung:

```
Flask>=3.0.0
qrcode[pil]>=7.4.2
Pillow>=10.0.0
gunicorn>=21.2.0
```

## 📋 Checklist trước khi push:

- [ ] File `requirements.txt` tồn tại
- [ ] File `app.py` tồn tại
- [ ] Thư mục `templates/` có đầy đủ file HTML
- [ ] Thư mục `static/` có file CSS
- [ ] File `.gitignore` không ignore `requirements.txt`

## 🚨 Nếu gặp lỗi khi push:

### Lỗi: "Authentication failed"

**Giải pháp:** Dùng Personal Access Token thay vì password

1. Vào GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Chọn quyền: `repo`
4. Copy token
5. Khi push, dùng token làm password

### Lỗi: "Repository not found"

**Giải pháp:** Kiểm tra lại URL repository và username

## ✅ Sau khi push thành công:

1. Render sẽ tự động detect code mới
2. Hoặc bạn có thể click "Manual Deploy"
3. Build sẽ thành công! 🎉

## 💡 Mẹo:

- Mỗi khi sửa code, nhớ commit và push:
  ```bash
  git add .
  git commit -m "Mô tả thay đổi"
  git push
  ```

- Render sẽ tự động deploy mỗi khi bạn push code mới!

Chúc bạn thành công! 🚀

