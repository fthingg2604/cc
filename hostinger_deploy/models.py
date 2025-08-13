from app import db
from datetime import datetime

class ImageUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    processed_filename = db.Column(db.String(255))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    pixel_size = db.Column(db.Integer, default=4)
    start_x = db.Column(db.Integer, default=0)
    start_y = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='uploaded')
    
class BotSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image_upload.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    pixels_placed = db.Column(db.Integer, default=0)
    total_pixels = db.Column(db.Integer)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed, paused
    error_message = db.Column(db.Text)
    
    image = db.relationship('ImageUpload', backref='bot_sessions')

class PixelLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('bot_session.id'), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(7), nullable=False)  # hex color
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.String(255))
    
    session = db.relationship('BotSession', backref='pixel_logs')
