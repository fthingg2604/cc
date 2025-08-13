import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
from color_palette import find_closest_color, WPLACE_PALETTE, FREE_COLORS, PREMIUM_COLORS

class ImageProcessor:
    def __init__(self, upload_folder, processed_folder):
        self.upload_folder = upload_folder
        self.processed_folder = processed_folder
    
    def process_image(self, filename, pixel_size=4, allowed_colors=None, max_width=128, max_height=128):
        """
        Process an uploaded image into wplace-compatible pixel art
        
        Args:
            filename: Name of the uploaded image file
            pixel_size: Size of each pixel in the output (1-128)
            allowed_colors: List of allowed hex colors (None for all colors)
            max_width: Maximum width in pixels for the output
            max_height: Maximum height in pixels for the output
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Load and prepare the image
            input_path = os.path.join(self.upload_folder, filename)
            image = Image.open(input_path)
            
            # Convert to RGB if necessary
            if image.mode in ['RGBA', 'P']:
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image to fit within max dimensions while maintaining aspect ratio
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height
            
            if original_width > max_width or original_height > max_height:
                if aspect_ratio > 1:  # Wider than tall
                    new_width = min(max_width, original_width)
                    new_height = int(new_width / aspect_ratio)
                else:  # Taller than wide
                    new_height = min(max_height, original_height)
                    new_width = int(new_height * aspect_ratio)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Get pixel data
            pixel_width, pixel_height = image.size
            pixels = np.array(image)
            
            # Map colors to wplace palette
            if allowed_colors is None:
                allowed_colors = WPLACE_PALETTE
            
            color_map = []
            pixel_data = []
            
            for y in range(pixel_height):
                row = []
                for x in range(pixel_width):
                    # Safely extract RGB values
                    if len(pixels.shape) == 3:
                        rgb = tuple(int(val) for val in pixels[y, x])
                    else:
                        # Grayscale image
                        gray_val = int(pixels[y, x])
                        rgb = (gray_val, gray_val, gray_val)
                    
                    # Ensure RGB values are in valid range
                    rgb = tuple(max(0, min(255, val)) for val in rgb)
                    
                    closest_color = find_closest_color(rgb, allowed_colors)
                    row.append(closest_color)
                    
                    # Store pixel data for bot script
                    pixel_data.append({
                        'x': x,
                        'y': y,
                        'color': closest_color,
                        'original_rgb': rgb
                    })
                color_map.append(row)
            
            # Create the processed image (scaled up by pixel_size)
            output_width = pixel_width * pixel_size
            output_height = pixel_height * pixel_size
            output_image = Image.new('RGB', (output_width, output_height))
            draw = ImageDraw.Draw(output_image)
            
            for y in range(pixel_height):
                for x in range(pixel_width):
                    color = color_map[y][x]
                    # Draw pixel block
                    x1 = x * pixel_size
                    y1 = y * pixel_size
                    x2 = x1 + pixel_size
                    y2 = y1 + pixel_size
                    draw.rectangle([x1, y1, x2-1, y2-1], fill=color)
            
            # Save processed image
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}_processed_{pixel_size}px.png"
            output_path = os.path.join(self.processed_folder, output_filename)
            output_image.save(output_path)
            
            # Create pixel data JSON
            json_filename = f"{base_name}_pixels_{pixel_size}px.json"
            json_path = os.path.join(self.processed_folder, json_filename)
            
            pixel_json = {
                'original_filename': filename,
                'dimensions': {
                    'width': pixel_width,
                    'height': pixel_height,
                    'total_pixels': len(pixel_data)
                },
                'pixel_size': pixel_size,
                'allowed_colors': allowed_colors,
                'color_stats': self._get_color_stats(pixel_data),
                'pixels': pixel_data
            }
            
            with open(json_path, 'w') as f:
                json.dump(pixel_json, f, indent=2)
            
            return {
                'success': True,
                'original_size': (original_width, original_height),
                'processed_size': (pixel_width, pixel_height),
                'output_size': (output_width, output_height),
                'output_filename': output_filename,
                'json_filename': json_filename,
                'total_pixels': len(pixel_data),
                'color_stats': pixel_json['color_stats']
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Image processing error: {e}")
            print(f"Full traceback: {error_details}")
            return {
                'success': False,
                'error': str(e),
                'details': error_details
            }
    
    def _get_color_stats(self, pixel_data):
        """Get statistics about colors used in the pixel art"""
        color_counts = {}
        free_count = 0
        premium_count = 0
        
        for pixel in pixel_data:
            color = pixel['color']
            color_counts[color] = color_counts.get(color, 0) + 1
            
            if color in FREE_COLORS:
                free_count += 1
            elif color in PREMIUM_COLORS:
                premium_count += 1
        
        return {
            'unique_colors': len(color_counts),
            'color_breakdown': color_counts,
            'free_pixels': free_count,
            'premium_pixels': premium_count,
            'total_pixels': len(pixel_data)
        }
    
    def create_preview_grid(self, json_filename, grid_size=20):
        """Create a small preview grid showing the pixel art"""
        try:
            json_path = os.path.join(self.processed_folder, json_filename)
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            width = data['dimensions']['width']
            height = data['dimensions']['height']
            
            # Create small preview
            preview_image = Image.new('RGB', (width * grid_size, height * grid_size))
            draw = ImageDraw.Draw(preview_image)
            
            # Create color map
            color_map = {}
            for pixel in data['pixels']:
                color_map[(pixel['x'], pixel['y'])] = pixel['color']
            
            # Draw preview grid
            for y in range(height):
                for x in range(width):
                    color = color_map.get((x, y), '#FFFFFF')
                    x1 = x * grid_size
                    y1 = y * grid_size
                    x2 = x1 + grid_size
                    y2 = y1 + grid_size
                    draw.rectangle([x1, y1, x2-1, y2-1], fill=color)
                    # Draw grid lines
                    draw.rectangle([x1, y1, x2-1, y2-1], outline='#CCCCCC')
            
            # Save preview
            base_name = os.path.splitext(json_filename)[0]
            preview_filename = f"{base_name}_preview.png"
            preview_path = os.path.join(self.processed_folder, preview_filename)
            preview_image.save(preview_path)
            
            return preview_filename
            
        except Exception as e:
            print(f"Error creating preview: {e}")
            return None
