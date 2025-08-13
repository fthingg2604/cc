# ⚡ WPlace Bot - Quick Start Guide

## 🚀 Chạy Nhanh 5 Phút

### Bước 1: Download & Setup
```bash
# Download tất cả files về 1 thư mục
mkdir wplace-bot
cd wplace-bot

# Copy tất cả files .py vào thư mục này
# Chạy setup
python setup.py
```

### Bước 2: Chạy Bot
```bash
# Chạy web server
python run_local.py

# Hoặc chạy demo nhanh
python start_bot.py
```

### Bước 3: Sử dụng
1. Mở: http://localhost:5000
2. Upload ảnh (PNG/JPG)
3. Nhấn "Xử lý ảnh"
4. Đi tới "Bot Control"
5. Nhấn "Bắt đầu vẽ"

---

## 🎯 Sử Dụng Standalone (Không Web)

```bash
# Chạy bot trực tiếp với ảnh có sẵn
python standalone_bot.py demo1.png 1000 1000

# Demo multi-account
python multi_account_demo.py
```

---

## 📱 Deploy Lên Hostinger

```bash
# Tạo package upload
python hostinger_deploy.py

# Upload file .zip lên Hostinger
# Giải nén và chạy: python3 hostinger_setup.py
```

---

## ⚡ Commands Hữu Ích

```bash
# Development
python run_local.py           # Web với auto-reload
python run_production.py      # Production mode

# Testing  
python start_bot.py          # Demo bot nhanh
python multi_account_demo.py # Test multi-account

# Deployment
python hostinger_deploy.py   # Tạo package deploy
python setup.py              # Install dependencies

# Standalone
python standalone_bot.py     # Bot không cần web
```

Đó là tất cả! Bot sẵn sàng vẽ pixel art trên wplace.live 🎨