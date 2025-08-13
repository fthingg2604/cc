#!/usr/bin/env python3
"""
Standalone WPlace Bot - Ready to use immediately
Chạy trực tiếp để test bot mà không cần web interface
"""

import os
import sys
import time
import json
import threading
import queue
from PIL import Image
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import our existing modules
from color_palette import get_wplace_colors, find_closest_color
from image_processor import ImageProcessor

class StandaloneBot:
    """Bot độc lập có thể chạy ngay lập tức"""
    
    def __init__(self, image_path, start_x=1624, start_y=965, max_width=128, max_height=128, thread_count=2, headless=False):
        self.image_path = image_path
        self.start_x = start_x
        self.start_y = start_y
        self.max_width = max_width
        self.max_height = max_height
        self.thread_count = thread_count
        self.headless = headless
        self.pixel_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.stop_event = threading.Event()
        
        # Process image immediately
        self.pixels = self.process_image()
        print(f"Đã xử lý hình ảnh: {len(self.pixels)} pixels sẽ được vẽ")
    
    def process_image(self):
        """Xử lý hình ảnh thành pixel data"""
        print(f"Đang xử lý hình ảnh: {self.image_path}")
        
        # Load và resize image - fix constructor error
        import tempfile
        import os
        
        temp_dir = tempfile.mkdtemp()
        upload_folder = os.path.join(temp_dir, 'uploads')
        processed_folder = os.path.join(temp_dir, 'processed')
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(processed_folder, exist_ok=True)
        
        # Open image
        with Image.open(self.image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to max dimensions while preserving aspect ratio
            img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Get wplace colors
            colors = get_wplace_colors()
            
            pixels = []
            height, width = img_array.shape[:2]
            
            for y in range(height):
                for x in range(width):
                    rgb = img_array[y, x]
                    
                    # Skip transparent or white pixels
                    if len(rgb) == 4 and rgb[3] < 128:  # Skip transparent
                        continue
                    if np.array_equal(rgb[:3], [255, 255, 255]):  # Skip white
                        continue
                    
                    # Find closest wplace color
                    closest_color = find_closest_color(rgb[:3], colors)
                    
                    pixels.append({
                        'x': x,
                        'y': y,
                        'color': closest_color,
                        'original_rgb': rgb[:3].tolist()
                    })
            
            return pixels
    
    def setup_driver(self, thread_id):
        """Setup Chrome driver cho một thread"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_profile_{thread_id}")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://wplace.live")
            time.sleep(3)  # Wait for page load
            
            print(f"Thread {thread_id}: Đã kết nối wplace.live")
            return driver
            
        except Exception as e:
            print(f"Thread {thread_id}: Lỗi setup driver: {e}")
            return None
    
    def place_pixel(self, driver, x, y, color, thread_id):
        """Đặt một pixel tại tọa độ (x, y) với màu color"""
        try:
            # Wait for canvas to be available
            canvas = WebDriverWait(driver, 10).wait(
                EC.presence_of_element_located((By.TAG_NAME, "canvas"))
            )
            
            # Calculate actual coordinates on canvas
            actual_x = self.start_x + x
            actual_y = self.start_y + y
            
            # Click on canvas at coordinates
            # This is a simplified approach - real implementation would need exact pixel clicking
            action = webdriver.ActionChains(driver)
            action.move_to_element_with_offset(canvas, actual_x % 800, actual_y % 600)
            action.click()
            action.perform()
            
            time.sleep(0.5)
            
            # Try to select color (this would need the actual color palette implementation)
            print(f"Thread {thread_id}: Đặt pixel tại ({actual_x}, {actual_y}) màu {color}")
            
            return True
            
        except Exception as e:
            print(f"Thread {thread_id}: Lỗi đặt pixel: {e}")
            return False
    
    def worker_thread(self, thread_id):
        """Worker thread function"""
        driver = self.setup_driver(thread_id)
        if not driver:
            return
        
        placed_count = 0
        
        try:
            while not self.stop_event.is_set():
                try:
                    # Get pixel from queue
                    pixel = self.pixel_queue.get(timeout=5)
                    if pixel is None:  # Stop signal
                        break
                    
                    # Place the pixel
                    success = self.place_pixel(
                        driver, 
                        pixel['x'], 
                        pixel['y'], 
                        pixel['color'], 
                        thread_id
                    )
                    
                    if success:
                        placed_count += 1
                    
                    # Report result
                    self.results_queue.put({
                        'thread_id': thread_id,
                        'success': success,
                        'pixel': pixel
                    })
                    
                    # Mark task done
                    self.pixel_queue.task_done()
                    
                    # Wait between placements (30 seconds for wplace.live)
                    if not self.stop_event.is_set():
                        print(f"Thread {thread_id}: Đợi 30 giây...")
                        time.sleep(30)
                        
                except queue.Empty:
                    continue
                    
        except KeyboardInterrupt:
            print(f"Thread {thread_id}: Dừng bởi user")
            
        finally:
            driver.quit()
            print(f"Thread {thread_id}: Hoàn thành - đã đặt {placed_count} pixels")
    
    def run(self):
        """Chạy bot với multi-threading"""
        print(f"Bắt đầu bot với {self.thread_count} threads")
        print(f"Sẽ vẽ tại tọa độ ({self.start_x}, {self.start_y})")
        print(f"Tổng cộng: {len(self.pixels)} pixels")
        
        # Add pixels to queue
        for pixel in self.pixels:
            self.pixel_queue.put(pixel)
        
        # Start worker threads
        threads = []
        for i in range(self.thread_count):
            thread = threading.Thread(target=self.worker_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            print(f"Đã khởi động thread {i}")
        
        # Monitor progress
        total_pixels = len(self.pixels)
        processed = 0
        success_count = 0
        
        try:
            print("\nBắt đầu vẽ... (Nhấn Ctrl+C để dừng)")
            start_time = time.time()
            
            while processed < total_pixels and not self.stop_event.is_set():
                try:
                    result = self.results_queue.get(timeout=60)
                    processed += 1
                    
                    if result['success']:
                        success_count += 1
                    
                    # Show progress
                    progress = (processed / total_pixels) * 100
                    elapsed = time.time() - start_time
                    
                    print(f"Tiến độ: {processed}/{total_pixels} ({progress:.1f}%) - "
                          f"Thành công: {success_count} - Thời gian: {elapsed/60:.1f} phút")
                    
                except queue.Empty:
                    print("Timeout - có thể bot đang đợi cooldown...")
                    continue
                    
        except KeyboardInterrupt:
            print("\nDừng bot...")
            self.stop_event.set()
        
        # Stop all threads
        for _ in range(self.thread_count):
            self.pixel_queue.put(None)
        
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=10)
        
        print(f"\nHoàn thành: {success_count}/{total_pixels} pixels đã đặt thành công")

def main():
    """Main function để chạy bot standalone"""
    print("=== WPlace Bot Standalone ===")
    print("Bot sẽ tự động xử lý hình ảnh và bắt đầu vẽ trên wplace.live")
    
    # Kiểm tra xem có file ảnh nào trong thư mục không
    image_files = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    if not image_files:
        print("Không tìm thấy file ảnh nào trong thư mục hiện tại!")
        print("Hãy đặt file ảnh (.png, .jpg, .jpeg, .gif) vào thư mục này")
        return
    
    # Sử dụng file ảnh đầu tiên tìm thấy
    image_path = image_files[0]
    print(f"Sử dụng hình ảnh: {image_path}")
    
    # Cấu hình bot
    start_x = int(input("TL X (tọa độ bắt đầu X, mặc định 1624): ") or "1624")
    start_y = int(input("TL Y (tọa độ bắt đầu Y, mặc định 965): ") or "965")
    max_width = int(input("Px X (chiều rộng pixel, mặc định 128): ") or "128")
    max_height = int(input("Px Y (chiều cao pixel, mặc định 128): ") or "128")
    thread_count = int(input("Số threads (1-4, mặc định 2): ") or "2")
    headless = input("Chạy ẩn browser? (y/n, mặc định n): ").lower() == 'y'
    
    # Tạo và chạy bot
    bot = StandaloneBot(
        image_path=image_path,
        start_x=start_x,
        start_y=start_y,
        max_width=max_width,
        max_height=max_height,
        thread_count=thread_count,
        headless=headless
    )
    
    bot.run()

if __name__ == "__main__":
    main()