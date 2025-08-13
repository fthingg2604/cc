#!/usr/bin/env python3
"""
Multi-Account Bot Demo - Test tính năng multiple accounts
"""

import json
import logging
from account_manager import AccountManager, create_sample_accounts_file
from multi_account_bot import MultiAccountBot

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def demo_multi_account():
    """Demo tính năng multiple accounts"""
    
    print("🚀 WPlace Multi-Account Bot Demo")
    print("=" * 50)
    
    # Tạo file accounts mẫu nếu chưa có
    try:
        manager = AccountManager()
        if len(manager.accounts) == 0:
            print("📝 Tạo file accounts.json mẫu...")
            create_sample_accounts_file()
            manager.load_accounts()
    except Exception as e:
        print(f"❌ Lỗi tạo accounts: {e}")
        return
    
    # Hiển thị thông tin accounts
    stats = manager.get_account_stats()
    print(f"📊 Thống kê accounts:")
    print(f"   - Tổng số: {stats['total_accounts']}")
    print(f"   - Premium: {stats['premium_accounts']}")
    print(f"   - Free: {stats['free_accounts']}")
    print()
    
    if stats['total_accounts'] == 0:
        print("⚠️  Chưa có accounts nào được cấu hình")
        print("💡 Hãy chỉnh sửa file accounts.json với thông tin tài khoản thực của bạn")
        return
    
    # Hiển thị danh sách accounts
    print("📋 Danh sách accounts:")
    for i, acc in enumerate(manager.accounts, 1):
        status = "Premium" if acc.is_premium else "Free"
        active = "Active" if acc.is_active else "Inactive"
        print(f"   {i}. {acc.username} ({status}, {active})")
    print()
    
    # Test demo với hình ảnh demo
    demo_files = ['demo1.png', 'demo2.png', 'demo3.png']
    
    for demo_file in demo_files:
        try:
            # Tìm file JSON tương ứng
            json_file = f"processed/{demo_file.replace('.png', '_pixels.json')}"
            
            # Kiểm tra file có tồn tại
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    pixel_count = len(data['pixels'])
                    print(f"🖼️  Found demo: {demo_file} ({pixel_count} pixels)")
                    
                    # Estimate time savings
                    single_time = (pixel_count * 30) / 60  # minutes
                    multi_time = single_time / stats['total_accounts']
                    
                    print(f"   ⏱️  Single account: {single_time:.1f} phút")
                    print(f"   🚀 Multi account ({stats['total_accounts']} acc): {multi_time:.1f} phút")
                    print(f"   📈 Tăng tốc: {stats['total_accounts']:.0f}x nhanh hơn!")
                    print()
                    
                    # Hỏi user có muốn chạy demo không
                    choice = input(f"Chạy demo với {demo_file}? (y/n): ").lower()
                    
                    if choice == 'y':
                        print(f"🎮 Đang chạy multi-account bot demo...")
                        print("⚠️  LƯU Ý: Demo này sẽ chạy thật trên wplace.live!")
                        confirm = input("Bạn có chắc chắn muốn tiếp tục? (yes/no): ").lower()
                        
                        if confirm == 'yes':
                            # Tạo multi-account bot
                            multi_bot = MultiAccountBot(headless=True, wait_time=30)
                            
                            def progress_callback(progress):
                                print(f"📈 Progress: {progress['current']}/{progress['total']} pixels")
                                for acc, count in progress['account_stats'].items():
                                    print(f"   {acc}: {count} pixels")
                            
                            # Chạy bot
                            result = multi_bot.run_pixel_script(
                                json_file,
                                start_x=1000,  # Tọa độ demo
                                start_y=1000,
                                progress_callback=progress_callback
                            )
                            
                            # Hiển thị kết quả
                            if result['success']:
                                stats = result['stats']
                                print("✅ Hoàn thành!")
                                print(f"   🎯 Pixels placed: {stats['placed_pixels']}/{stats['total_pixels']}")
                                print(f"   ⏱️  Thời gian: {stats['duration']:.1f} giây")
                                print(f"   📊 Success rate: {stats['success_rate']:.1f}%")
                                
                                print("\n📈 Thống kê theo account:")
                                for acc, count in stats['account_stats'].items():
                                    print(f"   {acc}: {count} pixels")
                            else:
                                print(f"❌ Lỗi: {result['error']}")
                            
                            # Cleanup
                            multi_bot.stop()
                            break
                        else:
                            print("❌ Hủy demo")
                    
            except FileNotFoundError:
                continue
                
        except Exception as e:
            print(f"❌ Lỗi với {demo_file}: {e}")
            continue
    
    print("\n🎉 Demo hoàn thành!")
    print("💡 Để sử dụng thực tế:")
    print("   1. Cập nhật accounts.json với tài khoản thật")
    print("   2. Upload hình ảnh qua web interface")
    print("   3. Chọn 'Đa tài khoản' trong Bot Control")

if __name__ == "__main__":
    demo_multi_account()