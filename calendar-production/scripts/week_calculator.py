#!/usr/bin/env python3
"""
ISO Week Number Calculator
Handles ISO 8601 week numbering for calendar generation

ISO 8601 week numbering rules:
- Week 1 is the first week with at least 4 days in the new year
- Weeks start on Monday
- Week numbers run from 1-53
"""

import datetime
from typing import Tuple, List, Dict
import json

# Handle import for both module usage and direct execution
try:
    from .localization_manager import LocalizationManager
except ImportError:
    from localization_manager import LocalizationManager

class WeekCalculator:
    def __init__(self, config_file=None, language="en"):
        self.config = self._load_config(config_file)
        self.language = language
        self.localization = LocalizationManager(config_file, default_language="en")
        self.localization.set_language(language)
        
    def _load_config(self, config_file):
        """Load configuration or use defaults"""
        default_config = {
            "week_start": "monday",
            "week_numbering": "iso",
            "first_week_minimum_days": 4
        }
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    return data.get('calendar_settings', default_config)
            except FileNotFoundError:
                print(f"Config file not found: {config_file}, using defaults")
        
        return default_config
    
    def get_iso_week(self, date: datetime.date) -> Tuple[int, int]:
        """
        Get ISO week number and year for a given date
        Returns: (year, week_number)
        """
        iso_calendar = date.isocalendar()
        return (iso_calendar[0], iso_calendar[1])
    
    def get_week_start_date(self, year: int, week: int) -> datetime.date:
        """Get the Monday that starts the given ISO week"""
        # January 4th is always in week 1
        jan4 = datetime.date(year, 1, 4)
        week1_monday = jan4 - datetime.timedelta(days=jan4.weekday())
        
        # Calculate the Monday of the requested week
        target_monday = week1_monday + datetime.timedelta(weeks=week - 1)
        return target_monday
    
    def get_month_weeks(self, year: int, month: int) -> List[Dict]:
        """
        Get all weeks that appear in a given month
        Returns list of week info with dates and week numbers
        """
        # First day of month
        first_day = datetime.date(year, month, 1)
        
        # Last day of month
        if month == 12:
            last_day = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        weeks = []
        current_date = first_day
        
        # Find the Monday that starts the first week containing first_day
        days_since_monday = current_date.weekday()
        week_start = current_date - datetime.timedelta(days=days_since_monday)
        
        while week_start <= last_day:
            week_end = week_start + datetime.timedelta(days=6)
            iso_year, iso_week = self.get_iso_week(week_start + datetime.timedelta(days=3))  # Thursday determines the week
            
            # Check how many days of this week are in the target month
            month_start = max(week_start, first_day)
            month_end = min(week_end, last_day)
            days_in_month = (month_end - month_start).days + 1 if month_end >= month_start else 0
            
            week_info = {
                "week_number": iso_week,
                "iso_year": iso_year,
                "week_start": week_start,
                "week_end": week_end,
                "days_in_month": days_in_month,
                "is_complete_week": days_in_month == 7,
                "dates": []
            }
            
            # Generate all dates in this week
            for i in range(7):
                date = week_start + datetime.timedelta(days=i)
                is_in_month = first_day <= date <= last_day
                is_previous_month = date < first_day
                is_next_month = date > last_day
                
                week_info["dates"].append({
                    "date": date,
                    "day": date.day,
                    "weekday": date.weekday(),  # 0=Monday, 6=Sunday
                    "in_current_month": is_in_month,
                    "is_previous_month": is_previous_month,
                    "is_next_month": is_next_month
                })
            
            weeks.append(week_info)
            week_start += datetime.timedelta(weeks=1)
        
        return weeks
    
    def analyze_month_layout(self, year: int, month: int) -> Dict:
        """
        Analyze month layout requirements for dynamic row sizing
        Returns row count, optimal dimensions, and layout info
        """
        # Get first day of month and days in month
        first_day = datetime.date(year, month, 1)
        if month == 12:
            last_day = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        days_in_month = last_day.day
        
        # Calculate rows needed
        # First day weekday: Monday=0, Sunday=6
        first_weekday = first_day.weekday()
        total_cells_needed = first_weekday + days_in_month
        rows_needed = (total_cells_needed + 6) // 7  # Ceiling division
        
        # Define layout constants with increased available space
        total_grid_height = 245  # mm - increased from 240mm (5mm more space)
        header_row_height = 8    # mm - weekday headers
        available_height = total_grid_height - header_row_height  # 237mm
        
        # Calculate optimal row height based on actual rows needed
        row_height = available_height / rows_needed
        # Optimize photo height - leave less margin for better space utilization
        photo_height = row_height - 3  # Reduced margin from 4mm to 3mm for even larger photos
        layout_type = f"{rows_needed}-row"
        
        # Calculate optimal photo width with equal padding
        # A3 width: 420mm, padding: 20mm total (10mm each side), available: 400mm
        # 7 weekday columns only (week numbers are now outside table in left margin)
        # Border spacing: 2mm × 6 gaps between 7 columns = 12mm
        # Available for 7 photos: 400 - 12 = 388mm
        photo_width = 388 / 7  # Approximately 55.4mm, round to 55mm
        photo_width = round(photo_width)  # 55mm - even wider!
        
        return {
            "rows_needed": rows_needed,
            "layout_type": layout_type,
            "row_height": round(row_height, 1),
            "photo_height": round(photo_height, 1),
            "photo_width": photo_width,  # Dynamic width calculation
            "first_weekday": first_weekday,
            "days_in_month": days_in_month,
            "has_overflow": rows_needed > 5
        }
    
    def generate_calendar_grid(self, year: int, month: int) -> Dict:
        """
        Generate complete calendar grid data for a month
        Includes overflow from previous/next months and layout analysis
        """
        weeks = self.get_month_weeks(year, month)
        
        # Get month name using localization
        month_name = self.localization.get_month_name(month)
        
        # Calculate previous and next month
        if month == 1:
            prev_month, prev_year = 12, year - 1
        else:
            prev_month, prev_year = month - 1, year
            
        if month == 12:
            next_month, next_year = 1, year + 1
        else:
            next_month, next_year = month + 1, year
        
        # Analyze layout requirements for this month
        layout_analysis = self.analyze_month_layout(year, month)

        grid_data = {
            "year": year,
            "month": month,
            "month_name": month_name,
            "previous_month": {
                "month": prev_month,
                "year": prev_year
            },
            "next_month": {
                "month": next_month,
                "year": next_year
            },
            "weeks": weeks,
            "total_weeks": len(weeks),
            "weekday_headers": self._get_weekday_headers(),
            "layout": layout_analysis,
            "config": self.config
        }
        
        return grid_data
    
    def _get_weekday_headers(self) -> List[str]:
        """Get weekday headers based on configuration and language"""
        weekdays = self.localization.get_weekday_names()
        
        if self.config.get("week_start") == "sunday":
            # Rotate to start with Sunday
            weekdays = [weekdays[6]] + weekdays[:6]
        
        return weekdays
    
    def get_year_overview(self, year: int) -> Dict:
        """Generate overview of all months in a year with week numbers"""
        year_data = {
            "year": year,
            "months": []
        }
        
        for month in range(1, 13):
            month_data = self.generate_calendar_grid(year, month)
            year_data["months"].append({
                "month": month,
                "month_name": month_data["month_name"],
                "total_weeks": month_data["total_weeks"],
                "week_numbers": [week["week_number"] for week in month_data["weeks"]]
            })
        
        return year_data

def main():
    """Demo/testing function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Calculate ISO week numbers for calendar generation")
    parser.add_argument('--year', type=int, default=datetime.date.today().year, help="Year to calculate")
    parser.add_argument('--month', type=int, help="Specific month to calculate (1-12)")
    parser.add_argument('--config', help="Path to calendar configuration file")
    parser.add_argument('--language', choices=['en', 'de', 'es'], default='en', help="Language for month/weekday names")
    parser.add_argument('--output', help="Output file for JSON data")
    
    args = parser.parse_args()
    
    calculator = WeekCalculator(args.config, args.language)
    
    if args.month:
        # Generate specific month
        data = calculator.generate_calendar_grid(args.year, args.month)
        print(f"\n=== Calendar Grid for {data['month_name']} {args.year} ===")
        print(f"Total weeks: {data['total_weeks']}")
        
        for week in data['weeks']:
            print(f"\nWeek {week['week_number']} ({week['iso_year']}):")
            for date_info in week['dates']:
                status = "current" if date_info['in_current_month'] else "overflow"
                print(f"  {date_info['date'].strftime('%a %d')}: {status}")
    else:
        # Generate year overview
        data = calculator.get_year_overview(args.year)
        print(f"\n=== Year Overview {args.year} ===")
        for month_info in data['months']:
            week_range = f"{min(month_info['week_numbers'])}-{max(month_info['week_numbers'])}"
            print(f"{month_info['month_name']:>12}: {month_info['total_weeks']} weeks (weeks {week_range})")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\nData saved to: {args.output}")

if __name__ == "__main__":
    main()