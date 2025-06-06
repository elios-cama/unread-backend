#!/usr/bin/env python3
"""
Batch processing script to generate book cover images for all covers.
Automatically selects the best matching book template color for each cover.
"""

import os
import glob
from mask_algo import apply_cover_to_book

def batch_process_covers():
    """
    Process all cover images in the covers folder and generate book images
    with color-matched templates from the originals folder.
    """
    # Define paths
    covers_dir = "covers"
    originals_dir = "originals"
    mask_path = "book_cover_mask_large.png"
    output_dir = "generated_books"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all cover files
    cover_extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp"]
    cover_files = []
    for ext in cover_extensions:
        cover_files.extend(glob.glob(os.path.join(covers_dir, ext)))
    
    if not cover_files:
        print(f"No cover files found in {covers_dir}")
        return
    
    print(f"Found {len(cover_files)} cover files to process:")
    for cover_file in cover_files:
        print(f"  - {os.path.basename(cover_file)}")
    print()
    
    # Process each cover
    successful = 0
    failed = 0
    
    for cover_file in cover_files:
        try:
            # Get the base filename without extension
            cover_name = os.path.splitext(os.path.basename(cover_file))[0]
            output_file = os.path.join(output_dir, f"{cover_name}_book.png")
            
            print(f"Processing: {os.path.basename(cover_file)}")
            print("-" * 50)
            
            # Apply the cover to book with color matching
            apply_cover_to_book(
                book_template_path="originals/white.png",  # Default, will be overridden
                user_cover_path=cover_file,
                mask_path=mask_path,
                output_path=output_file,
                originals_dir=originals_dir
            )
            
            successful += 1
            print(f"✅ Successfully generated: {output_file}")
            print()
            
        except Exception as e:
            failed += 1
            print(f"❌ Failed to process {cover_file}: {e}")
            print()
    
    # Summary
    print("=" * 60)
    print(f"BATCH PROCESSING COMPLETE")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output directory: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    batch_process_covers() 