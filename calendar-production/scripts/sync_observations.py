#!/usr/bin/env python3
"""
Sync Photo Observations Utility
Synchronizes photo-observations.json with photo_information.txt

This utility reads the authoritative photo_information.txt file and updates
the photo-observations.json file with the current observation IDs. This ensures
consistency between the two data sources.

Usage:
    python3 scripts/sync_observations.py
"""

import json
import os
from pathlib import Path

def sync_photo_observations():
    """Sync photo-observations.json with photo_information.txt"""
    
    # Paths
    photo_info_path = Path("photos/photo_information.txt")
    observations_json_path = Path("../data/photo-observations.json")
    
    if not photo_info_path.exists():
        print(f"❌ Error: photo_information.txt not found at {photo_info_path}")
        return False
    
    # Read photo_information.txt and extract observation data
    observations = {}
    
    try:
        with open(photo_info_path, 'r') as f:
            lines = f.readlines()
        
        print(f"📖 Reading photo information from {photo_info_path}")
        
        # Skip header line
        for line_num, line in enumerate(lines[1:], 2):
            parts = line.strip().split('\t')
            if len(parts) >= 3 and parts[1].strip():  # YYYYMM, filename, and observation_id exist
                yyyymm = parts[0].strip()
                filename = parts[1].strip()
                observation_id = parts[2].strip()
                
                # Skip placeholder entries and entries with observation_id "0"
                if filename == "placeholder" or observation_id == "0" or not observation_id:
                    continue
                
                # Find how many photos we've processed for this month so far
                month_photos_count = 0
                month_prefix = yyyymm[:4] + '-' + yyyymm[4:6] + '-'
                for existing_date in observations.keys():
                    if existing_date.startswith(month_prefix):
                        month_photos_count += 1
                
                # Day number is based on order in file (first photo = day 1, second = day 2, etc.)
                day_number = month_photos_count + 1
                
                # Create date key in YYYY-MM-DD format
                year = yyyymm[:4]
                month = yyyymm[4:6]
                date_key = f"{year}-{month}-{day_number:02d}"
                
                observations[date_key] = observation_id
        
        print(f"✅ Processed {len(observations)} observation entries")
        
        # Create output directory if it doesn't exist
        observations_json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to photo-observations.json with nice formatting
        with open(observations_json_path, 'w') as f:
            # Group by year-month for better readability
            grouped_data = {}
            for date_key in sorted(observations.keys()):
                year_month = date_key[:7]  # YYYY-MM
                if year_month not in grouped_data:
                    grouped_data[year_month] = {}
                grouped_data[year_month][date_key] = observations[date_key]
            
            # Write with grouped formatting
            f.write('{\n')
            first_group = True
            for year_month in sorted(grouped_data.keys()):
                if not first_group:
                    f.write(',\n\n')
                first_group = False
                
                # Write month data in one line
                month_entries = []
                for date_key in sorted(grouped_data[year_month].keys()):
                    obs_id = grouped_data[year_month][date_key]
                    month_entries.append(f'"{date_key}": "{obs_id}"')
                
                f.write(f'    {", ".join(month_entries)}')
            
            f.write('\n}\n')
        
        print(f"✅ Successfully updated {observations_json_path}")
        print(f"   Total observations: {len(observations)}")
        
        # Show sample of what was written
        sample_keys = sorted(observations.keys())[:5]
        print(f"   Sample entries:")
        for key in sample_keys:
            print(f"     {key}: {observations[key]}")
        
        return True
        
    except (IOError, IndexError) as e:
        print(f"❌ Error processing files: {e}")
        return False

def main():
    """Main entry point"""
    print("🔄 Syncing photo-observations.json with photo_information.txt")
    print("=" * 60)
    
    if sync_photo_observations():
        print("\n🎉 Successfully synchronized observation data!")
        print("   Both photo_information.txt and photo-observations.json are now consistent.")
    else:
        print("\n❌ Failed to synchronize observation data.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())