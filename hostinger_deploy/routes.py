import os
import json
import uuid
from flask import render_template, request, jsonify, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
from app import app, db
from models import ImageUpload, BotSession, PixelLog
from image_processor import ImageProcessor
from color_palette import create_color_palette_json, FREE_COLORS, PREMIUM_COLORS
from wplace_bot import WPlaceBot, MultiThreadBot
from multi_account_bot import MultiAccountBot
import logging
import threading

# Initialize image processor
image_processor = ImageProcessor(app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER'])

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with image upload interface"""
    recent_uploads = ImageUpload.query.order_by(ImageUpload.upload_time.desc()).limit(5).all()
    return render_template('index.html', recent_uploads=recent_uploads)

@app.route('/api/color-palette')
def get_color_palette():
    """Get the wplace color palette data"""
    return jsonify(create_color_palette_json())

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please use PNG, JPG, GIF, or SVG.'}), 400
    
    try:
        # Generate unique filename
        if not file.filename:
            return jsonify({'error': 'Invalid filename'}), 400
            
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Create database record
        image_upload = ImageUpload()
        image_upload.filename = unique_filename
        image_upload.original_filename = original_filename
        db.session.add(image_upload)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'image_id': image_upload.id,
            'filename': unique_filename,
            'original_filename': original_filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/process', methods=['POST'])
def process_image():
    """Process uploaded image into pixel art"""
    data = request.get_json()
    image_id = data.get('image_id')
    pixel_size = int(data.get('pixel_size', 4))
    use_free_only = data.get('use_free_only', False)
    max_width = int(data.get('max_width', 64))
    max_height = int(data.get('max_height', 64))
    
    # Get image record
    image_upload = ImageUpload.query.get(image_id)
    if not image_upload:
        return jsonify({'error': 'Image not found'}), 404
    
    try:
        # Determine allowed colors
        allowed_colors = FREE_COLORS if use_free_only else None
        
        # Process the image
        result = image_processor.process_image(
            filename=image_upload.filename,
            pixel_size=pixel_size,
            allowed_colors=allowed_colors,
            max_width=max_width,
            max_height=max_height
        )
        
        if not result['success']:
            return jsonify({'error': result['error']}), 500
        
        # Update database record
        image_upload.processed_filename = result['output_filename']
        image_upload.width = result['processed_size'][0]
        image_upload.height = result['processed_size'][1]
        image_upload.pixel_size = pixel_size
        image_upload.status = 'processed'
        db.session.commit()
        
        # Create preview
        json_filename = result['json_filename']
        preview_filename = image_processor.create_preview_grid(json_filename)
        
        return jsonify({
            'success': True,
            'image_id': image_id,
            'processed_filename': result['output_filename'],
            'json_filename': json_filename,
            'preview_filename': preview_filename,
            'dimensions': result['processed_size'],
            'total_pixels': result['total_pixels'],
            'color_stats': result['color_stats']
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Processing error: {e}")
        logging.error(f"Full traceback: {error_details}")
        return jsonify({'error': f'Processing failed: {str(e)}', 'details': error_details}), 500

@app.route('/bot-control/<int:image_id>')
def bot_control(image_id):
    """Bot control interface"""
    image_upload = ImageUpload.query.get_or_404(image_id)
    
    if image_upload.status != 'processed':
        flash('Image must be processed before bot control', 'error')
        return redirect(url_for('index'))
    
    # Get recent bot sessions for this image
    recent_sessions = BotSession.query.filter_by(image_id=image_id).order_by(BotSession.start_time.desc()).limit(3).all()
    
    return render_template('bot_control.html', 
                         image=image_upload, 
                         recent_sessions=recent_sessions)

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the bot automation"""
    data = request.get_json()
    image_id = data.get('image_id')
    start_x = int(data.get('start_x', 0))
    start_y = int(data.get('start_y', 0))
    headless = data.get('headless', False)
    thread_count = int(data.get('thread_count', 1))
    
    # Get image record
    image_upload = ImageUpload.query.get(image_id)
    if not image_upload or image_upload.status != 'processed':
        return jsonify({'error': 'Image not found or not processed'}), 404
    
    try:
        # Create bot session
        session = BotSession()
        session.image_id = image_id
        session.total_pixels = (image_upload.width or 0) * (image_upload.height or 0)
        session.status = 'starting'
        db.session.add(session)
        db.session.commit()
        
        # Update image record
        image_upload.start_x = start_x
        image_upload.start_y = start_y
        db.session.commit()
        
        # Start bot in background thread
        def run_bot():
            try:
                # Update session status
                session.status = 'running'
                db.session.commit()
                
                # Get JSON file path
                json_filename = image_upload.processed_filename.replace('.png', '.json').replace('_processed_', '_pixels_')
                json_path = os.path.join(app.config['PROCESSED_FOLDER'], json_filename)
                
                # Progress callback
                def progress_callback(progress):
                    session.pixels_placed = progress['success']
                    db.session.commit()
                
                # Choose bot based on request parameters
                bot_mode = data.get('bot_mode', 'single')
                multi_account = data.get('multi_account', False)
                
                if multi_account or bot_mode == 'multi-account':
                    # Use multi-account bot
                    bot = MultiAccountBot(headless=headless, wait_time=30)
                    result = bot.run_pixel_script(json_path, start_x, start_y, progress_callback)
                elif thread_count > 1:
                    # Use multi-threaded bot
                    bot = MultiThreadBot(thread_count=thread_count, headless=headless)
                    result = bot.run_pixel_script(json_path, start_x, start_y, progress_callback)
                else:
                    # Single-threaded bot
                    bot = WPlaceBot(headless=headless)
                    result = bot.run_pixel_script(json_path, start_x, start_y, progress_callback)
                    bot.close()
                
                # Update session with results
                if result['success']:
                    session.status = 'completed'
                    session.pixels_placed = result['stats']['placed_pixels']
                else:
                    session.status = 'failed'
                    session.error_message = result.get('error', 'Unknown error')
                
                db.session.commit()
                
            except Exception as e:
                session.status = 'failed'
                session.error_message = str(e)
                db.session.commit()
        
        # Start the bot thread
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'message': 'Bot started successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to start bot: {str(e)}'}), 500

@app.route('/api/bot/status/<int:session_id>')
def bot_status(session_id):
    """Get bot session status"""
    session = BotSession.query.get_or_404(session_id)
    
    return jsonify({
        'session_id': session.id,
        'status': session.status,
        'pixels_placed': session.pixels_placed,
        'total_pixels': session.total_pixels,
        'progress': (session.pixels_placed / session.total_pixels * 100) if session.total_pixels > 0 else 0,
        'error_message': session.error_message,
        'start_time': session.start_time.isoformat() if session.start_time else None,
        'end_time': session.end_time.isoformat() if session.end_time else None
    })

@app.route('/api/generate-script', methods=['POST'])
def generate_script():
    """Generate a standalone Python script for the bot"""
    data = request.get_json()
    image_id = data.get('image_id')
    start_x = int(data.get('start_x', 0))
    start_y = int(data.get('start_y', 0))
    thread_count = int(data.get('thread_count', 1))
    
    # Get image record
    image_upload = ImageUpload.query.get(image_id)
    if not image_upload or image_upload.status != 'processed':
        return jsonify({'error': 'Image not found or not processed'}), 404
    
    try:
        # Get JSON file path
        json_filename = image_upload.processed_filename.replace('.png', '.json').replace('_processed_', '_pixels_')
        json_path = os.path.join(app.config['PROCESSED_FOLDER'], json_filename)
        
        # Generate script (use appropriate bot type)
        if thread_count > 1:
            bot = MultiThreadBot(thread_count=thread_count)
            script_filename = f"wplace_multithread_bot_{image_upload.id}_{thread_count}threads.py"
        else:
            bot = WPlaceBot()
            script_filename = f"wplace_bot_{image_upload.id}.py"
        
        script_path = os.path.join(app.config['SCRIPTS_FOLDER'], script_filename)
        
        script_content = bot.generate_selenium_script(
            json_file_path=json_path,
            start_x=start_x,
            start_y=start_y,
            output_path=script_path
        )
        
        return jsonify({
            'success': True,
            'script_filename': script_filename,
            'script_content': script_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate script: {str(e)}'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download processed files"""
    # Determine which folder to serve from
    if filename.endswith('_processed.png') or filename.endswith('_preview.png'):
        return send_from_directory(app.config['PROCESSED_FOLDER'], filename)
    elif filename.endswith('.json'):
        return send_from_directory(app.config['PROCESSED_FOLDER'], filename)
    elif filename.endswith('.py'):
        return send_from_directory(app.config['SCRIPTS_FOLDER'], filename)
    else:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# Account Management APIs
@app.route('/api/accounts/stats', methods=['GET'])
def get_account_stats():
    try:
        from account_manager import AccountManager
        manager = AccountManager()
        stats = manager.get_account_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            'total_accounts': 0,
            'premium_accounts': 0,
            'free_accounts': 0,
            'logged_in_accounts': 0,
            'accounts': []
        })


@app.route('/api/accounts/list', methods=['GET'])
def list_accounts():
    try:
        from account_manager import AccountManager
        manager = AccountManager()
        accounts = manager.get_active_accounts()
        
        account_list = []
        for acc in accounts:
            account_list.append({
                'username': acc.username,
                'is_premium': acc.is_premium,
                'is_active': acc.is_active,
                'last_used': acc.last_used
            })
        
        return jsonify({
            'success': True,
            'accounts': account_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'accounts': []
        })


@app.route('/api/accounts/add', methods=['POST'])
def add_account():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        is_premium = data.get('is_premium', False)
        
        from account_manager import AccountManager
        manager = AccountManager()
        
        success = manager.add_account(username, password, is_premium=is_premium)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Account {username} added successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Account already exists'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/accounts/remove', methods=['POST'])
def remove_account():
    try:
        data = request.get_json()
        username = data['username']
        
        from account_manager import AccountManager
        manager = AccountManager()
        manager.remove_account(username)
        
        return jsonify({
            'success': True,
            'message': f'Account {username} removed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/accounts/test', methods=['GET'])
def test_accounts():
    try:
        from account_manager import AccountManager
        manager = AccountManager()
        
        # Login all accounts to test
        drivers = manager.login_all_accounts(headless=True)
        successful_logins = len(drivers)
        total_accounts = len(manager.get_active_accounts())
        
        # Close all test drivers
        manager.close_all_drivers()
        
        return jsonify({
            'success': True,
            'total_accounts': total_accounts,
            'successful_logins': successful_logins,
            'message': f'{successful_logins}/{total_accounts} accounts logged in successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'total_accounts': 0,
            'successful_logins': 0
        })
