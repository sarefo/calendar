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
    from .image_optimizer import ImageOptimizer
except ImportError:
    from calendar_generator import CalendarGenerator
    from update_landing_page import update_landing_page
    from qr_generator import QRGenerator
    from world_map_generator import WorldMapGenerator
    from html_to_pdf import HTMLToPDFConverter
    from image_optimizer import ImageOptimizer

_CALENDAR_BASE_URL = "https://sarefo.github.io/calendar/"
_PDF_PROJECT_PREFIX = "portioid_calendar"

class CalendarBuilder:
    def __init__(self, config_file: str = None, language: str = "en",
                 base_output_dir: str = "output", source_year: int = None):
        self.config_file = config_file or "data/calendar_config.json"
        self.language = language
        self.base_output_dir = base_output_dir
        self.source_year = source_year  # Photo source year for perpetual calendars
        self.config = self._load_config()

        # Initialize components
        self.calendar_gen = CalendarGenerator(config_file, language=language)
        self.qr_gen = QRGenerator()
        self.map_gen = WorldMapGenerator()
        self.image_optimizer = ImageOptimizer(web_size=400, web_quality=75)

    # ------------------------------------------------------------------
    # PDF filename helpers — single source of truth for naming conventions
    # ------------------------------------------------------------------

    def _monthly_pdf_name(self, year: int, month: int, mode: str) -> str:
        """Filename for a single month's PDF (mode = 'print' or 'web')."""
        if year is None:
            return f"{_PDF_PROJECT_PREFIX}_{month:02d}_{self.language}_{mode}.pdf"
        return f"{_PDF_PROJECT_PREFIX}_{year}{month:02d}_{self.language}_{mode}.pdf"

    def _bound_pdf_name(self, year: int, mode: str) -> str:
        """Filename for a bound (full-year) PDF."""
        if year is None:
            return f"{_PDF_PROJECT_PREFIX}_perpetual_{self.language}_{mode}.pdf"
        return f"{_PDF_PROJECT_PREFIX}_{year}_{self.language}_{mode}.pdf"

    def _cover_pdf_name(self, year: int, mode: str) -> str:
        """Filename for a cover-page PDF."""
        if year is None:
            return f"{_PDF_PROJECT_PREFIX}_cover_perpetual_{self.language}_{mode}.pdf"
        return f"{_PDF_PROJECT_PREFIX}_cover_{year}_{self.language}_{mode}.pdf"
    
    def get_output_paths(self, year: int = None) -> dict:
        """Get organized output paths for a specific year and language, or perpetual calendar"""
        if year is None:
            # Perpetual calendar mode
            base_dir = f"{self.base_output_dir}/perpetual"
            lang_dir = f"{base_dir}/{self.language}"
            
            return {
                "year_dir": base_dir,
                "lang_dir": lang_dir,
                "html_dir": f"{lang_dir}/html",
                "pdf_dir": f"{lang_dir}/pdf",
                "pdf_print_dir": f"{lang_dir}/pdf/print",
                "pdf_web_dir": f"{lang_dir}/pdf/web",
                "assets_dir": f"{lang_dir}/assets",
                "qr_dir": f"{lang_dir}/assets/qr",
                "maps_dir": f"{base_dir}/assets/maps"  # Language-independent - shared across all languages
            }
        else:
            # Regular year-based calendar
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
                "maps_dir": f"{year_dir}/assets/maps"  # Language-independent - shared across all languages
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
            print(f"   BUILD WILL FAIL if any photos are missing - no placeholders allowed")
        else:
            print(f"✅ Found {photo_status['photo_count']} photos for {year}-{month:02d}")
        
        return photo_status["photo_count"] > 0
    
    async def build_month(self, year: int = None, month: int = None,
                         generate_pdf: bool = True, web_mode: bool = False) -> dict:
        """Build calendar for a single month.

        Args:
            year: Calendar year (None for perpetual calendar).
            month: Calendar month (1-12).
            generate_pdf: Whether to generate PDF files.
            web_mode: If True, creates web-optimized PDFs (smaller file sizes).
        """
        is_perpetual = year is None
        photo_year = self.source_year if is_perpetual else year

        if is_perpetual:
            if photo_year is None:
                raise ValueError("source_year must be set on CalendarBuilder for perpetual calendar builds")
            print(f"\n📅 Building {self.language.upper()} perpetual calendar for month {month:02d} "
                  f"(photos from {photo_year})")
        else:
            print(f"\n📅 Building {self.language.upper()} calendar for {year}-{month:02d}")

        paths = self.get_output_paths(year)
        for path in paths.values():
            Path(path).mkdir(parents=True, exist_ok=True)

        if not self.validate_photos_for_month(photo_year, month):
            desc = f"month {month:02d}" if is_perpetual else f"{year}-{month:02d}"
            print(f"❌ Cannot build calendar for {desc}: insufficient photos")
            return {"success": False, "reason": "insufficient_photos"}

        try:
            try:
                map_location_data = self.calendar_gen._load_location_from_readme(photo_year, month)
                print(f"✅ Loaded location data: {map_location_data['location_display']}")
            except (FileNotFoundError, ValueError) as e:
                desc = f"month {month:02d}" if is_perpetual else f"{year}-{month:02d}"
                print(f"❌ Cannot build calendar for {desc}: {e}")
                return {"success": False, "reason": f"location_data_missing: {e}"}

            # QR code — perpetual uses month-only hash, year-based uses YYYYMM hash
            if is_perpetual:
                qr_file = self.qr_gen.generate_perpetual_qr(month, _CALENDAR_BASE_URL,
                                                             paths["qr_dir"], language=self.language)
                map_key = f"map-{month:02d}.svg"
            else:
                qr_file = self.qr_gen.generate_calendar_qr(year, month, _CALENDAR_BASE_URL,
                                                            paths["qr_dir"], language=self.language)
                map_key = f"map-{year}-{month:02d}.svg"
            print(f"✅ Generated QR code: {qr_file}")

            # World map — shared across languages (generated once)
            map_file_path = f"{paths['maps_dir']}/{map_key}"
            if Path(map_file_path).exists():
                print(f"✅ Using existing world map: {map_file_path}")
                map_file = map_file_path
            else:
                map_file = self.map_gen.save_map_svg(map_location_data, map_file_path)
                print(f"✅ Generated new world map: {map_file}")

            thumb_result = self.image_optimizer.optimize_month_photos(photo_year, month)
            if thumb_result["success"]:
                print(f"✅ Generated {thumb_result['processed']} web thumbnails")
            else:
                print(f"⚠️  Web thumbnails: {thumb_result['reason']}")

            photo_dirs = [f"photos/{photo_year}/{month:02d}"]

            if is_perpetual:
                html_file = self.calendar_gen.generate_perpetual_calendar_page(
                    month, photo_year, None, photo_dirs=photo_dirs,
                    output_dir=paths["html_dir"], use_absolute_paths=False
                )
            else:
                html_file = self.calendar_gen.generate_calendar_page(
                    year, month, None, photo_dirs=photo_dirs,
                    output_dir=paths["html_dir"], use_absolute_paths=False
                )
            print(f"✅ Generated HTML: {html_file}")

            result = {
                "success": True,
                "year": year,
                "month": month,
                "html_file": html_file,
                "qr_file": qr_file,
                "map_file": map_file,
                "location": map_location_data.get("location", f"Month {month}"),
            }

            if generate_pdf:
                pdf_output_dir = paths["pdf_web_dir"] if web_mode else paths["pdf_print_dir"]

                if is_perpetual:
                    pdf_html_file = self.calendar_gen.generate_perpetual_calendar_page(
                        month, photo_year, None, photo_dirs=photo_dirs,
                        output_dir=paths["html_dir"], use_absolute_paths=True
                    )
                else:
                    pdf_html_file = self.calendar_gen.generate_calendar_page(
                        year, month, None, photo_dirs=photo_dirs,
                        output_dir=paths["html_dir"], use_absolute_paths=True
                    )

                pdf_file = await self._convert_to_pdf(pdf_html_file, pdf_output_dir, year, month, web_mode)
                if pdf_file:
                    mode_label = "WEB" if web_mode else "PRINT"
                    result["pdf_file"] = pdf_file
                    print(f"✅ Generated {mode_label} PDF: {pdf_file}")

                try:
                    if pdf_html_file != html_file:
                        Path(pdf_html_file).unlink()
                except Exception:
                    pass

            return result

        except (FileNotFoundError, ValueError) as e:
            print(f"❌ Location data error for {year or 'perpetual'}-{month:02d}: {e}")
            return {"success": False, "reason": f"location_data_error: {e}"}
        except Exception as e:
            print(f"❌ Error building calendar for {year or 'perpetual'}-{month:02d}: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "reason": str(e)}
    
    async def _convert_to_pdf(self, html_file: str, output_dir: str, year: int, month: int,
                             web_mode: bool = False) -> str:
        """Convert an HTML file to PDF and return the output path (or None on failure)."""
        try:
            converter = HTMLToPDFConverter("auto")
            mode = "web" if web_mode else "print"
            pdf_path = Path(output_dir) / self._monthly_pdf_name(year, month, mode)
            return await converter.convert_html_to_pdf(html_file, str(pdf_path), web_mode=web_mode)
        except Exception as e:
            print(f"⚠️  PDF conversion failed: {e}")
            return None
    
    async def build_year(self, year: int = None,
                        output_dir: str = "output", 
                        months: list = None, generate_pdf: bool = True,
                        bind_pdf: bool = False, web_mode: bool = False) -> dict:
        """Build calendar for entire year or specified months (supports perpetual calendar)
        
        Args:
            year: Calendar year (None for perpetual calendar)
            output_dir: Base output directory
            months: List of months to build (None = all months)
            generate_pdf: Whether to generate PDF files
            bind_pdf: Whether to bind all PDFs into single file
            web_mode: If True, creates web-optimized PDFs (smaller file sizes)
        """
        
        if not months:
            months = list(range(1, 13))  # All months
        
        if year:
            print(f"\\n🏗️  Building calendar for {year}")
        else:
            print(f"\\n🏗️  Building perpetual calendar")
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
        calendar_type = f"{year}" if year else "perpetual calendar"
        print(f"\\n📊 Build Summary for {calendar_type}:")
        print(f"✅ Successful: {len(results['successful_months'])} months")
        if results["failed_months"]:
            print(f"❌ Failed: {len(results['failed_months'])} months")
        
        # Bind PDFs into single file if requested
        if generate_pdf and results["successful_months"] and bind_pdf:
            pdf_files = [f for f in results["generated_files"] if f and f.endswith('.pdf')]
            if pdf_files and len(pdf_files) > 1:
                try:
                    paths = self.get_output_paths(year)
                    mode = "web" if web_mode else "print"
                    bound_pdf_file = f"{paths['pdf_dir']}/{self._bound_pdf_name(year, mode)}"
                    bound_pdf = self.bind_pdfs_to_single_file(pdf_files, bound_pdf_file)
                    results["bound_pdf"] = bound_pdf
                    print(f"📚 Complete calendar PDF created: {bound_pdf}")
                except Exception as e:
                    print(f"❌ PDF binding failed: {e}")
                    if not PDF_MERGER_AVAILABLE:
                        print("   Install PyPDF2: pip install PyPDF2")
        
        return results
    
    async def build_complete(self, year: int = None, output_dir: str = "output", months: list = None) -> dict:
        """Complete build: HTML + both print and web PDFs + bind both versions + cover page
        
        Args:
            year: Calendar year (None for perpetual calendar)
            output_dir: Base output directory  
            months: List of months to build (None = all months)
        """
        
        if not months:
            months = list(range(1, 13))  # All months
        
        if year:
            print(f"🚀 Starting COMPLETE build for {year}")
        else:
            print(f"🚀 Starting COMPLETE build for perpetual calendar")
        print(f"📅 Building {len(months)} months with HTML + Print PDFs + Web PDFs + Binds + Cover")
        
        # Step 1: Build all months with print PDFs
        print(f"\n=== STEP 1: Building Print-Quality PDFs ===")
        print_results = await self.build_year(year, output_dir, months, generate_pdf=True, bind_pdf=False, web_mode=False)
        
        # Step 2: Build all months with web PDFs (HTML already exists, so this is faster)
        print(f"\n=== STEP 2: Building Web-Optimized PDFs ===")
        web_results = await self.build_year(year, output_dir, months, generate_pdf=True, bind_pdf=False, web_mode=True)
        
        # Step 3: Generate cover page (only for full 12-month builds)
        # For year-based calendars the cover uses photos from that year;
        # for perpetual calendars it uses self.source_year.
        cover_source_year = year if year else self.source_year
        cover_print_result = None
        cover_web_result = None
        if len(months) == 12:  # Only generate cover for complete calendar
            print(f"\n=== STEP 3: Generating Cover Page ===")
            try:
                cover_print_result = await self.build_cover_page(year, cover_source_year, True, False)
                if cover_print_result["success"]:
                    print(f"✅ Print cover page generated")
                else:
                    print(f"⚠️ Print cover page failed: {cover_print_result.get('reason', 'unknown error')}")

                cover_web_result = await self.build_cover_page(year, cover_source_year, True, True)
                if cover_web_result["success"]:
                    print(f"✅ Web cover page generated")
                else:
                    print(f"⚠️ Web cover page failed: {cover_web_result.get('reason', 'unknown error')}")

            except Exception as e:
                print(f"⚠️ Cover page generation failed: {e}")
        else:
            print(f"\n=== STEP 3: Skipping Cover Page (partial build: {len(months)} months) ===")
        
        # Step 4: Bind print PDFs (include cover if generated)
        print(f"\n=== STEP 4: Binding Print PDFs ===")
        paths = self.get_output_paths(year)
        print_pdf_files = []
        
        # Add cover page PDF first if it exists
        if cover_print_result and cover_print_result.get("success") and cover_print_result.get("pdf_file"):
            cover_pdf = cover_print_result["pdf_file"]
            if Path(cover_pdf).exists():
                print_pdf_files.append(cover_pdf)
                print(f"   Including cover page: {Path(cover_pdf).name}")
        
        # Add monthly PDFs
        for month in print_results["successful_months"]:
            pdf_file = f"{paths['pdf_print_dir']}/{self._monthly_pdf_name(year, month, 'print')}"
            if Path(pdf_file).exists():
                print_pdf_files.append(pdf_file)

        if print_pdf_files:
            print_bound_file = f"{paths['pdf_dir']}/{self._bound_pdf_name(year, 'print')}"
            try:
                bound_print = self.bind_pdfs_to_single_file(print_pdf_files, print_bound_file)
                print(f"✅ Print calendar bound: {bound_print}")
            except Exception as e:
                print(f"⚠️ Print PDF binding failed: {e}")
                bound_print = None
        else:
            bound_print = None

        # Step 5: Bind web PDFs (include cover if generated)
        print(f"\n=== STEP 5: Binding Web-Optimized PDFs ===")
        web_pdf_files = []

        # Add cover page PDF first if it exists
        if cover_web_result and cover_web_result.get("success") and cover_web_result.get("pdf_file"):
            cover_pdf = cover_web_result["pdf_file"]
            if Path(cover_pdf).exists():
                web_pdf_files.append(cover_pdf)
                print(f"   Including cover page: {Path(cover_pdf).name}")

        # Add monthly PDFs
        for month in web_results["successful_months"]:
            pdf_file = f"{paths['pdf_web_dir']}/{self._monthly_pdf_name(year, month, 'web')}"
            if Path(pdf_file).exists():
                web_pdf_files.append(pdf_file)

        if web_pdf_files:
            web_bound_file = f"{paths['pdf_dir']}/{self._bound_pdf_name(year, 'web')}"
            try:
                bound_web = self.bind_pdfs_to_single_file(web_pdf_files, web_bound_file)
                print(f"✅ Web calendar bound: {bound_web}")
            except Exception as e:
                print(f"⚠️ Web PDF binding failed: {e}")
                bound_web = None
        else:
            bound_web = None
        
        # Step 6: Update landing page
        print(f"\n=== STEP 6: Updating Landing Page ===")
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
        calendar_type = f"{year}" if year else "perpetual calendar"
        print(f"\n🎉 COMPLETE BUILD SUMMARY for {calendar_type}:")
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
    
    async def build_cover_page(self, year: int = None, source_year: int = None,
                              generate_pdf: bool = True, web_mode: bool = False) -> dict:
        """Build cover page for calendar.

        Args:
            year: Calendar year (None for perpetual calendar).
            source_year: Year whose photos to use. Defaults to self.source_year if not supplied.
            generate_pdf: Whether to generate PDF files.
            web_mode: If True, creates web-optimized PDFs (smaller file sizes).
        """
        if source_year is None:
            source_year = self.source_year
        if source_year is None:
            raise ValueError("source_year must be provided (either directly or via CalendarBuilder.source_year)")
        
        if year:
            print(f"\n📖 Building {self.language.upper()} cover page for {year}")
        else:
            print(f"\n📖 Building {self.language.upper()} perpetual cover page")
        
        # Get organized output paths
        paths = self.get_output_paths(year)
        
        # Create all necessary directories
        for path in paths.values():
            Path(path).mkdir(parents=True, exist_ok=True)
        
        try:
            # Generate cover page HTML
            html_file = self.calendar_gen.generate_cover_page(
                year=year,
                source_year=source_year,
                output_dir=paths["html_dir"],
                use_absolute_paths=False
            )
            print(f"✅ Generated cover HTML: {html_file}")
            
            result = {
                "success": True,
                "year": year,
                "html_file": html_file,
                "type": "cover"
            }
            
            # Generate PDF if requested
            if generate_pdf:
                # Generate PDF-specific HTML with absolute paths
                pdf_html_file = self.calendar_gen.generate_cover_page(
                    year=year,
                    source_year=source_year,
                    output_dir=paths["html_dir"],
                    use_absolute_paths=True
                )
                
                # Determine PDF output directory and filename based on mode
                pdf_output_dir = paths["pdf_web_dir"] if web_mode else paths["pdf_print_dir"]
                mode = "web" if web_mode else "print"
                pdf_filename = self._cover_pdf_name(year, mode)
                pdf_path = Path(pdf_output_dir) / pdf_filename
                
                try:
                    converter = HTMLToPDFConverter("auto")
                    pdf_file = await converter.convert_html_to_pdf(pdf_html_file, str(pdf_path), web_mode=web_mode)
                    if pdf_file:
                        result["pdf_file"] = pdf_file
                        print(f"✅ Generated {'web' if web_mode else 'print'} cover PDF: {pdf_filename}")
                    else:
                        print(f"⚠️  Cover PDF generation failed")
                        result["pdf_error"] = "conversion_failed"
                except Exception as e:
                    print(f"⚠️  Cover PDF conversion failed: {e}")
                    result["pdf_error"] = str(e)
                
                # Clean up PDF-specific HTML file
                try:
                    if pdf_html_file != html_file:
                        Path(pdf_html_file).unlink()
                except:
                    pass
            
            return result
            
        except Exception as e:
            print(f"❌ Error building cover page: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "reason": str(e)}
    
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
            try:
                output_path.unlink()
                print(f"🗑️  Removed existing file: {output_path.name}")
            except PermissionError:
                raise PermissionError(f"Cannot overwrite existing PDF file (may be open in PDF viewer): {output_path.name}. Please close any PDF viewers and try again.")
            except Exception as e:
                raise Exception(f"Error removing existing PDF file: {e}")
        
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
    parser.add_argument('--year', required=True,
                        help="Year to build (use 'perpetual' for perpetual calendar or a numeric year like 2026)")
    parser.add_argument('--source-year', type=int,
                        help="Year whose photos to use for perpetual calendars and cover pages "
                             "(defaults to --year for year-based builds)")
    parser.add_argument('--months', help="Comma-separated list of months (e.g., '1,2,3' or just '1')")
    parser.add_argument('--config', help="Path to calendar configuration file")
    parser.add_argument('--language', default='en',
                        help="Language(s) - single (e.g., 'en') or comma-separated (e.g., 'en,de,es')")
    parser.add_argument('--output', default="output", help="Output directory")
    parser.add_argument('--no-pdf', action='store_true', help="Skip PDF generation")
    parser.add_argument('--complete', action='store_true',
                        help="Complete build: HTML + print PDFs + web PDFs + bind + cover page")
    parser.add_argument('--cover', action='store_true', help="Generate cover page only")
    parser.add_argument('--bind-pdf', action='store_true', help="Bind all monthly PDFs into single file")
    parser.add_argument('--bind-existing', action='store_true',
                        help="Only bind existing PDFs without regenerating")

    args = parser.parse_args()
    
    # Track whether --year was explicitly provided (before conversion)
    year_provided = args.year is not None

    # Convert year argument to appropriate type
    if args.year:
        if args.year.lower() == 'perpetual':
            args.year = None  # None indicates perpetual calendar
        else:
            try:
                args.year = int(args.year)
            except ValueError:
                print(f"❌ Invalid year: '{args.year}'. Use a numeric year (e.g., 2026) or 'perpetual'")
                return 1

    # Require explicit --year parameter (either numeric year or "perpetual")
    if not year_provided:
        print("❌ --year parameter is required. Use a numeric year (e.g., --year 2026) or --year perpetual")
        print("\nExamples:")
        print("  python3 build_calendar.py --year 2026 --complete")
        print("  python3 build_calendar.py --year perpetual --complete --source-year 2026")
        print("  python3 build_calendar.py --year perpetual --months 1,2,3 --source-year 2026")
        return 1

    # Resolve source_year: for year-based builds default to the build year itself;
    # for perpetual builds it must be supplied explicitly.
    source_year = args.source_year
    if args.year is not None and source_year is None:
        source_year = args.year  # year-based build: photos come from the same year
    if args.year is None and source_year is None:
        print("❌ Perpetual calendar builds require --source-year (e.g., --source-year 2026)")
        return 1
    
    # Check if no meaningful arguments provided - show usage
    meaningful_args = [
        year_provided, args.months, args.complete, args.cover, args.bind_pdf, args.bind_existing
    ]
    if not any(meaningful_args):
        parser.print_help()
        print("\nExamples:")
        print("  python3 build_calendar.py --year 2026 --complete                    # Complete build for 2026 with cover")
        print("  python3 build_calendar.py --cover --year 2026 --language de         # German cover page for 2026")
        print("  python3 build_calendar.py --cover --year perpetual --language es    # Spanish perpetual cover page")
        print("  python3 build_calendar.py --year perpetual --months 1,2,3 --language en,de # Perpetual months 1-3 in English and German")
        print("  python3 build_calendar.py --months 6 --year 2026                   # Single month (June 2026)")
        print("  python3 build_calendar.py --complete --year perpetual --language de # German perpetual calendar")
        print("  python3 build_calendar.py --year perpetual --language de,en,es --no-pdf # Update perpetual HTML only")
        print("  python3 build_calendar.py --bind-existing --year 2026               # Bind existing 2026 PDFs")
        return 0
    
    # Parse languages (support comma-separated list)
    languages = [lang.strip() for lang in args.language.split(',')]
    # Derive supported languages from LocalizationManager (config-driven, not hardcoded)
    try:
        from localization_manager import LocalizationManager
    except ImportError:
        try:
            from .localization_manager import LocalizationManager
        except ImportError:
            LocalizationManager = None

    valid_languages = ['en', 'de', 'es']  # fallback if import fails
    if LocalizationManager is not None:
        try:
            valid_languages = LocalizationManager().get_supported_languages()
        except Exception:
            pass

    for lang in languages:
        if lang not in valid_languages:
            print(f"❌ Invalid language: {lang}. Supported languages: {', '.join(valid_languages)}")
            return 1
    
    # Handle cover page only mode
    if args.cover:
        print(f"📖 Generating cover page{'s' if len(languages) > 1 else ''}")
        
        # Process each language
        async def build_covers():
            overall_success = True
            
            for language in languages:
                print(f"\n{'='*50}")
                print(f"Building cover page for language: {language.upper()}")
                print(f"{'='*50}")
                
                # Initialize builder for this language
                try:
                    builder = CalendarBuilder(args.config, language, source_year=source_year)
                except Exception as e:
                    print(f"Failed to initialize builder for {language}: {e}")
                    overall_success = False
                    continue
                
                success_count = 0
                
                if not args.no_pdf:
                    # Build print cover page
                    print_result = await builder.build_cover_page(args.year, source_year, True, False)
                    if print_result["success"]:
                        success_count += 1
                        cover_type = f"cover for {args.year}" if args.year else "perpetual cover"
                        print(f"✅ Print cover created for {cover_type} in {language.upper()}")
                    else:
                        print(f"❌ Print cover failed for {language.upper()}: {print_result.get('reason', 'unknown error')}")
                        overall_success = False

                    # Build web cover page
                    web_result = await builder.build_cover_page(args.year, source_year, True, True)
                    if web_result["success"]:
                        success_count += 1
                        cover_type = f"cover for {args.year}" if args.year else "perpetual cover"
                        print(f"✅ Web cover created for {cover_type} in {language.upper()}")
                    else:
                        print(f"❌ Web cover failed for {language.upper()}: {web_result.get('reason', 'unknown error')}")
                        overall_success = False
                else:
                    # HTML only
                    result = await builder.build_cover_page(args.year, source_year, False, False)
                    if result["success"]:
                        success_count = 1
                        cover_type = f"cover for {args.year}" if args.year else "perpetual cover"
                        print(f"✅ HTML cover created for {cover_type} in {language.upper()}")
                    else:
                        print(f"❌ Cover failed for {language.upper()}: {result.get('reason', 'unknown error')}")
                        overall_success = False
                
                if success_count > 0:
                    print(f"✅ Successfully built cover page in {language.upper()}")
            
            # Final summary
            if overall_success:
                print(f"\n🎉 Successfully built cover pages for all languages: {', '.join(lang.upper() for lang in languages)}")
                return 0
            else:
                print(f"\n❌ Some cover builds failed. Check output above for details.")
                return 1
        
        # Run cover build
        return asyncio.run(build_covers())
    
    # Handle bind-existing mode
    if args.bind_existing:
        if not PDF_MERGER_AVAILABLE:
            print("❌ PDF merger not available.")
            print(f"Import errors: {PDF_IMPORT_ERROR}")
            print("Try installing: pip install pypdf")
            return 1
        
        if args.year:
            print(f"🔗 Binding existing PDFs for {args.year}")
        else:
            print("🔗 Binding existing PDFs for perpetual calendar")
        
        # Process each language
        for language in languages:
            print(f"\n--- Processing language: {language.upper()} ---")
            
            # Initialize builder for this language
            try:
                builder = CalendarBuilder(args.config, language)
            except Exception as e:
                print(f"Failed to initialize builder for {language}: {e}")
                continue
            
            # Get paths for current language
            paths = builder.get_output_paths(args.year)
            pdf_print_dir = Path(paths['pdf_print_dir'])
            pdf_web_dir = Path(paths['pdf_web_dir'])
            pdf_output_dir = Path(paths['pdf_dir'])
            
            if not pdf_print_dir.exists() and not pdf_web_dir.exists():
                print(f"❌ No PDF directories found for language '{language}'")
                print(f"   Checked: {pdf_print_dir}")
                print(f"   Checked: {pdf_web_dir}")
                continue
            
            # Find print and web PDF files separately
            print_pdfs = []
            web_pdfs = []
            
            # Look for cover page PDFs first
            cover_print_pdf = pdf_print_dir / builder._cover_pdf_name(args.year, "print")
            cover_web_pdf = pdf_web_dir / builder._cover_pdf_name(args.year, "web")
            
            cover_print_exists = cover_print_pdf.exists()
            cover_web_exists = cover_web_pdf.exists()
            
            if not cover_print_exists and not cover_web_exists:
                period_name = str(args.year) if args.year else "perpetual calendar"
                print(f"❌ Cover page PDF not found for {period_name} in {language}")
                print(f"   Expected print: {cover_print_pdf}")
                print(f"   Expected web: {cover_web_pdf}")
                print(f"   Run with --cover option first to generate cover page")
                continue
            
            # Add cover page PDFs first (they should appear first in bound PDF)
            if cover_print_exists:
                print_pdfs.append(str(cover_print_pdf))
            if cover_web_exists:
                web_pdfs.append(str(cover_web_pdf))
            
            # Look for monthly PDFs
            for month in range(1, 13):
                print_pdf = pdf_print_dir / builder._monthly_pdf_name(args.year, month, "print")
                web_pdf = pdf_web_dir / builder._monthly_pdf_name(args.year, month, "web")
                if print_pdf.exists():
                    print_pdfs.append(str(print_pdf))
                if web_pdf.exists():
                    web_pdfs.append(str(web_pdf))
            
            # Report what was found
            cover_count = int(cover_print_exists) + int(cover_web_exists)
            monthly_print_count = len(print_pdfs) - int(cover_print_exists)
            monthly_web_count = len(web_pdfs) - int(cover_web_exists)
            
            print(f"📄 Found cover page: {cover_count}/2 formats")
            print(f"📄 Found {monthly_print_count} monthly print PDFs and {monthly_web_count} monthly web PDFs")
            
            if not print_pdfs and not web_pdfs:
                period_name = str(args.year) if args.year else "perpetual calendar"
                print(f"❌ No monthly PDF files found for {period_name} in {language}")
                continue
            
            # Delete existing bound PDFs to ensure clean recreation (with error handling)
            print_bound_path = pdf_output_dir / builder._bound_pdf_name(args.year, "print")
            web_bound_path = pdf_output_dir / builder._bound_pdf_name(args.year, "web")
            
            # Try to remove existing print bound PDF
            if print_bound_path.exists():
                try:
                    print_bound_path.unlink()
                    print(f"🗑️  Removed existing print bound PDF: {print_bound_path.name}")
                except PermissionError:
                    print(f"⚠️  Cannot remove existing print bound PDF (file may be open): {print_bound_path.name}")
                    print(f"   Please close any PDF viewers and try again, or rename the existing file")
                    continue
                except Exception as e:
                    print(f"⚠️  Error removing existing print bound PDF: {e}")
                    continue
                    
            # Try to remove existing web bound PDF
            if web_bound_path.exists():
                try:
                    web_bound_path.unlink()
                    print(f"🗑️  Removed existing web bound PDF: {web_bound_path.name}")
                except PermissionError:
                    print(f"⚠️  Cannot remove existing web bound PDF (file may be open): {web_bound_path.name}")
                    print(f"   Please close any PDF viewers and try again, or rename the existing file")
                    continue
                except Exception as e:
                    print(f"⚠️  Error removing existing web bound PDF: {e}")
                    continue
            
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
            
            # Summary for this language
            if print_success or web_success:
                print(f"✅ Bind-existing completed for {language.upper()}:")
                if print_success:
                    print(f"   📚 Print bound: {print_bound_path.name}")
                if web_success:
                    print(f"   🌐 Web bound: {web_bound_path.name}")
        
        return 0
    
    # Determine months to build
    months_to_build = []
    if args.months:
        months_to_build = [int(m.strip()) for m in args.months.split(',')]
    else:
        months_to_build = None  # All months
    
    # Build calendar(s) - process each language
    async def build():
        try:
            overall_success = True
            
            for language in languages:
                print(f"\n{'='*50}")
                print(f"Building calendar for language: {language.upper()}")
                print(f"{'='*50}")
                
                # Initialize builder for this language
                try:
                    builder = CalendarBuilder(args.config, language, source_year=source_year)
                except Exception as e:
                    print(f"Failed to initialize builder for {language}: {e}")
                    overall_success = False
                    continue
                
                if args.complete:
                    # Complete build: HTML + both print and ultra PDFs + bind both
                    results = await builder.build_complete(args.year, args.output, months_to_build)
                    
                    if results["successful_months"]:
                        build_type = f"{args.year}" if args.year else "perpetual calendar"
                        print(f"✅ Complete build finished successfully for {build_type} in {language.upper()}!")
                    else:
                        print(f"❌ Complete build failed for {language.upper()}")
                        overall_success = False
                
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
                            month_display = f"{month:02d}" if not args.year else f"{args.year}-{month:02d}"
                            print(f"✅ Print PDF created for {month_display} in {language.upper()}")
                        else:
                            print(f"❌ Print PDF failed for {language.upper()}: {print_result.get('reason', 'unknown error')}")
                            overall_success = False
                        
                        # Build web version
                        web_result = await builder.build_month(
                            args.year, month, True, True  # generate_pdf=True, web_mode=True
                        )
                        if web_result["success"]:
                            success_count += 1
                            month_display = f"{month:02d}" if not args.year else f"{args.year}-{month:02d}"
                            print(f"✅ Web PDF created for {month_display} in {language.upper()}")
                        else:
                            print(f"❌ Web PDF failed for {language.upper()}: {web_result.get('reason', 'unknown error')}")
                            overall_success = False
                    else:
                        # HTML only
                        result = await builder.build_month(
                            args.year, month, False, False
                        )
                        if result["success"]:
                            success_count = 1
                        else:
                            overall_success = False
                    
                    if success_count > 0:
                        build_type = f"perpetual calendar month {month:02d}" if not args.year else f"calendar for {args.year}-{month:02d}"
                        print(f"✅ Successfully built {build_type} in {language.upper()}")
                else:
                    # Multiple months or full year - build both print and web PDFs by default
                    if not args.no_pdf:
                        # Build print PDFs
                        print(f"\n=== Building Print-Quality PDFs for {language.upper()} ===")
                        print_results = await builder.build_year(
                            args.year, args.output, 
                            months_to_build, True, False, False  # generate_pdf=True, bind_pdf=False, web_mode=False
                        )
                        
                        # Build web PDFs
                        print(f"\n=== Building Web-Optimized PDFs for {language.upper()} ===")
                        web_results = await builder.build_year(
                            args.year, args.output, 
                            months_to_build, True, False, True  # generate_pdf=True, bind_pdf=False, web_mode=True
                        )
                        
                        # Combine results
                        results = {
                            "year": print_results["year"],
                            "successful_months": list(set(print_results["successful_months"] + web_results["successful_months"])),
                            "failed_months": list(set(print_results["failed_months"] + web_results["failed_months"])),
                            "generated_files": print_results["generated_files"] + web_results["generated_files"]
                        }
                        
                        # Handle PDF binding if requested
                        if args.bind_pdf and results["successful_months"]:
                            print(f"\n=== Binding PDFs for {language.upper()} ===")
                            paths = builder.get_output_paths(args.year)
                            
                            # Bind print PDFs
                            print_pdf_files = []
                            for month in results["successful_months"]:
                                pdf_file = f"{paths['pdf_print_dir']}/{builder._monthly_pdf_name(args.year, month, 'print')}"
                                if Path(pdf_file).exists():
                                    print_pdf_files.append(pdf_file)

                            if print_pdf_files:
                                print_bound_file = f"{paths['pdf_dir']}/{builder._bound_pdf_name(args.year, 'print')}"
                                try:
                                    bound_print = builder.bind_pdfs_to_single_file(print_pdf_files, print_bound_file)
                                    print(f"✅ Print calendar bound: {bound_print}")
                                    results["bound_print_pdf"] = bound_print
                                except Exception as e:
                                    print(f"⚠️ Print PDF binding failed: {e}")
                                    overall_success = False

                            # Bind web PDFs
                            web_pdf_files = []
                            for month in results["successful_months"]:
                                pdf_file = f"{paths['pdf_web_dir']}/{builder._monthly_pdf_name(args.year, month, 'web')}"
                                if Path(pdf_file).exists():
                                    web_pdf_files.append(pdf_file)

                            if web_pdf_files:
                                web_bound_file = f"{paths['pdf_dir']}/{builder._bound_pdf_name(args.year, 'web')}"
                                try:
                                    bound_web = builder.bind_pdfs_to_single_file(web_pdf_files, web_bound_file)
                                    print(f"✅ Web calendar bound: {bound_web}")
                                    results["bound_web_pdf"] = bound_web
                                except Exception as e:
                                    print(f"⚠️ Web PDF binding failed: {e}")
                                    overall_success = False
                    else:
                        # HTML only
                        results = await builder.build_year(
                            args.year, args.output, 
                            months_to_build, False, False, False  # generate_pdf=False, bind_pdf=False, web_mode=False
                        )
                    
                    # Save build report
                    builder.create_build_report(results)
                    
                    if results["failed_months"]:
                        print(f"⚠️  Some months failed to build for {language.upper()}: {results['failed_months']}")
                        overall_success = False
                    else:
                        build_type = f"{args.year}" if args.year else "perpetual calendar"
                        print(f"✅ Successfully built calendar for {build_type} in {language.upper()}")
            
            # Update landing page once after all languages are processed
            if overall_success:
                try:
                    update_landing_page()
                    print(f"\n✅ Landing page updated with latest observation IDs")
                except Exception as e:
                    print(f"\n⚠️ Landing page update failed: {e}")
            
            # Final summary
            if overall_success:
                print(f"\n🎉 Successfully built calendars for all languages: {', '.join(lang.upper() for lang in languages)}")
                return 0
            else:
                print(f"\n❌ Some builds failed. Check output above for details.")
                return 1
            
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