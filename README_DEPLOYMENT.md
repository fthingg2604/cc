# 🎮 WPlace Bot - Hướng Dẫn Triển Khai & Sử Dụng

## 📋 Tổng Quan
WPlace Bot là công cụ tự động hóa để vẽ pixel art lên wplace.live. Bot hỗ trợ:
- ✅ Upload & xử lý hình ảnh 
- ✅ Chuyển đổi màu theo palette wplace.live
- ✅ Bot đơn tài khoản hoặc đa tài khoản
- ✅ Multi-threading để tăng tốc
- ✅ Web interface thân thiện

---

## 🚀 Cách 1: Chạy Trên Máy Local (Khuyên Dùng)

### Bước 1: Cài Đặt Dependencies
```bash
# Clone hoặc download project
cd wplace-bot

# Cài đặt tự động
python setup.py

# Hoặc cài thủ công
pip install Flask Flask-SQLAlchemy Pillow selenium numpy
```

### Bước 2: Chạy Bot
```bash
# Development mode (có reload tự động)
python run_local.py

# Production mode
python run_production.py

# Hoặc chạy trực tiếp
python main.py
```

### Bước 3: Sử dụng
1. Mở trình duyệt: `http://localhost:5000`
2. Upload hình ảnh (PNG, JPG, GIF, SVG)
3. Chọn palette màu (Free hoặc Premium)
4. Điều chỉnh tọa độ TL X, TL Y
5. Chọn chế độ bot và số luồng
6. Nhấn "Bắt đầu vẽ"

---

## 🌐 Cách 2: Deploy Lên Hostinger

### Bước 1: Tạo Package
```bash
python hostinger_deploy.py
```

### Bước 2: Upload & Setup
1. Upload file `wplace_bot_hostinger.zip` lên cPanel
2. Giải nén vào thư mục `public_html`
3. Chạy setup: `python3 hostinger_setup.py`
4. Set environment trong cPanel:
   - `SESSION_SECRET=your-secret-key-here`

### Bước 3: Cấu Hình Web Server
- Đảm bảo Python 3.8+ được enable
- CGI/WSGI support được bật
- File `.htaccess` đã có sẵn

---

## ⚡ Cách 3: Chạy Standalone (Không Web)

### Bot Đơn Giản
```bash
python standalone_bot.py
```

### Demo Nhanh
```bash
python start_bot.py
```

### Multi-Account Demo
```bash
python multi_account_demo.py
```

---

## 🔧 Tính Năng Đa Tài Khoản

### Setup Accounts
1. Tạo file `accounts.json`:
```json
{
  "accounts": [
    {
      "username": "account1",
      "password": "password1", 
      "is_premium": false,
      "is_active": true
    },
    {
      "username": "account2",
      "password": "password2",
      "is_premium": true,
      "is_active": true
    }
  ]
}
```

2. Hoặc dùng web interface:
   - Vào Bot Control
   - Chọn "Đa tài khoản"
   - Nhấn "Quản lý tài khoản"
   - Add/Remove accounts

### Lợi Ích Đa Tài Khoản
- **2 accounts**: Nhanh gấp 2x
- **3 accounts**: Nhanh gấp 3x  
- **4 accounts**: Nhanh gấp 4x
- Tự động phân chia pixel giữa các accounts
- Bypass rate limit 30 giây của wplace.live

---

## 📂 Cấu Trúc Files

### Core Files
- `main.py` - Entry point chính
- `app.py` - Flask application setup
- `routes.py` - Web routes & APIs
- `models.py` - Database models

### Bot Engine
- `wplace_bot.py` - Bot đơn tài khoản
- `multi_account_bot.py` - Bot đa tài khoản  
- `account_manager.py` - Quản lý accounts
- `image_processor.py` - Xử lý hình ảnh
- `color_palette.py` - Palette màu wplace.live

### Deployment
- `setup.py` - Auto install dependencies
- `run_local.py` - Development server
- `run_production.py` - Production server
- `hostinger_deploy.py` - Hostinger deployment

### Standalone Scripts
- `standalone_bot.py` - Bot không cần web
- `start_bot.py` - Demo bot nhanh
- `multi_account_demo.py` - Demo đa tài khoản

---

## 🔨 Requirements

### System Requirements
- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver
- 2GB+ RAM (cho multi-threading)

### Python Packages
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Pillow==10.1.0
selenium==4.15.2
numpy==1.26.2
```

---

## ⚙️ Cấu Hình Nâng Cao

### Environment Variables
```bash
export SESSION_SECRET="your-secret-key-here"
export DATABASE_URL="sqlite:///wplace_bot.db"  # Hoặc PostgreSQL
export UPLOAD_FOLDER="uploads"
export PROCESSED_FOLDER="processed"
```

### Bot Settings
```python
# Trong wplace_bot.py
WAIT_TIME = 30  # Seconds giữa mỗi pixel
HEADLESS = True  # Chạy ẩn browser
THREAD_COUNT = 2  # Số luồng (1-4)
```

### Image Processing
```python
# Trong image_processor.py  
MAX_WIDTH = 128  # Chiều rộng tối đa
MAX_HEIGHT = 128  # Chiều cao tối đa
USE_PREMIUM_COLORS = True  # Dùng màu premium
```

---

## 🐛 Troubleshooting

### Lỗi Thường Gặp

**1. ChromeDriver not found**
```bash
# Ubuntu/Debian
sudo apt install chromium-chromedriver

# Windows: Download từ https://chromedriver.chromium.org
```

**2. Permission denied**
```bash
chmod +x *.py
chmod 755 uploads/ processed/ scripts/
```

**3. Import errors**
```bash
# Đảm bảo trong thư mục project
cd wplace-bot
python setup.py
```

**4. Database errors**
```bash
# Reset database
rm wplace_bot.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Debug Mode
```bash
# Bật debug logs
export FLASK_DEBUG=1
python run_local.py
```

---

## 📞 Support & Issues

### Báo Lỗi
1. Kiểm tra logs trong terminal
2. Test với image đơn giản trước
3. Thử chế độ đơn luồng trước khi multi-thread
4. Đảm bảo accounts.json đúng format

### Performance Tips
- Dùng headless mode cho production
- Limit số luồng dựa trên RAM available
- Monitor CPU usage khi multi-account
- Test với ít pixels trước khi chạy full

---

## 📄 License & Credits

**WPlace Bot** được phát triển cho mục đích giáo dục và automation.

⚠️ **Lưu ý**: Tôn trọng Terms of Service của wplace.live và sử dụng có trách nhiệm.

---

## 🎯 Quick Start Commands

```bash
# Setup & chạy nhanh
git clone <repo>
cd wplace-bot
python setup.py
python run_local.py

# Truy cập: http://localhost:5000
# Upload ảnh -> Process -> Bot Control -> Start
```

**Happy Pixel Art Creating! 🎨**