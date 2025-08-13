// WPlace Bot Frontend JavaScript

let currentImageId = null;
let colorPalette = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeUpload();
    loadColorPalette();
    setupEventListeners();
});

// Upload functionality
function initializeUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');

    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

// Handle file upload
function handleFileUpload(file) {
    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
        alert('Định dạng file không hỗ trợ. Vui lòng sử dụng PNG, JPG, hoặc GIF.');
        return;
    }

    // Validate file size (16MB)
    if (file.size > 16 * 1024 * 1024) {
        alert('File quá lớn. Kích thước tối đa là 16MB.');
        return;
    }

    // Show progress
    const progressSection = document.getElementById('upload-progress');
    const progressBar = progressSection.querySelector('.progress-bar');
    progressSection.style.display = 'block';

    // Create FormData
    const formData = new FormData();
    formData.append('file', file);

    // Upload
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentImageId = data.image_id;
            showProcessingSection(data.original_filename);
            
            // Show original image preview
            const reader = new FileReader();
            reader.onload = function(e) {
                const originalPreview = document.getElementById('original-preview');
                if (originalPreview) {
                    originalPreview.src = e.target.result;
                }
            };
            reader.readAsDataURL(file);
            
            progressSection.style.display = 'none';
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        alert('Lỗi upload: ' + error.message);
        progressSection.style.display = 'none';
    });
}

// Show processing section
function showProcessingSection(filename) {
    document.getElementById('processing-section').style.display = 'block';
    document.getElementById('process-btn').disabled = false;
    
    // Update filename display if needed
    console.log('File uploaded:', filename);
}

// Setup event listeners
function setupEventListeners() {
    // Pixel size slider
    const pixelSizeSlider = document.getElementById('pixel-size');
    const pixelSizeValue = document.getElementById('pixel-size-value');
    
    pixelSizeSlider.addEventListener('input', function() {
        pixelSizeValue.textContent = this.value + 'px';
    });

    // Process button
    document.getElementById('process-btn').addEventListener('click', processImage);

    // Bot control button
    const startBotBtn = document.getElementById('start-bot-btn');
    if (startBotBtn) {
        startBotBtn.addEventListener('click', function() {
            window.location.href = `/bot-control/${currentImageId}`;
        });
    }

    // Download button
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadProcessedImage);
    }
}

// Process image
function processImage() {
    if (!currentImageId) {
        alert('Vui lòng upload hình ảnh trước');
        return;
    }

    const processBtn = document.getElementById('process-btn');
    const progressSection = document.getElementById('processing-progress');
    
    // Disable button and show progress
    processBtn.disabled = true;
    processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
    progressSection.style.display = 'block';

    // Get settings
    const pixelSize = parseInt(document.getElementById('pixel-size').value);
    const maxSize = parseInt(document.getElementById('max-size').value);
    const freeColorsOnly = document.getElementById('free-colors-only').checked;

    // Send processing request
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image_id: currentImageId,
            pixel_size: pixelSize,
            max_width: maxSize,
            max_height: maxSize,
            use_free_only: freeColorsOnly
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showPreview(data);
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Processing error:', error);
        alert('Lỗi xử lý: ' + error.message);
    })
    .finally(() => {
        // Reset button
        processBtn.disabled = false;
        processBtn.innerHTML = '<i class="fas fa-magic"></i> Xử Lý Hình Ảnh';
        progressSection.style.display = 'none';
    });
}

// Show preview
function showPreview(data) {
    const previewSection = document.getElementById('preview-section');
    const processedPreview = document.getElementById('processed-preview');
    
    // Show processed image
    processedPreview.src = `/download/${data.processed_filename}`;
    
    // Update stats
    document.getElementById('preview-dimensions').textContent = 
        `${data.dimensions[0]}x${data.dimensions[1]}`;
    document.getElementById('preview-total-pixels').textContent = 
        data.total_pixels.toLocaleString();
    document.getElementById('preview-colors').textContent = 
        `${data.color_stats.unique_colors} màu`;

    // Show section
    previewSection.style.display = 'block';
    
    // Scroll to preview
    previewSection.scrollIntoView({ behavior: 'smooth' });
}

// Load color palette
function loadColorPalette() {
    fetch('/api/color-palette')
    .then(response => response.json())
    .then(data => {
        colorPalette = data;
        displayColorPalette();
    })
    .catch(error => {
        console.error('Error loading color palette:', error);
    });
}

// Display color palette
function displayColorPalette() {
    if (!colorPalette) return;
    
    const paletteContainer = document.getElementById('color-palette');
    if (!paletteContainer) return;
    
    paletteContainer.innerHTML = '';
    
    // Add free colors
    colorPalette.free_colors.forEach(color => {
        const swatch = createColorSwatch(color, 'free');
        paletteContainer.appendChild(swatch);
    });
    
    // Add premium colors
    colorPalette.premium_colors.forEach(color => {
        const swatch = createColorSwatch(color, 'premium');
        paletteContainer.appendChild(swatch);
    });
}

// Create color swatch element
function createColorSwatch(color, type) {
    const swatch = document.createElement('div');
    swatch.className = `color-swatch ${type}`;
    swatch.style.backgroundColor = color.hex;
    swatch.title = `${color.hex} (${type})`;
    
    swatch.addEventListener('click', function() {
        // Copy color to clipboard
        navigator.clipboard.writeText(color.hex).then(() => {
            this.classList.add('success-flash');
            setTimeout(() => {
                this.classList.remove('success-flash');
            }, 500);
        });
    });
    
    return swatch;
}

// Download processed image
function downloadProcessedImage() {
    // This would trigger download of the processed files
    alert('Tính năng download sẽ được thêm vào sau');
}

// Utility functions
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatTime(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

// Add some visual feedback
function showSuccess(message) {
    // Create temporary success alert
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 1050;';
    alert.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 3000);
}

function showError(message) {
    // Create temporary error alert
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 1050;';
    alert.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}
