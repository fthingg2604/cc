#!/usr/bin/env python3
"""
Quick Test Script - Kiểm tra nhanh các thành phần của bot
"""

import sys
import os
from PIL import Image
import numpy as np

def test_image_processing():
    """Test xử lý hình ảnh"""
    print("=== Test Image Processing ===")
    
    try:
        from image_processor import ImageProcessor
        from color_palette import get_wplace_colors, find_closest_color
        
        processor = ImageProcessor()
        colors = get_wplace_colors()
        
        print(f"✓ Import thành công")
        print(f"✓ Có {len(colors)} màu trong palette")
        
        # Test với một pixel màu đỏ
        red_pixel = [255, 0, 0]
        closest = find_closest_color(red_pixel, colors)
        print(f"✓ Màu đỏ [255,0,0] -> wplace color: {closest}")
        
        return True
        
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def test_selenium():
    """Test Selenium setup"""
    print("\n=== Test Selenium ===")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("✓ Import Selenium thành công")
        
        # Test driver setup (không thực sự mở browser)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print("✓ Chrome options configured")
        
        # Thử tạo driver (có thể fail nếu không có ChromeDriver)
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://google.com")
            print("✓ ChromeDriver hoạt động tốt")
            driver.quit()
        except Exception as e:
            print(f"⚠ ChromeDriver có vấn đề: {e}")
            print("  Cần cài đặt ChromeDriver để bot hoạt động")
            
        return True
        
    except Exception as e:
        print(f"✗ Lỗi Selenium: {e}")
        return False

def test_web_app():
    """Test web application"""
    print("\n=== Test Web Application ===")
    
    try:
        from app import app, db
        from models import ImageUpload, BotSession
        
        print("✓ Import Flask app thành công")
        
        with app.app_context():
            # Test database
            try:
                db.create_all()
                print("✓ Database sẵn sàng")
            except Exception as e:
                print(f"⚠ Database issue: {e}")
                
        return True
        
    except Exception as e:
        print(f"✗ Lỗi Web App: {e}")
        return False

def test_example_image():
    """Tạo một hình ảnh test nhỏ"""
    print("\n=== Tạo Hình Ảnh Test ===")
    
    try:
        # Tạo hình ảnh 10x10 đơn giản
        img = Image.new('RGB', (10, 10), color='white')
        
        # Vẽ một vài pixel màu
        pixels = img.load()
        pixels[1, 1] = (255, 0, 0)  # Đỏ
        pixels[2, 2] = (0, 255, 0)  # Xanh lá
        pixels[3, 3] = (0, 0, 255)  # Xanh dương
        pixels[4, 4] = (255, 255, 0)  # Vàng
        
        img.save('test_image.png')
        print("✓ Đã tạo test_image.png (10x10 pixels)")
        print("  Bạn có thể dùng file này để test bot")
        
        return True
        
    except Exception as e:
        print(f"✗ Lỗi tạo hình: {e}")
        return False

def main():
    """Chạy tất cả tests"""
    print("WPlace Bot - Quick Test Suite")
    print("=" * 40)
    
    tests = [
        test_image_processing,
        test_selenium,
        test_web_app,
        test_example_image
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 40)
    print("KẾT QUẢ TỔNG KẾT:")
    
    if all(results):
        print("✓ Tất cả components đều sẵn sàng!")
        print("✓ Bạn có thể chạy bot bằng:")
        print("  python standalone_bot.py")
        print("  hoặc")
        print("  python main.py (để chạy web interface)")
    else:
        print("⚠ Một số components có vấn đề")
        print("  Kiểm tra lại các lỗi ở trên")
        
    print("\nGợi ý:")
    print("- Để test nhanh: python standalone_bot.py")
    print("- Để dùng web UI: python main.py rồi mở http://localhost:5000")

if __name__ == "__main__":
    main()