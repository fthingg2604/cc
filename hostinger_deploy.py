#!/usr/bin/env python3
"""
Hostinger Deployment Guide & Setup
Hướng dẫn deploy WPlace Bot lên Hostinger
"""

import os
import zipfile
import shutil

def create_hostinger_package():
    """Tạo package để upload lên Hostinger"""
    
    print("📦 Tạo package cho Hostinger...")
    
    # Files cần thiết cho Hostinger
    essential_files = [
        'main.py',
        'app.py', 
        'routes.py',
        'models.py',
        'wplace_bot.py',
        'multi_account_bot.py',
        'account_manager.py',
        'image_processor.py',
        'color_palette.py',
        'setup.py',
        'run_production.py',
        'standalone_bot.py',
        'start_bot.py'
    ]
    
    # Thư mục cần thiết
    essential_dirs = [
        'templates',
        'static',
        'uploads',
        'processed',
        'scripts'
    ]
    
    # Tạo thư mục deploy
    deploy_dir = 'hostinger_deploy'
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # Copy files
    print("📁 Copy files...")
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
            print(f"✅ {file}")
    
    # Copy directories
    for dir_name in essential_dirs:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(deploy_dir, dir_name))
            print(f"✅ {dir_name}/")
    
    # Tạo .htaccess cho Hostinger
    htaccess_content = """RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ main.py/$1 [QSA,L]

# Python CGI
AddHandler cgi-script .py
Options +ExecCGI

# Security headers
Header always set X-Frame-Options DENY
Header always set X-Content-Type-Options nosniff
Header always set X-XSS-Protection "1; mode=block"
"""
    
    with open(os.path.join(deploy_dir, '.htaccess'), 'w') as f:
        f.write(htaccess_content)
    print("✅ .htaccess")
    
    # Tạo requirements.txt
    requirements_content = """Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Werkzeug==3.0.1
SQLAlchemy==2.0.23
email-validator==2.1.0
Pillow==10.1.0
numpy==1.26.2
selenium==4.15.2
psycopg2-binary==2.9.9
gunicorn==21.2.0
"""
    
    with open(os.path.join(deploy_dir, 'requirements.txt'), 'w') as f:
        f.write(requirements_content)
    print("✅ requirements.txt")
    
    # Tạo hostinger_setup.py
    hostinger_setup_content = '''#!/usr/bin/env python3
"""
Hostinger Setup Script
Chạy script này sau khi upload lên Hostinger
"""

import sys
import os
import subprocess

def main():
    print("Setting up WPlace Bot on Hostinger...")
    
    # Install requirements
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"])
        print("✅ Requirements installed")
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
    
    # Create directories
    dirs = ['uploads', 'processed', 'scripts', 'instance']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        os.chmod(d, 0o755)
    
    # Set permissions
    os.chmod('main.py', 0o755)
    print("✅ Permissions set")
    
    print("🎉 Setup complete! Access your bot at your domain")

if __name__ == "__main__":
    main()
'''
    
    with open(os.path.join(deploy_dir, 'hostinger_setup.py'), 'w') as f:
        f.write(hostinger_setup_content)
    print("✅ hostinger_setup.py")
    
    # Tạo file zip
    zip_filename = 'wplace_bot_hostinger.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"📦 Package tạo thành công: {zip_filename}")
    return zip_filename

def print_deployment_guide():
    """In hướng dẫn deploy"""
    
    guide = """
🚀 HƯỚNG DẪN DEPLOY LÊN HOSTINGER

📋 BƯỚC 1: Chuẩn bị Hostinger
   - Đăng ký hosting Python tại Hostinger
   - Truy cập cPanel hoặc File Manager
   - Đảm bảo Python 3.8+ được hỗ trợ

📦 BƯỚC 2: Upload Files
   1. Upload file wplace_bot_hostinger.zip lên thư mục public_html
   2. Giải nén tất cả files
   3. Chạy: python3 hostinger_setup.py
   4. Set environment variables trong cPanel:
      - SESSION_SECRET=your-secret-key-here

🗄️ BƯỚC 3: Database (Tùy chọn)
   - Tạo MySQL/PostgreSQL database trong cPanel
   - Set DATABASE_URL=mysql://user:pass@host/dbname

🌐 BƯỚC 4: Test
   - Truy cập: https://yourdomain.com
   - Kiểm tra upload ảnh và bot control

⚠️ LƯU Ý:
   - Hostinger có thể giới hạn Selenium/Chrome
   - Nên test trước với shared hosting
   - VPS/Cloud hosting sẽ ổn định hơn

🔧 TROUBLESHOOTING:
   - Lỗi 500: Kiểm tra error logs trong cPanel
   - Import error: Cài đặt lại requirements
   - Permission denied: chmod 755 cho các files .py

═══════════════════════════════════════════════════════════

🏠 CHẠY LOCALHOST (Đơn giản nhất):

1. Cài đặt:
   python setup.py

2. Chạy development:
   python run_local.py

3. Truy cập: http://localhost:5000

4. Hoặc chạy standalone:
   python standalone_bot.py

═══════════════════════════════════════════════════════════
"""
    
    print(guide)

def main():
    print("🎮 WPlace Bot - Hostinger Deployment Tool")
    print("=" * 50)
    
    # Tạo package
    zip_file = create_hostinger_package()
    
    # In hướng dẫn
    print_deployment_guide()
    
    print(f"✅ Package sẵn sàng: {zip_file}")
    print("📤 Upload file này lên Hostinger và làm theo hướng dẫn")

if __name__ == "__main__":
    main()