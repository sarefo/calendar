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
        
        # Check Playwright
        try:
            import playwright
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
                                    print_options: dict = None) -> str:
        """Convert HTML to PDF using Playwright"""
        from playwright.async_api import async_playwright
        
        if not print_options:
            print_options = self._get_default_print_options()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate to HTML file
            html_path = Path(html_file).resolve()
            await page.goto(f"file://{html_path}")
            
            # Wait for any dynamic content
            await page.wait_for_timeout(2000)
            
            # Generate PDF
            pdf_path = Path(pdf_file)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
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
                **print_options
            )
            
            await browser.close()
        
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
        
        # Wait for content to load
        await page.waitFor(2000)
        
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
        
        # Additional CSS for WeasyPrint
        css_string = """
        @page {
            size: A3 landscape;
            margin: 0;
            bleed: 3mm;
        }
        * {
            print-color-adjust: exact !important;
        }
        """
        
        pdf_path = Path(pdf_file)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert HTML to PDF with proper base URL for relative paths
        html_path = Path(html_file).resolve()
        base_url = html_path.parent.as_uri() + "/"
        
        html_doc = HTML(filename=str(html_path), base_url=base_url)
        css_doc = CSS(string=css_string)
        
        html_doc.write_pdf(str(pdf_path), stylesheets=[css_doc])
        
        return str(pdf_path)
    
    def _get_default_print_options(self) -> dict:
        """Get default print options for high-quality output"""
        return {
            'preferCSSPageSize': True,
            'displayHeaderFooter': False,
            'printBackground': True,
        }
    
    async def convert_html_to_pdf(self, html_file: str, pdf_file: str,
                                print_options: dict = None) -> str:
        """Convert HTML file to PDF using the selected method"""
        
        if not Path(html_file).exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        
        print(f"Converting {html_file} to PDF using {self.method}...")
        
        if self.method == "playwright":
            return await self.convert_with_playwright(html_file, pdf_file, print_options)
        elif self.method == "pyppeteer":
            return await self.convert_with_pyppeteer(html_file, pdf_file, print_options)
        elif self.method == "weasyprint":
            return self.convert_with_weasyprint(html_file, pdf_file, print_options)
        else:
            raise ValueError(f"Unknown conversion method: {self.method}")
    
    async def convert_multiple_files(self, html_files: List[str], 
                                   output_dir: str = "output/print-ready",
                                   print_options: dict = None) -> List[str]:
        """Convert multiple HTML files to PDF"""
        
        converted_files = []
        
        for html_file in html_files:
            # Generate PDF filename
            html_path = Path(html_file)
            pdf_filename = html_path.stem + ".pdf"
            pdf_path = Path(output_dir) / pdf_filename
            
            # Convert file
            try:
                result_pdf = await self.convert_html_to_pdf(
                    str(html_path), str(pdf_path), print_options
                )
                converted_files.append(result_pdf)
                print(f"✓ Converted: {result_pdf}")
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
                html_files, args.output, print_options
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