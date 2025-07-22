# A3 Landscape Photo Calendar Production Workflow

**Project**: Professional macro photography calendar with daily photos  
**Format**: A3 Landscape (420mm × 297mm)  
**Target**: Print-ready PDFs for professional printing  
**Status**: ✅ Production-ready with complete build workflow, multi-format PDF generation, and full internationalization  
**Date**: July 2025  

---

## 📝 Documentation Updates

**IMPORTANT**: Always update this CLAUDE.md file after successfully implementing any changes to the calendar production system. This ensures the documentation stays current with the actual functionality and provides accurate guidance for future development.

**Latest Updates (July 2025)**:
- ✅ **MAJOR**: Full internationalization support (German and Spanish)
- ✅ **MAJOR**: Simplified folder structure - organized output under output/2026/
- ✅ **MAJOR**: Simplified PDF generation - only print and web formats
- ✅ **MAJOR**: Dual PDF generation - single commands now create both print and web PDFs
- ✅ **MAJOR**: Optimized A3 layout - extended green header with bleed, added ring binding space
- ✅ **MAJOR**: Consistent PDF naming - print files now use "_print" suffix like web files use "_web"
- ✅ **FIXED**: Photo display paths corrected for new nested folder structure
- ✅ **FIXED**: Calendar container height optimized to 208mm to ensure single-page output
- ✅ **FIXED**: Removed calendar padding for cleaner layout and more photo space
- ✅ **FIXED**: Crop marks only show in PDF, hidden in HTML preview
- ✅ Implemented complete build workflow (--complete option)
- ✅ Added dual-format PDF support (print and web compression modes)
- ✅ Enhanced PDF binding with separate print and web versions
- ✅ Updated --bind-existing to create both print and web bound PDFs
- ✅ Removed unused font files and PDF files from git tracking  

---

## 🎯 Project Overview

This system generates professional A3 landscape photo calendars featuring:

- **Daily macro photography** (one photo per day, 28-31 per month)
- **7-column grid layout** (Monday-Sunday) with ISO week numbering
- **Monthly location themes** with world map integration
- **Smart QR codes** with automatic date picker integration and language detection
- **Full internationalization** with German and Spanish support
- **Dual PDF formats** with intelligent compression:
  - **Print-ready** (CMYK, 300 DPI, PDF/X compliant): ~400MB total
  - **Web-optimized** (minimal file sizes): ~30MB total
- **Complete build workflow** generates both formats in one command
- **Clean minimal design** optimized for A3 print production

---

## 📁 Project Structure

```
calendar/
├── calendar-production/          # Core production system
│   ├── scripts/                  # Python automation scripts
│   │   ├── build_calendar.py     # 🚀 Master build script
│   │   ├── calendar_generator.py # HTML calendar generation
│   │   ├── localization_manager.py # 🌍 i18n support
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
│   │   ├── photo_information.txt # Photo ordering file (YYYYMM\tfilename\tobservation_id)
│   │   └── YYYY/                 # Year directory
│   │       └── MM/               # Month directory (01-12)
│   │           ├── photo1.jpg    # Photos listed in photo_information.txt
│   │           ├── photo2.jpg    # Order determined by file, not filename
│   │           ├── README.md     # Location data (required for all months)
│   │           └── ...           # etc.
│   └── website/                  # GitHub.io companion site (future)
```

---

## 🚀 **Latest Optimizations (July 2025)**

### **Complete Build Workflow** 🆕
- **Single Command**: `--complete` option generates everything in one command
- **Dual-Format PDFs**: Automatically creates print and web-optimized versions
- **Dual PDF Binding**: Separate bound files for print quality and web compression
- **Automatic Updates**: Landing page updated, all assets generated
- **Smart Workflow**: HTML generated once, PDFs created in parallel for efficiency

### **Web-Optimized PDF Mode** 🆕  
- **Smart Compression**: 200px images, 45% JPEG quality for minimal file sizes
- **Target Achievement**: ~30MB total file size for full 12-month calendar
- **92% Size Reduction**: Compared to print version for easy digital sharing
- **Maintains Usability**: Calendar layout and readability preserved for digital viewing
- **Perfect for Sharing**: Ideal file size for email, cloud sharing, mobile viewing

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

### **Cross-Year Photo Support** 🆕
- **YYYYMM Format**: Photo information system upgraded from MM to YYYYMM format
- **Seamless Overflow**: January calendars display December photos from previous year
- **Future-Proof**: December calendars can display January photos from next year  
- **Smart Mapping**: Automatic photo lookup across year boundaries
- **Placeholder Support**: Partial months use placeholder entries for missing days

### **Smart QR Code Integration**
- **Hash Parameters**: QR codes generate URLs with flexible hash formats:
  - `#YYYYMM` (e.g., `#202601`) for month navigation
  - `#YYYYMMDD` (e.g., `#20260115`) for specific date navigation
- **Auto Date Picker**: Landing page automatically sets date based on QR code (month or specific date)
- **Seamless Flow**: Scan printed calendar → auto-navigate to correct month/date online

### **Automation Enhancements**
- **Auto Location Reading**: System reads location data from `photos/YYYY/MM/README.md` files
- **Streamlined Header**: All elements (title, location, QR, map) integrated in 35mm header
- **PDF Consistency**: Enhanced print media CSS ensures uniform dimensions across all output

---

## 📊 PDF Format Comparison

The system generates three PDF formats optimized for different use cases:

| Format    | File Size (per month) | Total (12 months) | Image Size | Quality | Use Case                             |
| --------- | --------------------- | ----------------- | ---------- | ------- | ------------------------------------ |
| **Print** | 33-34MB               | ~400MB            | 800px      | 85%     | Professional printing, CMYK, 300 DPI |
| **Web**   | 2.5-3MB               | **~30MB**         | 200px      | 45%     | Email sharing, mobile viewing        |

**Size Reduction:**
- **Web vs Print**: 92% smaller for easy digital sharing

**Complete Build Output:**
- `YYYY_calendar_print.pdf` - Full quality for printing (~400MB)
- `YYYY_calendar_web.pdf` - Web-optimized for sharing (~30MB)

### **Full Internationalization System** 🌍 **NEW**

**Complete German and Spanish Support** with professional-quality localization:

#### **Core Language Features**
- **Supported Languages**: English (en), German (de), Spanish (es)
- **LocalizationManager**: Centralized translation system with fallbacks
- **Month Names**: Full localization (e.g., "März", "Febrero", "January")
- **Weekday Names**: Both full and short forms (e.g., "Do"/"Donnerstag", "Jue"/"Jueves")
- **Character Encoding**: Full UTF-8 support for special characters (ä, ö, ü, ß, é, á, í)

#### **Smart QR Code Language Detection** 🆕
- **Enhanced URLs**: QR codes include language parameters (`#202603&lang=de`)
- **Automatic UI Switching**: Landing page detects language from QR scan
- **Seamless Flow**: Scan German calendar → German interface automatically
- **Backwards Compatible**: Existing English QR codes continue working

#### **Multi-Language Location Data**
- **README.md Format**: 
  ```
  + location_en: Indonesia
  + location_de: Indonesien  
  + location_es: Indonesia
  + coordinates: 8°017′03″S 115°035′021″E
  ```
- **Smart Fallbacks**: German calendar uses German location, falls back to English if missing
- **Legacy Support**: Old single-language locations still work

#### **Build System Integration**
- **Language Parameter**: `--language de/es/en` for all build commands
- **Output Organization**: Language-specific QR codes and assets
- **Template Localization**: HTML `lang` attributes automatically set
- **Quality Assurance**: All special characters tested in production

#### **Landing Page Localization**
- **Dynamic Translation**: Complete UI translation based on QR parameters
- **Date Formatting**: Locale-appropriate date display (German: "15. März 2026")
- **Alert Messages**: Error messages in user's language
- **Calendar Navigation**: Month names in selected language

**Usage Examples:**
```bash
# German calendar with localized QR codes
python3 scripts/build_calendar.py --year 2026 --month 3 --language de

# Spanish calendar 
python3 scripts/build_calendar.py --year 2026 --month 2 --language es

# Complete German year with both PDF formats
python3 scripts/build_calendar.py --year 2026 --language de --complete
```

**Output Files (Clean Organized Structure):**
- HTML: `output/2026/de/html/202603.html` with `lang="de"` and German month names
- QR Codes: `output/2026/de/assets/qr/qr-2026-03-de.png` linking to German landing page  
- PDFs: `output/2026/de/pdf/print/202603_print.pdf` (print quality)
- PDFs: `output/2026/de/pdf/web/202603_web.pdf` (web optimized)
- Assets: `output/2026/de/assets/maps/map-2026-03.svg` (world maps)

---

## 🔧 Technical Implementation

### Core Components

#### 1. **Photo Management**
- **Structure**: `calendar-production/photos/YYYY/MM/` (e.g., `calendar-production/photos/2026/01/`)
- **Ordering**: Controlled by `calendar-production/photos/photo_information.txt` (tab-separated YYYYMM format)
- **Format**: `.jpg` files, square crop recommended
- **Processing**: Photoshop batch processing with provided specs
- **Cross-Year Support**: ✅ January calendars can show December photos from previous year
- **Location Data**: Each month directory must contain `README.md` with location information

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
- **Multi-language location data**: From `photos/YYYY/MM/README.md` files with language-specific entries
- **Smart QR codes**: Link to `https://sarefo.github.io/calendar/` with language detection
- **Enhanced URL formats**: 
  - `#YYYYMM` (e.g., `#202601`) → English interface, current day if in that month
  - `#YYYYMM&lang=de` (e.g., `#202603&lang=de`) → German interface with automatic translation
  - `#YYYYMMDD&lang=es` (e.g., `#20260215&lang=es`) → Spanish interface with specific date
- **Landing page**: Automatic UI language switching and date picker setting
- **Location fallbacks**: German calendars use German locations, fall back to English if missing
- **World maps**: Simplified SVG with location markers in streamlined header
- **Data validation**: System stops if location data is missing or has placeholders

#### 5. **Multi-Language Location Data System**
- **Multi-language entries**: Location data stored in `README.md` files with `location_en`, `location_de`, `location_es`
- **Smart fallbacks**: German calendars use German locations, fall back to English if German not available
- **Legacy compatibility**: Old single `location:` entries still work for backwards compatibility
- **Auto-Validation**: Checks for placeholder values and missing required fields
- **Language-aware errors**: Clear instructions include multi-language format examples
- **Simple Maintenance**: Location data co-located with photos for easy management

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
   # Format: YYYYMM\tfilename\tobservation_id (tab-separated)
   # Example: 202601\tIMG_8477\t149640464
   # Note: For partial months, use placeholder entries for missing days
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
- **Header section**: 38mm total (extends to top with 3mm bleed, content positioned 10mm from top for ring binding)
- **Calendar grid**: 208mm (optimized for single-page output with clear white margin at bottom)
- **Bottom margin**: 5mm clear white space ensuring professional appearance
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

**🚀 RECOMMENDED: Complete Build (Everything in One Command)**
```bash
# Complete build: HTML + Print PDFs + Web PDFs + Bind both versions + Update landing page
python3 scripts/build_calendar.py --year 2026 --complete

# Complete German calendar with all formats and localized QR codes
python3 scripts/build_calendar.py --year 2026 --language de --complete

# Complete Spanish calendar
python3 scripts/build_calendar.py --year 2026 --language es --complete

# Complete build for specific months
python3 scripts/build_calendar.py --year 2026 --months "1,2,3" --complete
```

**📋 Standard Build Options**
```bash
# Check photos for specific month
python3 scripts/build_calendar.py --check-photos --year 2026 --month 1

# Build single month (creates both print and web PDFs automatically)
python3 scripts/build_calendar.py --year 2026 --month 1

# Build German calendar for specific month (dual PDF generation)
python3 scripts/build_calendar.py --year 2026 --month 3 --language de

# Build Spanish calendar for specific months (dual PDF generation)
python3 scripts/build_calendar.py --year 2026 --months "1,2,3" --language es

# Build full year with print package
python3 scripts/build_calendar.py --year 2026

# Build full year and bind into single 12-page PDF
python3 scripts/build_calendar.py --year 2026 --bind-pdf

# Bind existing monthly PDFs without regenerating - creates both print and web versions
python3 scripts/build_calendar.py --year 2026 --bind-existing

# Skip PDF generation (HTML only)
python3 scripts/build_calendar.py --year 2026 --no-pdf
```

**💾 Compression Options**
```bash
# Web-optimized PDFs (smaller file sizes for digital sharing)
python3 scripts/build_calendar.py --year 2026 --web-pdf

# Compare both formats
python3 scripts/build_calendar.py --year 2026 --month 1          # Print (33MB)
python3 scripts/build_calendar.py --year 2026 --month 1 --web-pdf    # Web (2.5MB)
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
- Verify `calendar-production/photos/photo_information.txt` has entries in YYYYMM format
- Ensure tab-separated format: `YYYYMM\tfilename\tobservation_id`
- For partial months, add placeholder entries for missing days
- Check that `README.md` exists in photo directory with location data
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

**"PDF binding failed"**
- Install PDF merger: `python3 -m pip install pypdf`
- Alternative: `pip install PyPDF2`
- Check existing PDFs are in `output/print-ready/` directory
- Ensure PDF files follow `YYYYMM.pdf` naming convention

**"Can't find output HTML or PDF files"**
- **HTML Files**: Located at `calendar-production/output/YYYYMM.html` (e.g., `output/202609.html`)
- **PDF Files**: Located at `calendar-production/output/print-ready/YYYYMM.pdf` (e.g., `output/print-ready/202609.pdf`)
- **Language-specific assets**: QR codes include language suffix (e.g., `output/assets/qr-2026-09-de.png`)
- **Check current directory**: Run commands from `calendar-production/` directory
- **Verify build success**: Look for "✅ Generated HTML:" and "🎉 Successfully built" messages

---

## 📞 Support & Development

### Current Status
✅ **Production-ready workflow with complete build system**  
✅ **Dynamic row layout system - eliminates empty rows completely**  
✅ **Enhanced photo presentation: Variable dimensions (42.4mm vs 34.7mm height)**  
✅ **Streamlined design: removed weekday overlays and placeholders**  
✅ **Smart QR integration: flexible hash parameters for month/date navigation**  
✅ **Auto-location reading from README.md files**  
✅ **Dual-format PDF generation: Print and Web-optimized modes**  
✅ **Complete build workflow: Single command generates everything**  
✅ **Dual PDF binding: Separate print and web-optimized bound versions**  
✅ **Web-compression: ~30MB total file size achievement**  
✅ **Landing page with hash parameter support implemented**  
✅ **Clean header design with integrated elements**  
✅ **Enhanced print media CSS for PDF consistency**  
✅ **Cross-year photo support: YYYYMM format with seamless overflow**

### Next Steps
1. ✅ **Dynamic calendar layout system - NO MORE EMPTY ROWS!**
2. ✅ **Enhanced QR code integration with smart landing page**
3. ✅ **Optimized photo sizing - 10% larger photos in 75% of months**
4. ✅ **Auto-location reading and hash parameter support**
5. ✅ **Cross-year photo overflow - January shows December photos**
6. ✅ **Complete build workflow with dual-format PDF generation**
7. ✅ **Web-optimized PDF mode achieving ~30MB target**
8. ✅ **Full internationalization with German and Spanish support**
9. ✅ **Clean folder structure with organized output/2026/ hierarchy**
10. ⏳ **Generate remaining months for 2026 calendar with multi-language support**
10. ⏳ **Deploy optimized system to GitHub Pages with language detection**

### Contact
- **Project Repository**: This calendar system
- **Documentation**: This file (`CLAUDE.md`)
- **Issue Tracking**: Document issues encountered during testing