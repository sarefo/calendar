#!/usr/bin/env python3
"""
Image Optimizer for Calendar Production
Creates web-optimized thumbnails for HTML preview while preserving full-size images for PDF
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageOps
import argparse
from typing import List, Optional


class ImageOptimizer:
    def __init__(self, web_size: int = 400, web_quality: int = 75):
        """
        Initialize image optimizer
        
        Args:
            web_size: Maximum dimension for web thumbnails (default: 400px)
            web_quality: JPEG quality for web thumbnails (default: 75%)
        """
        self.web_size = web_size
        self.web_quality = web_quality
        
    def create_web_thumbnail(self, source_path: Path, output_path: Path) -> bool:
        """
        Create web-optimized thumbnail from source image
        
        Args:
            source_path: Path to source image
            output_path: Path to save thumbnail
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Open and process image
            with Image.open(source_path) as img:
                # Convert to RGB if necessary (handles CMYK, etc.)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Calculate thumbnail size maintaining aspect ratio
                img.thumbnail((self.web_size, self.web_size), Image.Resampling.LANCZOS)
                
                # Save as optimized JPEG
                img.save(
                    output_path,
                    'JPEG',
                    quality=self.web_quality,
                    optimize=True,
                    progressive=True
                )
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to create thumbnail for {source_path}: {e}")
            return False
    
    def optimize_month_photos(self, year: int, month: int, base_photo_dir: str = "photos") -> dict:
        """
        Create web thumbnails for all photos in a month directory
        
        Args:
            year: Year
            month: Month (1-12)
            base_photo_dir: Base photos directory
            
        Returns:
            Dictionary with optimization results
        """
        source_dir = Path(base_photo_dir) / str(year) / f"{month:02d}"
        web_dir = source_dir / "web"
        
        if not source_dir.exists():
            return {
                "success": False,
                "reason": f"Source directory not found: {source_dir}",
                "processed": 0,
                "failed": 0
            }
        
        # Find all JPEG files
        jpg_files = sorted([f for f in source_dir.iterdir() 
                           if f.suffix.lower() == '.jpg' and f.is_file()])
        
        if not jpg_files:
            return {
                "success": False,
                "reason": f"No JPEG files found in {source_dir}",
                "processed": 0,
                "failed": 0
            }
        
        processed = 0
        failed = 0
        
        print(f"📸 Optimizing images for {year}-{month:02d}...")
        
        for jpg_file in jpg_files:
            web_path = web_dir / jpg_file.name
            
            # Skip if web thumbnail already exists and is newer than source
            if (web_path.exists() and 
                web_path.stat().st_mtime > jpg_file.stat().st_mtime):
                processed += 1
                continue
            
            if self.create_web_thumbnail(jpg_file, web_path):
                processed += 1
                print(f"✅ Created thumbnail: {web_path.name}")
            else:
                failed += 1
        
        return {
            "success": failed == 0,
            "reason": f"Processed {processed}, failed {failed}" if failed > 0 else None,
            "processed": processed,
            "failed": failed,
            "web_dir": str(web_dir)
        }
    
    def optimize_year_photos(self, year: int, months: List[int] = None, 
                           base_photo_dir: str = "photos") -> dict:
        """
        Create web thumbnails for all photos in specified months of a year
        
        Args:
            year: Year
            months: List of months to process (None = all months 1-12)
            base_photo_dir: Base photos directory
            
        Returns:
            Dictionary with optimization results
        """
        if not months:
            months = list(range(1, 13))
        
        total_processed = 0
        total_failed = 0
        successful_months = []
        failed_months = []
        
        print(f"🚀 Starting image optimization for {year}")
        print(f"Target size: {self.web_size}px, Quality: {self.web_quality}%")
        
        for month in months:
            result = self.optimize_month_photos(year, month, base_photo_dir)
            
            total_processed += result["processed"]
            total_failed += result["failed"]
            
            if result["success"]:
                successful_months.append(month)
            else:
                failed_months.append(month)
                print(f"❌ Failed month {month}: {result['reason']}")
        
        return {
            "success": len(failed_months) == 0,
            "year": year,
            "total_processed": total_processed,
            "total_failed": total_failed,
            "successful_months": successful_months,
            "failed_months": failed_months
        }
    
    def get_web_thumbnail_path(self, original_path: str) -> str:
        """
        Get the web thumbnail path for an original image path
        
        Args:
            original_path: Path to original image
            
        Returns:
            Path to corresponding web thumbnail
        """
        original = Path(original_path)
        
        # If it's already a web path, return as-is
        if original.parent.name == "web":
            return str(original)
        
        # Create web subdirectory path
        web_path = original.parent / "web" / original.name
        return str(web_path)


def main():
    parser = argparse.ArgumentParser(description="Optimize calendar images for web viewing")
    parser.add_argument('--year', type=int, required=True, help="Year to optimize")
    parser.add_argument('--month', type=int, help="Specific month to optimize (1-12)")
    parser.add_argument('--months', help="Comma-separated list of months")
    parser.add_argument('--photos', default="photos", help="Base photos directory")
    parser.add_argument('--web-size', type=int, default=400, help="Web thumbnail size (default: 400px)")
    parser.add_argument('--web-quality', type=int, default=75, help="Web JPEG quality (default: 75%)")
    parser.add_argument('--force', action='store_true', help="Force regeneration of existing thumbnails")
    
    args = parser.parse_args()
    
    # Initialize optimizer
    optimizer = ImageOptimizer(args.web_size, args.web_quality)
    
    try:
        if args.month:
            # Single month
            result = optimizer.optimize_month_photos(args.year, args.month, args.photos)
            if result["success"]:
                print(f"✅ Successfully optimized {result['processed']} images for {args.year}-{args.month:02d}")
            else:
                print(f"❌ Optimization failed: {result['reason']}")
                return 1
                
        elif args.months:
            # Specific months
            months = [int(m.strip()) for m in args.months.split(',')]
            result = optimizer.optimize_year_photos(args.year, months, args.photos)
            
            print(f"\n📊 Optimization Summary for {args.year}:")
            print(f"✅ Processed: {result['total_processed']} images")
            print(f"✅ Successful months: {len(result['successful_months'])}")
            if result['failed_months']:
                print(f"❌ Failed months: {result['failed_months']}")
                return 1
                
        else:
            # Full year
            result = optimizer.optimize_year_photos(args.year, None, args.photos)
            
            print(f"\n📊 Optimization Summary for {args.year}:")
            print(f"✅ Processed: {result['total_processed']} images")
            print(f"✅ Successful months: {len(result['successful_months'])}")
            if result['failed_months']:
                print(f"❌ Failed months: {result['failed_months']}")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Check if PIL is available
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("❌ PIL (Pillow) is required for image optimization")
        print("Install it with: pip install Pillow")
        sys.exit(1)
    
    sys.exit(main())