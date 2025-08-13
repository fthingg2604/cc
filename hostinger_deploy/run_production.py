#!/usr/bin/env python3
"""
Run WPlace Bot in Production
Chạy bot trong môi trường production với Gunicorn
"""

import os
import sys
import subprocess
import logging

def setup_production_environment():
    """Setup môi trường production"""
    # Kiểm tra các environment variables cần thiết
    required_vars = ['SESSION_SECRET']
    
    for var in required_vars:
        if not os.environ.get(var):
            print(f"❌ Thiếu environment variable: {var}")
            print("💡 Hãy set các biến môi trường sau:")
            print("   export SESSION_SECRET='your-secret-key-here'")
            print("   export DATABASE_URL='postgresql://user:pass@host:port/dbname'  # Optional")
            return False
    
    # Set default database nếu chưa có
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///wplace_bot.db'
        print("⚠️  Sử dụng SQLite database mặc định")
    
    return True

def main():
    print("🚀 WPlace Bot - Production Server")
    print("=" * 50)
    
    # Check environment
    if not setup_production_environment():
        return 1
    
    # Tạo thư mục cần thiết
    folders = ['uploads', 'processed', 'scripts', 'static', 'instance']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Production settings
    workers = os.cpu_count() or 1
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🔧 Workers: {workers}")
    print(f"📍 Port: {port}")
    print(f"🗄️ Database: {os.environ.get('DATABASE_URL', '').split('://')[0]}")
    print("=" * 50)
    
    # Gunicorn command
    cmd = [
        sys.executable, '-m', 'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', str(workers),
        '--worker-class', 'sync',
        '--worker-connections', '1000',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--timeout', '30',
        '--keepalive', '2',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--log-level', 'info',
        'main:app'
    ]
    
    try:
        print("🌐 Production server đang khởi động...")
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Server đã dừng!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khởi động production server: {e}")
        return 1
    except FileNotFoundError:
        print("❌ Gunicorn không tìm thấy!")
        print("💡 Cài đặt: pip install gunicorn")
        return 1

if __name__ == "__main__":
    sys.exit(main())