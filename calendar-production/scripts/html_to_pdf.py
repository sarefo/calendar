#!/usr/bin/env python3
"""
HTML to PDF Converter for Professional Calendar Printing
Converts HTML calendar pages to print-ready PDF files

Supports multiple conversion methods:
1. Puppeteer (via pyppeteer) - Best quality, requires Node.js
2. WeasyPrint - Pure Python, good CSS support
3. Playwright - Alternative to Puppeteer
"""

import asyncio
import json
import argparse
from pathlib import Path
from typing import List, Optional
import subprocess
import sys

class HTMLToPDFConverter:
    def __init__(self, method: str = "auto"):
        self.method = method
        self.available_methods = self._check_available_methods()
        
        if method == "auto":
            self.method = self._select_best_method()
        elif method not in self.available_methods:
            raise ValueError(f"Method '{method}' not available. Available: {self.available_methods}")
    
    def _check_available_methods(self) -> List[str]:
        """Check which conversion methods are available"""
        methods = []
        
        # Check WeasyPrint
        try:
            import weasyprint
            methods.append("weasyprint")
        except ImportError:
            pass
        
        # Check Playwright (proper check)
        try:
            from playwright.async_api import async_playwright
            methods.append("playwright")
        except ImportError:
            pass
        
        # Check pyppeteer
        try:
            import pyppeteer
            methods.append("pyppeteer")
        except ImportError:
            pass
        
        return methods
    
    def _select_best_method(self) -> str:
        """Select the best available method"""
        if "playwright" in self.available_methods:
            return "playwright"
        elif "pyppeteer" in self.available_methods:
            return "pyppeteer"
        elif "weasyprint" in self.available_methods:
            return "weasyprint"
        else:
            raise RuntimeError("No PDF conversion methods available. Install weasyprint, playwright, or pyppeteer.")
    
    def install_dependencies(self, method: str = None):
        """Install dependencies for the specified method"""
        if not method:
            method = self.method
            
        print(f"Installing dependencies for {method}...")
        
        if method == "weasyprint":
            subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
        elif method == "playwright":
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        elif method == "pyppeteer":
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyppeteer"])
    
    async def convert_with_playwright(self, html_file: str, pdf_file: str, 
                                    print_options: dict = None, web_mode: bool = False) -> str:
        """Convert HTML to PDF using Playwright with image optimization
        
        Args:
            html_file: Path to source HTML file
            pdf_file: Output PDF file path
            print_options: PDF generation options
            web_mode: If True, creates web-optimized PDF (smaller file size)
        """
        from playwright.async_api import async_playwright
        import shutil
        
        if not print_options:
            print_options = self._get_default_print_options()
        
        # Create optimized version of HTML with smaller images
        optimized_html = self._create_optimized_html_for_pdf(html_file, web_mode=web_mode)
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Navigate to optimized HTML file
                html_path = Path(optimized_html).resolve()
                try:
                    await page.goto(f"file://{html_path}", wait_until="networkidle")
                except Exception as e:
                    print(f"Warning: Page load issue: {e}")
                    await page.goto(f"file://{html_path}")
                
                # Wait for fonts and dynamic content to load
                await page.wait_for_timeout(5000)
                
                # Generate PDF
                pdf_path = Path(pdf_file)
                pdf_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    await page.pdf(
                        path=str(pdf_path),
                        format='A3',
                        landscape=True,
                        print_background=True,
                        margin={
                            'top': '0mm',
                            'right': '0mm', 
                            'bottom': '0mm',
                            'left': '0mm'
                        },
                        prefer_css_page_size=True
                    )
                except Exception as e:
                    print(f"PDF generation error: {e}")
                    # Try with simpler options
                    await page.pdf(
                        path=str(pdf_path),
                        format='A3',
                        landscape=True,
                        print_background=True
                    )
                
                await browser.close()
        finally:
            # Clean up optimized files
            self._cleanup_optimized_files(html_file, optimized_html, web_mode=web_mode)
        
        return str(pdf_path)
    
    async def convert_with_pyppeteer(self, html_file: str, pdf_file: str,
                                   print_options: dict = None) -> str:
        """Convert HTML to PDF using pyppeteer"""
        import pyppeteer
        
        if not print_options:
            print_options = self._get_default_print_options()
        
        browser = await pyppeteer.launch()
        page = await browser.newPage()
        
        # Navigate to HTML file
        html_path = Path(html_file).resolve()
        await page.goto(f"file://{html_path}")
        
        # Wait for fonts and content to load
        await page.waitFor(5000)
        
        # Generate PDF
        pdf_path = Path(pdf_file)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        await page.pdf({
            'path': str(pdf_path),
            'format': 'A3',
            'landscape': True,
            'printBackground': True,
            'margin': {
                'top': '0mm',
                'right': '0mm',
                'bottom': '0mm', 
                'left': '0mm'
            },
            **print_options
        })
        
        await browser.close()
        return str(pdf_path)
    
    def convert_with_weasyprint(self, html_file: str, pdf_file: str,
                              print_options: dict = None) -> str:
        """Convert HTML to PDF using WeasyPrint"""
        import weasyprint
        from weasyprint import HTML, CSS
        
        # Additional CSS for WeasyPrint with better PDF compatibility
        css_string = """
        @page {
            size: A3 landscape;
            margin: 0;
        }
        * {
            print-color-adjust: exact !important;
            -webkit-print-color-adjust: exact !important;
        }
        .calendar-page {
            width: 420mm !important;
            height: 297mm !important;
        }
        .world-map-svg {
            display: block !important;
            visibility: visible !important;
        }
        .qr-code img {
            display: block !important;
            visibility: visible !important;
            image-rendering: auto !important;
        }
        .calendar-container {
            height: 252mm !important;
            overflow: visible !important;
            padding-bottom: 5mm !important;
        }
        .calendar-table {
            width: 100% !important;
            height: 100% !important;
        }
        .day-image {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            border-radius: 3mm 3mm 0 0 !important;
            object-fit: cover !important;
        }
        .calendar-week-row {
            page-break-inside: avoid !important;
        }
        """
        
        pdf_path = Path(pdf_file)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert HTML to PDF with proper base URL for relative paths
        html_path = Path(html_file).resolve()
        base_url = html_path.parent.as_uri() + "/"
        
        try:
            html_doc = HTML(filename=str(html_path), base_url=base_url)
            css_doc = CSS(string=css_string)
            
            html_doc.write_pdf(str(pdf_path), stylesheets=[css_doc])
        except Exception as e:
            print(f"WeasyPrint error: {e}")
            # Try alternative approach
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            html_doc = HTML(string=html_content, base_url=base_url)
            css_doc = CSS(string=css_string)
            html_doc.write_pdf(str(pdf_path), stylesheets=[css_doc])
        
        return str(pdf_path)
    
    def _get_default_print_options(self) -> dict:
        """Get default print options for high-quality output"""
        return {
            'prefer_css_page_size': True,
            'display_header_footer': False,
            'print_background': True,
        }
    
    def _preprocess_html_for_pdf(self, html_file: str) -> str:
        """Preprocess HTML file by copying images to temp directory and updating paths"""
        import shutil
        import re
        
        html_path = Path(html_file)
        html_content = html_path.read_text(encoding='utf-8')
        base_path = html_path.parent.resolve()
        
        # Create temporary directory for images
        temp_dir = html_path.parent / "temp_images_pdf"
        temp_dir.mkdir(exist_ok=True)
        
        converted_count = 0
        
        def replace_relative_path(match):
            nonlocal converted_count
            src_path = match.group(1)
            
            # Skip data URLs and absolute URLs (but not local absolute paths)
            if src_path.startswith(('data:', 'http:', 'https:', 'file:')):
                print(f"  Skipping {src_path[:50]}... (data/absolute URL)")
                return match.group(0)
            
            # Resolve the source image path
            if src_path.startswith('/'):
                # Absolute path
                source_path = Path(src_path).resolve()
            elif src_path.startswith('../'):
                relative_path = src_path[3:]  # Remove '../'
                source_path = (base_path.parent / relative_path).resolve()
            else:
                source_path = (base_path / src_path).resolve()
            
            print(f"  Processing: {src_path}")
            print(f"    Source: {source_path}")
            print(f"    Exists: {source_path.exists()}")
            
            if source_path.exists():
                # Copy image to temp directory
                image_name = source_path.name
                temp_image_path = temp_dir / image_name
                
                # Handle duplicate names by adding counter
                counter = 1
                while temp_image_path.exists():
                    name_parts = source_path.stem, counter, source_path.suffix
                    temp_image_path = temp_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                    counter += 1
                
                shutil.copy2(source_path, temp_image_path)
                converted_count += 1
                
                # Return relative path from HTML file to temp image
                relative_temp_path = f"temp_images_pdf/{temp_image_path.name}"
                print(f"    Copied to: {temp_image_path}")
                print(f"    New path: {relative_temp_path}")
                return f'src="{relative_temp_path}"'
            else:
                print(f"    WARNING: File not found, keeping original path")
                return match.group(0)
        
        print(f"Preprocessing HTML for PDF conversion...")
        print(f"Base path: {base_path}")
        print(f"Temp dir: {temp_dir}")
        
        # Replace all img src attributes
        updated_content = re.sub(r'src="([^"]+)"', replace_relative_path, html_content)
        
        print(f"Converted {converted_count} image paths and copied to temp directory")
        
        # Create temporary file with updated content
        temp_file = html_path.parent / f"{html_path.stem}_pdf_temp.html"
        temp_file.write_text(updated_content, encoding='utf-8')
        
        print(f"Created temporary HTML file: {temp_file}")
        return str(temp_file)

    def _create_optimized_html_for_pdf(self, html_file: str, web_mode: bool = False) -> str:
        """Create optimized HTML with reduced image sizes for PDF generation
        
        Args:
            html_file: Path to the source HTML file
            web_mode: If True, creates web-optimized images (max 200px, quality 45)
                      If False, creates print-optimized images (max 800px, quality 85)
        """
        from PIL import Image
        import shutil
        import re
        
        html_path = Path(html_file)
        html_content = html_path.read_text(encoding='utf-8')
        base_path = html_path.parent.resolve()
        
        # Create temporary directory for optimized images
        if web_mode:
            suffix = "web_optimized"
        else:
            suffix = "pdf_optimized"
        temp_dir = html_path.parent / f"temp_{suffix}"
        temp_dir.mkdir(exist_ok=True)
        
        optimized_count = 0
        
        # Set optimization parameters based on mode
        if web_mode:
            max_size = 200  # Small for web compression
            quality = 45    # Lower quality for minimum file size
            print(f"Creating WEB-OPTIMIZED HTML for minimal file size...")
        else:
            max_size = 800  # Larger for print quality
            quality = 85    # Higher quality for print
            print(f"Creating PRINT-OPTIMIZED HTML for PDF conversion...")
        
        def optimize_and_replace_image(match):
            nonlocal optimized_count
            src_path = match.group(1)
            
            # Skip data URLs and absolute URLs
            if src_path.startswith(('data:', 'http:', 'https:')):
                return match.group(0)
            
            # Resolve the source image path
            if src_path.startswith('/'):
                source_path = Path(src_path).resolve()
            elif src_path.startswith('../'):
                relative_path = src_path[3:]
                source_path = (base_path.parent / relative_path).resolve()
            else:
                source_path = (base_path / src_path).resolve()
            
            if source_path.exists():
                try:
                    # Create optimized image name
                    if web_mode:
                        prefix = "web_"
                    else:
                        prefix = "opt_"
                    optimized_name = f"{prefix}{source_path.name}"
                    optimized_path = temp_dir / optimized_name
                    
                    # Resize image based on mode
                    with Image.open(source_path) as img:
                        # Convert to RGB if needed
                        if img.mode not in ['RGB', 'L']:
                            img = img.convert('RGB')
                        
                        # Resize maintaining aspect ratio
                        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                        
                        # Save with quality optimization
                        img.save(optimized_path, 'JPEG', quality=quality, optimize=True)
                    
                    optimized_count += 1
                    
                    # Return relative path from HTML file to optimized image
                    relative_path = f"temp_{suffix}/{optimized_name}"
                    if web_mode:
                        mode_label = "WEB"
                    else:
                        mode_label = "PRINT"
                    print(f"  {mode_label}: {source_path.name} -> {relative_path}")
                    return f'src="{relative_path}"'
                    
                except Exception as e:
                    print(f"  Warning: Could not optimize {source_path}: {e}")
                    return match.group(0)
            else:
                return match.group(0)
        
        print(f"Temp dir: {temp_dir}")
        print(f"Image size limit: {max_size}px, Quality: {quality}%")
        
        # Replace all img src attributes with optimized versions
        updated_content = re.sub(r'src="([^"]+)"', optimize_and_replace_image, html_content)
        
        if web_mode:
            print(f"Optimized {optimized_count} images for web viewing")
        else:
            print(f"Optimized {optimized_count} images for PDF generation")
        
        # Create temporary file with updated content
        temp_file = html_path.parent / f"{html_path.stem}_{suffix}.html"
        temp_file.write_text(updated_content, encoding='utf-8')
        
        print(f"Created optimized HTML file: {temp_file}")
        return str(temp_file)
    
    def _cleanup_optimized_files(self, original_html: str, optimized_html: str, web_mode: bool = False):
        """Clean up optimized files"""
        try:
            import shutil
            html_path = Path(original_html)
            
            # Clean up appropriate temp directory based on mode
            if web_mode:
                suffix = "web_optimized"
                mode_label = "WEB-optimized"
            else:
                suffix = "pdf_optimized"
                mode_label = "PRINT-optimized"
            
            temp_dir = html_path.parent / f"temp_{suffix}"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                print(f"✅ Cleaned up {mode_label} images: {temp_dir}")
            
            # Clean up optimized HTML file
            opt_html = Path(optimized_html)
            if opt_html.exists() and f"_{suffix}.html" in opt_html.name:
                opt_html.unlink()
                print(f"✅ Cleaned up optimized HTML: {opt_html}")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

    async def convert_html_to_pdf(self, html_file: str, pdf_file: str,
                                print_options: dict = None, web_mode: bool = False) -> str:
        """Convert HTML file to PDF using the selected method
        
        Args:
            html_file: Source HTML file path
            pdf_file: Output PDF file path  
            print_options: PDF generation options
            web_mode: If True, creates web-optimized PDF (smaller file size)
        """
        
        if not Path(html_file).exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        
        if web_mode:
            mode_label = "WEB-optimized"
        else:
            mode_label = "PRINT-ready"
        print(f"Converting {html_file} to {mode_label} PDF using {self.method}...")
        
        if self.method == "playwright":
            result = await self.convert_with_playwright(html_file, pdf_file, print_options, web_mode)
        elif self.method == "weasyprint":
            # Web mode not yet supported for WeasyPrint - use standard method
            if web_mode:
                print("⚠️ Web mode not yet supported for WeasyPrint, using standard optimization")
            result = self.convert_with_weasyprint(html_file, pdf_file, print_options)
        elif self.method == "pyppeteer":
            # Web mode not yet supported for pyppeteer - use standard method
            if web_mode:
                print("⚠️ Web mode not yet supported for pyppeteer, using standard optimization")
            result = await self.convert_with_pyppeteer(html_file, pdf_file, print_options)
        else:
            raise ValueError(f"Unknown conversion method: {self.method}")
        
        return result
    
    def _cleanup_temp_files(self, original_html: str, processed_html: str):
        """Clean up temporary files"""
        try:
            import shutil
            html_path = Path(original_html)
            temp_dir = html_path.parent / "temp_images_pdf"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                print(f"✅ Cleaned up temporary files: {temp_dir}")
            
            # Clean up temporary HTML file
            temp_html = Path(processed_html)
            if temp_html.exists() and "_pdf_temp.html" in temp_html.name:
                temp_html.unlink()
                print(f"✅ Cleaned up temporary HTML: {temp_html}")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    async def convert_multiple_files(self, html_files: List[str], 
                                   output_dir: str = "output/print-ready",
                                   print_options: dict = None, web_mode: bool = False) -> List[str]:
        """Convert multiple HTML files to PDF
        
        Args:
            html_files: List of HTML files to convert
            output_dir: Directory to save PDFs
            print_options: PDF generation options
            web_mode: If True, creates web-optimized PDFs (smaller file sizes)
        """
        
        converted_files = []
        if web_mode:
            mode_suffix = "_web"
        else:
            mode_suffix = ""
        
        for html_file in html_files:
            # Generate PDF filename with appropriate suffix
            html_path = Path(html_file)
            pdf_filename = html_path.stem + mode_suffix + ".pdf"
            pdf_path = Path(output_dir) / pdf_filename
            
            # Convert file
            try:
                result_pdf = await self.convert_html_to_pdf(
                    str(html_path), str(pdf_path), print_options, web_mode
                )
                converted_files.append(result_pdf)
                if web_mode:
                    mode_label = "WEB-optimized"
                else:
                    mode_label = "PRINT-ready"
                print(f"✓ {mode_label}: {result_pdf}")
            except Exception as e:
                print(f"✗ Failed to convert {html_file}: {e}")
        
        return converted_files
    
    def create_print_package(self, pdf_files: List[str], 
                           package_dir: str = "output/print-package") -> str:
        """Create a complete print package with all PDFs and instructions"""
        
        package_path = Path(package_dir)
        package_path.mkdir(parents=True, exist_ok=True)
        
        # Copy PDFs to package directory
        copied_files = []
        for pdf_file in pdf_files:
            src_path = Path(pdf_file)
            dest_path = package_path / src_path.name
            
            # Copy file
            import shutil
            shutil.copy2(src_path, dest_path)
            copied_files.append(str(dest_path))
        
        # Create print instructions
        instructions = self._generate_print_instructions(copied_files)
        instructions_file = package_path / "PRINT_INSTRUCTIONS.txt"
        
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        # Create file list
        file_list = package_path / "FILE_LIST.txt"
        with open(file_list, 'w') as f:
            f.write("Calendar Print Package\\n")
            f.write("=" * 25 + "\\n\\n")
            f.write("PDF Files:\\n")
            for pdf_file in copied_files:
                f.write(f"  - {Path(pdf_file).name}\\n")
            f.write(f"\\nTotal files: {len(copied_files)}\\n")
        
        print(f"✓ Created print package: {package_path}")
        return str(package_path)
    
    def _generate_print_instructions(self, pdf_files: List[str]) -> str:
        """Generate detailed print instructions"""
        return f"""PROFESSIONAL CALENDAR PRINTING INSTRUCTIONS
==========================================

Package Contents: {len(pdf_files)} PDF files
Format: A3 Landscape (420mm × 297mm)
Print Specification: PDF/X compliant

PRINTER REQUIREMENTS:
- A3 paper support (minimum)
- Color printing capability
- 300 DPI minimum resolution
- CMYK color space support

PRINT SETTINGS:
- Paper Size: A3 (420mm × 297mm)
- Orientation: Landscape
- Quality: Highest/Best available
- Color Mode: CMYK
- Scaling: None (100% / Actual Size)
- Margins: None (Full bleed)

PAPER RECOMMENDATIONS:
- Weight: 200-300 GSM
- Finish: Matte or Semi-gloss
- Type: Photo paper or high-quality cardstock

BINDING OPTIONS:
- Spiral binding (recommended)
- Saddle stitching
- Perfect binding
- Ring binding

QUALITY CHECK:
1. Verify all photos are sharp and well-exposed
2. Check that text is clearly readable
3. Ensure colors are vibrant but not oversaturated
4. Confirm crop marks are visible (if enabled)

PROFESSIONAL PRINT SHOPS:
These files are compatible with:
- Local print shops
- Online printing services (VistaPrint, etc.)
- Professional offset printers
- Large format printers

TROUBLESHOOTING:
- If colors appear different, ask for CMYK color matching
- If text appears blurry, ensure 300 DPI output
- If layout is cut off, verify "fit to page" is disabled

Generated: {Path().cwd()}
Contact: [Your contact information]
"""

def main():
    parser = argparse.ArgumentParser(description="Convert HTML calendars to print-ready PDFs")
    parser.add_argument('--input', required=True, help="HTML file or directory containing HTML files")
    parser.add_argument('--output', default="output/print-ready", help="Output directory for PDFs")
    parser.add_argument('--method', choices=['auto', 'playwright', 'pyppeteer', 'weasyprint'], 
                       default='auto', help="PDF conversion method")
    parser.add_argument('--install', action='store_true', help="Install dependencies for selected method")
    parser.add_argument('--package', action='store_true', help="Create complete print package")
    parser.add_argument('--quality', choices=['draft', 'standard', 'high'], default='high',
                       help="Print quality setting")
    parser.add_argument('--web-mode', action='store_true', 
                       help="Create web-optimized PDFs (smaller file sizes for monitor viewing)")
    
    args = parser.parse_args()
    
    try:
        converter = HTMLToPDFConverter(args.method)
        
        if args.install:
            converter.install_dependencies()
            return 0
        
        print(f"Using conversion method: {converter.method}")
        
        # Determine input files
        input_path = Path(args.input)
        if input_path.is_file():
            html_files = [str(input_path)]
        elif input_path.is_dir():
            html_files = [str(f) for f in input_path.glob("*.html")]
        else:
            print(f"Input path not found: {args.input}")
            return 1
        
        if not html_files:
            print("No HTML files found")
            return 1
        
        print(f"Found {len(html_files)} HTML files to convert")
        
        # Set up print options based on quality
        print_options = {}
        if args.quality == "high":
            print_options = {
                'preferCSSPageSize': True,
                'printBackground': True,
            }
        
        # Convert files
        async def convert_all():
            pdf_files = await converter.convert_multiple_files(
                html_files, args.output, print_options, web_mode=args.web_mode
            )
            
            if args.package and pdf_files:
                package_dir = converter.create_print_package(pdf_files)
                print(f"\\n✓ Print package ready: {package_dir}")
            
            return pdf_files
        
        # Run conversion
        pdf_files = asyncio.run(convert_all())
        
        print(f"\\n✓ Successfully converted {len(pdf_files)} files")
        print(f"✓ PDFs saved to: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())