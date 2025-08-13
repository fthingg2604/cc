#!/usr/bin/env python3
"""
Multi Account Bot - Bot sử dụng nhiều tài khoản để vẽ nhanh hơn
"""

import os
import sys
import time

# Add current directory to path for standalone execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json
import logging
import threading
import queue
from selenium.webdriver.support.ui import WebDriverWait
from account_manager import AccountManager
from wplace_bot import WPlaceBot

class MultiAccountBot:
    """Bot sử dụng nhiều tài khoản để vẽ nhanh hơn"""
    
    def __init__(self, accounts_file="accounts.json", headless=False, wait_time=30):
        self.account_manager = AccountManager(accounts_file)
        self.headless = headless
        self.wait_time = wait_time
        self.pixel_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.logger = logging.getLogger(__name__)
        self.account_drivers = {}
        
    def get_available_accounts(self):
        """Lấy danh sách accounts có thể sử dụng"""
        return self.account_manager.get_active_accounts()
    
    def setup_accounts(self):
        """Setup và login tất cả accounts"""
        self.logger.info("Setting up multiple accounts...")
        self.account_drivers = self.account_manager.login_all_accounts(self.headless)
        
        if not self.account_drivers:
            self.logger.error("No accounts successfully logged in!")
            return False
        
        self.logger.info(f"Successfully setup {len(self.account_drivers)} accounts")
        return True
    
    def account_worker_thread(self, username, driver):
        """Worker thread cho một account cụ thể"""
        account = self.account_manager.get_account_by_username(username)
        if not account:
            return
            
        placed_count = 0
        self.logger.info(f"Account {username}: Starting worker thread")
        
        try:
            while not self.stop_event.is_set():
                try:
                    pixel_data = self.pixel_queue.get(timeout=5)
                    if pixel_data is None:
                        break
                    
                    x = pixel_data['x']
                    y = pixel_data['y']
                    color = pixel_data['color']
                    
                    # Create temporary bot for this driver
                    temp_bot = WPlaceBot(headless=self.headless, wait_time=self.wait_time)
                    temp_bot.driver = driver
                    temp_bot.wait = WebDriverWait(driver, 10)
                    
                    success = temp_bot.place_pixel(x, y, color)
                    
                    if success:
                        placed_count += 1
                    
                    self.results_queue.put({
                        'account': username,
                        'pixel': pixel_data,
                        'success': success,
                        'timestamp': time.time()
                    })
                    
                    self.pixel_queue.task_done()
                    account.last_used = time.time()
                    
                    # Rate limiting
                    if not self.stop_event.is_set():
                        self.logger.debug(f"Account {username}: Waiting {self.wait_time}s...")
                        time.sleep(self.wait_time)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Account {username}: Error placing pixel: {e}")
                    self.results_queue.put({
                        'account': username,
                        'pixel': pixel_data if 'pixel_data' in locals() else None,
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    })
                    
        finally:
            self.logger.info(f"Account {username}: Placed {placed_count} pixels")
    
    def run_pixel_script(self, json_file_path, start_x=0, start_y=0, progress_callback=None):
        """Chạy bot với multiple accounts"""
        try:
            if not self.setup_accounts():
                return {'success': False, 'error': 'Failed to setup accounts'}
            
            with open(json_file_path, 'r') as f:
                pixel_data = json.load(f)
            
            pixels = pixel_data['pixels']
            total_pixels = len(pixels)
            account_count = len(self.account_drivers)
            
            # Add pixels to queue
            for pixel in pixels:
                actual_pixel = {
                    'x': start_x + pixel['x'],
                    'y': start_y + pixel['y'],
                    'color': pixel['color'],
                    'original_rgb': pixel['original_rgb']
                }
                self.pixel_queue.put(actual_pixel)
            
            # Start worker threads for each account
            threads = []
            for username, driver in self.account_drivers.items():
                thread = threading.Thread(target=self.account_worker_thread, args=(username, driver))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                self.logger.info(f"Started worker thread for account: {username}")
            
            # Monitor progress
            stats = {
                'total_pixels': total_pixels,
                'placed_pixels': 0,
                'failed_pixels': 0,
                'start_time': time.time(),
                'account_stats': {username: 0 for username in self.account_drivers.keys()},
                'errors': []
            }
            
            self.logger.info(f"Starting multi-account pixel placement: {total_pixels} pixels across {account_count} accounts")
            
            # Process results
            processed_count = 0
            while processed_count < total_pixels and not self.stop_event.is_set():
                try:
                    result = self.results_queue.get(timeout=10)
                    processed_count += 1
                    
                    account = result['account']
                    if result['success']:
                        stats['placed_pixels'] += 1
                        stats['account_stats'][account] += 1
                    else:
                        stats['failed_pixels'] += 1
                        if 'error' in result:
                            stats['errors'].append(f"{account}: {result['error']}")
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback({
                            'current': processed_count,
                            'total': total_pixels,
                            'success': stats['placed_pixels'],
                            'failed': stats['failed_pixels'],
                            'account_stats': stats['account_stats']
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
            
            self.logger.info(f"Multi-account bot execution completed: {stats['placed_pixels']}/{total_pixels} pixels placed ({stats['success_rate']:.1f}% success rate)")
            
            return {'success': True, 'stats': stats}
            
        except Exception as e:
            error_msg = f"Error running multi-account pixel script: {str(e)}"
            self.logger.error(error_msg)
            self.stop()
            return {'success': False, 'error': error_msg}
    
    def stop(self):
        """Stop all workers and close drivers"""
        self.stop_event.set()
        
        # Add sentinel values to stop workers
        for _ in range(len(self.account_drivers)):
            self.pixel_queue.put(None)
        
        # Close all drivers
        self.account_manager.close_all_drivers()
    
    def get_account_stats(self):
        """Lấy thống kê về các accounts"""
        accounts = self.account_manager.get_active_accounts()
        stats = {
            'total_accounts': len(accounts),
            'premium_accounts': len([acc for acc in accounts if acc.is_premium]),
            'free_accounts': len([acc for acc in accounts if not acc.is_premium]),
            'logged_in_accounts': len(self.account_drivers),
            'accounts': []
        }
        
        for acc in accounts:
            stats['accounts'].append({
                'username': acc.username,
                'is_premium': acc.is_premium,
                'is_active': acc.is_active,
                'last_used': acc.last_used,
                'is_logged_in': acc.username in self.account_drivers
            })
        
        return stats
    
    def generate_selenium_script(self, json_file_path, start_x=0, start_y=0, output_path=None):
        """Generate multi-account Selenium script"""
        accounts = self.get_available_accounts()
        account_count = len(accounts)
        
        script_template = f'''#!/usr/bin/env python3
"""
Multi-Account WPlace Bot Script
Generated for placing pixels on wplace.live with {account_count} accounts
"""

import time
import json
import threading
import queue
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
WAIT_TIME = {self.wait_time}

# Account credentials (EDIT THESE!)
ACCOUNTS = ['''

        for i, acc in enumerate(accounts):
            script_template += f'''
    {{"username": "{acc.username}", "password": "{acc.password}"}},'''
            
        script_template += f'''
]

class AccountBot:
    def __init__(self, account, headless=True):
        self.account = account
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_{{self.account['username']}}")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://wplace.live")
        time.sleep(2)
        
    def login(self):
        try:
            # Login implementation here
            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_btn.click()
            time.sleep(1)
            
            username_field = self.driver.find_element(By.NAME, "username")
            username_field.send_keys(self.account['username'])
            
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(self.account['password'])
            
            submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            time.sleep(3)
            
            return True
        except Exception as e:
            print(f"Login failed for {{self.account['username']}}: {{e}}")
            return False
    
    def place_pixel(self, x, y, color):
        try:
            # Pixel placement implementation
            canvas = self.driver.find_element(By.ID, "canvas")
            self.driver.execute_script(f"arguments[0].click();", canvas)
            time.sleep(0.5)
            
            print(f"Account {{self.account['username']}}: Placed pixel at ({{x}}, {{y}}) with color {{color}}")
            return True
            
        except Exception as e:
            print(f"Account {{self.account['username']}}: Error placing pixel: {{e}}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.quit()

def worker_thread(account, pixel_queue, results_queue):
    bot = AccountBot(account)
    
    try:
        bot.setup_driver()
        if not bot.login():
            return
            
        print(f"Account {{account['username']}}: Ready")
        
        while True:
            try:
                pixel = pixel_queue.get(timeout=5)
                if pixel is None:
                    break
                
                x = START_X + pixel['x']
                y = START_Y + pixel['y']
                color = pixel['color']
                
                success = bot.place_pixel(x, y, color)
                results_queue.put({{'account': account['username'], 'success': success}})
                
                time.sleep(WAIT_TIME)
                
            except queue.Empty:
                continue
                
    finally:
        bot.close()
        print(f"Account {{account['username']}}: Finished")

def main():
    with open(PIXEL_FILE, 'r') as f:
        data = json.load(f)
    
    pixels = data['pixels']
    print(f"Starting multi-account bot: {{len(pixels)}} pixels across {{len(ACCOUNTS)}} accounts")
    
    pixel_queue = queue.Queue()
    results_queue = queue.Queue()
    
    for pixel in pixels:
        pixel_queue.put(pixel)
    
    threads = []
    for account in ACCOUNTS:
        thread = threading.Thread(target=worker_thread, args=(account, pixel_queue, results_queue))
        thread.start()
        threads.append(thread)
    
    total_pixels = len(pixels)
    processed = 0
    success_count = 0
    
    try:
        while processed < total_pixels:
            result = results_queue.get(timeout=60)
            processed += 1
            if result['success']:
                success_count += 1
            
            print(f"Progress: {{processed}}/{{total_pixels}} ({{success_count}} successful)")
    
    except KeyboardInterrupt:
        print("\\nStopping...")
    
    for _ in range(len(ACCOUNTS)):
        pixel_queue.put(None)
    
    for thread in threads:
        thread.join()
    
    print(f"Completed: {{success_count}}/{{total_pixels}} pixels placed successfully")

if __name__ == "__main__":
    main()
'''
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(script_template)
            import os
            os.chmod(output_path, 0o755)
        
        return script_template