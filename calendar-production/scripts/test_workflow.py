#!/usr/bin/env python3
"""
Simple workflow test script
Tests basic functionality without external dependencies
"""

import os
import json
from pathlib import Path
from datetime import datetime, date
import calendar as cal

def test_photo_directory():
    """Test photo directory structure and count"""
    print("🧪 Testing photo directory structure...")
    
    year = 2026
    month = 1
    photo_dir = Path(f"../photos/{year}/{month:02d}")
    
    if not photo_dir.exists():
        print(f"❌ Photo directory not found: {photo_dir}")
        return False
    
    # Get all .jpg files in alphabetical order
    jpg_files = sorted([f for f in photo_dir.iterdir() if f.suffix.lower() == '.jpg'])
    
    # Get number of days in January 2026
    _, days_in_month = cal.monthrange(year, month)
    
    print(f"📅 January {year} has {days_in_month} days")
    print(f"📷 Found {len(jpg_files)} photos in {photo_dir}")
    
    if len(jpg_files) >= days_in_month:
        print(f"✅ Sufficient photos for calendar generation")
        
        # Show first few photos
        print("📋 First 5 photos:")
        for i, photo in enumerate(jpg_files[:5]):
            print(f"  Day {i+1}: {photo.name}")
        
        return True
    else:
        print(f"⚠️  Warning: Need {days_in_month} photos, only have {len(jpg_files)}")
        return False

def test_config_files():
    """Test configuration files"""
    print("\n🧪 Testing configuration files...")
    
    config_files = [
        "data/calendar_config.json",
        "data/locations.json"
    ]
    
    all_good = True
    
    for config_file in config_files:
        if Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                print(f"✅ {config_file}: Valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ {config_file}: Invalid JSON - {e}")
                all_good = False
        else:
            print(f"❌ {config_file}: Not found")
            all_good = False
    
    return all_good

def test_templates():
    """Test template files"""
    print("\n🧪 Testing template files...")
    
    template_files = [
        "templates/calendar_grid.html",
        "templates/print_styles.css"
    ]
    
    all_good = True
    
    for template_file in template_files:
        if Path(template_file).exists():
            print(f"✅ {template_file}: Found")
        else:
            print(f"❌ {template_file}: Not found")
            all_good = False
    
    return all_good

def test_week_calculation():
    """Test ISO week calculation"""
    print("\n🧪 Testing week calculation...")
    
    try:
        # Simple week calculation test
        test_date = date(2026, 1, 15)  # Middle of January
        iso_calendar = test_date.isocalendar()
        
        print(f"📅 {test_date} is in ISO week {iso_calendar.week} of {iso_calendar.year}")
        
        # Test month boundaries
        first_day = date(2026, 1, 1)
        last_day = date(2026, 1, 31)
        
        print(f"📅 January 1, 2026 is ISO week {first_day.isocalendar().week}")
        print(f"📅 January 31, 2026 is ISO week {last_day.isocalendar().week}")
        
        return True
    except Exception as e:
        print(f"❌ Week calculation failed: {e}")
        return False

def test_directory_structure():
    """Test output directory structure"""
    print("\n🧪 Testing directory structure...")
    
    required_dirs = [
        "scripts",
        "templates", 
        "data",
        "photos",
        "output",
        "website"
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {dir_name}/: Found")
        else:
            print(f"❌ {dir_name}/: Not found")
            all_good = False
    
    return all_good

def generate_sample_html():
    """Generate a simple HTML sample to test the template structure"""
    print("\n🧪 Generating sample HTML...")
    
    try:
        # Simple template without Jinja2
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>January 2026 - Test Calendar</title>
    <style>
        @page { size: A3 landscape; margin: 0; }
        body { font-family: Arial, sans-serif; margin: 20px; }
        .calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; }
        .day { border: 1px solid #ccc; padding: 10px; min-height: 100px; }
        .header { background: #2C3E50; color: white; padding: 20px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>January 2026 - Vilcabamba, Ecuador</h1>
        <p>Test calendar generation</p>
    </div>
    
    <div class="calendar-grid">
        <div class="day"><strong>Mon</strong></div>
        <div class="day"><strong>Tue</strong></div>
        <div class="day"><strong>Wed</strong></div>
        <div class="day"><strong>Thu</strong></div>
        <div class="day"><strong>Fri</strong></div>
        <div class="day"><strong>Sat</strong></div>
        <div class="day"><strong>Sun</strong></div>
"""
        
        # Add days 1-31
        for day in range(1, 32):
            html_content += f'        <div class="day">{day}</div>\n'
        
        html_content += """    </div>
</body>
</html>"""
        
        # Save test HTML
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        test_file = output_dir / "test-calendar-2026-01.html"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Generated test HTML: {test_file}")
        return str(test_file)
        
    except Exception as e:
        print(f"❌ HTML generation failed: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Calendar Workflow Test Suite")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Configuration Files", test_config_files),
        ("Template Files", test_templates),
        ("Photo Directory", test_photo_directory),
        ("Week Calculation", test_week_calculation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Generate sample HTML
    html_file = generate_sample_html()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Workflow is ready.")
        if html_file:
            print(f"🔍 Review test HTML: {html_file}")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())