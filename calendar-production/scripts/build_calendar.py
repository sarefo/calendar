#!/usr/bin/env python3
"""
Master Build Script for Calendar Production
Orchestrates the complete workflow from photos to print-ready PDFs

This script coordinates all the individual tools to produce
professional A3 landscape photo calendars.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import subprocess
PDF_MERGER_AVAILABLE = False
PDF_IMPORT_ERROR = ""
try:
    from pypdf import PdfWriter, PdfReader
    PDF_MERGER_AVAILABLE = True
except ImportError as e1:
    PDF_IMPORT_ERROR += f"pypdf: {e1}; "
    try:
        from PyPDF2 import PdfWriter, PdfReader
        PDF_MERGER_AVAILABLE = True
    except ImportError as e2:
        PDF_IMPORT_ERROR += f"PyPDF2: {e2}"

# Import our custom modules
# Handle import for both module usage and direct execution
try:
    from .calendar_generator import CalendarGenerator
    from .update_landing_page import update_landing_page
    from .qr_generator import QRGenerator
    from .world_map_generator import WorldMapGenerator
    from .html_to_pdf import HTMLToPDFConverter
except ImportError:
    from calendar_generator import CalendarGenerator
    from update_landing_page import update_landing_page
    from qr_generator import QRGenerator
    from world_map_generator import WorldMapGenerator
    from html_to_pdf import HTMLToPDFConverter

class CalendarBuilder:
    def __init__(self, config_file: str = None, language: str = "en"):
        self.config_file = config_file or "data/calendar_config.json"
        self.language = language
        self.config = self._load_config()
        
        # Initialize components
        self.calendar_gen = CalendarGenerator(config_file, language=language)
        # Clear any template cache to ensure fresh template loading
        self.calendar_gen.jinja_env.cache = {}
        self.calendar_gen.jinja_env.auto_reload = True
        self.qr_gen = QRGenerator()
        self.map_gen = WorldMapGenerator()
        
    def _load_config(self):
        """Load build configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found: {self.config_file}")
            return {}
    
    def check_photo_directory(self, year: int, month: int) -> dict:
        """Check photo directory and return status"""
        photo_dir = Path(f"photos/{year}/{month:02d}")
        
        status = {
            "exists": photo_dir.exists(),
            "path": str(photo_dir),
            "photo_count": 0,
            "photos": []
        }
        
        if status["exists"]:
            jpg_files = sorted([f for f in photo_dir.iterdir() if f.suffix.lower() == '.jpg'])
            status["photo_count"] = len(jpg_files)
            status["photos"] = [f.name for f in jpg_files]
        
        return status
    
    def validate_photos_for_month(self, year: int, month: int) -> bool:
        """Validate that we have enough photos for the month"""
        from calendar import monthrange
        
        # Get number of days in month
        _, days_in_month = monthrange(year, month)
        
        photo_status = self.check_photo_directory(year, month)
        
        if not photo_status["exists"]:
            print(f"❌ Photo directory not found: {photo_status['path']}")
            return False
        
        if photo_status["photo_count"] < days_in_month:
            print(f"⚠️  Warning: Only {photo_status['photo_count']} photos found, "
                  f"need {days_in_month} for {year}-{month:02d}")
            print(f"   Missing photos will use placeholder images")
        else:
            print(f"✅ Found {photo_status['photo_count']} photos for {year}-{month:02d}")
        
        return photo_status["photo_count"] > 0
    
    async def build_month(self, year: int, month: int,
                         output_dir: str = "output", generate_pdf: bool = True, web_mode: bool = False, ultra_web: bool = False) -> dict:
        """Build calendar for a single month
        
        Args:
            year: Calendar year
            month: Calendar month (1-12)
            output_dir: Base output directory
            generate_pdf: Whether to generate PDF files
            web_mode: If True, creates web-optimized PDFs (smaller file sizes)
            ultra_web: If True, creates ultra-compressed PDFs (minimal file sizes)
        """
        
        print(f"\\n📅 Building calendar for {year}-{month:02d}")
        
        # Validate photos
        if not self.validate_photos_for_month(year, month):
            print(f"❌ Cannot build calendar for {year}-{month:02d}: insufficient photos")
            return {"success": False, "reason": "insufficient_photos"}
        
        try:
            # Load and validate location data first - fail fast if missing
            try:
                map_location_data = self.calendar_gen._load_location_from_readme(year, month)
                print(f"✅ Loaded location data: {map_location_data['location_display']}")
            except (FileNotFoundError, ValueError) as e:
                print(f"❌ Cannot build calendar for {year}-{month:02d}: {e}")
                return {"success": False, "reason": f"location_data_missing: {e}"}
            
            # Generate QR code
            base_url = "https://sarefo.github.io/calendar/"
            qr_file = self.qr_gen.generate_calendar_qr(
                year, month, base_url,
                f"{output_dir}/assets",
                language=self.language
            )
            print(f"✅ Generated QR code: {qr_file}")
            
            # Generate world map
            map_file = self.map_gen.save_map_svg(
                map_location_data,
                f"{output_dir}/assets/map-{year}-{month:02d}.svg"
            )
            print(f"✅ Generated world map: {map_file}")
            
            # Generate calendar HTML (using source photos directly)
            # Clear template cache and reload template environment completely
            from jinja2 import Environment, FileSystemLoader, select_autoescape
            self.calendar_gen.jinja_env = Environment(
                loader=FileSystemLoader(self.calendar_gen.template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
            html_file = self.calendar_gen.generate_calendar_page(
                year, month, None,
                photo_dirs=[f"photos/{year}/{month:02d}"],
                output_dir=output_dir,
                use_absolute_paths=False
            )
            print(f"✅ Generated HTML: {html_file}")
            
            result = {
                "success": True,
                "year": year,
                "month": month,
                "html_file": html_file,
                "qr_file": qr_file,
                "map_file": map_file,
                "location": map_location_data.get("location", f"Month {month}")
            }
            
            # Generate PDF if requested
            if generate_pdf:
                # Generate a PDF-specific HTML with absolute paths using different filename
                pdf_html_file = self.calendar_gen.generate_calendar_page_for_pdf(
                    year, month, None,
                    photo_dirs=[f"photos/{year}/{month:02d}"],
                    output_dir=output_dir,
                    use_absolute_paths=True
                )
                
                pdf_file = await self._convert_to_pdf(pdf_html_file, output_dir, year, month, web_mode, ultra_web)
                if pdf_file:
                    result["pdf_file"] = pdf_file
                    print(f"✅ Generated PDF: {pdf_file}")
                    
                # Clean up the temporary PDF HTML file
                try:
                    if pdf_html_file != html_file:
                        Path(pdf_html_file).unlink()
                except:
                    pass
            
            return result
            
        except (FileNotFoundError, ValueError) as e:
            # Location data errors - already handled above, but catch any others
            print(f"❌ Location data error for {year}-{month:02d}: {e}")
            return {"success": False, "reason": f"location_data_error: {e}"}
        except Exception as e:
            print(f"❌ Error building calendar for {year}-{month:02d}: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "reason": str(e)}
    
    async def _convert_to_pdf(self, html_file: str, output_dir: str, year: int, month: int, web_mode: bool = False, ultra_web: bool = False) -> str:
        """Convert HTML to PDF
        
        Args:
            html_file: Source HTML file
            output_dir: Base output directory
            year: Calendar year
            month: Calendar month
            web_mode: If True, creates web-optimized PDF (smaller file size)
            ultra_web: If True, creates ultra-compressed PDF (minimal file size)
        """
        try:
            converter = HTMLToPDFConverter("auto")
            
            # Generate PDF filename from year and month with appropriate suffix
            if ultra_web:
                suffix = "_ultra"
            elif web_mode:
                suffix = "_web"
            else:
                suffix = ""
            pdf_filename = f"{year}{month:02d}{suffix}.pdf"
            pdf_path = Path(output_dir) / "print-ready" / pdf_filename
            
            # Convert to PDF with compression mode options
            pdf_file = await converter.convert_html_to_pdf(html_file, str(pdf_path), web_mode=web_mode, ultra_web=ultra_web)
            return pdf_file
            
        except Exception as e:
            print(f"⚠️  PDF conversion failed: {e}")
            return None
    
    async def build_year(self, year: int,
                        output_dir: str = "output", 
                        months: list = None, generate_pdf: bool = True,
                        bind_pdf: bool = False, web_mode: bool = False, ultra_web: bool = False) -> dict:
        """Build calendar for entire year or specified months
        
        Args:
            year: Calendar year
            output_dir: Base output directory
            months: List of months to build (None = all months)
            generate_pdf: Whether to generate PDF files
            bind_pdf: Whether to bind all PDFs into single file
            web_mode: If True, creates web-optimized PDFs (smaller file sizes)
            ultra_web: If True, creates ultra-compressed PDFs (minimal file sizes)
        """
        
        if not months:
            months = list(range(1, 13))  # All months
        
        print(f"\\n🏗️  Building calendar for {year}")
        print(f"Months: {months}")
        
        results = {
            "year": year,
            "successful_months": [],
            "failed_months": [],
            "generated_files": []
        }
        
        for month in months:
            month_result = await self.build_month(
                year, month, output_dir, generate_pdf, web_mode, ultra_web
            )
            
            if month_result["success"]:
                results["successful_months"].append(month)
                results["generated_files"].extend([
                    month_result.get("html_file"),
                    month_result.get("pdf_file"),
                    month_result.get("qr_file"),
                    month_result.get("map_file")
                ])
            else:
                results["failed_months"].append(month)
        
        # Generate summary
        print(f"\\n📊 Build Summary for {year}:")
        print(f"✅ Successful: {len(results['successful_months'])} months")
        if results["failed_months"]:
            print(f"❌ Failed: {len(results['failed_months'])} months")
        
        # Create print package if we have PDFs
        if generate_pdf and results["successful_months"]:
            pdf_files = [f for f in results["generated_files"] if f and f.endswith('.pdf')]
            if pdf_files:
                try:
                    converter = HTMLToPDFConverter("auto")
                    package_dir = converter.create_print_package(
                        pdf_files, f"{output_dir}/print-package-{year}"
                    )
                    results["print_package"] = package_dir
                    print(f"📦 Print package created: {package_dir}")
                except Exception as e:
                    print(f"⚠️  Print package creation failed: {e}")
                
                # Bind PDFs into single file if requested
                if bind_pdf and len(pdf_files) > 1:
                    try:
                        bound_pdf_file = f"{output_dir}/print-ready/{year}_calendar_complete.pdf"
                        bound_pdf = self.bind_pdfs_to_single_file(pdf_files, bound_pdf_file)
                        results["bound_pdf"] = bound_pdf
                        print(f"📚 Complete calendar PDF created: {bound_pdf}")
                    except Exception as e:
                        print(f"❌ PDF binding failed: {e}")
                        if not PDF_MERGER_AVAILABLE:
                            print("   Install PyPDF2: pip install PyPDF2")
        
        return results
    
    async def build_complete(self, year: int, output_dir: str = "output", months: list = None) -> dict:
        """Complete build: HTML + both print and ultra PDFs + bind both versions
        
        Args:
            year: Calendar year
            output_dir: Base output directory  
            months: List of months to build (None = all months)
        """
        
        if not months:
            months = list(range(1, 13))  # All months
        
        print(f"🚀 Starting COMPLETE build for {year}")
        print(f"📅 Building {len(months)} months with HTML + Print PDFs + Ultra PDFs + Binds")
        
        # Step 1: Build all months with print PDFs
        print(f"\n=== STEP 1: Building Print-Quality PDFs ===")
        print_results = await self.build_year(year, output_dir, months, generate_pdf=True, bind_pdf=False, web_mode=False, ultra_web=False)
        
        # Step 2: Build all months with ultra PDFs (HTML already exists, so this is faster)
        print(f"\n=== STEP 2: Building Ultra-Compressed PDFs ===")
        ultra_results = await self.build_year(year, output_dir, months, generate_pdf=True, bind_pdf=False, web_mode=False, ultra_web=True)
        
        # Step 3: Bind print PDFs
        print(f"\n=== STEP 3: Binding Print PDFs ===")
        print_pdf_files = []
        for month in print_results["successful_months"]:
            pdf_file = f"{output_dir}/print-ready/{year}{month:02d}.pdf"
            if Path(pdf_file).exists():
                print_pdf_files.append(pdf_file)
        
        if print_pdf_files:
            print_bound_file = f"{output_dir}/print-ready/{year}_calendar_print.pdf"
            try:
                bound_print = self.bind_pdfs_to_single_file(print_pdf_files, print_bound_file)
                print(f"✅ Print calendar bound: {bound_print}")
            except Exception as e:
                print(f"⚠️ Print PDF binding failed: {e}")
                bound_print = None
        else:
            bound_print = None
            
        # Step 4: Bind ultra PDFs  
        print(f"\n=== STEP 4: Binding Ultra-Compressed PDFs ===")
        ultra_pdf_files = []
        for month in ultra_results["successful_months"]:
            pdf_file = f"{output_dir}/print-ready/{year}{month:02d}_ultra.pdf"
            if Path(pdf_file).exists():
                ultra_pdf_files.append(pdf_file)
                
        if ultra_pdf_files:
            ultra_bound_file = f"{output_dir}/print-ready/{year}_calendar_ultra.pdf"
            try:
                bound_ultra = self.bind_pdfs_to_single_file(ultra_pdf_files, ultra_bound_file)
                print(f"✅ Ultra calendar bound: {bound_ultra}")
            except Exception as e:
                print(f"⚠️ Ultra PDF binding failed: {e}")
                bound_ultra = None
        else:
            bound_ultra = None
        
        # Step 5: Update landing page
        print(f"\n=== STEP 5: Updating Landing Page ===")
        try:
            update_landing_page()
            print("✅ Landing page updated")
        except Exception as e:
            print(f"⚠️ Landing page update failed: {e}")
        
        # Compile results
        results = {
            "year": year,
            "months_built": len(months),
            "successful_months": list(set(print_results["successful_months"] + ultra_results["successful_months"])),
            "failed_months": list(set(print_results["failed_months"] + ultra_results["failed_months"])),
            "print_pdfs": len(print_pdf_files),
            "ultra_pdfs": len(ultra_pdf_files), 
            "print_bound": bound_print,
            "ultra_bound": bound_ultra,
        }
        
        # Final summary
        print(f"\n🎉 COMPLETE BUILD SUMMARY for {year}:")
        print(f"📄 HTML files: {len(results['successful_months'])} months")
        print(f"🖨️  Print PDFs: {results['print_pdfs']} files")
        print(f"💾 Ultra PDFs: {results['ultra_pdfs']} files")
        if results['print_bound']:
            print(f"📚 Print bound: {Path(results['print_bound']).name}")
        if results['ultra_bound']:
            print(f"📘 Ultra bound: {Path(results['ultra_bound']).name}")
        
        if results["failed_months"]:
            print(f"❌ Failed months: {results['failed_months']}")
        
        return results
    
    def bind_pdfs_to_single_file(self, pdf_files: list, output_file: str) -> str:
        """Bind multiple PDFs into a single PDF file"""
        if not PDF_MERGER_AVAILABLE:
            raise ImportError("PDF merger not available. Install PyPDF2 or pypdf: pip install PyPDF2")
        
        if not pdf_files:
            raise ValueError("No PDF files provided for binding")
        
        # Filter out None values and ensure files exist
        valid_pdf_files = []
        for pdf_file in pdf_files:
            if pdf_file and Path(pdf_file).exists():
                valid_pdf_files.append(pdf_file)
            elif pdf_file:
                print(f"⚠️  Warning: PDF file not found: {pdf_file}")
        
        if not valid_pdf_files:
            raise ValueError("No valid PDF files found for binding")
        
        # Sort PDF files by month (assuming filename format YYYYMM.pdf)
        def get_month_from_filename(filename):
            try:
                basename = Path(filename).stem
                if len(basename) >= 6 and basename[:6].isdigit():
                    return int(basename[4:6])  # Extract month from YYYYMM
                return 0
            except:
                return 0
        
        valid_pdf_files.sort(key=get_month_from_filename)
        
        print(f"📄 Binding {len(valid_pdf_files)} PDFs into single file...")
        for i, pdf_file in enumerate(valid_pdf_files, 1):
            month = get_month_from_filename(pdf_file)
            print(f"   {i:2d}. Month {month:2d}: {Path(pdf_file).name}")
        
        # Create output directory if needed
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing file if it exists to ensure replacement (not appending)
        if output_path.exists():
            output_path.unlink()
            print(f"🗑️  Removed existing file: {output_path.name}")
        
        # Merge PDFs
        pdf_writer = PdfWriter()
        
        for pdf_file in valid_pdf_files:
            try:
                with open(pdf_file, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                print(f"✅ Added: {Path(pdf_file).name}")
            except Exception as e:
                print(f"❌ Error adding {pdf_file}: {e}")
                continue
        
        # Write combined PDF (create new file)
        with open(output_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        
        print(f"📚 Combined PDF created: {output_path}")
        print(f"   Total pages: {len(pdf_writer.pages)}")
        
        return str(output_path)
    
    def create_build_report(self, build_results: dict, output_file: str = None):
        """Create detailed build report"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"output/build_report_{timestamp}.json"
        
        # Add metadata
        build_results["build_info"] = {
            "timestamp": datetime.now().isoformat(),
            "config_file": self.config_file,
            "total_files": len([f for f in build_results.get("generated_files", []) if f])
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(build_results, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Build report saved: {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description="Build complete calendar production")
    parser.add_argument('--year', type=int, default=datetime.now().year, help="Year to build")
    parser.add_argument('--month', type=int, help="Specific month to build (1-12)")
    parser.add_argument('--months', help="Comma-separated list of months (e.g., '1,2,3')")
    parser.add_argument('--config', help="Path to calendar configuration file")
    parser.add_argument('--language', choices=['en', 'de', 'es'], default='en', help="Language for calendar generation")
    parser.add_argument('--output', default="output", help="Output directory")
    parser.add_argument('--no-pdf', action='store_true', help="Skip PDF generation")
    parser.add_argument('--web-pdf', action='store_true', help="Create web-optimized PDFs (smaller file sizes for monitor viewing)")
    parser.add_argument('--ultra-pdf', action='store_true', help="Create ultra-compressed PDFs (minimal file sizes <40MB total)")
    parser.add_argument('--complete', action='store_true', help="Complete build: generate HTML + both print and ultra PDFs + bind both versions")
    parser.add_argument('--bind-pdf', action='store_true', help="Bind all monthly PDFs into single file")
    parser.add_argument('--bind-existing', action='store_true', help="Only bind existing PDFs without regenerating")
    parser.add_argument('--check-photos', action='store_true', help="Only check photo availability")
    parser.add_argument('--install-deps', action='store_true', help="Install required dependencies")
    
    args = parser.parse_args()
    
    if args.install_deps:
        print("Installing dependencies...")
        deps = ["jinja2", "qrcode[pil]", "playwright", "PyPDF2"]
        for dep in deps:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            except subprocess.CalledProcessError:
                print(f"Failed to install {dep}")
        
        # Install playwright browsers
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        except subprocess.CalledProcessError:
            print("Failed to install playwright browsers")
        
        return 0
    
    # Initialize builder
    try:
        builder = CalendarBuilder(args.config, args.language)
    except Exception as e:
        print(f"Failed to initialize builder: {e}")
        return 1
    
    # Handle photo checking mode
    if args.check_photos:
        months = []
        if args.month:
            months = [args.month]
        elif args.months:
            months = [int(m.strip()) for m in args.months.split(',')]
        else:
            months = list(range(1, 13))
        
        print(f"📷 Checking photos for {args.year}")
        for month in months:
            builder.validate_photos_for_month(args.year, month)
        return 0
    
    # Handle bind-existing mode
    if args.bind_existing:
        if not PDF_MERGER_AVAILABLE:
            print("❌ PDF merger not available.")
            print(f"Import errors: {PDF_IMPORT_ERROR}")
            print("Try installing: pip install pypdf")
            return 1
        
        print(f"🔗 Binding existing PDFs for {args.year}")
        
        # Look for existing PDFs in the print-ready directory
        pdf_dir = Path(args.output) / "print-ready"
        if not pdf_dir.exists():
            print(f"❌ PDF directory not found: {pdf_dir}")
            return 1
        
        # Find print and ultra PDF files separately
        print_pdfs = []
        ultra_pdfs = []
        
        # Look for monthly PDFs (YYYYMM.pdf and YYYYMM_ultra.pdf)
        for month in range(1, 13):
            month_str = f"{month:02d}"
            print_pdf = pdf_dir / f"{args.year}{month_str}.pdf"
            ultra_pdf = pdf_dir / f"{args.year}{month_str}_ultra.pdf"
            
            if print_pdf.exists():
                print_pdfs.append(str(print_pdf))
            if ultra_pdf.exists():
                ultra_pdfs.append(str(ultra_pdf))
        
        print(f"📄 Found {len(print_pdfs)} print PDFs and {len(ultra_pdfs)} ultra PDFs")
        
        if not print_pdfs and not ultra_pdfs:
            print(f"❌ No monthly PDF files found for {args.year}")
            return 1
        
        # Delete existing bound PDFs to ensure clean recreation
        print_bound_path = pdf_dir / f"{args.year}_calendar_print.pdf"
        ultra_bound_path = pdf_dir / f"{args.year}_calendar_ultra.pdf"
        
        if print_bound_path.exists():
            print_bound_path.unlink()
            print(f"🗑️  Removed existing print bound PDF: {print_bound_path.name}")
            
        if ultra_bound_path.exists():
            ultra_bound_path.unlink()
            print(f"🗑️  Removed existing ultra bound PDF: {ultra_bound_path.name}")
        
        # Bind print PDFs
        print_success = False
        if print_pdfs:
            try:
                print(f"\n📚 Binding {len(print_pdfs)} print PDFs...")
                bound_print = builder.bind_pdfs_to_single_file(print_pdfs, str(print_bound_path))
                print(f"✅ Print calendar created: {Path(bound_print).name}")
                print_success = True
            except Exception as e:
                print(f"❌ Failed to bind print PDFs: {e}")
        
        # Bind ultra PDFs
        ultra_success = False
        if ultra_pdfs:
            try:
                print(f"\n📘 Binding {len(ultra_pdfs)} ultra PDFs...")
                bound_ultra = builder.bind_pdfs_to_single_file(ultra_pdfs, str(ultra_bound_path))
                print(f"✅ Ultra calendar created: {Path(bound_ultra).name}")
                ultra_success = True
            except Exception as e:
                print(f"❌ Failed to bind ultra PDFs: {e}")
        
        # Summary
        if print_success or ultra_success:
            print(f"\n🎉 Bind-existing completed:")
            if print_success:
                print(f"   📚 Print bound: {print_bound_path.name}")
            if ultra_success:
                print(f"   📘 Ultra bound: {ultra_bound_path.name}")
            return 0
        else:
            print(f"\n❌ No PDFs were successfully bound")
            return 1
    
    # Determine months to build
    months_to_build = []
    if args.month:
        months_to_build = [args.month]
    elif args.months:
        months_to_build = [int(m.strip()) for m in args.months.split(',')]
    else:
        months_to_build = None  # All months
    
    # Build calendar(s)
    async def build():
        try:
            if args.complete:
                # Complete build: HTML + both print and ultra PDFs + bind both
                results = await builder.build_complete(args.year, args.output, months_to_build)
                
                if results["successful_months"]:
                    print(f"\\n🎉 Complete build finished successfully!")
                    return 0
                else:
                    print(f"\\n❌ Complete build failed")
                    return 1
                    
            elif months_to_build and len(months_to_build) == 1:
                # Single month build
                result = await builder.build_month(
                    args.year, months_to_build[0], 
                    args.output, not args.no_pdf, args.web_pdf, args.ultra_pdf
                )
                
                if result["success"]:
                    print(f"\\n🎉 Successfully built calendar for {args.year}-{months_to_build[0]:02d}")
                    # Update landing page with latest observation IDs
                    update_landing_page()
                else:
                    print(f"\\n❌ Failed to build calendar: {result.get('reason', 'unknown error')}")
                    return 1
            else:
                # Multiple months or full year
                results = await builder.build_year(
                    args.year, args.output, 
                    months_to_build, not args.no_pdf, args.bind_pdf, args.web_pdf, args.ultra_pdf
                )
                
                # Save build report
                builder.create_build_report(results)
                
                if results["failed_months"]:
                    print(f"\\n⚠️  Some months failed to build: {results['failed_months']}")
                    return 1
                else:
                    print(f"\\n🎉 Successfully built calendar for {args.year}")
                    # Update landing page with latest observation IDs
                    update_landing_page()
            
            return 0
            
        except Exception as e:
            print(f"\\n❌ Build failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    # Run the build
    return asyncio.run(build())

if __name__ == "__main__":
    exit(main())