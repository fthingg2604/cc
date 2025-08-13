#!/usr/bin/env python3
"""
Test script để kiểm tra standalone_bot.py hoạt động
"""

import os
import sys

def test_standalone():
    """Test standalone bot với demo image"""
    print("🧪 Testing Standalone Bot...")
    
    # Kiểm tra có demo files không
    demo_files = ['demo1.png', 'demo2.png', 'demo3.png', 'test_image.png']
    found_file = None
    
    for file in demo_files:
        if os.path.exists(file):
            found_file = file
            break
    
    if not found_file:
        print("❌ Không tìm thấy file demo nào!")
        print("💡 Tạo file test_image.png để test...")
        
        # Tạo file test đơn giản
        from PIL import Image
        import numpy as np
        
        # Tạo ảnh 10x10 pixels với vài màu
        img_array = np.zeros((10, 10, 3), dtype=np.uint8)
        img_array[0:5, 0:5] = [255, 0, 0]  # Red
        img_array[0:5, 5:10] = [0, 255, 0]  # Green  
        img_array[5:10, 0:5] = [0, 0, 255]  # Blue
        img_array[5:10, 5:10] = [255, 255, 0]  # Yellow
        
        img = Image.fromarray(img_array)
        img.save('test_image.png')
        found_file = 'test_image.png'
        print(f"✅ Tạo test file: {found_file}")
    
    print(f"📸 Test với file: {found_file}")
    
    # Import standalone bot
    try:
        from standalone_bot import StandaloneBot
        print("✅ Import StandaloneBot thành công")
        
        # Test tạo bot instance với parameters mới
        bot = StandaloneBot(
            image_path=found_file,
            start_x=1000,
            start_y=1000, 
            max_width=32,  # Nhỏ để test nhanh
            max_height=32,
            thread_count=1,
            headless=True
        )
        
        print(f"✅ Bot tạo thành công với {len(bot.pixels)} pixels")
        print("✅ Test hoàn thành - standalone_bot.py đã được sửa!")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test: {e}")
        return False

if __name__ == "__main__":
    test_standalone()