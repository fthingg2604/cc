#!/usr/bin/env python3
"""
Demo Script - Tạo hình ảnh mẫu và test bot ngay
"""

from PIL import Image, ImageDraw
import os

def create_demo_images():
    """Tạo các hình ảnh demo để test bot"""
    
    # Demo 1: Hình vuông nhỏ 8x8
    print("Tạo demo1.png - Hình vuông 8x8 màu cơ bản...")
    img1 = Image.new('RGB', (8, 8), 'white')
    pixels1 = img1.load()
    
    # Tạo pattern đơn giản
    colors = [
        (255, 0, 0),    # Đỏ
        (0, 255, 0),    # Xanh lá
        (0, 0, 255),    # Xanh dương
        (255, 255, 0),  # Vàng
    ]
    
    for y in range(8):
        for x in range(8):
            if x == 0 or x == 7 or y == 0 or y == 7:
                pixels1[x, y] = colors[0]  # Border đỏ
            elif x == y:
                pixels1[x, y] = colors[1]  # Đường chéo xanh lá
            elif x + y == 7:
                pixels1[x, y] = colors[2]  # Đường chéo khác xanh dương
            else:
                pixels1[x, y] = colors[3]  # Fill vàng
    
    img1.save('demo1.png')
    
    # Demo 2: Text "HI" 16x16
    print("Tạo demo2.png - Text 'HI' 16x16...")
    img2 = Image.new('RGB', (16, 16), 'white')
    draw = ImageDraw.Draw(img2)
    
    # Vẽ chữ H
    draw.rectangle([2, 2, 3, 14], fill=(255, 0, 0))  # Cột trái H
    draw.rectangle([5, 2, 6, 14], fill=(255, 0, 0))  # Cột phải H
    draw.rectangle([2, 7, 6, 8], fill=(255, 0, 0))   # Ngang H
    
    # Vẽ chữ I
    draw.rectangle([10, 2, 13, 3], fill=(0, 0, 255))  # Ngang trên I
    draw.rectangle([11, 2, 12, 14], fill=(0, 0, 255)) # Cột I
    draw.rectangle([10, 13, 13, 14], fill=(0, 0, 255)) # Ngang dưới I
    
    img2.save('demo2.png')
    
    # Demo 3: Rainbow 20x4
    print("Tạo demo3.png - Rainbow 20x4...")
    img3 = Image.new('RGB', (20, 4), 'white')
    pixels3 = img3.load()
    
    rainbow_colors = [
        (255, 0, 0),    # Đỏ
        (255, 165, 0),  # Cam
        (255, 255, 0),  # Vàng
        (0, 255, 0),    # Xanh lá
        (0, 0, 255),    # Xanh dương
        (75, 0, 130),   # Chàm
        (238, 130, 238) # Tím
    ]
    
    for x in range(20):
        color_index = (x * len(rainbow_colors)) // 20
        color = rainbow_colors[color_index]
        for y in range(4):
            pixels3[x, y] = color
    
    img3.save('demo3.png')
    
    print("\n✅ Đã tạo 3 file demo:")
    print("  - demo1.png: 8x8 pattern (64 pixels, ~32 phút)")
    print("  - demo2.png: 16x16 text HI (256 pixels, ~2 giờ)")
    print("  - demo3.png: 20x4 rainbow (80 pixels, ~40 phút)")

def show_usage():
    """Hiển thị hướng dẫn sử dụng"""
    print("\n" + "="*50)
    print("🚀 HƯỚNG DẪN SỬ DỤNG BOT")
    print("="*50)
    
    print("\n1. TEST NHANH (khuyên dùng):")
    print("   python standalone_bot.py")
    print("   → Chọn demo1.png khi được hỏi")
    print("   → Nhập tọa độ: 1624, 965")
    print("   → Chọn 1-2 threads")
    
    print("\n2. WEB INTERFACE:")
    print("   python main.py")
    print("   → Mở http://localhost:5000")
    print("   → Upload file demo")
    
    print("\n3. KIỂM TRA HỆ THỐNG:")
    print("   python quick_test.py")
    print("   → Check mọi thứ hoạt động tốt")
    
    print("\n⚠️  LƯU Ý:")
    print("   - Demo1 (8x8) chỉ mất ~32 phút để hoàn thành")
    print("   - Bot sẽ đợi 30 giây giữa mỗi pixel")
    print("   - Có thể dừng bằng Ctrl+C")
    print("   - Đảm bảo Chrome đã cài đặt")

def main():
    print("🎨 WPlace Bot Demo Creator")
    print("Tạo hình ảnh mẫu để test bot ngay lập tức!")
    
    create_demo_images()
    show_usage()
    
    print("\n" + "="*50)
    print("🎯 SẴN SÀNG TEST BOT!")
    print("Chạy: python standalone_bot.py")
    print("="*50)

if __name__ == "__main__":
    main()