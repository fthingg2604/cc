#!/usr/bin/env python3
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
