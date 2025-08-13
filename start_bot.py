#!/usr/bin/env python3
"""
WPlace Bot - Khởi động đơn giản nhất
Chỉ cần chạy file này để test bot ngay!
"""

import os
import sys
import time
from PIL import Image
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from color_palette import get_wplace_colors, find_closest_color, hex_to_rgb

class SimpleBot:
    """Bot đơn giản nhất để test ngay"""
    
    def __init__(self):
        self.driver = None
        print("🤖 WPlace Bot đơn giản - Sẵn sàng test!")
        
    def setup_browser(self, headless=True):
        """Mở browser"""
        print("🌐 Đang mở Chrome...")
        
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://wplace.live")
            time.sleep(3)
            print("✅ Đã kết nối wplace.live!")
            return True
        except Exception as e:
            print(f"❌ Lỗi mở browser: {e}")
            return False
    
    def process_image(self, image_path):
        """Xử lý hình ảnh thành pixels"""
        print(f"🎨 Đang xử lý {image_path}...")
        
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize nhỏ để test nhanh
                img.thumbnail((32, 32), Image.Resampling.LANCZOS)
                img_array = np.array(img)
                
                colors = get_wplace_colors()
                pixels = []
                
                height, width = img_array.shape[:2]
                for y in range(height):
                    for x in range(width):
                        rgb = img_array[y, x]
                        
                        # Skip white/transparent
                        if np.array_equal(rgb[:3], [255, 255, 255]):
                            continue
                            
                        closest_color = find_closest_color(rgb[:3], colors)
                        pixels.append({
                            'x': x, 'y': y, 
                            'color': closest_color,
                            'rgb': hex_to_rgb(closest_color)
                        })
                
                print(f"✅ Xử lý xong: {len(pixels)} pixels")
                return pixels
                
        except Exception as e:
            print(f"❌ Lỗi xử lý hình: {e}")
            return []
    
    def place_pixel_test(self, x, y, color):
        """Test đặt pixel (chỉ mô phỏng)"""
        rgb = hex_to_rgb(color)
        print(f"🎯 Đặt pixel tại ({x}, {y}) màu {color} {rgb}")
        
        # Simulate waiting (real bot would wait 30s)
        time.sleep(1)  # Test mode: chỉ đợi 1 giây
        return True
    
    def run_test(self, image_path, start_x=1624, start_y=965):
        """Chạy test bot"""
        pixels = self.process_image(image_path)
        if not pixels:
            return False
            
        print(f"\n🚀 Bắt đầu test với {len(pixels)} pixels")
        print(f"📍 Vị trí: ({start_x}, {start_y})")
        print("⏰ Test mode: mỗi pixel 1 giây (thực tế sẽ là 30 giây)")
        
        success_count = 0
        for i, pixel in enumerate(pixels[:10]):  # Test 10 pixels đầu
            actual_x = start_x + pixel['x']
            actual_y = start_y + pixel['y']
            
            if self.place_pixel_test(actual_x, actual_y, pixel['color']):
                success_count += 1
            
            print(f"Tiến độ: {i+1}/10 pixels")
            
        print(f"\n✅ Test hoàn thành: {success_count}/10 pixels")
        return True
    
    def close(self):
        if self.driver:
            self.driver.quit()

def main():
    print("=" * 50)
    print("🎮 WPLACE BOT - TEST NHANH")
    print("=" * 50)
    
    # Kiểm tra file demo
    demo_files = ['demo1.png', 'demo2.png', 'demo3.png', 'test_image.png']
    available_files = [f for f in demo_files if os.path.exists(f)]
    
    if not available_files:
        print("❌ Không có file demo! Chạy: python demo.py")
        return
    
    print(f"📁 File có sẵn: {', '.join(available_files)}")
    
    # Chọn file
    image_file = available_files[0]  # Dùng file đầu tiên
    print(f"🎨 Sử dụng: {image_file}")
    
    # Input
    try:
        start_x = int(input("Tọa độ X (enter=1624): ") or "1624")
        start_y = int(input("Tọa độ Y (enter=965): ") or "965") 
        test_mode = input("Chế độ test nhanh? (y/n, enter=y): ").lower() != 'n'
    except KeyboardInterrupt:
        print("\nThoát!")
        return
    
    # Chạy bot
    bot = SimpleBot()
    
    try:
        if test_mode:
            print("\n🧪 TEST MODE: Mô phỏng đặt pixel (không vào wplace.live)")
            bot.run_test(image_file, start_x, start_y)
        else:
            print("\n🚀 LIVE MODE: Kết nối wplace.live thật")
            if bot.setup_browser(headless=False):
                input("Nhấn Enter khi đã sẵn sàng đặt pixel...")
                bot.run_test(image_file, start_x, start_y)
                
    except KeyboardInterrupt:
        print("\n⏹ Dừng bot!")
    finally:
        bot.close()
    
    print("\n" + "=" * 50)
    print("🎯 Test hoàn tất!")
    print("Để chạy bot thật với web UI: python main.py")
    print("=" * 50)

if __name__ == "__main__":
    main()