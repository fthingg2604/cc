#!/usr/bin/env python3
"""
Run WPlace Bot Locally
Chạy bot trên máy local với môi trường development
"""

import os
import sys
import logging
from app import app

def setup_environment():
    """Setup môi trường development"""
    # Set environment variables nếu chưa có
    if not os.environ.get('SESSION_SECRET'):
        os.environ['SESSION_SECRET'] = 'dev-secret-key-change-in-production'
    
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///wplace_bot.db'
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    print("🎮 WPlace Bot - Local Development Server")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Tạo thư mục cần thiết
    folders = ['uploads', 'processed', 'scripts', 'static', 'instance']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    print("🌐 Server đang khởi động...")
    print("📍 Địa chỉ: http://localhost:5000")
    print("🔧 Mode: Development")
    print("📝 Logs sẽ hiển thị ở terminal này")
    print("\n⚠️  Để dừng server: Ctrl+C")
    print("=" * 50)
    
    try:
        # Chạy Flask development server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server đã dừng!")
    except Exception as e:
        print(f"❌ Lỗi khởi động server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())