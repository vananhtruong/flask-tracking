# 🔧 Sửa lỗi: Could not open requirements file

## ❌ Lỗi bạn gặp:
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
==> Build failed 😞
```

## 🔍 Nguyên nhân:
1. File `requirements.txt` chưa được commit/push lên GitHub
2. Root Directory trên Render không đúng
3. File bị ignore trong `.gitignore`

## ✅ Cách sửa:

### Bước 1: Kiểm tra file requirements.txt có trong Git không

Mở Terminal/Command Prompt và chạy:

```bash
git status
```

Nếu thấy `requirements.txt` trong danh sách "Untracked files" hoặc "Changes not staged", cần commit:

```bash
git add requirements.txt
git commit -m "Add requirements.txt"
git push
```

### Bước 2: Kiểm tra file có bị ignore không

Mở file `.gitignore` và đảm bảo KHÔNG có dòng:
```
requirements.txt
```

Nếu có, xóa dòng đó đi.

### Bước 3: Kiểm tra trên GitHub

1. Vào repository trên GitHub
2. Kiểm tra xem file `requirements.txt` có xuất hiện không
3. Nếu không có → cần commit và push lại

### Bước 4: Kiểm tra cấu hình trên Render

1. Vào https://render.com
2. Click vào service của bạn
3. Vào tab **"Settings"**
4. Kiểm tra phần **"Root Directory"**:
   - Nếu để trống = Render sẽ tìm ở root của repo ✅
   - Nếu có giá trị = đảm bảo đường dẫn đúng

### Bước 5: Commit lại tất cả file cần thiết

Chạy các lệnh sau để đảm bảo tất cả file đã được commit:

```bash
# Kiểm tra trạng thái
git status

# Thêm tất cả file (nếu cần)
git add .

# Commit
git commit -m "Fix: Add all required files for deployment"

# Push lên GitHub
git push
```

### Bước 6: Redeploy trên Render

1. Vào Render.com → Service của bạn
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Chờ build lại

## 📋 Checklist các file cần có trên GitHub:

- ✅ `app.py`
- ✅ `requirements.txt`
- ✅ `runtime.txt` (tùy chọn)
- ✅ `render.yaml` (tùy chọn)
- ✅ `templates/` (tất cả file HTML)
- ✅ `static/` (CSS và các file tĩnh)
- ✅ `data/` (thư mục, file JSON sẽ tự tạo)

## 🚨 Nếu vẫn lỗi:

### Cách 1: Tạo lại file requirements.txt

Đảm bảo file có nội dung:
```
Flask>=3.0.0
qrcode[pil]>=7.4.2
Pillow>=10.0.0
gunicorn>=21.2.0
```

### Cách 2: Kiểm tra Build Command trên Render

1. Vào Settings → Build & Deploy
2. Build Command phải là:
   ```
   pip install -r requirements.txt
   ```
3. Nếu khác, sửa lại

### Cách 3: Xóa và tạo lại service

Nếu vẫn không được:
1. Xóa service cũ trên Render
2. Tạo lại service mới
3. Đảm bảo chọn đúng repository và branch

## 💡 Mẹo debug:

1. Xem **Logs** trên Render để biết chính xác lỗi ở đâu
2. Kiểm tra **Build Logs** xem Render đang tìm file ở đâu
3. Đảm bảo tất cả file đã được push lên GitHub

## ✅ Sau khi sửa xong:

Build sẽ thành công và bạn sẽ thấy:
```
==> Build succeeded! 🎉
```

Chúc bạn thành công! 🚀

