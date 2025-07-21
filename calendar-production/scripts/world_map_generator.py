#!/usr/bin/env python3
"""
World Map Generator for Calendar Headers
Creates simple SVG world maps with location markers

Uses simplified world outline for print compatibility
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Tuple

class WorldMapGenerator:
    def __init__(self):
        # Load the proper world map SVG from data directory
        self.world_svg_path = Path("data/world.svg")
        # Use Natural Earth / Robinson projection coordinate system
        # viewBox for the world.svg: "200 0 1800 857" (width=1800, height=857)
        self.world_width = 1800
        self.world_height = 857
        self.world_viewbox_x = 200
        self.world_viewbox_y = 0
    
    def coordinates_to_svg(self, lat: float, lon: float, width: int = 400, height: int = 200) -> Tuple[float, float]:
        """Convert latitude/longitude to SVG coordinates"""
        # Simple equirectangular projection
        x = (lon + 180) * (width / 360)
        y = (90 - lat) * (height / 180)
        return x, y
    
    def parse_coordinates(self, coord_str: str) -> Tuple[float, float]:
        """
        Parse coordinate string like "4.25°S, 79.23°W" or "8°017′03″S 115°035′021″E"
        Returns (latitude, longitude) as floats
        """
        try:
            import re
            
            # Handle degree-minute-second format with ′ and ″ symbols
            coord_str = coord_str.replace('″', '').replace('′', ' ')  # Remove seconds, convert minutes to space
            
            # Extract latitude and longitude patterns
            # Look for patterns like "8°017 03 S" or "4.25°S"
            lat_match = re.search(r'([0-9.]+)(?:°([0-9]+)\s*([0-9]+))?\s*[SN]', coord_str)
            lon_match = re.search(r'([0-9.]+)(?:°([0-9]+)\s*([0-9]+))?\s*[EW]', coord_str)
            
            if not lat_match or not lon_match:
                # Fall back to simple decimal parsing
                parts = coord_str.replace('°', '').replace(' ', '').split(',')
                if len(parts) != 2:
                    raise ValueError(f"Invalid coordinate format: {coord_str}")
                
                # Parse latitude
                lat_str = parts[0]
                if lat_str.endswith('N'):
                    lat = float(lat_str[:-1])
                elif lat_str.endswith('S'):
                    lat = -float(lat_str[:-1])
                else:
                    lat = float(lat_str)
                
                # Parse longitude
                lon_str = parts[1]
                if lon_str.endswith('E'):
                    lon = float(lon_str[:-1])
                elif lon_str.endswith('W'):
                    lon = -float(lon_str[:-1])
                else:
                    lon = float(lon_str)
                
                return lat, lon
            
            # Parse latitude (DMS or decimal)
            lat_deg = float(lat_match.group(1))
            lat_min = float(lat_match.group(2)) if lat_match.group(2) else 0
            lat_sec = float(lat_match.group(3)) if lat_match.group(3) else 0
            lat = lat_deg + lat_min/60 + lat_sec/3600
            if 'S' in coord_str.upper():
                lat = -lat
            
            # Parse longitude (DMS or decimal)
            lon_deg = float(lon_match.group(1))
            lon_min = float(lon_match.group(2)) if lon_match.group(2) else 0
            lon_sec = float(lon_match.group(3)) if lon_match.group(3) else 0
            lon = lon_deg + lon_min/60 + lon_sec/3600
            if 'W' in coord_str.upper():
                lon = -lon
            
            return lat, lon
            
        except (ValueError, IndexError, AttributeError) as e:
            raise ValueError(f"Could not parse coordinates '{coord_str}': {e}")
    
    def _load_world_svg_content(self) -> str:
        """Load the world SVG content and extract the inner paths"""
        try:
            if not self.world_svg_path.exists():
                return self._fallback_world_content()
            
            with open(self.world_svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract everything between the opening and closing svg tags
            import re
            # Find the content between <svg...> and </svg>
            svg_match = re.search(r'<svg[^>]*>(.*?)</svg>', content, re.DOTALL)
            if svg_match:
                inner_content = svg_match.group(1)
                # Remove the defs and namedview elements that are specific to the standalone SVG
                inner_content = re.sub(r'<defs[^>]*>.*?</defs>', '', inner_content, flags=re.DOTALL)
                inner_content = re.sub(r'<sodipodi:namedview[^>]*>.*?</sodipodi:namedview>', '', inner_content, flags=re.DOTALL)
                inner_content = re.sub(r'<sodipodi:namedview[^>]*/>', '', inner_content)
                return inner_content.strip()
            else:
                return self._fallback_world_content()
        except Exception as e:
            print(f"Warning: Could not load world.svg: {e}")
            return self._fallback_world_content()
    
    def _fallback_world_content(self) -> str:
        """Fallback world map content if world.svg is not available"""
        return '''
        <!-- Fallback: Simple world continents -->
        <rect x="200" y="0" width="1800" height="857" fill="#f0f0f0" stroke="#ccc" stroke-width="1"/>
        <text x="1100" y="428" text-anchor="middle" font-family="Inter, sans-serif" 
              font-size="24" fill="#666">World Map</text>
        '''
    
    def generate_location_marker(self, lat: float, lon: float, 
                               label: str = "", color: str = "#E74C3C") -> str:
        """Generate SVG marker for a location - red circle for visibility"""
        x, y = self.coordinates_to_svg(lat, lon, self.world_width, self.world_height)
        
        marker_svg = f"""
        <!-- Location marker for {label} -->
        <g class="location-marker">
            <circle cx="{x}" cy="{y}" r="12" fill="none" stroke="{color}" stroke-width="3" opacity="0.8"/>
            <circle cx="{x}" cy="{y}" r="5" fill="{color}" opacity="0.9"/>
        </g>
        """
        
        return marker_svg
    
    def generate_world_map_svg(self, location_data: Dict, width: int = 400, height: int = 200) -> str:
        """
        Generate complete SVG world map with location marker using proper world.svg
        
        Args:
            location_data: Dict with 'coordinates' and 'location' keys
            width: Target SVG width (will be scaled to fit)
            height: Target SVG height (will be scaled to fit)
            
        Returns:
            Complete SVG as string
        """
        
        # Parse coordinates
        try:
            lat, lon = self.parse_coordinates(location_data.get('coordinates', '0°N, 0°E'))
        except ValueError as e:
            print(f"Warning: {e}, using default coordinates")
            lat, lon = 0, 0
        
        location_name = location_data.get('location', 'Unknown Location')
        
        # Load the world map content
        world_content = self._load_world_svg_content()
        
        # Generate location marker (using world.svg coordinate system)
        marker = self.generate_location_marker(lat, lon, label="", color="#E74C3C")
        
        # Build complete SVG with proper viewBox for the world.svg
        # The world.svg uses viewBox="200 0 1800 857"
        svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="{self.world_viewbox_x} {self.world_viewbox_y} {self.world_width} {self.world_height}" 
     xmlns="http://www.w3.org/2000/svg">
    
    <!-- World map content from world.svg -->
    {world_content}
    
    <!-- Location marker -->
    {marker}
    
</svg>"""
        
        return svg
    
    def save_map_svg(self, location_data: Dict, output_path: str, 
                    width: int = 400, height: int = 200) -> str:
        """Generate and save world map SVG"""
        
        svg_content = self.generate_world_map_svg(location_data, width, height)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_file)
    
    def generate_year_maps(self, locations_file: str, output_dir: str = "output/maps") -> list:
        """Generate world maps for all locations in a year"""
        
        with open(locations_file, 'r') as f:
            locations_data = json.load(f)
        
        generated_files = []
        
        for month_key, location_data in locations_data.items():
            # Generate filename
            filename = f"map-{month_key}.svg"
            output_path = Path(output_dir) / filename
            
            # Generate map
            map_file = self.save_map_svg(location_data, output_path)
            generated_files.append(map_file)
            
            print(f"✓ Generated map: {map_file}")
        
        return generated_files
    
    def create_preview_html(self, svg_files: list, output_path: str = "output/maps/preview.html"):
        """Create HTML preview of all generated maps"""
        
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>World Maps Preview</title>
    <style>
        body { font-family: Inter, sans-serif; margin: 20px; background: #f5f5f5; }
        .map-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .map-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .map-title { margin: 0 0 10px 0; font-weight: 600; color: #2C3E50; }
        .map-svg { width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>World Maps Preview</h1>
    <div class="map-grid">
"""
        
        for svg_file in svg_files:
            filename = Path(svg_file).name
            month_info = filename.replace('map-', '').replace('.svg', '')
            
            html_content += f"""
        <div class="map-card">
            <h3 class="map-title">{month_info}</h3>
            <object data="{filename}" type="image/svg+xml" class="map-svg">
                <img src="{filename}" alt="Map for {month_info}" class="map-svg">
            </object>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>"""
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)

def main():
    parser = argparse.ArgumentParser(description="Generate world maps for calendar headers")
    parser.add_argument('--locations', required=True, help="JSON file with location data")
    parser.add_argument('--output', default="output/maps", help="Output directory")
    parser.add_argument('--width', type=int, default=400, help="Map width in pixels")
    parser.add_argument('--height', type=int, default=200, help="Map height in pixels")
    parser.add_argument('--preview', action='store_true', help="Generate HTML preview")
    parser.add_argument('--test', help="Test with single location (month key like '2024-01')")
    
    args = parser.parse_args()
    
    generator = WorldMapGenerator()
    
    try:
        if args.test:
            # Test single location
            with open(args.locations, 'r') as f:
                locations_data = json.load(f)
            
            if args.test not in locations_data:
                print(f"Location key '{args.test}' not found in {args.locations}")
                return 1
            
            location_data = locations_data[args.test]
            output_path = f"{args.output}/test-{args.test}.svg"
            
            result = generator.save_map_svg(location_data, output_path, args.width, args.height)
            print(f"✓ Generated test map: {result}")
            
        else:
            # Generate all maps
            svg_files = generator.generate_year_maps(args.locations, args.output)
            print(f"✓ Generated {len(svg_files)} world maps")
            
            if args.preview:
                preview_file = generator.create_preview_html(svg_files, f"{args.output}/preview.html")
                print(f"✓ Generated preview: {preview_file}")
                
    except Exception as e:
        print(f"Error generating world maps: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())