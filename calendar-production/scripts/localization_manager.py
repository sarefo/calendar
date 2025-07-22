#!/usr/bin/env python3
"""
Localization Manager for Calendar System
Handles translation loading and retrieval for multi-language calendar generation

Supports: English (en), German (de), Spanish (es)
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path

class LocalizationManager:
    def __init__(self, config_file: Optional[str] = None, default_language: str = "en"):
        """
        Initialize LocalizationManager
        
        Args:
            config_file: Path to calendar_config.json file
            default_language: Default language code (en, de, es)
        """
        self.default_language = default_language
        self.current_language = default_language
        self.translations = {}
        
        # Load configuration
        self._load_config(config_file)
        
    def _load_config(self, config_file: Optional[str] = None):
        """Load configuration file and extract localization data"""
        
        # Determine config file path
        if not config_file:
            # Try to find config file relative to this script
            script_dir = Path(__file__).parent
            config_file = script_dir.parent / "data" / "calendar_config.json"
        
        config_file = Path(config_file)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            self.translations = config_data.get('localization', {})
            
            # Validate that we have translations
            if not self.translations:
                raise ValueError("No localization data found in configuration file")
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {e}")
    
    def set_language(self, language_code: str):
        """
        Set the current language
        
        Args:
            language_code: Language code (en, de, es)
        """
        if not self.is_language_supported(language_code):
            raise ValueError(f"Language '{language_code}' is not supported. "
                           f"Available languages: {self.get_supported_languages()}")
        
        self.current_language = language_code
    
    def get_current_language(self) -> str:
        """Get the current language code"""
        return self.current_language
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        # Extract language codes from weekdays (they should all have the same languages)
        weekdays = self.translations.get('weekdays', {})
        languages = set()
        
        for key in weekdays.keys():
            if not key.endswith('_short'):
                languages.add(key)
        
        return sorted(list(languages))
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported"""
        return language_code in self.get_supported_languages()
    
    def get_month_name(self, month: int, language: Optional[str] = None, fallback: bool = True) -> str:
        """
        Get localized month name
        
        Args:
            month: Month number (1-12)
            language: Language code, uses current language if None
            fallback: Use default language if translation not found
            
        Returns:
            Localized month name
        """
        if not 1 <= month <= 12:
            raise ValueError(f"Month must be between 1 and 12, got {month}")
        
        lang = language or self.current_language
        months = self.translations.get('months', {})
        
        # Try requested language
        if lang in months and len(months[lang]) >= month:
            return months[lang][month - 1]  # Convert to 0-based index
        
        # Fallback to default language
        if fallback and self.default_language in months:
            if len(months[self.default_language]) >= month:
                return months[self.default_language][month - 1]
        
        # Last resort: return English month name or month number
        english_months = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"]
        if month <= len(english_months):
            return english_months[month - 1]
        
        return f"Month {month}"
    
    def get_weekday_name(self, weekday: int, language: Optional[str] = None, 
                        short: bool = False, fallback: bool = True) -> str:
        """
        Get localized weekday name
        
        Args:
            weekday: Weekday number (0=Monday, 6=Sunday)
            language: Language code, uses current language if None
            short: Return short form (e.g., "Mon" instead of "Monday")
            fallback: Use default language if translation not found
            
        Returns:
            Localized weekday name
        """
        if not 0 <= weekday <= 6:
            raise ValueError(f"Weekday must be between 0 and 6, got {weekday}")
        
        lang = language or self.current_language
        weekdays = self.translations.get('weekdays', {})
        
        # Determine the key to look for
        key = f"{lang}_short" if short else lang
        
        # Try requested language and format
        if key in weekdays and len(weekdays[key]) > weekday:
            return weekdays[key][weekday]
        
        # Fallback to default language
        if fallback:
            fallback_key = f"{self.default_language}_short" if short else self.default_language
            if fallback_key in weekdays and len(weekdays[fallback_key]) > weekday:
                return weekdays[fallback_key][weekday]
        
        # Last resort: return English weekday name
        english_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        english_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        weekday_list = english_short if short else english_weekdays
        if weekday < len(weekday_list):
            return weekday_list[weekday]
        
        return f"Day {weekday}"
    
    def get_weekday_names(self, language: Optional[str] = None, short: bool = False) -> List[str]:
        """
        Get all weekday names in order (Monday to Sunday)
        
        Args:
            language: Language code, uses current language if None
            short: Return short forms
            
        Returns:
            List of weekday names
        """
        return [self.get_weekday_name(i, language, short) for i in range(7)]
    
    def get_month_names(self, language: Optional[str] = None) -> List[str]:
        """
        Get all month names in order (January to December)
        
        Args:
            language: Language code, uses current language if None
            
        Returns:
            List of month names
        """
        return [self.get_month_name(i, language) for i in range(1, 13)]
    
    def format_date(self, year: int, month: int, day: int, 
                   language: Optional[str] = None, format_style: str = "long") -> str:
        """
        Format date in localized format
        
        Args:
            year: Year (e.g., 2026)
            month: Month (1-12)
            day: Day (1-31)
            language: Language code, uses current language if None
            format_style: Format style ("long", "short", "numeric")
            
        Returns:
            Formatted date string
        """
        lang = language or self.current_language
        month_name = self.get_month_name(month, lang)
        
        if format_style == "long":
            if lang == "de":
                return f"{day}. {month_name} {year}"
            elif lang == "es":
                return f"{day} de {month_name} de {year}"
            else:  # English or fallback
                return f"{month_name} {day}, {year}"
        elif format_style == "short":
            return f"{day:02d}.{month:02d}.{year}" if lang == "de" else f"{month:02d}/{day:02d}/{year}"
        else:  # numeric
            return f"{year}-{month:02d}-{day:02d}"


def main():
    """Demo/testing function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test localization manager")
    parser.add_argument('--language', choices=['en', 'de', 'es'], default='en',
                       help="Language to test")
    parser.add_argument('--config', help="Path to calendar configuration file")
    
    args = parser.parse_args()
    
    try:
        lm = LocalizationManager(args.config, default_language='en')
        lm.set_language(args.language)
        
        print(f"Testing localization for language: {args.language}")
        print(f"Supported languages: {lm.get_supported_languages()}")
        print()
        
        # Test months
        print("Months:")
        for i in range(1, 13):
            print(f"  {i:2d}: {lm.get_month_name(i)}")
        print()
        
        # Test weekdays
        print("Weekdays (full):")
        weekdays = lm.get_weekday_names()
        for i, day in enumerate(weekdays):
            print(f"  {i}: {day}")
        print()
        
        print("Weekdays (short):")
        weekdays_short = lm.get_weekday_names(short=True)
        for i, day in enumerate(weekdays_short):
            print(f"  {i}: {day}")
        print()
        
        # Test date formatting
        test_date = (2026, 1, 15)
        print(f"Date formatting for {test_date[2]}.{test_date[1]:02d}.{test_date[0]}:")
        print(f"  Long:    {lm.format_date(*test_date, format_style='long')}")
        print(f"  Short:   {lm.format_date(*test_date, format_style='short')}")
        print(f"  Numeric: {lm.format_date(*test_date, format_style='numeric')}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())