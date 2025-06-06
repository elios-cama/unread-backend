from PIL import Image
import math
import os
from collections import Counter

def get_dominant_color(image):
    """
    Extract the dominant color from an image by analyzing pixel frequencies.
    Returns RGB tuple of the most common color.
    """
    # Resize image for faster processing
    small_image = image.resize((50, 50))
    pixels = list(small_image.getdata())
    
    # Remove very light/white pixels (background) from consideration
    filtered_pixels = [pixel for pixel in pixels if sum(pixel[:3]) < 700]
    
    if not filtered_pixels:
        # If all pixels are light, use all pixels
        filtered_pixels = pixels
    
    # Count color frequencies
    color_count = Counter(filtered_pixels)
    dominant_color = color_count.most_common(1)[0][0]
    
    return dominant_color[:3]  # Return RGB only

def color_distance(color1, color2):
    """Calculate Euclidean distance between two RGB colors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))

def find_closest_book_template(cover_color, originals_dir):
    """
    Find the closest matching book template based on cover's dominant color.
    """
    # Define representative colors for each book template
    template_colors = {
        'black.png': (30, 30, 30),
        'blue.png': (70, 130, 180),
        'green.png': (60, 120, 60),
        'red.png': (180, 60, 60),
        'grey.png': (120, 120, 120),
        'white.png': (240, 240, 240)
    }
    
    # Find the closest color match
    min_distance = float('inf')
    best_template = 'white.png'  # Default fallback
    
    for template, template_color in template_colors.items():
        distance = color_distance(cover_color, template_color)
        if distance < min_distance:
            min_distance = distance
            best_template = template
    
    template_path = os.path.join(originals_dir, best_template)
    return template_path, best_template

def apply_cover_to_book(book_template_path, user_cover_path, mask_path, output_path, originals_dir=None):
    """
    Applies a user-provided book cover onto the book template.
    Uses manual perspective mapping and color-matched book templates.
    """
    try:
        # 1. Load the cover image first to analyze its color
        user_cover = Image.open(user_cover_path)
        
        # Handle transparency issues - ensure cover has solid colors
        if user_cover.mode == 'RGBA':
            # If image has alpha channel, composite it with white background
            white_bg = Image.new('RGB', user_cover.size, (255, 255, 255))
            user_cover = Image.alpha_composite(white_bg.convert('RGBA'), user_cover)
        
        # Convert to RGBA for processing
        user_cover = user_cover.convert("RGBA")
        
        # 2. Extract dominant color and find matching book template
        if originals_dir and os.path.exists(originals_dir):
            dominant_color = get_dominant_color(user_cover)
            book_template_path, template_name = find_closest_book_template(dominant_color, originals_dir)
            print(f"Dominant color: RGB{dominant_color}")
            print(f"Selected book template: {template_name}")
        
        # 3. Load the selected book template and mask
        book_template = Image.open(book_template_path).convert("RGBA")
        cover_mask = Image.open(mask_path).convert("L")

        # 4. Get dimensions
        cover_width, cover_height = user_cover.size
        template_width, template_height = book_template.size
        print(f"Cover dimensions: {cover_width} x {cover_height}")
        print(f"Template dimensions: {template_width} x {template_height}")

        # 5. Define the quadrilateral points where the cover should appear
        # DIRECT SPECIFICATION of coordinates for precise control
        
        # Book cover area coordinates - manually measured for perfect alignment
        quad_points = [
            (614, 374),     # Top-left
            (1200, 286),    # Top-right  
            (1200, 1860),   # Bottom-right - made 130 pixels lower than bottom-left
            (614, 1730)     # Bottom-left
        ]
        
        # Verify that bottom-right is lower than bottom-left (higher y-value means lower on screen)
        tl, tr, br, bl = quad_points
        print(f"Top: left y={tl[1]}, right y={tr[1]}, difference={tr[1]-tl[1]} (negative means right is higher)")
        print(f"Bottom: left y={bl[1]}, right y={br[1]}, difference={br[1]-bl[1]} (positive means right is lower)")
        print(f"Bottom-right IS lower than bottom-left: {br[1] > bl[1]}")
        
        print(f"Using quadrilateral: {quad_points}")

        # 6. Manual approach: Create the transformation step by step
        def map_point_to_quad(x_ratio, y_ratio, quad):
            """
            Map a point from unit square [0,1] x [0,1] to the quadrilateral
            x_ratio, y_ratio are between 0 and 1
            Expanded slightly to eliminate border gaps
            """
            tl, tr, br, bl = quad
            
            # Expand the mapping slightly beyond the quad boundaries
            # This helps eliminate transparent borders
            expand_factor = 0.02  # Expand by 2% on each side
            
            # Adjust ratios to map from expanded area
            expanded_x = (x_ratio - expand_factor) / (1 - 2 * expand_factor)
            expanded_y = (y_ratio - expand_factor) / (1 - 2 * expand_factor)
            
            # Clamp to valid range
            expanded_x = max(0, min(1, expanded_x))
            expanded_y = max(0, min(1, expanded_y))
            
            # Bilinear interpolation with expanded coordinates
            # First interpolate along top and bottom edges
            top_x = tl[0] + expanded_x * (tr[0] - tl[0])
            top_y = tl[1] + expanded_x * (tr[1] - tl[1])
            
            # Bottom edge should use the same parameter for interpolation
            # Using expanded_x here to match how we're interpolating along the top edge
            # This ensures both top and bottom edges are interpolated consistently
            bottom_x = bl[0] + expanded_x * (br[0] - bl[0])
            bottom_y = bl[1] + expanded_x * (br[1] - bl[1])
            
            # Then interpolate between top and bottom
            # This is where vertical interpolation occurs
            # For each horizontal position, we interpolate vertically between
            # the top and bottom edges
            final_x = top_x + expanded_y * (bottom_x - top_x)
            final_y = top_y + expanded_y * (bottom_y - top_y)
            
            return (int(final_x), int(final_y))

        # 7. Create the transformed image
        transformed_cover = Image.new('RGBA', book_template.size, (0, 0, 0, 0))
        cover_pixels = user_cover.load()
        transformed_pixels = transformed_cover.load()
        
        print("Starting manual transformation...")
        
        # Sample the cover image and map to quadrilateral
        # Use higher density for better quality and coverage
        sample_density = 1  # Sample every pixel for best quality
        
        for src_y in range(0, cover_height, sample_density):
            for src_x in range(0, cover_width, sample_density):
                # Calculate ratios (0 to 1)
                x_ratio = src_x / cover_width
                y_ratio = src_y / cover_height
                
                # Map to destination quadrilateral
                dest_x, dest_y = map_point_to_quad(x_ratio, y_ratio, quad_points)
                
                # Check bounds
                if 0 <= dest_x < template_width and 0 <= dest_y < template_height:
                    # Get source pixel and ensure it's opaque
                    src_pixel = cover_pixels[src_x, src_y]
                    
                    # Ensure pixel is fully opaque (no transparency)
                    if len(src_pixel) == 4:  # RGBA
                        src_pixel = (src_pixel[0], src_pixel[1], src_pixel[2], 255)
                    
                    # Fill a larger area around the destination point for better coverage
                    fill_radius = max(1, sample_density)
                    for dy in range(-fill_radius, fill_radius + 1):
                        for dx in range(-fill_radius, fill_radius + 1):
                            final_x = dest_x + dx
                            final_y = dest_y + dy
                            if 0 <= final_x < template_width and 0 <= final_y < template_height:
                                transformed_pixels[final_x, final_y] = src_pixel
        
        print("Manual transformation complete!")

        # 8. Apply smoothing to reduce pixelation
        # Resize up and down to smooth the result
        temp_size = (template_width * 2, template_height * 2)
        smoothed = transformed_cover.resize(temp_size, Image.LANCZOS)
        transformed_cover = smoothed.resize((template_width, template_height), Image.LANCZOS)

        # 9. Apply the mask and create final result
        if cover_mask.size != book_template.size:
            cover_mask = cover_mask.resize(book_template.size, Image.LANCZOS)

        result = book_template.copy()
        result.paste(transformed_cover, (0, 0), cover_mask)

        # 10. Save the final result
        result.save(output_path)
        print(f"Book cover successfully applied and saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

# Example usage
if __name__ == "__main__":
    apply_cover_to_book(
        "originals/white.png",  # Default template, will be overridden by color matching
        "covers/tesson.jpg", 
        "book_cover_mask_large.png",
        "book_with_custom_cover.png",
        "originals"  # Directory with colored book templates
    )