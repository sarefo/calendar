# A3 Landscape Photo Calendar Production Workflow

**Project**: Professional macro photography calendar with daily photos  
**Format**: A3 Landscape (420mm × 297mm)  
**Target**: Print-ready PDFs for professional printing  
**Status**: ✅ Production-ready with optimized print layout  
**Date**: July 2025  

---

## 🎯 Project Overview

This system generates professional A3 landscape photo calendars featuring:

- **Daily macro photography** (one photo per day, 28-31 per month)
- **7-column grid layout** (Monday-Sunday) with ISO week numbering
- **Monthly location themes** with world map integration
- **Smart QR codes** with automatic date picker integration
- **Print-ready output** (CMYK, 300 DPI, PDF/X compliant)
- **Clean minimal design** optimized for A3 print production

---

## 📁 Project Structure

```
calendar/
├── calendar-production/          # Core production system
│   ├── scripts/                  # Python automation scripts
│   │   ├── build_calendar.py     # 🚀 Master build script
│   │   ├── calendar_generator.py # HTML calendar generation
│   │   ├── week_calculator.py    # ISO week numbering
│   │   ├── qr_generator.py       # QR code creation
│   │   ├── world_map_generator.py # SVG world maps
│   │   ├── html_to_pdf.py        # PDF conversion
│   │   ├── photoshop_specs.py    # Photo crop specifications
│   │   └── test_workflow.py      # 🧪 Test suite
│   ├── templates/                # HTML/CSS templates
│   │   ├── calendar_grid.html    # Main calendar template
│   │   └── print_styles.css      # CMYK print-optimized styles
│   ├── data/                     # Configuration & content
│   │   ├── calendar_config.json  # Calendar settings
││   ├── output/                   # Generated files
│   │   ├── print-ready/          # Final PDFs
│   │   └── previews/             # HTML previews
│   ├── photos/                   # Photo repository (consolidated location)
│   │   ├── photo_information.txt # Photo ordering file (month\tfilename\tobservation_id)
│   │   └── YYYY/                 # Year directory
│   │       └── MM/               # Month directory (01-12)
│   │           ├── photo1.jpg    # Photos listed in photo_information.txt
│   │           ├── photo2.jpg    # Order determined by file, not filename
│   │           └── ...           # etc.
│   └── website/                  # GitHub.io companion site (future)
```

---

## 🚀 **Latest Optimizations (July 2025)**

### **Dynamic Row Layout System** 🆕
- **Smart Row Analysis**: Automatically detects each month's row requirements (5 vs 6 rows needed)
- **Optimized Photo Sizes**: Dynamic photo dimensions based on available space:
  - **5-row months (9 of 12)**: Photos are **54mm × 42.4mm** (larger for better impact)
  - **6-row months (3 of 12)**: Photos are **54mm × 34.7mm** (optimized to fit 6 rows)
- **No Empty Rows**: Eliminates wasted space that appeared in 75% of months
- **Better Space Utilization**: +10% larger photos with professional consistency

### **Print-First Design Philosophy**
- **Variable Photo Sizing**: Dynamic dimensions (42.4mm vs 34.7mm height) for optimal space usage
- **Clean Layout**: Removed weekday text overlays, "No Photo" placeholders, and footer clutter  
- **A3 Optimization**: Enhanced 240mm calendar grid height for maximum photo visibility
- **Enhanced Typography**: 16pt day numbers with improved text shadow for print clarity

### **Smart QR Code Integration**
- **Hash Parameters**: QR codes generate URLs like `https://sarefo.github.io/calendar/#202601`
- **Auto Date Picker**: Landing page automatically sets date based on QR code month
- **Seamless Flow**: Scan printed calendar → auto-navigate to correct month online

### **Automation Enhancements**
- **Auto Location Reading**: System reads location data from `photos/YYYY/MM/README.md` files
- **Streamlined Header**: All elements (title, location, QR, map) integrated in 35mm header
- **PDF Consistency**: Enhanced print media CSS ensures uniform dimensions across all output

---

## 🔧 Technical Implementation

### Core Components

#### 1. **Photo Management**
- **Structure**: `calendar-production/photos/YYYY/MM/` (e.g., `calendar-production/photos/2026/01/`)
- **Ordering**: Controlled by `calendar-production/photos/photo_information.txt` (tab-separated format)
- **Format**: `.jpg` files, square crop recommended
- **Processing**: Photoshop batch processing with provided specs

#### 2. **Calendar Generation**
- **Grid**: 7 columns (Mon-Sun) with ISO week numbers using HTML table layout
- **Dynamic Photos**: Variable dimensions based on month row requirements:
  - **5-row months**: 54mm × 42.4mm (Jan, Feb, Apr, May, Jun, Jul, Sep, Oct, Dec)
  - **6-row months**: 54mm × 34.7mm (Mar, Aug, Nov)
- **Smart Layout**: Automatic row height calculation eliminates empty rows
- **Typography**: Inter font family, CMYK-safe colors, 16pt day numbers
- **Layout**: Streamlined 35mm header with integrated elements, 240mm calendar grid
- **PDF Compatibility**: Enhanced print media CSS ensures consistent dimensions

#### 3. **Print Optimization**
- **Format**: A3 landscape (420×297mm) with 3mm bleed
- **Resolution**: 300 DPI for all elements
- **Color**: CMYK color space (ISO Coated v2 300%)
- **PDF**: PDF/X-1a compliant with embedded fonts

#### 4. **Smart QR & Location Integration**
- **Required location data**: From `photos/YYYY/MM/README.md` files (no fallbacks)
- **QR codes**: Link to `https://sarefo.github.io/calendar/#YYYYMM` with hash parameters
- **Landing page**: Automatic date picker setting based on QR code month
- **World maps**: Simplified SVG with location markers in streamlined header
- **Data validation**: System stops if location data is missing or has placeholders

#### 5. **Streamlined Location Data System**
- **Single Source**: Location data stored only in `README.md` files with photos
- **No Fallbacks**: System fails fast if location data is missing or incomplete
- **Auto-Validation**: Checks for placeholder values and missing required fields
- **Simple Maintenance**: Location data co-located with photos for easy management
- **Smart Error Messages**: Clear instructions when location data needs to be added

---

## 🚀 Production Workflow

### Phase 1: Photo Preparation

1. **Organize Photos and Location Data**
   ```bash
   # Create month directory
   mkdir -p calendar-production/photos/2026/01
   
   # Create README.md with complete location info (required - no fallbacks!)
   echo "+ location: Tulamben, Bali, Indonesia" > calendar-production/photos/2026/01/README.md
   echo "+ coordinates: 8°017'03\"S 115°035'021\"E" >> calendar-production/photos/2026/01/README.md
   echo "+ year: 2026" >> calendar-production/photos/2026/01/README.md
   
   # Update calendar-production/photos/photo_information.txt with photo order
   # Format: month\tfilename\tobservation_id (tab-separated)
   # Example: 01\tIMG_8477\t149640464
   ```

2. **Generate Crop Specifications**
   ```bash
   cd calendar-production
   python3 scripts/photoshop_specs.py --input-dir photos/2026/01 --output photoshop_specs.json
   ```

3. **Photoshop Batch Processing**
   - Open Photoshop
   - Follow specifications in `photoshop_specs.txt`
   - Crop to square (1:1 aspect ratio)
   - Resize to 2400×2400px at 300 DPI
   - Convert to CMYK color profile
   - Save as high-quality JPEG

### Phase 2: Calendar Generation

1. **Test Photo Setup**
   ```bash
   python3 scripts/test_workflow.py
   ```

2. **Generate Single Month**
   ```bash
   python3 scripts/build_calendar.py --year 2026 --month 1
   ```

3. **Generate Full Year**
   ```bash
   python3 scripts/build_calendar.py --year 2026
   ```

### Phase 3: Print Production

1. **Install Dependencies** (first time only)
   ```bash
   python3 scripts/build_calendar.py --install-deps
   ```

2. **Generate Print-Ready PDFs**
   ```bash
   python3 scripts/build_calendar.py --year 2026
   ```

3. **Create Print Package**
   - Automatically generated in `output/print-package-YYYY/`
   - Includes PDFs, print instructions, and file list
   - Ready for any professional print shop

---

## 📋 Configuration Files

### `data/calendar_config.json`
Core calendar settings:
```json
{
  "calendar_settings": {
    "week_start": "monday",           // or "sunday"
    "week_numbering": "iso",          // ISO 8601 standard
    "language": "en"                  // for localization
  },
  "layout": {
    "format": "A3_landscape",         // fixed for this project
    "grid": { "columns": 7 }          // Mon-Sun layout
  },
  "print": {
    "resolution_dpi": 300,            // print quality
    "color_profile": "CMYK_ISO_Coated_v2_300",
    "pdf_standard": "PDF_X_1a"       // print compatibility
  }
}
```

### Photo Directory Location Data
Each photo month directory contains location information in `README.md`:
```
calendar-production/photos/YYYY/MM/README.md:
+ location: [City, Country/Region]
+ coordinates: [Lat°N/S, Long°E/W]
+ year: [YYYY]
```

Example:
```
+ location: Tulamben, Bali, Indonesia
+ coordinates: 8°017′03″S 115°035′021″E
+ year: 2026
```

---

## 🎨 Design Specifications

### Layout Dimensions (A3 Landscape)
- **Total size**: 420mm × 297mm
- **Bleed area**: 3mm all around
- **Header section**: 35mm (title, location, QR code - all integrated)
- **Calendar grid**: 240mm (optimized for photo visibility)
- **Photo cells**: Dynamic dimensions based on month requirements:
  - **5-row months**: 54mm × 42.4mm (Jan, Feb, Apr, May, Jun, Jul, Sep, Oct, Dec)
  - **6-row months**: 54mm × 34.7mm (Mar, Aug, Nov)
  - **Row heights**: Automatically calculated (46.4mm vs 38.7mm per row)

### Typography
- **Primary font**: Inter (Google Fonts)
- **Title**: 24pt, bold
- **Weekday headers**: 10pt, uppercase
- **Day numbers**: 16pt, bold with enhanced text shadow (no weekday text)
- **Week numbers**: 8pt on left margin

### Color Palette (CMYK)
- **Primary**: #2C3E50 (C:85 M:65 Y:45 K:25)
- **Secondary**: #34495E (C:75 M:55 Y:35 K:15)
- **Accent**: #E74C3C (C:15 M:85 Y:85 K:5)
- **Text**: High contrast with background

---

## 🔧 Script Reference

### `build_calendar.py` - Master Build Script
```bash
# Check photos for specific month
python3 scripts/build_calendar.py --check-photos --year 2026 --month 1

# Build single month
python3 scripts/build_calendar.py --year 2026 --month 1

# Build specific months
python3 scripts/build_calendar.py --year 2026 --months "1,2,3"

# Build full year with print package
python3 scripts/build_calendar.py --year 2026

# Skip PDF generation (HTML only)
python3 scripts/build_calendar.py --year 2026 --no-pdf
```

### Individual Script Usage

**Photo Specifications**:
```bash
python3 scripts/photoshop_specs.py --input-dir photos/2026/01 --output specs.json
```

**QR Code Generation**:
```bash
python3 scripts/qr_generator.py --year 2026 --month 1 --base-url "https://sarefo.github.io/calendar/"
```

**World Map Generation** (for individual locations):
```bash
python3 scripts/world_map_generator.py --coordinates "8°017′03″S 115°035′021″E" --location "Bali, Indonesia" --output output/map.svg
```

**Week Number Calculation**:
```bash
python3 scripts/week_calculator.py --year 2026 --month 1 --output week_data.json
```

**HTML to PDF Conversion**:
```bash
python3 scripts/html_to_pdf.py --input output/calendar.html --output output/print-ready/
```

**Landing Page Update**:
```bash
python3 scripts/update_landing_page.py
```

---

## 🖨️ Print Shop Instructions

### File Format
- **PDF/X-1a compliant** (universal print shop compatibility)
- **CMYK color space** with ICC profiles embedded
- **300 DPI resolution** throughout
- **Fonts embedded** or outlined

### Paper Specifications
- **Size**: A3 (420mm × 297mm)
- **Orientation**: Landscape
- **Weight**: 200-300 GSM recommended
- **Finish**: Matte or semi-gloss
- **Type**: Photo paper or high-quality cardstock

### Print Settings
- **Scaling**: None (100% / Actual Size)
- **Color Management**: CMYK with color matching
- **Quality**: Highest available
- **Margins**: None (full bleed printing)

### Binding Options
- **Spiral binding** (recommended for calendars)
- **Saddle stitching** for booklet format
- **Ring binding** for wall hanging
- **Perfect binding** for book format

---

## ✅ Quality Checklist

### Pre-Print Verification
- [ ] All photos are sharp and properly exposed
- [ ] Text is clearly readable at print size
- [ ] Colors are vibrant but not oversaturated
- [ ] Week numbers are correctly calculated
- [ ] QR codes are functional and link correctly
- [ ] World maps show correct location markers
- [ ] PDF files are PDF/X-1a compliant
- [ ] All fonts are embedded
- [ ] Bleed area is properly set (3mm)

### Post-Print Review
- [ ] Colors match digital preview
- [ ] Text is crisp and readable
- [ ] Photos are well-positioned
- [ ] Calendar grid is properly aligned
- [ ] QR codes scan successfully
- [ ] Overall layout appears professional

---

## 🔮 Future Enhancements

### Phase 2: GitHub.io Website
- **Interactive calendar** with date picker
- **Photo stories** with location context and biodiversity info
- **iNaturalist integration** for species identification
- **DuoNat integration** for biodiversity exploration
- **Mobile-responsive design**

### Phase 3: Advanced Features
- **Multi-language support** (Spanish, Portuguese)
- **Custom color themes** per location
- **Enhanced world maps** with terrain/satellite imagery
- **Photo metadata integration** (camera settings, species info)
- **Batch year generation** with progress tracking

### Phase 4: Print Automation
- **Direct print shop API integration**
- **Online ordering system**
- **Inventory management**
- **Shipping coordination**

---

## 🆘 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'X'"**
```bash
python3 scripts/build_calendar.py --install-deps
```

**"No photos found for month"**
- Check photo directory structure: `calendar-production/photos/YYYY/MM/`
- Ensure photos have `.jpg` extension  
- Verify `calendar-production/photos/photo_information.txt` has entries for the month
- Run: `python3 scripts/build_calendar.py --check-photos --year YYYY --month MM`

**"PDF conversion failed"**
- Install Playwright: `pip install playwright && playwright install chromium`
- Alternative: Use WeasyPrint: `pip install weasyprint`

**"Colors look different when printed"**
- Verify CMYK color profile is embedded
- Ask print shop for CMYK color matching
- Consider test print on same paper stock

**"QR codes don't scan"**
- Ensure sufficient contrast between code and background
- Test QR codes at actual print size
- Verify URL is accessible

---

## 📞 Support & Development

### Current Status
✅ **Production-ready workflow with optimized A3 print layout**  
✅ **Dynamic row layout system - eliminates empty rows completely**  
✅ **Enhanced photo presentation: Variable dimensions (42.4mm vs 34.7mm height)**  
✅ **Streamlined design: removed weekday overlays and placeholders**  
✅ **Smart QR integration: hash parameters for automatic date picker**  
✅ **Auto-location reading from README.md files**  
✅ **Print-optimized PDFs generated with dynamic sizing**  
✅ **Landing page with hash parameter support implemented**  
✅ **Clean header design with integrated elements**  
✅ **Enhanced print media CSS for PDF consistency**  

### Next Steps
1. ✅ **Dynamic calendar layout system - NO MORE EMPTY ROWS!**
2. ✅ **Enhanced QR code integration with smart landing page**
3. ✅ **Optimized photo sizing - 10% larger photos in 75% of months**
4. ✅ **Auto-location reading and hash parameter support**
5. ⏳ **Generate remaining months for 2026 calendar**
6. ⏳ **Deploy optimized system to GitHub Pages**

### Contact
- **Project Repository**: This calendar system
- **Documentation**: This file (`CLAUDE.md`)
- **Issue Tracking**: Document issues encountered during testing