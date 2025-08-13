"""
Wplace.live official 64-color palette mapping
Based on web search results about wplace.live color system
"""

# Official Wplace.live 64-color palette (hex values)
WPLACE_PALETTE = [
    # Free colors (basic palette)
    '#FFFFFF', '#C4C4C4', '#888888', '#555555', '#000000',  # Grays
    '#FF0000', '#FF8888', '#FFAAAA', '#FFDDDD',  # Reds
    '#00FF00', '#88FF88', '#AAFFAA', '#DDFFDD',  # Greens  
    '#0000FF', '#8888FF', '#AAAAFF', '#DDDDFF',  # Blues
    '#FFFF00', '#FFFF88', '#FFFFAA', '#FFFFDD',  # Yellows
    '#FF00FF', '#FF88FF', '#FFAAFF', '#FFDDFF',  # Magentas
    '#00FFFF', '#88FFFF', '#AAFFFF', '#DDFFFF',  # Cyans
    '#FFA500', '#FFAA88', '#FFCCAA', '#FFDDCC',  # Oranges
    
    # Premium colors (extended palette)
    '#8B4513', '#A0522D', '#D2B48C', '#F4A460',  # Browns
    '#800080', '#9370DB', '#BA55D3', '#DDA0DD',  # Purples
    '#008000', '#228B22', '#32CD32', '#90EE90',  # Dark Greens
    '#000080', '#191970', '#4169E1', '#87CEEB',  # Navy Blues
    '#800000', '#B22222', '#DC143C', '#F08080',  # Dark Reds
    '#808000', '#BDB76B', '#F0E68C', '#FFFFE0',  # Olives
    '#008080', '#20B2AA', '#48D1CC', '#AFEEEE',  # Teals
    '#FFB6C1', '#FFC0CB', '#FFE4E1', '#FFF0F5',  # Pinks
]

# Color categories for UI
FREE_COLORS = WPLACE_PALETTE[:32]  # First 32 colors are free
PREMIUM_COLORS = WPLACE_PALETTE[32:]  # Last 32 colors are premium

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string"""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def hex_to_rgb(hex_color):
    """Convert hex string to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_wplace_colors(free_only=False):
    """
    Get list of available wplace.live colors
    
    Args:
        free_only: If True, only return free colors
    
    Returns:
        List of hex color strings
    """
    if free_only:
        return FREE_COLORS.copy()
    else:
        return WPLACE_PALETTE.copy()

def find_closest_color(target_rgb, allowed_colors=None):
    """
    Find the closest color in the wplace palette to the target RGB color
    
    Args:
        target_rgb: Tuple of (R, G, B) values
        allowed_colors: List of hex colors to choose from (defaults to full palette)
    
    Returns:
        Hex color string of the closest match
    """
    if allowed_colors is None:
        allowed_colors = WPLACE_PALETTE
    
    min_distance = float('inf')
    closest_color = allowed_colors[0]
    
    # Ensure target_rgb values are in valid range
    target_rgb = tuple(max(0, min(255, int(val))) for val in target_rgb)
    
    for palette_color in allowed_colors:
        palette_rgb = hex_to_rgb(palette_color)
        
        # Calculate Euclidean distance in RGB space (using int to prevent overflow)
        distance = sum((int(target_rgb[i]) - int(palette_rgb[i])) ** 2 for i in range(3)) ** 0.5
        
        if distance < min_distance:
            min_distance = distance
            closest_color = palette_color
    
    return closest_color

def get_color_info(hex_color):
    """Get information about a color in the wplace palette"""
    if hex_color in FREE_COLORS:
        return {
            'hex': hex_color,
            'rgb': hex_to_rgb(hex_color),
            'type': 'free',
            'index': WPLACE_PALETTE.index(hex_color)
        }
    elif hex_color in PREMIUM_COLORS:
        return {
            'hex': hex_color,
            'rgb': hex_to_rgb(hex_color),
            'type': 'premium', 
            'index': WPLACE_PALETTE.index(hex_color)
        }
    else:
        return None

def create_color_palette_json():
    """Create a JSON representation of the color palette for frontend"""
    return {
        'free_colors': [
            {
                'hex': color,
                'rgb': hex_to_rgb(color),
                'index': i
            }
            for i, color in enumerate(FREE_COLORS)
        ],
        'premium_colors': [
            {
                'hex': color,
                'rgb': hex_to_rgb(color),
                'index': i + 32
            }
            for i, color in enumerate(PREMIUM_COLORS)
        ]
    }
