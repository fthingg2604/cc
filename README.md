# WPlace Bot - Pixel Art Automation cho wplace.live

Bot tự động vẽ pixel art trên wplace.live từ hình ảnh upload với hỗ trợ đa luồng.

## 🚀 Cách Sử Dụng Nhanh

### 1. Test nhanh hệ thống
```bash
python quick_test.py
```

### 2. Chạy bot standalone (không cần web)
```bash
# Đặt file ảnh (.png, .jpg) vào thư mục này
python standalone_bot.py
```

### 3. Chạy web interface đầy đủ
```bash
python main.py
# Mở http://localhost:5000
```

## 📋 Yêu Cầu Hệ Thống

- Python 3.8+
- Chrome browser
- ChromeDriver (tự động tải về)
- Các package: selenium, pillow, flask, numpy

## 🎯 Tính Năng

### Bot Automation
- ✅ Đa luồng (1-4 threads) cho tốc độ cao
- ✅ Tự động convert hình ảnh sang 64-color palette của wplace.live
- ✅ Rate limiting (30s/pixel) tuân thủ quy định wplace.live
- ✅ Error handling và auto retry
- ✅ Progress tracking real-time

### Web Interface
- ✅ Upload drag & drop
- ✅ Preview trước khi vẽ
- ✅ Coordinate picker (TL X, TL Y format)
- ✅ Thread count selector
- ✅ Bot control panel
- ✅ Download script standalone

### Xử Lý Hình Ảnh
- ✅ Auto resize (max 128x128)
- ✅ Color quantization to wplace.live palette
- ✅ Transparency handling
- ✅ Aspect ratio preservation

## 🎮 Hướng Dẫn Sử Dụng

### Cách 1: Standalone Bot (Đơn giản nhất)

1. Đặt file ảnh (.png, .jpg) vào thư mục dự án
2. Chạy: `python standalone_bot.py`
3. Nhập tọa độ bắt đầu (ví dụ: 1624, 965)
4. Chọn số threads (2 threads khuyên dùng)
5. Bot sẽ tự động xử lý và bắt đầu vẽ

### Cách 2: Web Interface (Đầy đủ tính năng)

1. Chạy: `python main.py`
2. Mở trình duyệt: http://localhost:5000
3. Upload hình ảnh bằng drag & drop
4. Chọn palette (Free/Premium colors)
5. Xem preview và adjust settings
6. Vào Bot Control để config và start

### Cấu Hình Tọa Độ

Format hiển thị giống wplace.live:
- **TL X, TL Y**: Top-Left corner (góc trên trái)
- **Px X, Px Y**: Pixel dimensions (kích thước)

Ví dụ: `TL X: 1624, TL Y: 965, Px X: 64, Px Y: 64`

### Chọn Số Threads

- **1 thread**: An toàn nhất, chậm nhất
- **2 threads**: Khuyên dùng - cân bằng tốc độ/an toàn
- **3-4 threads**: Nhanh nhất nhưng rủi ro cao hơn

Thời gian ước tính:
- 100 pixels × 30s = 50 phút (1 thread)
- 100 pixels × 30s ÷ 2 = 25 phút (2 threads)

## 🛠️ Troubleshooting

### Lỗi ChromeDriver
```bash
# Cài đặt ChromeDriver tự động
pip install webdriver-manager
```

### Lỗi Import
```bash
# Cài đặt dependencies
pip install selenium pillow flask numpy sqlalchemy
```

### Bot không đặt được pixel
- Kiểm tra kết nối internet
- Đảm bảo wplace.live đang hoạt động
- Thử giảm số threads xuống 1
- Kiểm tra tọa độ có đúng không

### Hình ảnh không được xử lý
- Đảm bảo file là .png, .jpg, .jpeg, .gif
- File size < 16MB
- Thử resize hình ảnh nhỏ hơn

## 📁 Cấu Trúc Files

```
├── main.py              # Web application entry point
├── standalone_bot.py    # Bot độc lập, chạy ngay
├── quick_test.py        # Test components
├── app.py              # Flask app setup
├── routes.py           # Web routes
├── wplace_bot.py       # Bot core logic
├── image_processor.py  # Image processing
├── color_palette.py    # wplace.live colors
├── models.py           # Database models
├── templates/          # Web templates
├── static/            # CSS, JS files
├── uploads/           # Uploaded images
├── processed/         # Processed images
└── scripts/           # Generated scripts
```

## 🎨 Color Palette

Bot sử dụng chính xác 64 màu của wplace.live:
- 32 màu free (miễn phí)
- 32 màu premium (trả phí)

Có thể chọn chỉ dùng free colors hoặc full palette.

## ⚠️ Lưu Ý Quan Trọng

1. **Rate Limiting**: Bot tự động đợi 30 giây giữa mỗi pixel theo quy định wplace.live
2. **Đa luồng**: Nhiều threads = nhanh hơn nhưng tăng risk bị ban
3. **Tọa độ**: Kiểm tra kỹ trước khi start, sai tọa độ = vẽ sai chỗ
4. **Kích thước**: Hình lớn sẽ mất nhiều giờ để hoàn thành

## 🚀 Performance Tips

- Dùng 2 threads cho tốc độ tối ưu
- Resize hình về 64x64 hoặc nhỏ hơn
- Chạy headless mode để tiết kiệm tài nguyên
- Test với hình nhỏ trước khi vẽ hình lớn

## 📞 Support

Nếu gặp vấn đề:
1. Chạy `python quick_test.py` để check system
2. Kiểm tra console logs để thấy lỗi cụ thể
3. Thử standalone bot trước khi dùng web interface