#!/usr/bin/env python3
"""
Multi-threaded WPlace Bot Script
Generated for placing pixels on wplace.live
Total threads: 3
"""

import time
import json
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
PIXEL_FILE = "processed/d6010981-f730-4cff-8f15-a6e598ce015f_converted_b31af7ceeb46a96faaaab9f30b7a0aa7_pixels_4px.json"
START_X = 1624
START_Y = 965
THREAD_COUNT = 3
WAIT_TIME = 30  # seconds between pixel placements

class WorkerBot:
    def __init__(self, thread_id, headless=True):
        self.thread_id = thread_id
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://wplace.live")
        time.sleep(2)
        
    def place_pixel(self, x, y, color):
        try:
            # Click on canvas at coordinates
            canvas = self.driver.find_element(By.ID, "canvas")
            self.driver.execute_script(f"arguments[0].click();", canvas)
            time.sleep(0.5)
            
            # Select color (simplified)
            color_element = self.driver.find_element(By.CSS_SELECTOR, f'[data-color="{color}"]')
            color_element.click()
            time.sleep(0.5)
            
            print(f"Thread {self.thread_id}: Placed pixel at ({x}, {y}) with color {color}")
            return True
            
        except Exception as e:
            print(f"Thread {self.thread_id}: Error placing pixel: {e}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.quit()

def worker_thread(thread_id, pixel_queue, results_queue):
    bot = WorkerBot(thread_id)
    
    try:
        bot.setup_driver()
        print(f"Thread {thread_id}: Ready")
        
        while True:
            try:
                pixel = pixel_queue.get(timeout=5)
                if pixel is None:  # Stop signal
                    break
                
                x = START_X + pixel['x']
                y = START_Y + pixel['y']
                color = pixel['color']
                
                success = bot.place_pixel(x, y, color)
                results_queue.put({'thread_id': thread_id, 'success': success})
                
                time.sleep(WAIT_TIME)
                
            except queue.Empty:
                continue
                
    finally:
        bot.close()
        print(f"Thread {thread_id}: Finished")

def main():
    # Load pixel data
    with open(PIXEL_FILE, 'r') as f:
        data = json.load(f)
    
    pixels = data['pixels']
    print(f"Starting multi-threaded bot: {len(pixels)} pixels across {THREAD_COUNT} threads")
    
    # Create queues
    pixel_queue = queue.Queue()
    results_queue = queue.Queue()
    
    # Add pixels to queue
    for pixel in pixels:
        pixel_queue.put(pixel)
    
    # Start worker threads
    threads = []
    for i in range(THREAD_COUNT):
        thread = threading.Thread(target=worker_thread, args=(i, pixel_queue, results_queue))
        thread.start()
        threads.append(thread)
    
    # Monitor progress
    total_pixels = len(pixels)
    processed = 0
    success_count = 0
    
    try:
        while processed < total_pixels:
            result = results_queue.get(timeout=30)
            processed += 1
            if result['success']:
                success_count += 1
            
            print(f"Progress: {processed}/{total_pixels} ({success_count} successful)")
    
    except KeyboardInterrupt:
        print("\nStopping...")
    
    # Stop threads
    for _ in range(THREAD_COUNT):
        pixel_queue.put(None)
    
    # Wait for threads to finish
    for thread in threads:
        thread.join()
    
    print(f"Completed: {success_count}/{total_pixels} pixels placed successfully")

if __name__ == "__main__":
    main()
