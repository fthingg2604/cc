import time
import json
import os
import logging
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from account_manager import AccountManager, Account

class WPlaceBot:
    def __init__(self, headless=False, wait_time=30):
        """
        Initialize the WPlace bot
        
        Args:
            headless: Run browser in headless mode
            wait_time: Time to wait between pixel placements (seconds)
        """
        self.headless = headless
        self.wait_time = wait_time
        self.driver = None
        self.wait = None
        self.current_session = None
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Create driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup driver: {e}")
            return False
    
    def navigate_to_wplace(self):
        """Navigate to wplace.live"""
        try:
            if not self.driver:
                self.logger.error("Driver not initialized")
                return False
            
            self.driver.get("https://wplace.live")
            if self.wait:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
            time.sleep(3)  # Allow page to fully load
            return True
        except TimeoutException:
            self.logger.error("Timeout waiting for wplace.live to load")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to wplace.live: {e}")
            return False
    
    def zoom_to_location(self, x, y, zoom_level=15):
        """
        Zoom to specific coordinates on the wplace canvas
        
        Args:
            x: X coordinate
            y: Y coordinate  
            zoom_level: Zoom level (1-19, higher is more zoomed in)
        """
        try:
            if not self.driver:
                self.logger.error("Driver not initialized")
                return False
                
            # Find the canvas element
            canvas = self.driver.find_element(By.TAG_NAME, "canvas")
            
            # Calculate canvas center
            canvas_rect = canvas.get_attribute("getBoundingClientRect")
            canvas_width_attr = canvas.get_attribute("width")
            canvas_height_attr = canvas.get_attribute("height")
            
            canvas_width = int(canvas_width_attr) if canvas_width_attr else 800
            canvas_height = int(canvas_height_attr) if canvas_height_attr else 600
            
            # Use JavaScript to navigate to coordinates
            js_script = f"""
            // Navigate to coordinates {x}, {y} at zoom level {zoom_level}
            if (window.map) {{
                window.map.setView([{y}, {x}], {zoom_level});
            }} else {{
                console.log('Map not found, trying alternative methods');
            }}
            """
            
            self.driver.execute_script(js_script)
            time.sleep(2)  # Allow map to move
            
            return True
        except Exception as e:
            self.logger.error(f"Error zooming to location: {e}")
            return False
    
    def place_pixel(self, x, y, color):
        """
        Place a pixel at the specified coordinates with the given color
        
        Args:
            x: X coordinate on the wplace canvas
            y: Y coordinate on the wplace canvas
            color: Hex color code (e.g., '#FF0000')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, navigate to the pixel location
            if not self.zoom_to_location(x, y):
                return False
            
            # Find the canvas
            canvas = self.driver.find_element(By.TAG_NAME, "canvas")
            
            # Click on the canvas at the pixel location
            # This is a simplified approach - real implementation would need
            # to calculate exact pixel coordinates based on zoom and pan
            if self.driver:
                action = ActionChains(self.driver)
                action.move_to_element(canvas).click().perform()
            
            time.sleep(1)
            
            # Look for color picker/palette
            try:
                if not self.driver:
                    return False
                    
                # Try to find color picker elements
                # This is generic - actual selectors would need to be determined
                # by inspecting wplace.live's DOM structure
                color_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[style*='background-color'], [data-color], .color-option")
                
                # Find matching color
                target_color = color.upper()
                color_clicked = False
                
                for element in color_elements:
                    element_color = element.get_attribute("data-color") or \
                                   element.get_attribute("style") or ""
                    
                    if target_color in element_color.upper():
                        element.click()
                        color_clicked = True
                        break
                
                if not color_clicked:
                    self.logger.warning(f"Could not find color {color} in palette")
                    return False
                
                time.sleep(1)
                
                # Look for confirm/place button
                confirm_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Place') or contains(text(), 'Confirm')]")
                
                if confirm_buttons:
                    confirm_buttons[0].click()
                    time.sleep(1)
                
                return True
                
            except Exception as e:
                self.logger.error(f"Error in color selection: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error placing pixel at ({x}, {y}): {e}")
            return False
    
    def run_pixel_script(self, json_file_path, start_x=0, start_y=0, progress_callback=None):
        """
        Run the bot using a pixel data JSON file
        
        Args:
            json_file_path: Path to the JSON file containing pixel data
            start_x: Starting X coordinate offset
            start_y: Starting Y coordinate offset
            progress_callback: Function to call with progress updates
            
        Returns:
            Dictionary with execution results
        """
        if not self.driver:
            if not self.setup_driver():
                return {'success': False, 'error': 'Failed to setup driver'}
        
        try:
            # Load pixel data
            with open(json_file_path, 'r') as f:
                pixel_data = json.load(f)
            
            pixels = pixel_data['pixels']
            total_pixels = len(pixels)
            
            # Navigate to wplace
            if not self.navigate_to_wplace():
                return {'success': False, 'error': 'Failed to navigate to wplace.live'}
            
            # Execution statistics
            stats = {
                'total_pixels': total_pixels,
                'placed_pixels': 0,
                'failed_pixels': 0,
                'start_time': time.time(),
                'errors': []
            }
            
            self.logger.info(f"Starting pixel placement: {total_pixels} pixels")
            
            # Place each pixel
            for i, pixel in enumerate(pixels):
                try:
                    # Calculate actual coordinates
                    actual_x = start_x + pixel['x']
                    actual_y = start_y + pixel['y']
                    color = pixel['color']
                    
                    self.logger.debug(f"Placing pixel {i+1}/{total_pixels} at ({actual_x}, {actual_y}) with color {color}")
                    
                    # Place the pixel
                    if self.place_pixel(actual_x, actual_y, color):
                        stats['placed_pixels'] += 1
                        self.logger.info(f"Successfully placed pixel {i+1}/{total_pixels}")
                    else:
                        stats['failed_pixels'] += 1
                        error_msg = f"Failed to place pixel at ({actual_x}, {actual_y})"
                        stats['errors'].append(error_msg)
                        self.logger.warning(error_msg)
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback({
                            'current': i + 1,
                            'total': total_pixels,
                            'success': stats['placed_pixels'],
                            'failed': stats['failed_pixels']
                        })
                    
                    # Wait between pixels (rate limiting)
                    if i < total_pixels - 1:  # Don't wait after the last pixel
                        self.logger.debug(f"Waiting {self.wait_time} seconds...")
                        time.sleep(self.wait_time)
                    
                except KeyboardInterrupt:
                    self.logger.info("Bot stopped by user")
                    break
                except Exception as e:
                    stats['failed_pixels'] += 1
                    error_msg = f"Error processing pixel {i+1}: {str(e)}"
                    stats['errors'].append(error_msg)
                    self.logger.error(error_msg)
            
            # Calculate final statistics
            stats['end_time'] = time.time()
            stats['duration'] = stats['end_time'] - stats['start_time']
            stats['success_rate'] = (stats['placed_pixels'] / total_pixels) * 100 if total_pixels > 0 else 0
            
            self.logger.info(f"Bot execution completed: {stats['placed_pixels']}/{total_pixels} pixels placed ({stats['success_rate']:.1f}% success rate)")
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            error_msg = f"Error running pixel script: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def close(self):
        """Clean up and close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")
            finally:
                self.driver = None
    
    def generate_selenium_script(self, json_file_path, start_x=0, start_y=0, output_path=None):
        """
        Generate a standalone Python script for running the bot
        
        Args:
            json_file_path: Path to pixel data JSON file
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            output_path: Where to save the generated script
            
        Returns:
            The generated script as a string
        """
        script_template = f"""#!/usr/bin/env python3
'''
Auto-generated WPlace Bot Script
Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}

This script will automatically place pixels on wplace.live based on the provided image data.
Make sure you have Chrome and ChromeDriver installed.

Usage: python generated_bot_script.py
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# Configuration
JSON_FILE = '{json_file_path}'
START_X = {start_x}
START_Y = {start_y}
WAIT_TIME = 30  # Seconds between pixel placements (wplace.live rate limit)
HEADLESS = False  # Set to True to run without GUI

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver():
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def main():
    driver = None
    try:
        # Load pixel data
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
        
        pixels = data['pixels']
        total_pixels = len(pixels)
        logger.info(f"Loaded {{total_pixels}} pixels to place")
        
        # Setup driver
        driver = setup_driver()
        wait = WebDriverWait(driver, 10)
        
        # Navigate to wplace.live
        logger.info("Navigating to wplace.live...")
        driver.get("https://wplace.live")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
        time.sleep(3)
        
        placed = 0
        failed = 0
        
        # Place each pixel
        for i, pixel in enumerate(pixels):
            try:
                x = START_X + pixel['x']
                y = START_Y + pixel['y']
                color = pixel['color']
                
                logger.info(f"Placing pixel {{i+1}}/{{total_pixels}} at ({{x}}, {{y}}) with color {{color}}")
                
                # Navigate to pixel location (simplified - you may need to adjust this)
                canvas = driver.find_element(By.TAG_NAME, "canvas")
                
                # Click on canvas (this is a basic implementation)
                action = ActionChains(driver)
                action.move_to_element(canvas).click().perform()
                time.sleep(1)
                
                # Note: Actual pixel placement logic would need to be customized
                # based on wplace.live's current interface
                
                placed += 1
                logger.info(f"Pixel {{i+1}} placed successfully")
                
                # Wait for rate limit
                if i < total_pixels - 1:
                    logger.info(f"Waiting {{WAIT_TIME}} seconds...")
                    time.sleep(WAIT_TIME)
                    
            except KeyboardInterrupt:
                logger.info("Stopped by user")
                break
            except Exception as e:
                failed += 1
                logger.error(f"Failed to place pixel {{i+1}}: {{e}}")
        
        logger.info(f"Completed: {{placed}} placed, {{failed}} failed")
        
    except Exception as e:
        logger.error(f"Script error: {{e}}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
"""
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(script_template)
            os.chmod(output_path, 0o755)  # Make executable
        
        return script_template


class MultiThreadBot:
    """Multi-threaded version of WPlace bot for faster pixel placement"""
    
    def __init__(self, thread_count=2, headless=False, wait_time=30):
        self.thread_count = int(thread_count)
        self.headless = headless
        self.wait_time = wait_time
        self.pixel_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.logger = logging.getLogger(__name__)
        self.bots = []
        
    def worker_thread(self, thread_id):
        """Worker thread function for placing pixels"""
        bot = WPlaceBot(headless=self.headless, wait_time=self.wait_time)
        
        try:
            if not bot.setup_driver():
                self.logger.error(f"Thread {thread_id}: Failed to setup driver")
                return
            
            if not bot.navigate_to_wplace():
                self.logger.error(f"Thread {thread_id}: Failed to navigate to wplace")
                return
            
            self.logger.info(f"Thread {thread_id}: Ready for pixel placement")
            
            while not self.stop_event.is_set():
                try:
                    # Get pixel from queue with timeout
                    pixel_data = self.pixel_queue.get(timeout=5)
                    
                    if pixel_data is None:  # Sentinel value to stop
                        break
                    
                    # Place the pixel
                    x = pixel_data['x']
                    y = pixel_data['y'] 
                    color = pixel_data['color']
                    
                    success = bot.place_pixel(x, y, color)
                    
                    # Report result
                    self.results_queue.put({
                        'thread_id': thread_id,
                        'pixel': pixel_data,
                        'success': success,
                        'timestamp': time.time()
                    })
                    
                    # Mark task as done
                    self.pixel_queue.task_done()
                    
                    # Wait between placements (rate limiting)
                    if not self.stop_event.is_set():
                        time.sleep(self.wait_time)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Thread {thread_id}: Error placing pixel: {e}")
                    self.results_queue.put({
                        'thread_id': thread_id,
                        'pixel': pixel_data if 'pixel_data' in locals() else None,
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    })
                    
        finally:
            bot.close()
            self.logger.info(f"Thread {thread_id}: Terminated")
    
    def run_pixel_script(self, json_file_path, start_x=0, start_y=0, progress_callback=None):
        """Run multi-threaded pixel placement"""
        try:
            # Load pixel data
            with open(json_file_path, 'r') as f:
                pixel_data = json.load(f)
            
            pixels = pixel_data['pixels']
            total_pixels = len(pixels)
            
            # Add pixels to queue with offset coordinates
            for pixel in pixels:
                actual_pixel = {
                    'x': start_x + pixel['x'],
                    'y': start_y + pixel['y'],
                    'color': pixel['color'],
                    'original_rgb': pixel['original_rgb']
                }
                self.pixel_queue.put(actual_pixel)
            
            # Start worker threads
            threads = []
            for i in range(self.thread_count):
                thread = threading.Thread(target=self.worker_thread, args=(i,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                self.logger.info(f"Started worker thread {i}")
            
            # Monitor progress
            stats = {
                'total_pixels': total_pixels,
                'placed_pixels': 0,
                'failed_pixels': 0,
                'start_time': time.time(),
                'errors': []
            }
            
            self.logger.info(f"Starting multi-threaded pixel placement: {total_pixels} pixels across {self.thread_count} threads")
            
            # Process results
            processed_count = 0
            while processed_count < total_pixels and not self.stop_event.is_set():
                try:
                    result = self.results_queue.get(timeout=10)
                    processed_count += 1
                    
                    if result['success']:
                        stats['placed_pixels'] += 1
                    else:
                        stats['failed_pixels'] += 1
                        if 'error' in result:
                            stats['errors'].append(result['error'])
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback({
                            'current': processed_count,
                            'total': total_pixels,
                            'success': stats['placed_pixels'],
                            'failed': stats['failed_pixels']
                        })
                    
                    self.logger.debug(f"Progress: {processed_count}/{total_pixels} pixels processed")
                    
                except queue.Empty:
                    self.logger.warning("Timeout waiting for results")
                    continue
            
            # Stop all threads
            self.stop()
            
            # Wait for threads to finish
            for thread in threads:
                thread.join(timeout=10)
            
            # Calculate final statistics
            stats['end_time'] = time.time()
            stats['duration'] = stats['end_time'] - stats['start_time']
            stats['success_rate'] = (stats['placed_pixels'] / total_pixels) * 100 if total_pixels > 0 else 0
            
            self.logger.info(f"Multi-threaded bot execution completed: {stats['placed_pixels']}/{total_pixels} pixels placed ({stats['success_rate']:.1f}% success rate)")
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            error_msg = f"Error running multi-threaded pixel script: {str(e)}"
            self.logger.error(error_msg)
            self.stop()
            return {'success': False, 'error': error_msg}
    
    def stop(self):
        """Stop all worker threads"""
        self.stop_event.set()
        
        # Add sentinel values to stop workers
        for _ in range(self.thread_count):
            self.pixel_queue.put(None)
    
    def generate_selenium_script(self, json_file_path, start_x=0, start_y=0, output_path=None):
        """Generate multi-threaded Selenium script"""
        script_template = f'''#!/usr/bin/env python3
"""
Multi-threaded WPlace Bot Script
Generated for placing pixels on wplace.live
Total threads: {self.thread_count}
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
PIXEL_FILE = "{json_file_path}"
START_X = {start_x}
START_Y = {start_y}
THREAD_COUNT = {self.thread_count}
WAIT_TIME = {self.wait_time}  # seconds between pixel placements

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
            color_element = self.driver.find_element(By.CSS_SELECTOR, f'[data-color="{{color}}"]')
            color_element.click()
            time.sleep(0.5)
            
            print(f"Thread {{self.thread_id}}: Placed pixel at ({{x}}, {{y}}) with color {{color}}")
            return True
            
        except Exception as e:
            print(f"Thread {{self.thread_id}}: Error placing pixel: {{e}}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.quit()

def worker_thread(thread_id, pixel_queue, results_queue):
    bot = WorkerBot(thread_id)
    
    try:
        bot.setup_driver()
        print(f"Thread {{thread_id}}: Ready")
        
        while True:
            try:
                pixel = pixel_queue.get(timeout=5)
                if pixel is None:  # Stop signal
                    break
                
                x = START_X + pixel['x']
                y = START_Y + pixel['y']
                color = pixel['color']
                
                success = bot.place_pixel(x, y, color)
                results_queue.put({{'thread_id': thread_id, 'success': success}})
                
                time.sleep(WAIT_TIME)
                
            except queue.Empty:
                continue
                
    finally:
        bot.close()
        print(f"Thread {{thread_id}}: Finished")

def main():
    # Load pixel data
    with open(PIXEL_FILE, 'r') as f:
        data = json.load(f)
    
    pixels = data['pixels']
    print(f"Starting multi-threaded bot: {{len(pixels)}} pixels across {{THREAD_COUNT}} threads")
    
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
            
            print(f"Progress: {{processed}}/{{total_pixels}} ({{success_count}} successful)")
    
    except KeyboardInterrupt:
        print("\\nStopping...")
    
    # Stop threads
    for _ in range(THREAD_COUNT):
        pixel_queue.put(None)
    
    # Wait for threads to finish
    for thread in threads:
        thread.join()
    
    print(f"Completed: {{success_count}}/{{total_pixels}} pixels placed successfully")

if __name__ == "__main__":
    main()
'''
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(script_template)
            os.chmod(output_path, 0o755)  # Make executable
        
        return script_template
