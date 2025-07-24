#!/usr/bin/env python3
"""
Calendar Generator
Main script for generating A3 landscape photo calendars with month overflow

Features:
- 7-column grid (Monday-Sunday)
- ISO week numbering
- Previous/next month photo overflow
- Professional print formatting
- HTML template rendering
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional
import re

# Import our custom modules
# Handle import for both module usage and direct execution
try:
    from .week_calculator import WeekCalculator
    from .world_map_generator import WorldMapGenerator
except ImportError:
    from week_calculator import WeekCalculator
    from world_map_generator import WorldMapGenerator

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("Installing required dependency: jinja2")
    os.system("pip install jinja2")
    from jinja2 import Environment, FileSystemLoader, select_autoescape

class CalendarGenerator:
    def __init__(self, config_file=None, template_dir=None, language="en"):
        self.config_file = config_file or "data/calendar_config.json"
        self.template_dir = template_dir or "templates"
        self.language = language
        self.config = self._load_config()
        self.week_calculator = WeekCalculator(config_file, language)
        self.world_map_generator = WorldMapGenerator()
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
    def _load_config(self):
        """Load calendar configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {self.config_file}")
            return self._default_config()
    
    def _default_config(self):
        """Default configuration if file not found"""
        return {
            "calendar_settings": {
                "week_start": "monday",
                "week_numbering": "iso",
                "language": "en"
            },
            "layout": {
                "format": "A3_landscape",
                "grid": {"columns": 7}
            },
            "colors": {
                "primary": "#2C3E50",
                "background": "#FFFFFF"
            }
        }
    
    def _load_photo_information(self) -> Dict[str, List[str]]:
        """Load photo information from photo_information.txt"""
        photo_info = {}
        photo_info_path = Path("photos/photo_information.txt")
        
        if not photo_info_path.exists():
            return photo_info
            
        with open(photo_info_path, 'r') as f:
            lines = f.readlines()
            
        # Skip header line
        for line in lines[1:]:
            parts = line.strip().split('\t')
            if len(parts) >= 2 and parts[1].strip():  # YYYYMM and filename exist
                yyyymm = parts[0].strip()
                filename = parts[1].strip()
                
                if yyyymm not in photo_info:
                    photo_info[yyyymm] = []
                photo_info[yyyymm].append(filename)
        
        return photo_info
    
    def _load_photo_observations(self) -> Dict[str, str]:
        """Load photo observation data from ../data/photo-observations.json"""
        observations_path = Path("../data/photo-observations.json")
        
        if not observations_path.exists():
            print(f"Warning: Photo observations file not found: {observations_path}")
            return {}
            
        try:
            with open(observations_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load photo observations: {e}")
            return {}
    
    def _load_location_from_readme(self, year: int, month: int) -> Dict[str, str]:
        """Load location information from README.md in photo folder"""
        readme_path = Path(f"photos/{year}/{month:02d}/README.md")
        
        if not readme_path.exists():
            print(f"❌ Error: README.md not found at {readme_path}")
            print(f"   Please create {readme_path} with location data:")
            print(f"   + location_en: [City, Country]")
            print(f"   + location_de: [Stadt, Land]") 
            print(f"   + location_es: [Ciudad, País]")
            print(f"   + coordinates: [Lat°N/S, Long°E/W]")
            print(f"   + year: {year}")
            raise FileNotFoundError(f"Location data required: {readme_path} not found")
        
        location_data = {}
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the README content - support both old and new format
        for line in content.split('\n'):
            line = line.strip()
            # New multi-language format
            if line.startswith('+ location_en:'):
                location_data['location_en'] = line.replace('+ location_en:', '').strip()
            elif line.startswith('+ location_de:'):
                location_data['location_de'] = line.replace('+ location_de:', '').strip()
            elif line.startswith('+ location_es:'):
                location_data['location_es'] = line.replace('+ location_es:', '').strip()
            # Legacy format (backwards compatibility)
            elif line.startswith('+ location:'):
                location_data['location'] = line.replace('+ location:', '').strip()
            elif line.startswith('+ coordinates:'):
                location_data['coordinates'] = line.replace('+ coordinates:', '').strip()
        
        # Validate required location data - no fallback values!
        missing_data = []
        placeholder_data = []
        
        # Determine which location format we're using
        location_key = f'location_{self.language}'
        if location_key not in location_data:
            # Fall back to English if the requested language isn't available
            if 'location_en' in location_data:
                location_key = 'location_en'
            elif 'location' in location_data:
                # Legacy format compatibility
                location_key = 'location'
            else:
                missing_data.append(f'location_{self.language} (or location_en)')
        
        # Check for missing location
        if location_key in location_data:
            location_value = location_data.get(location_key, '').strip()
            if not location_value:
                missing_data.append(location_key)
            elif any(placeholder in location_value for placeholder in ['[Location needed]', '[Stadt benötigt]', '[Ubicación necesaria]']):
                placeholder_data.append(location_key)
        
        # Check for missing coordinates
        if 'coordinates' not in location_data or not location_data.get('coordinates').strip():
            missing_data.append('coordinates')
        elif '[Coordinates needed]' in location_data.get('coordinates', ''):
            placeholder_data.append('coordinates')
        
        # Fail fast if data is missing or has placeholders
        if missing_data or placeholder_data:
            error_msg = []
            if missing_data:
                error_msg.append(f"Missing: {', '.join(missing_data)}")
            if placeholder_data:
                error_msg.append(f"Has placeholders: {', '.join(placeholder_data)}")
                
            print(f"❌ Error: Incomplete location data in {readme_path}")
            print(f"   {'; '.join(error_msg)}")
            print(f"   Please update the file with actual location information.")
            raise ValueError(f"Incomplete location data in {readme_path}: {'; '.join(error_msg)}")
        
        # Set the location display based on current language
        location_data['location_display'] = location_data.get(location_key, location_data.get('location_en', location_data.get('location', 'Unknown Location')))
        
        # Also keep the location field for backwards compatibility
        if 'location' not in location_data:
            location_data['location'] = location_data['location_display']
        
        return location_data
    
    def _generate_world_map_content(self, location_data: Dict[str, str]) -> str:
        """Generate SVG content for world map (inner SVG elements only)"""
        try:
            # Get full SVG from world map generator
            full_svg = self.world_map_generator.generate_world_map_svg(location_data, width=400, height=200)
            
            # Extract just the inner content (everything between <svg> and </svg>)
            import re
            match = re.search(r'<svg[^>]*>(.*?)</svg>', full_svg, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return self._fallback_world_map_content()
        except Exception as e:
            print(f"Warning: Could not generate world map: {e}")
            return self._fallback_world_map_content()
    
    def _fallback_world_map_content(self) -> str:
        """Fallback world map content if generation fails"""
        return """
        <!-- Fallback world map -->
        <rect width="400" height="200" fill="#F8FAFE" stroke="#E1E8ED" stroke-width="1"/>
        <text x="200" y="100" text-anchor="middle" font-family="Inter, sans-serif" 
              font-size="12" fill="#666">World Map</text>
        """

    def find_photo_for_date(self, target_date: date, photo_dirs: List[str], use_absolute_paths: bool = False, web_optimized: bool = False) -> Optional[str]:
        """
        Find photo for a specific date from photo directories
        Uses order from photo_information.txt: first photo = day 1, second = day 2, etc.
        
        Args:
            target_date: The date to find a photo for
            photo_dirs: List of photo directories to search
            use_absolute_paths: If True, return absolute file:// URLs instead of relative paths
            web_optimized: If True, prefer web thumbnails for faster loading
        """
        # Load photo information if not already loaded
        if not hasattr(self, '_photo_info'):
            self._photo_info = self._load_photo_information()
        
        month_key = f"{target_date.year}{target_date.month:02d}"
        day_of_month = target_date.day
        
        # Check if we have photo info for this month
        if month_key in self._photo_info:
            photos_for_month = self._photo_info[month_key]
            photo_index = day_of_month - 1  # Convert to 0-based index
            
            if photo_index < len(photos_for_month):
                filename = photos_for_month[photo_index]
                
                # Find the actual file in photo directories
                for photo_dir in photo_dirs:
                    photo_path = Path(photo_dir) / f"{filename}.jpg"
                    
                    # Check for web thumbnail if web_optimized is requested
                    if web_optimized and not use_absolute_paths:
                        web_photo_path = Path(photo_dir) / "web" / f"{filename}.jpg"
                        if web_photo_path.exists():
                            # Return relative path to web thumbnail
                            return f"../../../../{web_photo_path}"
                    
                    # Fall back to original photo
                    if photo_path.exists():
                        if use_absolute_paths:
                            # Return absolute filesystem path for PDF conversion (not file:// URI)
                            return str(photo_path.resolve())
                        else:
                            # Return relative path from output directory to source photos
                            # Account for new nested structure: output/2026/de/html/ -> photos/
                            return f"../../../../{photo_path}"
        
        # Fallback to old behavior if photo_information.txt doesn't have entry
        for photo_dir in photo_dirs:
            photo_path = Path(photo_dir)
            if not photo_path.exists():
                continue
            
            # Get all .jpg files in alphanumerical order
            jpg_files = sorted([f for f in photo_path.iterdir() 
                              if f.suffix.lower() == '.jpg'])
            
            if not jpg_files:
                continue
            
            # Map day of month to photo index (1-based)
            photo_index = day_of_month - 1  # Convert to 0-based index
            
            if photo_index < len(jpg_files):
                photo_file = jpg_files[photo_index]
                
                # Check for web thumbnail if web_optimized is requested
                if web_optimized and not use_absolute_paths:
                    web_photo_file = photo_path / "web" / photo_file.name
                    if web_photo_file.exists():
                        # Return relative path to web thumbnail
                        return f"../../../../{web_photo_file}"
                
                # Fall back to original photo
                if use_absolute_paths:
                    # Return absolute filesystem path for PDF conversion (not file:// URI)
                    return str(photo_file.resolve())
                else:
                    # Return relative path from output directory to source photos
                    # Account for new nested structure: output/2026/de/html/ -> photos/
                    return f"../../../../{photo_file}"
        
        return None
    
    def _extract_date_from_filename(self, filename: str) -> Optional[date]:
        """Extract date from filename using various patterns"""
        try:
            # Remove extension
            name = Path(filename).stem
            
            # Try various date patterns
            patterns = [
                r'(\d{4})[_-](\d{2})[_-](\d{2})',  # YYYY-MM-DD or YYYY_MM_DD
                r'(\d{4})(\d{2})(\d{2})',          # YYYYMMDD
                r'(\d{2})[_-](\d{2})[_-](\d{4})',  # DD-MM-YYYY
                r'(\d{2})[_-](\d{2})[_-](\d{2})',  # DD-MM-YY
            ]
            
            for pattern in patterns:
                match = re.search(pattern, name)
                if match:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY-MM-DD format
                        return date(int(groups[0]), int(groups[1]), int(groups[2]))
                    elif len(groups[2]) == 4:  # DD-MM-YYYY format
                        return date(int(groups[2]), int(groups[1]), int(groups[0]))
                    else:  # DD-MM-YY format
                        year = 2000 + int(groups[2]) if int(groups[2]) < 50 else 1900 + int(groups[2])
                        return date(year, int(groups[1]), int(groups[0]))
        except (ValueError, IndexError):
            pass
        
        return None
    
    def generate_perpetual_month_data(self, month: int, source_year: int = 2026, location_data: Dict = None, photo_dirs: List[str] = None, use_absolute_paths: bool = False, web_optimized: bool = False) -> Dict:
        """Generate data for a perpetual calendar month (day numbers only, no weekdays/week numbers)"""
        
        # Always load location data from README.md using source year
        readme_location = self._load_location_from_readme(source_year, month)
        location_data = {
            **readme_location,
            "website_url": "https://sarefo.github.io/calendar/",
            "photographer_name": "Photographer"
        }
        
        # Load photo observations for iNaturalist links
        photo_observations = self._load_photo_observations()
        
        # Default photo directories using source year
        if not photo_dirs:
            photo_dirs = [
                f"photos/{source_year}/{month:02d}",
                f"photos/{source_year}/{month:02d}-processed"
            ]
        
        # Get number of days in this month (use source year for calculation)
        import calendar
        days_in_month = calendar.monthrange(source_year, month)[1]
        
        # Special handling for February - always include day 29 for perpetual calendar
        if month == 2:
            days_in_month = 29
        
        # Determine grid layout based on number of days
        if days_in_month == 31:
            columns = 7  # 7x5 grid for 31-day months
            rows = 5
        else:
            columns = 6  # 6x5 grid for shorter months (28-30 days)
            rows = 5
        
        # Create simple day layout (no weekday alignment)
        weeks = []
        current_week = {"dates": []}
        
        for day in range(1, days_in_month + 1):
            # Create date object using source year for photo lookup
            # Special handling for February 29th - use 2024 (leap year)
            if month == 2 and day == 29:
                day_date = date(2024, month, day)  # Use leap year for Feb 29
            else:
                day_date = date(source_year, month, day)
            
            day_info = {
                'date': day_date,
                'day': day,
                'is_current_month': True,
                'is_previous_month': False,
                'is_next_month': False
            }
            
            # Find photo for this day
            day_info['image_path'] = self.find_photo_for_date(day_date, photo_dirs, use_absolute_paths, web_optimized)
            
            # Add iNaturalist observation ID if available
            date_key = day_date.strftime('%Y-%m-%d')
            observation_id = photo_observations.get(date_key)
            if observation_id and observation_id != "0":
                day_info['observation_id'] = observation_id
                day_info['inaturalist_url'] = f"https://www.inaturalist.org/observations/{observation_id}"
            
            current_week["dates"].append(day_info)
            
            # Create new week every 'columns' days
            if len(current_week["dates"]) == columns:
                weeks.append(current_week)
                current_week = {"dates": []}
        
        # Add any remaining days in final week
        if current_week["dates"]:
            # Fill remaining slots with empty days
            while len(current_week["dates"]) < columns:
                current_week["dates"].append({
                    'date': None,
                    'day': "",
                    'is_current_month': False,
                    'is_previous_month': False,
                    'is_next_month': False,
                    'image_path': None
                })
            weeks.append(current_week)
        
        # Generate world map SVG content
        world_map_svg = self._generate_world_map_content(location_data)
        
        # Use localization manager for month names
        try:
            from .localization_manager import LocalizationManager
        except ImportError:
            from localization_manager import LocalizationManager
        
        localization = LocalizationManager(default_language=self.language)
        month_name = localization.get_month_name(month)
        
        # Dynamic layout based on month length - OPTIMIZED FOR PERPETUAL CALENDARS
        # Elegant spacing: 7mm side margins (vs 13mm in year calendar) with proper bleed clearance
        # Available width: 420mm - 6mm (bleed) - 14mm (margins) = 400mm
        if days_in_month == 31:
            # 7x5 grid for 31-day months - calculated for elegant fit
            photo_width = 56.0  # Fits elegantly in 400mm width with spacing (400mm ÷ 7 - spacing)
            photo_height = 47.3  # Expanded from 42.4mm (+4.9mm)  
            row_height = 49.8   # Expanded from 46.4mm to accommodate larger photos
        else:
            # 6x5 grid for shorter months - wider photos with elegant spacing
            photo_width = 65.0  # Fits elegantly in 400mm width with spacing (400mm ÷ 6 - spacing)
            photo_height = 47.3  # Expanded from 42.4mm (+4.9mm)
            row_height = 49.8   # Expanded from 46.4mm to accommodate larger photos
        
        layout_info = {
            'layout_type': 'perpetual',
            'columns': columns,
            'rows_needed': rows,
            'row_height': row_height,
            'photo_width': photo_width,
            'photo_height': photo_height,
            'days_in_month': days_in_month
        }
        
        return {
            'year': None,  # No year in perpetual calendar
            'month': month,
            'month_name': month_name,
            'location': location_data.get('location', 'Unknown Location'),
            'location_display': location_data.get(f'location_{self.language}', location_data.get('location_en', location_data.get('location', 'Unknown Location'))),
            'coordinates': location_data.get('coordinates', ''),
            'weeks': weeks,
            'layout': layout_info,
            'world_map_svg': world_map_svg,
            'language': self.language,
            'website_url': location_data.get('website_url', 'https://sarefo.github.io/calendar/')
        }

    def generate_month_data(self, year: int, month: int, location_data: Dict = None, photo_dirs: List[str] = None, use_absolute_paths: bool = False, web_optimized: bool = False) -> Dict:
        """Generate all data needed for a month's calendar"""
        
        # Get calendar grid from week calculator
        grid_data = self.week_calculator.generate_calendar_grid(year, month)
        
        # Always load location data from README.md
        readme_location = self._load_location_from_readme(year, month)
        location_data = {
            **readme_location,
            "website_url": "https://sarefo.github.io/calendar/",
            "photographer_name": "Photographer"
        }
        
        # Load photo observations for iNaturalist links
        photo_observations = self._load_photo_observations()
        
        # Default photo directories using new structure
        if not photo_dirs:
            photo_dirs = [
                f"photos/{year}/{month:02d}",
                f"photos/{year}/{month:02d}-processed"
            ]
        
        # Add photo paths and observation data to each day
        for week in grid_data['weeks']:
            for day_info in week['dates']:
                # Determine which photo directory to use based on month
                current_month = day_info['date'].month
                current_year = day_info['date'].year
                
                if current_month == month and current_year == year:
                    # Current month - use main photo directories
                    day_info['image_path'] = self.find_photo_for_date(day_info['date'], photo_dirs, use_absolute_paths, web_optimized)
                else:
                    # Previous/next month - look in respective directories
                    overflow_dirs = [
                        f"photos/{current_year}/{current_month:02d}",
                        f"photos/{current_year}/{current_month:02d}-processed"
                    ]
                    day_info['image_path'] = self.find_photo_for_date(day_info['date'], overflow_dirs, use_absolute_paths, web_optimized)
                
                # Add iNaturalist observation ID if available
                date_key = day_info['date'].strftime('%Y-%m-%d')
                observation_id = photo_observations.get(date_key)
                if observation_id and observation_id != "0":
                    day_info['observation_id'] = observation_id
                    day_info['inaturalist_url'] = f"https://www.inaturalist.org/observations/{observation_id}"
                
                # Don't add placeholder for empty days
        
        # Generate world map SVG content
        world_map_svg = self._generate_world_map_content(location_data)
        
        # Combine all data
        calendar_data = {
            **grid_data,
            **location_data,
            "config": self.config,
            "language": self.language,
            "world_map_svg": world_map_svg
        }
        
        return calendar_data
    
    def render_calendar_html(self, calendar_data: Dict, template_name: str = "calendar_grid.html") -> str:
        """Render calendar data to HTML using Jinja2 template"""
        template = self.jinja_env.get_template(template_name)
        return template.render(**calendar_data)
    
    def save_calendar_html(self, html_content: str, output_path: str):
        """Save rendered HTML to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_calendar_page(self, year: int, month: int, location_data: Dict = None, 
                             photo_dirs: List[str] = None, output_dir: str = "output", use_absolute_paths: bool = False, web_optimized: bool = True) -> str:
        """Generate a complete calendar page for one month"""
        
        # Generate calendar data
        calendar_data = self.generate_month_data(year, month, location_data, photo_dirs, use_absolute_paths, web_optimized)
        
        # Render HTML
        html_content = self.render_calendar_html(calendar_data)
        
        # Save to file
        output_filename = f"{year}{month:02d}.html"
        output_path = Path(output_dir) / output_filename
        self.save_calendar_html(html_content, output_path)
        
        return str(output_path)
    
    def generate_calendar_page_for_pdf(self, year: int, month: int, location_data: Dict = None, 
                                      photo_dirs: List[str] = None, output_dir: str = "output", use_absolute_paths: bool = True) -> str:
        """Generate a calendar page specifically for PDF conversion with different filename"""
        
        # Generate calendar data (PDF should NEVER use web optimization - always full-size images)
        calendar_data = self.generate_month_data(year, month, location_data, photo_dirs, use_absolute_paths, web_optimized=False)
        
        # Render HTML
        html_content = self.render_calendar_html(calendar_data)
        
        # Save to file with PDF-specific filename
        output_filename = f"{year}{month:02d}_pdf.html"
        output_path = Path(output_dir) / output_filename
        self.save_calendar_html(html_content, output_path)
        
        return str(output_path)
    
    def generate_full_year(self, year: int, locations_file: str = None, 
                          photos_base_dir: str = "photos", output_dir: str = "output") -> List[str]:
        """Generate calendar pages for an entire year"""
        
        # Load location data
        locations_data = {}
        if locations_file and Path(locations_file).exists():
            with open(locations_file, 'r') as f:
                locations_data = json.load(f)
        
        generated_files = []
        
        for month in range(1, 13):
            # Get location data for this month
            month_key = f"{year}-{month:02d}"
            location_data = locations_data.get(month_key, {
                "location": f"Month {month}, {year}",
                "coordinates": "0°N, 0°E",
                "website_url": "example.com",
                "photographer_name": "Photographer"
            })
            
            # Determine photo directories for this month
            photo_dirs = [
                f"{photos_base_dir}/{year}/{month:02d}",
                f"{photos_base_dir}/{year}/{month:02d}-processed"
            ]
            
            # Generate calendar page
            output_file = self.generate_calendar_page(
                year, month, location_data, photo_dirs, output_dir
            )
            generated_files.append(output_file)
            
            print(f"✓ Generated: {output_file}")
        
        return generated_files

    def generate_perpetual_calendar_page(self, month: int, source_year: int = 2026, location_data: Dict = None, 
                                       photo_dirs: List[str] = None, output_dir: str = "output", use_absolute_paths: bool = False, web_optimized: bool = True) -> str:
        """Generate a complete perpetual calendar page for one month"""
        
        # Generate perpetual calendar data
        calendar_data = self.generate_perpetual_month_data(month, source_year, location_data, photo_dirs, use_absolute_paths, web_optimized)
        
        # Render HTML using perpetual template
        html_content = self.render_calendar_html(calendar_data, "calendar_grid_perpetual.html")
        
        # Save HTML
        output_file = f"{output_dir}/{month:02d}.html"
        self.save_calendar_html(html_content, output_file)
        
        return output_file
    
    def generate_perpetual_calendar_page_for_pdf(self, month: int, source_year: int = 2026, location_data: Dict = None, 
                                                photo_dirs: List[str] = None, output_dir: str = "output", use_absolute_paths: bool = True) -> str:
        """Generate a perpetual calendar page specifically for PDF conversion"""
        
        # Generate perpetual calendar data (PDF should NEVER use web optimization)
        calendar_data = self.generate_perpetual_month_data(month, source_year, location_data, photo_dirs, use_absolute_paths, web_optimized=False)
        
        # Render HTML using perpetual template
        html_content = self.render_calendar_html(calendar_data, "calendar_grid_perpetual.html")
        
        # Save with PDF-specific filename
        output_file = f"{output_dir}/{month:02d}_pdf.html"
        self.save_calendar_html(html_content, output_file)
        
        return output_file

def main():
    parser = argparse.ArgumentParser(description="Generate A3 landscape photo calendars")
    parser.add_argument('--year', type=int, default=datetime.now().year, help="Year to generate")
    parser.add_argument('--month', type=int, help="Specific month to generate (1-12)")
    parser.add_argument('--config', help="Path to calendar configuration file")
    parser.add_argument('--templates', default="templates", help="Templates directory")
    parser.add_argument('--locations', help="JSON file with location data")
    parser.add_argument('--photos', default="photos", help="Base photos directory")
    parser.add_argument('--output', default="output", help="Output directory")
    parser.add_argument('--preview', action='store_true', help="Generate preview (screen-optimized)")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = CalendarGenerator(args.config, args.templates)
    
    try:
        if args.month:
            # Generate single month
            location_data = {"location": f"Month {args.month}", "coordinates": "0°N, 0°E"}
            output_file = generator.generate_calendar_page(
                args.year, args.month, location_data, 
                [f"{args.photos}/{args.year}-{args.month:02d}"], args.output
            )
            print(f"✓ Generated calendar: {output_file}")
        else:
            # Generate full year
            output_files = generator.generate_full_year(
                args.year, args.locations, args.photos, args.output
            )
            print(f"\n✓ Generated {len(output_files)} calendar pages for {args.year}")
            print(f"✓ Output directory: {args.output}")
            
            # Show summary
            print("\nGenerated files:")
            for file_path in output_files:
                print(f"  - {file_path}")
                
    except Exception as e:
        print(f"Error generating calendar: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())