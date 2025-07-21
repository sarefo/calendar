#!/usr/bin/env python3
"""
QR Code Generator for Calendar
Generates QR codes linking to GitHub.io photo stories site

Requires: qrcode library
Install with: pip install qrcode[pil]
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
# Optional styled imports - will fallback to basic if not available
try:
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
    STYLED_AVAILABLE = True
except ImportError:
    STYLED_AVAILABLE = False

try:
    from qrcode.image.styles.colorfills import SquareGradientColorFill
    GRADIENT_AVAILABLE = True
except ImportError:
    GRADIENT_AVAILABLE = False
import argparse
import json
from pathlib import Path

class QRGenerator:
    def __init__(self):
        self.default_base_url = "https://sarefo.github.io/calendar-stories"
        
    def generate_qr_code(self, url: str, output_path: str, size: int = 400, 
                        border: int = 2, style: str = "default") -> str:
        """
        Generate QR code for given URL
        
        Args:
            url: URL to encode
            output_path: Path to save QR code image
            size: Size in pixels (will be square)
            border: Border size in modules
            style: Style variant (default, rounded, gradient)
            
        Returns:
            Path to generated QR code image
        """
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,  # Size of QR code (1 is smallest)
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
            box_size=size // 25,  # Size of each box in pixels
            border=border,
        )
        
        qr.add_data(url)
        qr.make(fit=True)
        
        # Generate image based on style
        if style == "rounded" and STYLED_AVAILABLE:
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                fill_color="#2C3E50",
                back_color="white"
            )
        elif style == "gradient" and GRADIENT_AVAILABLE:
            img = qr.make_image(
                image_factory=StyledPilImage,
                color_mask=SquareGradientColorFill(
                    back_color=(255, 255, 255),
                    center_color=(44, 62, 80),    # #2C3E50
                    edge_color=(52, 73, 94)       # #34495E
                )
            )
        else:
            # Default black and white (works with all qrcode versions)
            img = qr.make_image(fill_color="#2C3E50", back_color="white")
        
        # Resize to exact size
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Save image
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_file, "PNG", optimize=True)
        
        return str(output_file)
    
    def generate_calendar_qr(self, year: int, month: int, base_url: str = None, 
                           output_dir: str = "output/qr", style: str = "default") -> str:
        """Generate QR code for specific calendar month"""
        
        if not base_url:
            base_url = self.default_base_url
            
        # Construct URL for specific month
        url = f"{base_url}/?year={year}&month={month:02d}"
        
        # Generate filename
        filename = f"qr-{year}-{month:02d}.png"
        output_path = Path(output_dir) / filename
        
        return self.generate_qr_code(url, output_path, size=300, style=style)
    
    def generate_year_qr_codes(self, year: int, base_url: str = None, 
                              output_dir: str = "output/qr", style: str = "default") -> list:
        """Generate QR codes for all months in a year"""
        
        generated_files = []
        
        for month in range(1, 13):
            qr_file = self.generate_calendar_qr(year, month, base_url, output_dir, style)
            generated_files.append(qr_file)
            print(f"✓ Generated QR code: {qr_file}")
        
        return generated_files
    
    def create_branded_qr(self, url: str, output_path: str, 
                         title: str = "Photo Stories", subtitle: str = None,
                         size: int = 400) -> str:
        """
        Create QR code with branding text
        
        Args:
            url: URL to encode
            output_path: Output file path
            title: Main title text
            subtitle: Optional subtitle text
            size: Total image size
            
        Returns:
            Path to generated image
        """
        
        # Generate base QR code (smaller to make room for text)
        qr_size = int(size * 0.7)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=qr_size // 25,
            border=2,
        )
        
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="#2C3E50", back_color="white")
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        # Create final image with text
        final_img = Image.new('RGB', (size, size), 'white')
        
        # Paste QR code centered horizontally, towards top
        qr_x = (size - qr_size) // 2
        qr_y = int(size * 0.05)
        final_img.paste(qr_img, (qr_x, qr_y))
        
        # Add text below QR code
        draw = ImageDraw.Draw(final_img)
        
        try:
            # Try to use a nice font
            title_font = ImageFont.truetype("arial.ttf", size=int(size * 0.08))
            subtitle_font = ImageFont.truetype("arial.ttf", size=int(size * 0.05))
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw title
        text_y = qr_y + qr_size + int(size * 0.05)
        
        # Get text dimensions for centering
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (size - title_width) // 2
        
        draw.text((title_x, text_y), title, fill="#2C3E50", font=title_font)
        
        # Draw subtitle if provided
        if subtitle:
            subtitle_y = text_y + int(size * 0.1)
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (size - subtitle_width) // 2
            
            draw.text((subtitle_x, subtitle_y), subtitle, fill="#7F8C8D", font=subtitle_font)
        
        # Save image
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        final_img.save(output_file, "PNG", optimize=True)
        
        return str(output_file)
    
    def generate_svg_qr(self, url: str, output_path: str, size: int = 15) -> str:
        """Generate SVG QR code for print scalability"""
        
        import qrcode.image.svg
        
        factory = qrcode.image.svg.SvgPathImage
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=size,
            border=2,
            image_factory=factory
        )
        
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#2C3E50", back_color="white")
        
        # Save SVG
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            img.save(f)
        
        return str(output_file)

def main():
    parser = argparse.ArgumentParser(description="Generate QR codes for calendar project")
    parser.add_argument('--url', help="URL to encode")
    parser.add_argument('--year', type=int, help="Generate QR codes for specific year")
    parser.add_argument('--month', type=int, help="Generate QR code for specific month")
    parser.add_argument('--base-url', default="https://sarefo.github.io/calendar-stories", 
                       help="Base URL for calendar stories site")
    parser.add_argument('--output', default="output/qr", help="Output directory")
    parser.add_argument('--style', choices=['default', 'rounded', 'gradient'], 
                       default='default', help="QR code style")
    parser.add_argument('--size', type=int, default=400, help="QR code size in pixels")
    parser.add_argument('--branded', action='store_true', help="Create branded QR with text")
    parser.add_argument('--svg', action='store_true', help="Generate SVG format for print")
    parser.add_argument('--title', default="Photo Stories", help="Title for branded QR")
    parser.add_argument('--subtitle', help="Subtitle for branded QR")
    
    args = parser.parse_args()
    
    generator = QRGenerator()
    
    try:
        if args.url:
            # Generate QR for specific URL
            if args.branded:
                output_path = args.output if args.output.endswith('.png') else f"{args.output}/branded_qr.png"
                result = generator.create_branded_qr(
                    args.url, output_path, args.title, args.subtitle, args.size
                )
            elif args.svg:
                output_path = args.output if args.output.endswith('.svg') else f"{args.output}/qr.svg"
                result = generator.generate_svg_qr(args.url, output_path)
            else:
                output_path = args.output if args.output.endswith('.png') else f"{args.output}/qr.png"
                result = generator.generate_qr_code(args.url, output_path, args.size, style=args.style)
            
            print(f"✓ Generated QR code: {result}")
            
        elif args.year:
            if args.month:
                # Generate for specific month
                result = generator.generate_calendar_qr(
                    args.year, args.month, args.base_url, args.output, args.style
                )
                print(f"✓ Generated QR code: {result}")
            else:
                # Generate for entire year
                results = generator.generate_year_qr_codes(
                    args.year, args.base_url, args.output, args.style
                )
                print(f"✓ Generated {len(results)} QR codes for {args.year}")
        else:
            print("Please specify either --url or --year")
            return 1
            
    except Exception as e:
        print(f"Error generating QR code: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    # Check if qrcode is installed
    try:
        import qrcode
    except ImportError:
        print("Installing required dependency: qrcode[pil]")
        import subprocess
        subprocess.check_call(["pip", "install", "qrcode[pil]"])
        import qrcode
    
    exit(main())