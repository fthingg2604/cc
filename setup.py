#!/usr/bin/env python3
"""
WPlace Bot Setup Script
Cài đặt dependencies và thiết lập môi trường cho WPlace Bot
"""

import subprocess
import sys
import os

def install_requirements():
    """Cài đặt các packages cần thiết"""
    requirements = [
        "Flask==3.0.0",
        "Flask-SQLAlchemy==3.1.1", 
        "Werkzeug==3.0.1",
        "SQLAlchemy==2.0.23",
        "email-validator==2.1.0",
        "Pillow==10.1.0",
        "numpy==1.26.2",
        "selenium==4.15.2",
        "psycopg2-binary==2.9.9",
        "gunicorn==21.2.0"
    ]
    
    print("🚀 Đang cài đặt WPlace Bot...")
    print("=" * 50)
    
    for package in requirements:
        print(f"📦 Cài đặt {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} đã cài đặt thành công")
        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi cài đặt {package}: {e}")
            return False
    
    return True

def create_folders():
    """Tạo các thư mục cần thiết"""
    folders = [
        "uploads",
        "processed", 
        "scripts",
        "static",
        "templates",
        "instance"
    ]
    
    print("\n📁 Tạo các thư mục...")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Thư mục {folder} đã tạo")

def setup_database():
    """Thiết lập database"""
    print("\n🗄️ Thiết lập database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database đã được thiết lập")
        return True
    except Exception as e:
        print(f"❌ Lỗi thiết lập database: {e}")
        return False

def main():
    print("🎮 WPlace Bot Setup")
    print("Automated Python bot for wplace.live pixel art")
    print("=" * 50)
    
    # Cài đặt packages
    if not install_requirements():
        print("❌ Cài đặt packages thất bại!")
        return False
    
    # Tạo thư mục
    create_folders()
    
    # Setup database
    if not setup_database():
        print("⚠️ Database setup có vấn đề, bot vẫn có thể chạy")
    
    print("\n🎉 Setup hoàn thành!")
    print("\n📋 Hướng dẫn sử dụng:")
    print("1. Chạy web server: python main.py")
    print("2. Hoặc chạy standalone: python standalone_bot.py")
    print("3. Demo nhanh: python start_bot.py")
    print("4. Multi-account demo: python multi_account_demo.py")
    print("\n🌐 Web interface: http://localhost:5000")

if __name__ == "__main__":
    main()