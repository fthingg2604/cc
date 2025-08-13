# 🎯 WPlace Bot - Hướng Dẫn Hoàn Chỉnh

## ✅ Đã Hoàn Thành Tất Cả Yêu Cầu

### 🔧 Vấn đề đã sửa:
1. **✅ Tọa độ Px X, Px Y** - Đã có trong web interface (readonly hiển thị kích thước)
2. **✅ Chạy trên CMD** - Tất cả file .py đã có shebang và path setup
3. **✅ Deploy Hostinger** - Package `wplace_bot_hostinger.zip` đã sẵn sàng
4. **✅ Standalone Bot** - Đã sửa lỗi ImageProcessor và thêm Px X, Px Y input

---

## 🚀 3 Cách Sử Dụng Bot

### 1️⃣ Chạy Web Interface (Khuyên dùng)
```bash
# Download tất cả files về 1 thư mục
cd wplace-bot

# Cài đặt
python setup.py

# Chạy web server
python run_local.py

# Truy cập: http://localhost:5000
```

**Sử dụng:**
- Upload ảnh → Process → Bot Control
- Chọn tọa độ TL X, TL Y 
- Chọn chế độ bot (Single/Multi-thread/Multi-account)
- Start Bot

### 2️⃣ Chạy Standalone (CMD)
```bash
# Đặt file ảnh vào thư mục
# Chạy bot
python standalone_bot.py

# Bot sẽ hỏi:
# TL X (tọa độ bắt đầu X): 1624
# TL Y (tọa độ bắt đầu Y): 965  
# Px X (chiều rộng pixel): 128
# Px Y (chiều cao pixel): 128
# Số threads: 2
# Chạy ẩn browser: n
```

### 3️⃣ Deploy lên Hostinger
```bash
# Tạo package
python hostinger_deploy.py

# Upload wplace_bot_hostinger.zip lên Hostinger
# Giải nén trong public_html
# Chạy: python3 hostinger_setup.py
# Set SESSION_SECRET trong cPanel
```

---

## 🎮 Tính Năng Multiple Accounts

### Setup Accounts:
1. **Web Interface**: Bot Control → Đa tài khoản → Quản lý tài khoản
2. **Manual**: Tạo file `accounts.json`:
```json
{
  "accounts": [
    {
      "username": "acc1",
      "password": "pass1",
      "is_premium": false,
      "is_active": true
    },
    {
      "username": "acc2", 
      "password": "pass2",
      "is_premium": true,
      "is_active": true
    }
  ]
}
```

### Lợi ích:
- **2 accounts** = Vẽ nhanh gấp 2x
- **3 accounts** = Vẽ nhanh gấp 3x
- **4 accounts** = Vẽ nhanh gấp 4x

---

## 📁 Files Quan Trọng

### Chạy Bot:
- `run_local.py` - Web development server
- `run_production.py` - Production server  
- `standalone_bot.py` - Bot không cần web (đã sửa)
- `start_bot.py` - Demo bot nhanh

### Deploy:
- `setup.py` - Auto install dependencies
- `hostinger_deploy.py` - Tạo package Hostinger
- `wplace_bot_hostinger.zip` - Package sẵn sàng upload

### Demo:
- `multi_account_demo.py` - Demo đa tài khoản
- `test_standalone.py` - Test standalone bot

---

## 💡 Quick Commands

```bash
# Cài đặt nhanh
python setup.py

# Web interface
python run_local.py

# Standalone với input Px X, Px Y
python standalone_bot.py

# Demo multi-account 
python multi_account_demo.py

# Tạo package Hostinger
python hostinger_deploy.py

# Test standalone
python test_standalone.py
```

---

## 🔥 Tính Năng Nổi Bật

### ✅ Đã Có:
- Web interface với upload ảnh
- Xử lý màu theo palette wplace.live  
- Multi-threading (1-4 threads)
- **Multiple accounts (2-4x faster)**
- Deploy scripts cho Hostinger
- Standalone bot với Px X, Px Y input
- Auto rate limiting (30s cooldown)
- Error handling & logging

### 🎯 Coordinates System:
- **TL X, TL Y**: Top-Left starting position trên canvas
- **Px X, Px Y**: Pixel dimensions (chiều rộng x chiều cao) của ảnh

---

## ⚡ Performance Tips

1. **Fastest**: Multi-account mode (2-4 accounts)
2. **Balanced**: Multi-thread mode (2 threads)  
3. **Safe**: Single thread mode
4. **Headless**: Chạy ẩn browser cho server
5. **Local**: Tốt nhất cho development và test

---

**🎉 Bot hoàn toàn sẵn sàng sử dụng!**

Download package `wplace_bot_hostinger.zip` hoặc copy tất cả files để sử dụng ngay! 🚀