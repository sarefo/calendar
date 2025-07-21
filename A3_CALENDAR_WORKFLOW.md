# A3 Landscape Photo Calendar Production Workflow

**Project**: Professional macro photography calendar with daily photos  
**Format**: A3 Landscape (420mm × 297mm)  
**Target**: Print-ready PDFs for professional printing  
**Status**: ✅ Core workflow implemented and tested  
**Date**: July 2025  

---

## 🎯 Project Overview

This system generates professional A3 landscape photo calendars featuring:

- **Daily macro photography** (one photo per day, 28-31 per month)
- **7-column grid layout** (Monday-Sunday) with ISO week numbering
- **Monthly location themes** with world map integration
- **QR codes** linking to GitHub.io photo stories website
- **Print-ready output** (CMYK, 300 DPI, PDF/X compliant)
- **Previous/next month overflow** with reduced opacity

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
│   │   └── locations.json        # Monthly location data
│   ├── output/                   # Generated files
│   │   ├── print-ready/          # Final PDFs
│   │   └── previews/             # HTML previews
│   └── website/                  # GitHub.io companion site (future)
└── photos/                       # Photo repository
    ├── photo_information.txt     # Photo ordering file (month\tfilename\tobservation_id)
    └── YYYY/                     # Year directory
        └── MM/                   # Month directory (01-12)
            ├── photo1.jpg        # Photos listed in photo_information.txt
            ├── photo2.jpg        # Order determined by file, not filename
            └── ...               # etc.
```

---

## 🔧 Technical Implementation

### Core Components

#### 1. **Photo Management**
- **Structure**: `photos/YYYY/MM/` (e.g., `photos/2026/01/`)
- **Ordering**: Controlled by `photos/photo_information.txt` (tab-separated format)
- **Format**: `.jpg` files, square crop recommended
- **Processing**: Photoshop batch processing with provided specs

#### 2. **Calendar Generation**
- **Grid**: 7 columns (Mon-Sun) with ISO week numbers
- **Overflow**: Previous/next month photos at 50% opacity
- **Typography**: Inter font family, CMYK-safe colors
- **Layout**: 45mm header, flexible calendar, 25mm footer

#### 3. **Print Optimization**
- **Format**: A3 landscape (420×297mm) with 3mm bleed
- **Resolution**: 300 DPI for all elements
- **Color**: CMYK color space (ISO Coated v2 300%)
- **PDF**: PDF/X-1a compliant with embedded fonts

#### 4. **Location Integration**
- **World maps**: Simplified SVG with location markers
- **QR codes**: Link to photo stories website
- **Theming**: Monthly location data in JSON format

---

## 🚀 Production Workflow

### Phase 1: Photo Preparation

1. **Organize Photos**
   ```bash
   # Create month directory
   mkdir -p photos/2026/01
   
   # Update photos/photo_information.txt with photo order
   # Format: month\tfilename\tobservation_id (tab-separated)
   # Example: 01\tIMG_8477\t149640464
   ```

2. **Generate Crop Specifications**
   ```bash
   cd calendar-production
   python3 scripts/photoshop_specs.py --input-dir ../photos/2026/01 --output photoshop_specs.json
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
   python3 scripts/build_calendar.py --year 2026 --locations data/locations.json
   ```

### Phase 3: Print Production

1. **Install Dependencies** (first time only)
   ```bash
   python3 scripts/build_calendar.py --install-deps
   ```

2. **Generate Print-Ready PDFs**
   ```bash
   python3 scripts/build_calendar.py --year 2026 --locations data/locations.json
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

### `data/locations.json`
Monthly location themes:
```json
{
  "2026-01": {
    "location": "Vilcabamba, Ecuador",
    "coordinates": "4.25°S, 79.23°W",
    "website_url": "https://sarefo.github.io/calendar-stories/?month=2026-01",
    "photographer_name": "Your Name"
  }
}
```

---

## 🎨 Design Specifications

### Layout Dimensions (A3 Landscape)
- **Total size**: 420mm × 297mm
- **Bleed area**: 3mm all around
- **Header section**: 45mm (title + world map)
- **Calendar grid**: Flexible height
- **Footer section**: 25mm (QR code + branding)

### Typography
- **Primary font**: Inter (Google Fonts)
- **Title**: 24pt, bold
- **Weekday headers**: 10pt, uppercase
- **Day numbers**: 14pt, bold with text shadow
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
python3 scripts/build_calendar.py --year 2026 --locations data/locations.json

# Skip PDF generation (HTML only)
python3 scripts/build_calendar.py --year 2026 --no-pdf
```

### Individual Script Usage

**Photo Specifications**:
```bash
python3 scripts/photoshop_specs.py --input-dir ../photos/2026/01 --output specs.json
```

**QR Code Generation**:
```bash
python3 scripts/qr_generator.py --year 2026 --month 1 --base-url "https://sarefo.github.io/calendar-stories"
```

**World Map Generation**:
```bash
python3 scripts/world_map_generator.py --locations data/locations.json --output output/maps
```

**Week Number Calculation**:
```bash
python3 scripts/week_calculator.py --year 2026 --month 1 --output week_data.json
```

**HTML to PDF Conversion**:
```bash
python3 scripts/html_to_pdf.py --input output/calendar.html --output output/print-ready/
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
- Check photo directory structure: `photos/YYYY/MM/`
- Ensure photos have `.jpg` extension
- Verify `photos/photo_information.txt` has entries for the month
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
✅ **Core workflow implemented and tested**  
✅ **January 2026 photos verified (31 photos)**  
🔄 **Ready for production testing**  
⏳ **GitHub.io website planned for future session**  

### Next Steps
1. **Test full month generation** with your January 2026 photos
2. **Generate first prototype** for print testing
3. **Iterate on design** based on print results
4. **Plan GitHub.io website** in separate session

### Contact
- **Project Repository**: This calendar system
- **Documentation**: This file (`A3_CALENDAR_WORKFLOW.md`)
- **Issue Tracking**: Document issues encountered during testing

---

**🎉 The A3 landscape calendar production workflow is ready for prototype testing!**