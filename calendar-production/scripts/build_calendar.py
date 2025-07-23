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
    def __init__(self, config_file: str = None, language: str = "en", base_output_dir: str = "output"):
        self.config_file = config_file or "data/calendar_config.json"
        self.language = language
        self.base_output_dir = base_output_dir
        self.config = self._load_config()
        
        # Initialize components
        self.calendar_gen = CalendarGenerator(config_file, language=language)
        # Clear any template cache to ensure fresh template loading
        self.calendar_gen.jinja_env.cache = {}
        self.calendar_gen.jinja_env.auto_reload = True
        self.qr_gen = QRGenerator()
        self.map_gen = WorldMapGenerator()
    
    def get_output_paths(self, year: int) -> dict:
        """Get organized output paths for a specific year and language"""
        year_dir = f"{self.base_output_dir}/{year}"
        lang_dir = f"{year_dir}/{self.language}"
        
        return {
            "year_dir": year_dir,
            "lang_dir": lang_dir,
            "html_dir": f"{lang_dir}/html",
            "pdf_dir": f"{lang_dir}/pdf",
            "pdf_print_dir": f"{lang_dir}/pdf/print",
            "pdf_web_dir": f"{lang_dir}/pdf/web",
            "assets_dir": f"{lang_dir}/assets",
            "qr_dir": f"{lang_dir}/assets/qr",
            "maps_dir": f"{lang_dir}/assets/maps"
        }
        
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
                         generate_pdf: bool = True, web_mode: bool = False) -> dict:
        """Build calendar for a single month
        
        Args:
            year: Calendar year
            month: Calendar month (1-12)
            output_dir: Base output directory
            generate_pdf: Whether to generate PDF files
            web_mode: If True, creates web-optimized PDFs (smaller file sizes)
        """
        
        print(f"\\n📅 Building {self.language.upper()} calendar for {year}-{month:02d}")
        
        # Get organized output paths
        paths = self.get_output_paths(year)
        
        # Create all necessary directories
        for path in paths.values():
            Path(path).mkdir(parents=True, exist_ok=True)
        
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
            
            # Generate QR code in language-specific directory
            base_url = "https://sarefo.github.io/calendar/"
            qr_file = self.qr_gen.generate_calendar_qr(
                year, month, base_url,
                paths["qr_dir"],
                language=self.language
            )
            print(f"✅ Generated QR code: {qr_file}")
            
            # Generate world map in language-specific directory
            map_file = self.map_gen.save_map_svg(
                map_location_data,
                f"{paths['maps_dir']}/map-{year}-{month:02d}.svg"
            )
            print(f"✅ Generated world map: {map_file}")
            
            # Generate calendar HTML in language-specific directory
            # Clear template cache and reload template environment completely
            from jinja2 import Environment, FileSystemLoader, select_autoescape
            self.calendar_gen.jinja_env = Environment(
                loader=FileSystemLoader(self.calendar_gen.template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
            html_file = self.calendar_gen.generate_calendar_page(
                year, month, None,
                photo_dirs=[f"photos/{year}/{month:02d}"],
                output_dir=paths["html_dir"],
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
                # Determine PDF output directory based on mode
                if web_mode:
                    pdf_output_dir = paths["pdf_web_dir"]
                    pdf_suffix = "_web"
                else:
                    pdf_output_dir = paths["pdf_print_dir"]
                    pdf_suffix = ""
                
                # Generate a PDF-specific HTML with absolute paths using different filename
                pdf_html_file = self.calendar_gen.generate_calendar_page_for_pdf(
                    year, month, None,
                    photo_dirs=[f"photos/{year}/{month:02d}"],
                    output_dir=paths["html_dir"],
                    use_absolute_paths=True
                )
                
                pdf_file = await self._convert_to_pdf(pdf_html_file, pdf_output_dir, year, month, web_mode)
                if pdf_file:
                    result["pdf_file"] = pdf_file
                    print(f"✅ Generated {pdf_suffix.upper() or 'PRINT'} PDF: {pdf_file}")
                    
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
    
    async def _convert_to_pdf(self, html_file: str, output_dir: str, year: int, month: int, web_mode: bool = False) -> str:
        """Convert HTML to PDF
        
        Args:
            html_file: Source HTML file
            output_dir: Base output directory
            year: Calendar year
            month: Calendar month
            web_mode: If True, creates web-optimized PDF (smaller file size)
        """
        try:
            converter = HTMLToPDFConverter("auto")
            
            # Generate PDF filename with language code and project name
            if web_mode:
                suffix = "_web"
            else:
                suffix = "_print"
            pdf_filename = f"portioid_calendar_{year}{month:02d}_{self.language}{suffix}.pdf"
            pdf_path = Path(output_dir) / pdf_filename
            
            # Convert to PDF with compression mode options
            pdf_file = await converter.convert_html_to_pdf(html_file, str(pdf_path), web_mode=web_mode)
            return pdf_file
            
        except Exception as e:
            print(f"⚠️  PDF conversion failed: {e}")
            return None
    
    async def build_year(self, year: int,
                        output_dir: str = "output", 
                        months: list = None, generate_pdf: bool = True,
                        bind_pdf: bool = False, web_mode: bool = False) -> dict:
        """Build calendar for entire year or specified months
        
        Args:
            year: Calendar year
            output_dir: Base output directory
            months: List of months to build (None = all months)
            generate_pdf: Whether to generate PDF files
            bind_pdf: Whether to bind all PDFs into single file
            web_mode: If True, creates web-optimized PDFs (smaller file sizes)
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
                year, month, generate_pdf, web_mode
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
        
        # Bind PDFs into single file if requested
        if generate_pdf and results["successful_months"] and bind_pdf:
            pdf_files = [f for f in results["generated_files"] if f and f.endswith('.pdf')]
            if pdf_files and len(pdf_files) > 1:
                try:
                    paths = self.get_output_paths(year)
                    bound_pdf_file = f"{paths['pdf_dir']}/portioid_calendar_{year}_{self.language}_complete.pdf"
                    bound_pdf = self.bind_pdfs_to_single_file(pdf_files, bound_pdf_file)
                    results["bound_pdf"] = bound_pdf
                    print(f"📚 Complete calendar PDF created: {bound_pdf}")
                except Exception as e:
                    print(f"❌ PDF binding failed: {e}")
                    if not PDF_MERGER_AVAILABLE:
                        print("   Install PyPDF2: pip install PyPDF2")
        
        return results
    
    async def build_complete(self, year: int, output_dir: str = "output", months: list = None) -> dict:
        """Complete build: HTML + both print and web PDFs + bind both versions
        
        Args:
            year: Calendar year
            output_dir: Base output directory  
            months: List of months to build (None = all months)
        """
        
        if not months:
            months = list(range(1, 13))  # All months
        
        print(f"🚀 Starting COMPLETE build for {year}")
        print(f"📅 Building {len(months)} months with HTML + Print PDFs + Web PDFs + Binds")
        
        # Step 1: Build all months with print PDFs
        print(f"\n=== STEP 1: Building Print-Quality PDFs ===")
        print_results = await self.build_year(year, output_dir, months, generate_pdf=True, bind_pdf=False, web_mode=False)
        
        # Step 2: Build all months with web PDFs (HTML already exists, so this is faster)
        print(f"\n=== STEP 2: Building Web-Optimized PDFs ===")
        web_results = await self.build_year(year, output_dir, months, generate_pdf=True, bind_pdf=False, web_mode=True)
        
        # Step 3: Bind print PDFs
        print(f"\n=== STEP 3: Binding Print PDFs ===")
        paths = self.get_output_paths(year)
        print_pdf_files = []
        for month in print_results["successful_months"]:
            pdf_file = f"{paths['pdf_print_dir']}/portioid_calendar_{year}{month:02d}_{self.language}_print.pdf"
            if Path(pdf_file).exists():
                print_pdf_files.append(pdf_file)
        
        if print_pdf_files:
            print_bound_file = f"{paths['pdf_dir']}/portioid_calendar_{year}_{self.language}_print.pdf"
            try:
                bound_print = self.bind_pdfs_to_single_file(print_pdf_files, print_bound_file)
                print(f"✅ Print calendar bound: {bound_print}")
            except Exception as e:
                print(f"⚠️ Print PDF binding failed: {e}")
                bound_print = None
        else:
            bound_print = None
            
        # Step 4: Bind web PDFs  
        print(f"\n=== STEP 4: Binding Web-Optimized PDFs ===")
        web_pdf_files = []
        for month in web_results["successful_months"]:
            pdf_file = f"{paths['pdf_web_dir']}/portioid_calendar_{year}{month:02d}_{self.language}_web.pdf"
            if Path(pdf_file).exists():
                web_pdf_files.append(pdf_file)
                
        if web_pdf_files:
            web_bound_file = f"{paths['pdf_dir']}/portioid_calendar_{year}_{self.language}_web.pdf"
            try:
                bound_web = self.bind_pdfs_to_single_file(web_pdf_files, web_bound_file)
                print(f"✅ Web calendar bound: {bound_web}")
            except Exception as e:
                print(f"⚠️ Web PDF binding failed: {e}")
                bound_web = None
        else:
            bound_web = None
        
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
            "successful_months": list(set(print_results["successful_months"] + web_results["successful_months"])),
            "failed_months": list(set(print_results["failed_months"] + web_results["failed_months"])),
            "print_pdfs": len(print_pdf_files),
            "web_pdfs": len(web_pdf_files), 
            "print_bound": bound_print,
            "web_bound": bound_web,
        }
        
        # Final summary
        print(f"\n🎉 COMPLETE BUILD SUMMARY for {year}:")
        print(f"📄 HTML files: {len(results['successful_months'])} months")
        print(f"🖨️  Print PDFs: {results['print_pdfs']} files")
        print(f"💻 Web PDFs: {results['web_pdfs']} files")
        if results['print_bound']:
            print(f"📚 Print bound: {Path(results['print_bound']).name}")
        if results['web_bound']:
            print(f"🌐 Web bound: {Path(results['web_bound']).name}")
        
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
        
        # Sort PDF files by month (assuming filename format portioid_calendar_YYYYMM_lang_print.pdf or portioid_calendar_YYYYMM_lang_web.pdf)
        def get_month_from_filename(filename):
            try:
                basename = Path(filename).stem
                # Handle new format: portioid_calendar_YYYYMM_lang_print/web
                if "_" in basename:
                    parts = basename.split("_")
                    # Look for the YYYYMM part (should be third element: portioid_calendar_YYYYMM_lang_suffix)
                    if len(parts) >= 3:
                        year_month_part = parts[2]  # portioid_calendar_YYYYMM_...
                        if len(year_month_part) >= 6 and year_month_part[:6].isdigit():
                            return int(year_month_part[4:6])  # Extract month from YYYYMM
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
    parser.add_argument('--complete', action='store_true', help="Complete build: generate HTML + both print and web PDFs + bind both versions")
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
        
        # Get paths for current language
        paths = builder.get_output_paths(args.year)
        pdf_print_dir = Path(paths['pdf_print_dir'])
        pdf_web_dir = Path(paths['pdf_web_dir'])
        pdf_output_dir = Path(paths['pdf_dir'])
        
        if not pdf_print_dir.exists() and not pdf_web_dir.exists():
            print(f"❌ No PDF directories found for language '{args.language}'")
            print(f"   Checked: {pdf_print_dir}")
            print(f"   Checked: {pdf_web_dir}")
            return 1
        
        # Find print and web PDF files separately
        print_pdfs = []
        web_pdfs = []
        
        # Look for monthly PDFs (portioid_calendar_YYYYMM_lang_print.pdf and portioid_calendar_YYYYMM_lang_web.pdf)
        for month in range(1, 13):
            month_str = f"{month:02d}"
            print_pdf = pdf_print_dir / f"portioid_calendar_{args.year}{month_str}_{args.language}_print.pdf"
            web_pdf = pdf_web_dir / f"portioid_calendar_{args.year}{month_str}_{args.language}_web.pdf"
            
            if print_pdf.exists():
                print_pdfs.append(str(print_pdf))
            if web_pdf.exists():
                web_pdfs.append(str(web_pdf))
        
        print(f"📄 Found {len(print_pdfs)} print PDFs and {len(web_pdfs)} web PDFs")
        
        if not print_pdfs and not web_pdfs:
            print(f"❌ No monthly PDF files found for {args.year}")
            return 1
        
        # Delete existing bound PDFs to ensure clean recreation
        print_bound_path = pdf_output_dir / f"portioid_calendar_{args.year}_{args.language}_print.pdf"
        web_bound_path = pdf_output_dir / f"portioid_calendar_{args.year}_{args.language}_web.pdf"
        
        if print_bound_path.exists():
            print_bound_path.unlink()
            print(f"🗑️  Removed existing print bound PDF: {print_bound_path.name}")
            
        if web_bound_path.exists():
            web_bound_path.unlink()
            print(f"🗑️  Removed existing web bound PDF: {web_bound_path.name}")
        
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
        
        # Bind web PDFs
        web_success = False
        if web_pdfs:
            try:
                print(f"\n🌐 Binding {len(web_pdfs)} web PDFs...")
                bound_web = builder.bind_pdfs_to_single_file(web_pdfs, str(web_bound_path))
                print(f"✅ Web calendar created: {Path(bound_web).name}")
                web_success = True
            except Exception as e:
                print(f"❌ Failed to bind web PDFs: {e}")
        
        # Summary
        if print_success or web_success:
            print(f"\n🎉 Bind-existing completed:")
            if print_success:
                print(f"   📚 Print bound: {print_bound_path.name}")
            if web_success:
                print(f"   🌐 Web bound: {web_bound_path.name}")
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
                # Single month build - generate both print and web PDFs unless specifically disabled
                month = months_to_build[0]
                success_count = 0
                
                if not args.no_pdf:
                    # Build print version
                    print_result = await builder.build_month(
                        args.year, month, True, False  # generate_pdf=True, web_mode=False
                    )
                    if print_result["success"]:
                        success_count += 1
                        print(f"✅ Print PDF created for {args.year}-{month:02d}")
                    else:
                        print(f"❌ Print PDF failed: {print_result.get('reason', 'unknown error')}")
                    
                    # Build web version
                    web_result = await builder.build_month(
                        args.year, month, True, True  # generate_pdf=True, web_mode=True
                    )
                    if web_result["success"]:
                        success_count += 1
                        print(f"✅ Web PDF created for {args.year}-{month:02d}")
                    else:
                        print(f"❌ Web PDF failed: {web_result.get('reason', 'unknown error')}")
                else:
                    # HTML only
                    result = await builder.build_month(
                        args.year, month, False, False
                    )
                    if result["success"]:
                        success_count = 1
                
                if success_count > 0:
                    print(f"\\n🎉 Successfully built calendar for {args.year}-{month:02d}")
                    # Update landing page with latest observation IDs
                    update_landing_page()
                else:
                    print(f"\\n❌ Failed to build calendar")
                    return 1
            else:
                # Multiple months or full year
                results = await builder.build_year(
                    args.year, args.output, 
                    months_to_build, not args.no_pdf, args.bind_pdf, args.web_pdf
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