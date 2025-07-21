#!/usr/bin/env python3
"""
Photoshop Crop Specifications Generator
Generates precise cropping specifications for calendar photos

Usage:
    python photoshop_specs.py --input-dir /path/to/photos --output specs.txt
    python photoshop_specs.py --analyze-batch /path/to/photos

Output specifications for Photoshop batch processing:
- Square format: 2400×2400px at 300 DPI
- Consistent file naming: YYYY-MM-DD.jpg
- Color profile guidance: sRGB → CMYK conversion
"""

import os
import argparse
from pathlib import Path
from datetime import datetime
import json

class PhotoshopSpecs:
    def __init__(self):
        self.target_size = 2400  # pixels (square)
        self.dpi = 300
        self.color_profile = "sRGB IEC61966-2.1"
        self.output_profile = "CMYK (ISO Coated v2 300%)"
        
    def generate_crop_specs(self, input_dir, output_file):
        """Generate cropping specifications for all photos in directory"""
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
            
        specs = {
            "project": "A3 Landscape Photo Calendar",
            "specifications": {
                "target_size": f"{self.target_size}×{self.target_size}px",
                "resolution": f"{self.dpi} DPI",
                "format": "JPEG",
                "quality": "Maximum (12)",
                "color_profile": self.color_profile,
                "output_profile": self.output_profile,
                "naming_convention": "YYYY-MM-DD.jpg"
            },
            "batch_processing": {
                "action": "Crop to Square",
                "steps": [
                    "1. Open image in Photoshop",
                    "2. Use Crop Tool (C) with 1:1 aspect ratio",
                    "3. Position crop to focus on main subject",
                    "4. Apply crop",
                    "5. Image → Image Size → Set to 2400×2400px at 300 DPI",
                    "6. Edit → Convert to Profile → ISO Coated v2 300% (CMYK)",
                    "7. File → Export → Export As → JPEG (Quality: 12)",
                    "8. Save with date-based filename"
                ]
            },
            "files": []
        }
        
        # Scan for image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.raw', '.cr2', '.nef'}
        image_files = []
        
        for file_path in input_path.rglob('*'):
            if file_path.suffix.lower() in image_extensions:
                image_files.append(file_path)
        
        # Generate specs for each file
        for i, file_path in enumerate(sorted(image_files)):
            relative_path = file_path.relative_to(input_path)
            suggested_date = self._suggest_date_from_filename(file_path.name)
            
            file_spec = {
                "original_file": str(relative_path),
                "suggested_filename": f"{suggested_date}.jpg" if suggested_date else f"photo_{i+1:03d}.jpg",
                "crop_instructions": "Focus on main subject, maintain square aspect ratio",
                "priority": "high" if "macro" in file_path.name.lower() else "medium"
            }
            specs["files"].append(file_spec)
        
        # Write specifications
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(specs, f, indent=2, ensure_ascii=False)
        
        # Also create a simple text version for easy reference
        text_file = output_file.replace('.json', '.txt')
        self._write_text_specs(specs, text_file)
        
        return len(image_files)
    
    def _suggest_date_from_filename(self, filename):
        """Try to extract date from filename or return None"""
        try:
            # Try common date patterns in filenames
            import re
            
            # Pattern: YYYY-MM-DD or YYYY_MM_DD or YYYYMMDD
            date_patterns = [
                r'(\d{4})[_-]?(\d{2})[_-]?(\d{2})',
                r'(\d{2})[_-](\d{2})[_-](\d{4})',  # DD-MM-YYYY
                r'(\d{2})[_-](\d{2})[_-](\d{2})'   # DD-MM-YY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, filename)
                if match:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY-MM-DD format
                        return f"{groups[0]}-{groups[1]}-{groups[2]}"
                    elif len(groups[2]) == 4:  # DD-MM-YYYY format
                        return f"{groups[2]}-{groups[1]}-{groups[0]}"
                    else:  # DD-MM-YY format (assume 20XX)
                        year = f"20{groups[2]}" if int(groups[2]) < 50 else f"19{groups[2]}"
                        return f"{year}-{groups[1]}-{groups[0]}"
        except:
            pass
        return None
    
    def _write_text_specs(self, specs, output_file):
        """Write human-readable text specifications"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== PHOTOSHOP BATCH PROCESSING SPECIFICATIONS ===\n\n")
            f.write(f"Project: {specs['project']}\n")
            f.write(f"Target Size: {specs['specifications']['target_size']}\n")
            f.write(f"Resolution: {specs['specifications']['resolution']}\n")
            f.write(f"Color Profile: {specs['specifications']['color_profile']}\n")
            f.write(f"Output Profile: {specs['specifications']['output_profile']}\n\n")
            
            f.write("BATCH PROCESSING STEPS:\n")
            for step in specs['batch_processing']['steps']:
                f.write(f"  {step}\n")
            f.write("\n")
            
            f.write("FILES TO PROCESS:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Original File':<40} {'Suggested Name':<20} {'Priority':<10}\n")
            f.write("-" * 80 + "\n")
            
            for file_spec in specs['files']:
                f.write(f"{file_spec['original_file']:<40} "
                       f"{file_spec['suggested_filename']:<20} "
                       f"{file_spec['priority']:<10}\n")
            
            f.write(f"\nTotal files: {len(specs['files'])}\n")

def main():
    parser = argparse.ArgumentParser(description="Generate Photoshop crop specifications for calendar photos")
    parser.add_argument('--input-dir', required=True, help="Directory containing photos to process")
    parser.add_argument('--output', default="photoshop_specs.json", help="Output file for specifications")
    parser.add_argument('--analyze-batch', action='store_true', help="Analyze batch and provide summary")
    
    args = parser.parse_args()
    
    generator = PhotoshopSpecs()
    
    try:
        file_count = generator.generate_crop_specs(args.input_dir, args.output)
        
        print(f"✓ Generated specifications for {file_count} files")
        print(f"✓ JSON specs saved to: {args.output}")
        print(f"✓ Text specs saved to: {args.output.replace('.json', '.txt')}")
        print("\nPhotoshop Batch Processing Ready!")
        print("Follow the steps in the text file for consistent results.")
        
        if args.analyze_batch:
            print(f"\nBatch Analysis:")
            print(f"- Target size: 2400×2400px at 300 DPI")
            print(f"- Output size: ~8×8 inches (perfect for A3 calendar grid)")
            print(f"- File size: ~2-5MB per processed image")
            print(f"- Total processing time: ~{file_count * 2} minutes (estimated)")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())