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
        # Simplified world map outline (major continents only)
        # Coordinates are in SVG viewBox 0 0 400 200 (2:1 aspect ratio)
        self.world_outline = self._get_world_outline()
        
    def _get_world_outline(self) -> str:
        """Simplified SVG path for world continents (optimized for small size)"""
        # Very simplified world map paths
        return """
        <!-- North America -->
        <path d="M50,40 Q60,30 80,35 L100,30 Q120,35 140,40 L145,50 Q140,60 130,65 L120,75 Q100,80 80,75 L70,70 Q55,65 50,55 Z" 
              fill="#E8E8E8" stroke="#CCC" stroke-width="0.5"/>
        
        <!-- South America -->
        <path d="M90,90 Q95,85 105,90 L110,110 Q108,130 105,140 L100,150 Q95,155 90,150 L85,140 Q82,120 85,100 Z" 
              fill="#E8E8E8" stroke="#CCC" stroke-width="0.5"/>
        
        <!-- Europe -->
        <path d="M180,35 Q190,30 200,35 L205,40 Q200,50 195,45 L185,45 Q180,40 180,35 Z" 
              fill="#E8E8E8" stroke="#CCC" stroke-width="0.5"/>
        
        <!-- Africa -->
        <path d="M170,55 Q180,50 190,55 L195,70 Q190,90 185,110 L180,120 Q175,125 170,120 L165,110 Q160,90 165,70 Z" 
              fill="#E8E8E8" stroke="#CCC" stroke-width="0.5"/>
        
        <!-- Asia -->
        <path d="M200,30 Q230,25 260,35 L290,40 Q310,45 320,50 L325,60 Q320,70 310,75 L280,80 Q250,75 220,70 L210,60 Q200,50 200,40 Z" 
              fill="#E8E8E8" stroke="#CCC" stroke-width="0.5"/>
        
        <!-- Australia -->
        <path d="M280,120 Q290,115 300,120 L305,125 Q300,135 295,130 L285,130 Q280,125 280,120 Z" 
              fill="#E8E8E8" stroke="#CCC" stroke-width="0.5"/>
        """
    
    def coordinates_to_svg(self, lat: float, lon: float, width: int = 400, height: int = 200) -> Tuple[float, float]:
        """Convert latitude/longitude to SVG coordinates"""
        # Simple equirectangular projection
        x = (lon + 180) * (width / 360)
        y = (90 - lat) * (height / 180)
        return x, y
    
    def parse_coordinates(self, coord_str: str) -> Tuple[float, float]:
        """
        Parse coordinate string like "4.25°S, 79.23°W" or "6.25°N, 75.56°W"
        Returns (latitude, longitude) as floats
        """
        try:
            # Split by comma
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
                lat = float(lat_str)  # Assume positive is North
            
            # Parse longitude
            lon_str = parts[1]
            if lon_str.endswith('E'):
                lon = float(lon_str[:-1])
            elif lon_str.endswith('W'):
                lon = -float(lon_str[:-1])
            else:
                lon = float(lon_str)  # Assume positive is East
            
            return lat, lon
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Could not parse coordinates '{coord_str}': {e}")
    
    def generate_location_marker(self, lat: float, lon: float, 
                               label: str = "", color: str = "#E74C3C") -> str:
        """Generate SVG marker for a location"""
        x, y = self.coordinates_to_svg(lat, lon)
        
        marker_svg = f"""
        <!-- Location marker for {label} -->
        <g class="location-marker">
            <circle cx="{x}" cy="{y}" r="3" fill="{color}" stroke="white" stroke-width="1"/>
            <circle cx="{x}" cy="{y}" r="1.5" fill="white"/>
        </g>
        """
        
        if label:
            # Add label if coordinates allow (not too close to edges)
            if 20 < x < 380 and 20 < y < 180:
                label_x = x + 8
                label_y = y - 5
                marker_svg += f"""
                <text x="{label_x}" y="{label_y}" font-family="Inter, sans-serif" 
                      font-size="8" fill="{color}" font-weight="500">{label}</text>
                """
        
        return marker_svg
    
    def generate_world_map_svg(self, location_data: Dict, width: int = 400, height: int = 200) -> str:
        """
        Generate complete SVG world map with location marker
        
        Args:
            location_data: Dict with 'coordinates' and 'location' keys
            width: SVG width
            height: SVG height
            
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
        
        # Generate location marker
        marker = self.generate_location_marker(lat, lon, label="", color="#E74C3C")
        
        # Build complete SVG
        svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" 
     xmlns="http://www.w3.org/2000/svg">
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="#F8FAFE" stroke="#E1E8ED" stroke-width="1"/>
    
    <!-- World outline -->
    <g class="world-continents">
        {self.world_outline}
    </g>
    
    <!-- Location marker -->
    {marker}
    
    <!-- Grid lines (optional, subtle) -->
    <defs>
        <pattern id="grid" width="40" height="20" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#E8E8E8" stroke-width="0.25" opacity="0.5"/>
        </pattern>
    </defs>
    <rect width="{width}" height="{height}" fill="url(#grid)" opacity="0.3"/>
    
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