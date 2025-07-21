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

# Import our custom modules
from calendar_generator import CalendarGenerator
from update_landing_page import update_landing_page
from qr_generator import QRGenerator
from world_map_generator import WorldMapGenerator
from html_to_pdf import HTMLToPDFConverter

class CalendarBuilder:
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "data/calendar_config.json"
        self.config = self._load_config()
        
        # Initialize components
        self.calendar_gen = CalendarGenerator(config_file)
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
    
    async def build_month(self, year: int, month: int, locations_file: str = None,
                         output_dir: str = "output", generate_pdf: bool = True) -> dict:
        """Build calendar for a single month"""
        
        print(f"\\n📅 Building calendar for {year}-{month:02d}")
        
        # Validate photos
        if not self.validate_photos_for_month(year, month):
            print(f"❌ Cannot build calendar for {year}-{month:02d}: insufficient photos")
            return {"success": False, "reason": "insufficient_photos"}
        
        try:
            # Load location data
            location_data = None
            if locations_file and Path(locations_file).exists():
                with open(locations_file, 'r') as f:
                    all_locations = json.load(f)
                    month_key = f"{year}-{month:02d}"
                    location_data = all_locations.get(month_key, {
                        "location": f"Month {month}, {year}",
                        "coordinates": "0°N, 0°E",
                        "website_url": "https://sarefo.github.io/calendar/",
                        "photographer_name": "Photographer"
                    })
            # If no locations file provided, let calendar generator read from README.md
            
            # Generate QR code
            base_url = "https://sarefo.github.io/calendar/"
            if location_data:
                base_url = location_data.get("website_url", base_url)
            qr_file = self.qr_gen.generate_calendar_qr(
                year, month, base_url,
                f"{output_dir}/assets"
            )
            print(f"✅ Generated QR code: {qr_file}")
            
            # Generate world map
            # Get location data for map generation (from README if location_data is None)
            map_location_data = location_data
            if not map_location_data:
                map_location_data = self.calendar_gen._load_location_from_readme(year, month)
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
                year, month, location_data,
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
                "location": location_data.get("location", f"Month {month}") if location_data else map_location_data.get("location", f"Month {month}")
            }
            
            # Generate PDF if requested
            if generate_pdf:
                pdf_file = await self._convert_to_pdf(html_file, output_dir)
                if pdf_file:
                    result["pdf_file"] = pdf_file
                    print(f"✅ Generated PDF: {pdf_file}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error building calendar for {year}-{month:02d}: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "reason": str(e)}
    
    async def _convert_to_pdf(self, html_file: str, output_dir: str) -> str:
        """Convert HTML to PDF"""
        try:
            converter = HTMLToPDFConverter("auto")
            
            # Generate PDF filename
            html_path = Path(html_file)
            pdf_filename = html_path.stem + ".pdf"
            pdf_path = Path(output_dir) / "print-ready" / pdf_filename
            
            # Convert to PDF
            pdf_file = await converter.convert_html_to_pdf(html_file, str(pdf_path))
            return pdf_file
            
        except Exception as e:
            print(f"⚠️  PDF conversion failed: {e}")
            return None
    
    async def build_year(self, year: int, locations_file: str = None,
                        output_dir: str = "output", 
                        months: list = None, generate_pdf: bool = True) -> dict:
        """Build calendar for entire year or specified months"""
        
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
                year, month, locations_file, output_dir, generate_pdf
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
        
        return results
    
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
    parser.add_argument('--locations', default="data/locations.json", help="Location data file")
    parser.add_argument('--output', default="output", help="Output directory")
    parser.add_argument('--no-pdf', action='store_true', help="Skip PDF generation")
    parser.add_argument('--check-photos', action='store_true', help="Only check photo availability")
    parser.add_argument('--install-deps', action='store_true', help="Install required dependencies")
    
    args = parser.parse_args()
    
    if args.install_deps:
        print("Installing dependencies...")
        deps = ["jinja2", "qrcode[pil]", "playwright"]
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
        builder = CalendarBuilder(args.config)
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
            if months_to_build and len(months_to_build) == 1:
                # Single month build
                result = await builder.build_month(
                    args.year, months_to_build[0], args.locations, 
                    args.output, not args.no_pdf
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
                    args.year, args.locations, args.output, 
                    months_to_build, not args.no_pdf
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