# WPlace Bot

## Overview

WPlace Bot is a web-based automation tool that converts uploaded images into pixel art and automatically places them on wplace.live (a collaborative pixel canvas platform). The application processes user-uploaded images, converts them to fit the wplace.live color palette, and provides bot automation to place pixels on the canvas. Built with Flask and featuring a modern web interface, it includes image processing capabilities, color palette optimization, multi-threading support, and multiple accounts management for accelerated pixel placement.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Interface**: Bootstrap-based responsive design with dark theme support
- **JavaScript**: Vanilla JavaScript for file uploads, drag-and-drop functionality, and real-time bot control
- **File Upload System**: Supports PNG, JPG, GIF, and SVG files with 16MB size limit
- **Color Palette UI**: Interactive color picker showing free and premium colors from wplace.live
- **Coordinate Display**: TL (Top-Left) and Px (Pixel dimensions) format matching wplace.live interface
- **Thread Selection**: User-configurable thread count (1-4 threads) with performance estimates

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite with support for PostgreSQL via environment configuration
- **Image Processing**: PIL (Pillow) for image manipulation and color quantization
- **Bot Engine**: Selenium WebDriver for browser automation and pixel placement
- **File Management**: Organized upload and processing folders with unique filename generation

### Data Models
- **ImageUpload**: Stores uploaded image metadata, dimensions, and processing parameters
- **BotSession**: Tracks automation sessions with status, progress, and error logging
- **PixelLog**: Records individual pixel placement attempts with coordinates and success status

### Color System
- **Palette Management**: 64-color wplace.live palette with free (32) and premium (32) color tiers
- **Color Matching**: Closest color algorithm using RGB distance calculation
- **Palette Restrictions**: Support for both free-only and full palette modes

### Bot Automation
- **Browser Control**: Chrome WebDriver with headless mode support
- **Multi-Threading**: Support for 1-4 concurrent threads for faster pixel placement
- **Multiple Accounts**: Support for multiple wplace.live accounts with automated login and session management
- **Account Management**: JSON-based account storage with premium/free tier tracking
- **Rate Limiting**: Configurable wait times between pixel placements (default 30 seconds)
- **Error Handling**: Comprehensive exception handling for network issues and canvas interactions
- **Session Management**: Persistent session tracking with pause/resume capabilities
- **Thread Management**: Queue-based work distribution across multiple browser instances
- **Speed Optimization**: Multi-account mode provides 2-4x faster pixel placement compared to single account

### File Processing Pipeline
1. **Upload Validation**: File type and size checking
2. **Image Preprocessing**: Format conversion, transparency handling, and RGB normalization
3. **Dimension Optimization**: Aspect ratio preservation with maximum 128x128 pixel output
4. **Color Quantization**: Conversion to wplace.live palette with user-selectable restrictions
5. **Pixel Mapping**: Generation of coordinate-color mappings for bot placement

## External Dependencies

### Core Dependencies
- **Flask**: Web framework for HTTP handling and templating
- **SQLAlchemy**: Database ORM for data persistence
- **Pillow (PIL)**: Image processing and manipulation
- **Selenium**: Browser automation for wplace.live interaction
- **NumPy**: Numerical operations for image processing algorithms

### Frontend Libraries
- **Bootstrap**: UI framework with dark theme support
- **Font Awesome**: Icon library for user interface elements

### Browser Requirements
- **Chrome/Chromium**: Required for Selenium automation
- **ChromeDriver**: WebDriver for programmatic browser control

### External Services
- **wplace.live**: Target platform for pixel placement (collaborative canvas)
- **File System**: Local storage for uploaded images and processed outputs

### Environment Configuration
- **DATABASE_URL**: Database connection string (defaults to SQLite)
- **SESSION_SECRET**: Flask session encryption key
- **Upload Management**: Configurable folder paths for file organization

## Recent Changes & Status

### December 2024 - Multi-Account Feature Complete
- ✅ Added AccountManager for multiple wplace.live accounts
- ✅ Implemented MultiAccountBot with 2-4x speed improvement
- ✅ Web interface supports account management (add/remove/test accounts)
- ✅ API endpoints for account operations (/api/accounts/*)
- ✅ Fixed standalone_bot.py ImageProcessor constructor issue
- ✅ Added Px X, Px Y input options to standalone mode
- ✅ Created deployment package for Hostinger (wplace_bot_hostinger.zip)
- ✅ All Python files configured for CMD execution with proper shebangs
- ✅ Complete deployment documentation and quick start guides

### Deployment Options
1. **Local Development**: `python run_local.py` → http://localhost:5000
2. **Standalone Bot**: `python standalone_bot.py` (with Px X, Px Y inputs)
3. **Hostinger Deploy**: Upload `wplace_bot_hostinger.zip` package
4. **Production**: `python run_production.py` with Gunicorn

### Project Status: Production Ready ✅
- Multi-account automation working (2-4x speed boost)
- Web interface fully functional with account management
- Standalone scripts for CMD usage
- Deployment packages ready for hosting services
- Comprehensive documentation and user guides