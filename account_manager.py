"""
Account Manager - Quản lý nhiều tài khoản wplace.live
Hỗ trợ login và quản lý session cho multiple accounts
"""

import json
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Account:
    """Thông tin tài khoản"""
    username: str
    password: str
    email: str = ""
    is_premium: bool = False
    last_used: Optional[float] = None
    is_active: bool = True
    cookies: Optional[str] = None

class AccountManager:
    """Quản lý nhiều tài khoản wplace.live"""
    
    def __init__(self, accounts_file="accounts.json"):
        self.accounts_file = accounts_file
        self.accounts: List[Account] = []
        self.logged_in_drivers = {}  # {account_username: driver}
        self.logger = logging.getLogger(__name__)
        
        # Load accounts from file
        self.load_accounts()
    
    def load_accounts(self):
        """Load danh sách accounts từ file"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.accounts = [Account(**acc) for acc in data]
                self.logger.info(f"Loaded {len(self.accounts)} accounts")
            except Exception as e:
                self.logger.error(f"Error loading accounts: {e}")
                self.accounts = []
        else:
            self.logger.info("No accounts file found, starting with empty list")
    
    def save_accounts(self):
        """Save danh sách accounts vào file"""
        try:
            data = []
            for acc in self.accounts:
                data.append({
                    'username': acc.username,
                    'password': acc.password,
                    'email': acc.email,
                    'is_premium': acc.is_premium,
                    'last_used': acc.last_used,
                    'is_active': acc.is_active,
                    'cookies': acc.cookies
                })
            
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.accounts)} accounts")
        except Exception as e:
            self.logger.error(f"Error saving accounts: {e}")
    
    def add_account(self, username: str, password: str, email: str = "", is_premium: bool = False):
        """Thêm tài khoản mới"""
        # Check if account already exists
        for acc in self.accounts:
            if acc.username == username:
                self.logger.warning(f"Account {username} already exists")
                return False
        
        new_account = Account(
            username=username,
            password=password,
            email=email,
            is_premium=is_premium
        )
        
        self.accounts.append(new_account)
        self.save_accounts()
        self.logger.info(f"Added account: {username}")
        return True
    
    def remove_account(self, username: str):
        """Xóa tài khoản"""
        self.accounts = [acc for acc in self.accounts if acc.username != username]
        self.save_accounts()
        self.logger.info(f"Removed account: {username}")
    
    def get_active_accounts(self) -> List[Account]:
        """Lấy danh sách accounts đang active"""
        return [acc for acc in self.accounts if acc.is_active]
    
    def setup_driver_for_account(self, account: Account, headless: bool = True) -> Optional[webdriver.Chrome]:
        """Setup Chrome driver cho một account cụ thể"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            
            # Unique profile for each account
            profile_dir = f"/tmp/chrome_profile_{account.username}"
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://wplace.live")
            time.sleep(2)
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup driver for {account.username}: {e}")
            return None
    
    def login_account(self, account: Account, driver: webdriver.Chrome) -> bool:
        """Login tài khoản vào wplace.live"""
        try:
            self.logger.info(f"Logging in account: {account.username}")
            
            # Check if already logged in
            if self.is_logged_in(driver):
                self.logger.info(f"Account {account.username} already logged in")
                return True
            
            # Find and click login button
            login_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Đăng nhập')]"))
            )
            login_btn.click()
            time.sleep(1)
            
            # Enter username
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            username_field.send_keys(account.username)
            
            # Enter password
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(account.password)
            
            # Submit form
            submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            
            # Wait for login success
            time.sleep(3)
            
            if self.is_logged_in(driver):
                self.logger.info(f"Successfully logged in: {account.username}")
                account.last_used = time.time()
                
                # Save cookies for future use
                cookies = driver.get_cookies()
                account.cookies = json.dumps(cookies)
                self.save_accounts()
                
                return True
            else:
                self.logger.error(f"Login failed for: {account.username}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error logging in {account.username}: {e}")
            return False
    
    def is_logged_in(self, driver: webdriver.Chrome) -> bool:
        """Kiểm tra xem đã login chưa"""
        try:
            # Look for elements that indicate logged in state
            user_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'username') or contains(@class, 'user-info')]")
            logout_elements = driver.find_elements(By.XPATH, "//button[contains(text(), 'Logout') or contains(text(), 'Đăng xuất')]")
            
            return len(user_elements) > 0 or len(logout_elements) > 0
            
        except Exception:
            return False
    
    def login_all_accounts(self, headless: bool = True) -> dict:
        """Login tất cả accounts và trả về dictionary của drivers"""
        results = {}
        active_accounts = self.get_active_accounts()
        
        self.logger.info(f"Logging in {len(active_accounts)} accounts...")
        
        for account in active_accounts:
            driver = self.setup_driver_for_account(account, headless)
            if driver:
                if self.login_account(account, driver):
                    results[account.username] = driver
                    self.logged_in_drivers[account.username] = driver
                else:
                    driver.quit()
            
            # Small delay between logins
            time.sleep(2)
        
        self.logger.info(f"Successfully logged in {len(results)} accounts")
        return results
    
    def close_all_drivers(self):
        """Đóng tất cả browser drivers"""
        for username, driver in self.logged_in_drivers.items():
            try:
                driver.quit()
                self.logger.info(f"Closed driver for {username}")
            except Exception as e:
                self.logger.error(f"Error closing driver for {username}: {e}")
        
        self.logged_in_drivers.clear()
    
    def get_account_by_username(self, username: str) -> Optional[Account]:
        """Lấy account theo username"""
        for acc in self.accounts:
            if acc.username == username:
                return acc
        return None
    
    def update_account_status(self, username: str, is_active: bool):
        """Cập nhật trạng thái account"""
        account = self.get_account_by_username(username)
        if account:
            account.is_active = is_active
            self.save_accounts()
    
    def get_premium_accounts(self) -> List[Account]:
        """Lấy danh sách premium accounts"""
        return [acc for acc in self.get_active_accounts() if acc.is_premium]
    
    def get_free_accounts(self) -> List[Account]:
        """Lấy danh sách free accounts"""
        return [acc for acc in self.get_active_accounts() if not acc.is_premium]

def create_sample_accounts_file():
    """Tạo file accounts.json mẫu"""
    sample_accounts = [
        {
            "username": "user1",
            "password": "password1",
            "email": "user1@example.com",
            "is_premium": False,
            "last_used": None,
            "is_active": True,
            "cookies": None
        },
        {
            "username": "user2",
            "password": "password2", 
            "email": "user2@example.com",
            "is_premium": True,
            "last_used": None,
            "is_active": True,
            "cookies": None
        }
    ]
    
    with open("accounts.json", "w", encoding="utf-8") as f:
        json.dump(sample_accounts, f, indent=2, ensure_ascii=False)
    
    print("Created sample accounts.json file")
    print("Please edit this file with your real account credentials")

if __name__ == "__main__":
    # Test account manager
    create_sample_accounts_file()
    
    manager = AccountManager()
    print(f"Loaded {len(manager.accounts)} accounts")
    
    for acc in manager.accounts:
        print(f"- {acc.username} ({'Premium' if acc.is_premium else 'Free'})")