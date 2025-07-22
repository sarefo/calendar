#!/usr/bin/env python3
"""
Update the landing page with current observation IDs from photo_information.txt
"""

import re
from pathlib import Path

def read_photo_information():
    """Read and parse photo_information.txt"""
    photo_info_path = Path(__file__).parent.parent / "photos" / "photo_information.txt"
    observations = {}
    
    if not photo_info_path.exists():
        print(f"❌ Photo information file not found: {photo_info_path}")
        return observations
    
    with open(photo_info_path, 'r') as f:
        lines = f.readlines()
    
    # Skip header line
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) >= 3:
            yyyymm = parts[0].strip()
            observation_id = parts[2].strip()
            
            if yyyymm and observation_id:
                if yyyymm not in observations:
                    observations[yyyymm] = []
                observations[yyyymm].append(observation_id)
    
    return observations

def generate_js_mapping(observations):
    """Generate JavaScript mapping for observation IDs"""
    js_lines = []
    
    # Sort months by YYYYMM
    sorted_months = sorted(observations.keys())
    
    for i, yyyymm_str in enumerate(sorted_months):
        if len(yyyymm_str) != 6 or not yyyymm_str.isdigit():
            continue
            
        year = int(yyyymm_str[:4])
        month_num = int(yyyymm_str[4:6])
        month_name = [
            "", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ][month_num]
        
        obs_list = observations[yyyymm_str]
        
        js_lines.append(f"            // {month_name} {year}")
        
        # Create date mappings for each day of the month
        day_mappings = []
        for day, obs_id in enumerate(obs_list, 1):
            date_str = f"'{year}-{month_num:02d}-{day:02d}'"
            day_mappings.append(f"{date_str}: '{obs_id}'")
        
        # Add comma if not the last month
        comma = "," if i < len(sorted_months) - 1 else ""
        js_lines.append("            " + ", ".join(day_mappings) + comma)
        js_lines.append("")  # Empty line between months
    
    return "\n".join(js_lines)

def update_landing_page():
    """Update the landing page with current observation IDs"""
    landing_page_path = Path(__file__).parent.parent.parent / "index.html"
    
    if not landing_page_path.exists():
        print(f"❌ Landing page not found: {landing_page_path}")
        return False
    
    # Read current observations
    observations = read_photo_information()
    if not observations:
        print("❌ No observation data found")
        return False
    
    # Generate new JavaScript mapping
    js_mapping = generate_js_mapping(observations)
    
    # Read current landing page
    with open(landing_page_path, 'r') as f:
        content = f.read()
    
    # Find and replace the photoObservations object
    pattern = r'const photoObservations = \{[^}]*\};'
    new_js = f"""const photoObservations = {{
{js_mapping}        }};"""
    
    updated_content = re.sub(pattern, new_js, content, flags=re.DOTALL)
    
    if updated_content == content:
        print("⚠️  No changes needed - observation mapping is already up to date")
        return True
    
    # Write updated content
    with open(landing_page_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Landing page updated with current observation IDs")
    return True

if __name__ == "__main__":
    update_landing_page()