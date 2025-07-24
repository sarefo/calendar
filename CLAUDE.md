# A3 Landscape Photo Calendar Production Workflow

**Project**: Professional macro photography calendar with daily photos  
**Format**: A3 Landscape (420mm × 297mm)  
**Target**: Print-ready PDFs for professional printing  
**Status**: ✅ Production-ready with complete build workflow, multi-format PDF generation, and full internationalization  
**Date**: Updated July 2025  

---

## 📝 Documentation Updates

**IMPORTANT**: Always update this CLAUDE.md file after successfully implementing any changes to the calendar production system. This ensures the documentation stays current with the actual functionality and provides accurate guidance for future development.

**Latest Updates (July 2025)**:
- ✅ **MAJOR**: Professional cover page system with 12-photo showcase grid
- ✅ **MAJOR**: Multi-language cover page support (English, German, Spanish)
- ✅ **MAJOR**: Cover page integration in complete build workflow (--complete includes cover)
- ✅ **MAJOR**: Dedicated --cover option for standalone cover page generation
- ✅ **MAJOR**: Cover page PDF generation (both print and web formats)
- ✅ **MAJOR**: Cover photo selection from photo_information.txt "cover" column
- ✅ **MAJOR**: Perpetual calendar system - day-only layout without weekdays or week numbers
- ✅ **MAJOR**: Streamlined world map system - single map per month shared across all languages
- ✅ **MAJOR**: GitHub Pages integration - calendar HTML files accessible via subdirectory paths
- ✅ **MAJOR**: Enhanced PDF naming with language extensions and project branding
- ✅ **MAJOR**: Full internationalization support (German and Spanish)
- ✅ **MAJOR**: Simplified folder structure - organized output under output/2026/
- ✅ **MAJOR**: Dual PDF generation - single commands now create both print and web PDFs
- ✅ **MAJOR**: Optimized A3 layout - extended green header with bleed, added ring binding space
- ✅ **MAJOR**: Perpetual calendar landing page support - handles #01-#12 parameters
- ✅ **FIXED**: Complete 12-month cover photo system (all months 1-12 now have cover photos)
- ✅ **FIXED**: Calendar container height optimized to 208mm to ensure single-page output
- ✅ **FIXED**: Crop marks only show in PDF, hidden in HTML preview
- ✅ **FIXED**: QR code processing - excluded from smart cropping, maintains square aspect ratio, saved as PNG
- ✅ **FIXED**: Landing page perpetual calendar navigation - maps month-only parameters to current year  

---

## 🎯 Project Overview

This system generates professional A3 landscape photo calendars featuring:

### **Two Calendar Types:**

#### **Year-Based Calendars** (Traditional)
- **7-column grid layout** (Monday-Sunday) with ISO week numbering
- **Dynamic row layout** (5-row vs 6-row months) with optimized photo sizing
- **Cross-year photo support** with seamless month overflow
- **Complete yearly workflows** with automated binding

#### **Perpetual Calendars** 🆕 (Universal)
- **Day-only layout** without weekdays or week numbers - works for any year
- **6x5 grid for short months** (28-30 days) and **7x5 grid for long months** (31 days)
- **February 29th support** included for leap year compatibility
- **Larger month names** (no year display) with prominent 50pt typography
- **Universal QR codes** with simplified month-only hash parameters

### **Professional Cover Page System** 🆕
- **4×3 photo showcase grid** featuring 12 selected photos (one per month)
- **Multi-language titles and subtitles** with elegant typography
- **Year badges** for year-based calendars or "Perpetual Calendar" badges
- **Location integration** with automatic reading from README.md files
- **Cover photo selection** via "cover" marking in photo_information.txt
- **Dual PDF formats** (print-ready and web-optimized versions)
- **Professional A3 layout** with proper bleed and crop marks

### **Shared Features:**
- **Daily macro photography** (one photo per day, 28-31 per month)
- **Monthly location themes** with world map integration
- **Smart QR codes** with automatic date picker integration and language detection
- **Full internationalization** with German and Spanish support
- **Dual PDF formats** with intelligent compression:
  - **Print-ready** (CMYK, 300 DPI, PDF/X compliant): ~400MB total
  - **Web-optimized** (minimal file sizes): ~30MB total
- **Complete build workflow** generates both formats in one command
- **GitHub Pages compatibility** with calendar HTML files served from subdirectories
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
│   │   ├── calendar_grid.html    # Year-based calendar template
│   │   ├── calendar_grid_perpetual.html # Perpetual calendar template
│   │   ├── cover_page.html       # Cover page template
│   │   └── print_styles.css      # CMYK print-optimized styles
│   ├── data/                     # Configuration & content
│   │   ├── calendar_config.json  # Calendar settings
││   ├── output/                   # Generated files
│   │   ├── YYYY/lang/pdf/        # Final PDFs (print and web)
│   │   └── YYYY/lang/html/       # Calendar HTML files
│   ├── photos/                   # Photo repository (consolidated location)
│   │   ├── photo_information.txt # Photo ordering file (YYYYMM\tfilename\tobservation_id\tcover_photo)
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
  - `#YYYYMM` (e.g., `#202601`) for year-based month navigation
  - `#YYYYMMDD` (e.g., `#20260115`) for specific date navigation
  - `#MM` (e.g., `#01`, `#12`) for perpetual calendar month navigation
- **Auto Date Picker**: Landing page automatically sets date based on QR code (month or specific date)
- **Smart Year Mapping**: Perpetual calendar QR codes map to current year, today's date if in that month
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
  + location: Indonesia
  + coordinates: 8°017′03″S 115°035′021″E
  + year: 2026
  ```
- **Simple Format**: Single location entry per month directory
- **Consistent Structure**: All location data follows same format

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
- PDFs: `output/2026/de/pdf/print/portioid_calendar_202603_de_print.pdf` (print quality)
- PDFs: `output/2026/de/pdf/web/portioid_calendar_202603_de_web.pdf` (web optimized)
- Bound PDFs: `output/2026/de/pdf/portioid_calendar_2026_de_print.pdf` (full year print)
- Bound PDFs: `output/2026/de/pdf/portioid_calendar_2026_de_web.pdf` (full year web)
- Assets: `output/2026/de/assets/maps/map-2026-03.svg` (world maps)

### **Enhanced PDF Naming Convention** 🆕

**New Format**: `portioid_calendar_YYYYMM_LANG_TYPE.pdf`

**Examples:**
- `portioid_calendar_202603_en_print.pdf` - March 2026 English print version
- `portioid_calendar_202603_de_web.pdf` - March 2026 German web version  
- `portioid_calendar_2026_es_print.pdf` - Full year 2026 Spanish print bound

**Benefits:**
- **Clear Project Branding**: "portioid_calendar" prefix identifies the project
- **Language Identification**: Easy to distinguish language versions
- **Type Clarity**: "_print" vs "_web" makes compression level obvious
- **Professional Naming**: Consistent, descriptive filenames for sharing and archiving

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
  - `#YYYYMM` (e.g., `#202601`) → Year-based calendar, current day if in that month
  - `#YYYYMM&lang=de` (e.g., `#202603&lang=de`) → German interface with automatic translation
  - `#YYYYMMDD&lang=es` (e.g., `#20260215&lang=es`) → Spanish interface with specific date
  - `#MM` (e.g., `#01`, `#12`) → Perpetual calendar, maps to current year and today if in that month
  - `#MM&lang=de` (e.g., `#07&lang=de`) → German perpetual calendar interface
- **Landing page**: Automatic UI language switching and date picker setting
- **Location fallbacks**: German calendars use German locations, fall back to English if missing
- **World maps**: Simplified SVG with location markers in streamlined header
- **Data validation**: System stops if location data is missing or has placeholders

#### 5. **Location Data System**
- **Simple format**: Location data stored in `README.md` files with single `location:` entry
- **Required fields**: Each month directory must contain location and coordinates
- **Auto-Validation**: Checks for placeholder values and missing required fields
- **Clear error messages**: Instructions show exact format requirements
- **Simple Maintenance**: Location data co-located with photos for easy management

---

## 🔄 Perpetual Calendar System 🆕

### **Overview**
The perpetual calendar system generates universal calendars that work for any year without weekdays or week numbers. Perfect for timeless photo displays and universal planning.

### **Key Features**

#### **Dynamic Grid Layout**
- **6x5 grid** for short months (28-30 days): February, April, June, September, November
- **7x5 grid** for long months (31 days): January, March, May, July, August, October, December
- **Always 5 rows** - no wasted space regardless of month length
- **Wider photos** in 6-column layout (63mm vs 54mm width)

#### **February 29th Support** 
- **Always included** in perpetual February calendars
- **Leap year compatible** - works for both leap and non-leap years
- **Photo support** available from 2026 photo collection

#### **Simplified Design**
- **No year display** - prominent 50pt month names
- **No weekday headers** - clean day-only layout (1, 2, 3... 31)
- **No week numbers** - eliminates year-specific elements
- **Universal QR codes** - simple month-only hash parameters (`#01`, `#02`, etc.)
- **Smart landing page integration** - automatically maps to current year with today's date if in that month

### **Usage Commands**

```bash
# Generate single perpetual month (HTML + both PDFs)
python3 scripts/build_calendar.py --months "2"

# Generate multiple perpetual months  
python3 scripts/build_calendar.py --months "1,2,3,4"

# Generate all 12 perpetual months
python3 scripts/build_calendar.py

# Multi-language perpetual calendars
python3 scripts/build_calendar.py --months "2" --language de  # German
python3 scripts/build_calendar.py --months "2" --language es  # Spanish

# HTML only (no PDFs)
python3 scripts/build_calendar.py --months "2" --no-pdf
```

### **Output Structure**
```
output/perpetual/
├── assets/maps/          # Shared world maps (language-independent)
├── en/                   # English perpetual calendars
│   ├── html/            # 01.html, 02.html, ... 12.html
│   ├── pdf/print/       # portioid_calendar_MM_en_print.pdf
│   ├── pdf/web/         # portioid_calendar_MM_en_web.pdf
│   └── assets/qr/       # qr-MM.png (English QR codes)
├── de/                   # German perpetual calendars  
│   └── assets/qr/       # qr-MM-de.png (German QR codes)
└── es/                   # Spanish perpetual calendars
    └── assets/qr/       # qr-MM-es.png (Spanish QR codes)
```

### **File Naming Convention**
- **HTML**: `MM.html` (e.g., `02.html` for February)
- **Print PDFs**: `portioid_calendar_MM_lang_print.pdf`
- **Web PDFs**: `portioid_calendar_MM_lang_web.pdf`
- **QR Codes**: `qr-MM-lang.png` (English omits language suffix)

### **Layout Examples**
- **February (29 days)**: 6x5 grid with wider 63mm photos
- **January (31 days)**: 7x5 grid with standard 54mm photos  
- **April (30 days)**: 6x5 grid with wider 63mm photos

### **Comparison: Year-Based vs Perpetual**
```bash
# Year-based calendar (traditional)
python3 scripts/build_calendar.py --year 2026 --months "2"
# → Output: 2026/en/html/202602.html

# Perpetual calendar (universal) 
python3 scripts/build_calendar.py --months "2"
# → Output: perpetual/en/html/02.html
```

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
   # Format: YYYYMM\tfilename\tobservation_id\tcover_photo (tab-separated)
   # Example: 202601\tIMG_8477\t149640464\tcover
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
   pip install -r requirements.txt
   ```

2. **Generate Print-Ready PDFs**
   ```bash
   python3 scripts/build_calendar.py --year 2026
   ```

3. **Access Print-Ready Files**
   - Generated in `output/YYYY/lang/pdf/print/`
   - Contains high-quality PDFs optimized for printing
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

#### **Year-Based Calendars**
```bash
# Complete build: HTML + Print PDFs + Web PDFs + Cover Page + Bind both versions + Update landing page
python3 scripts/build_calendar.py --year 2026 --complete

# Complete German calendar with all formats, cover page, and localized QR codes
python3 scripts/build_calendar.py --year 2026 --language de --complete

# Complete Spanish calendar with cover page
python3 scripts/build_calendar.py --year 2026 --language es --complete

# Complete build for specific months (no cover page for partial builds)
python3 scripts/build_calendar.py --year 2026 --months "1,2,3" --complete
```

#### **Perpetual Calendars** 🆕
```bash
# Complete perpetual calendar - all 12 months + cover page (HTML + both PDF formats)
python3 scripts/build_calendar.py --complete

# Complete German perpetual calendar with cover page and localized QR codes
python3 scripts/build_calendar.py --language de --complete

# Complete perpetual calendar for specific months (no cover page for partial builds)
python3 scripts/build_calendar.py --months "1,2,3" --complete
```

#### **Cover Page Generation** 🆕
```bash
# Generate English cover page for 2026 (HTML + both PDFs)
python3 scripts/build_calendar.py --cover --year 2026 --language en

# Generate German perpetual cover page (HTML + both PDFs)
python3 scripts/build_calendar.py --cover --language de

# Generate Spanish cover page (HTML only)
python3 scripts/build_calendar.py --cover --year 2026 --language es --no-pdf

# Generate cover pages for multiple languages
python3 scripts/build_calendar.py --cover --year 2026 --language en,de,es
```

**📋 Standard Build Options**

#### **Year-Based Calendar Commands**
```bash
# Build single month (creates both print and web PDFs automatically)
python3 scripts/build_calendar.py --year 2026 --months "1"

# Build German calendar for specific month (dual PDF generation)
python3 scripts/build_calendar.py --year 2026 --months "3" --language de

# Build Spanish calendar for specific months (dual PDF generation)
python3 scripts/build_calendar.py --year 2026 --months "1,2,3" --language es
```

#### **Perpetual Calendar Commands** 🆕
```bash
# Build single perpetual month (dual PDF generation)
python3 scripts/build_calendar.py --months "2"

# Build German perpetual month with February 29th support
python3 scripts/build_calendar.py --months "2" --language de

# Build multiple perpetual months
python3 scripts/build_calendar.py --months "1,2,3,4"

# HTML only (no PDFs)
python3 scripts/build_calendar.py --months "2" --no-pdf
```

# Build full year with print package
python3 scripts/build_calendar.py --year 2026

# Build full year and bind into single 12-page PDF
python3 scripts/build_calendar.py --year 2026 --bind-pdf

# Bind existing monthly PDFs without regenerating - creates both print and web versions
python3 scripts/build_calendar.py --year 2026 --bind-existing

# Build full year with both print and web PDFs + binding
python3 scripts/build_calendar.py --year 2026 --bind-pdf

# Skip PDF generation (HTML only)
python3 scripts/build_calendar.py --year 2026 --no-pdf
```

**💾 PDF Output Formats** 🆕
By default, all calendar build commands create BOTH print and web PDFs automatically:
```bash
# Single month - creates both print (33MB) and web (2.5MB) PDFs
python3 scripts/build_calendar.py --year 2026 --month 1

# Multiple months - creates both formats for each month  
python3 scripts/build_calendar.py --year 2026 --months "11,12"

# Full year - creates both formats (print: ~400MB, web: ~30MB total)
python3 scripts/build_calendar.py --year 2026
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
- **Additional language support** (Portuguese, French)
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
pip install -r requirements.txt
```

**"No photos found for month"**
- Check photo directory structure: `calendar-production/photos/YYYY/MM/`
- Ensure photos have `.jpg` extension  
- Verify `calendar-production/photos/photo_information.txt` has entries in YYYYMM format
- Ensure tab-separated format: `YYYYMM\tfilename\tobservation_id\tcover_photo`
- For partial months, add placeholder entries for missing days
- Check that `README.md` exists in photo directory with location data
- Verify photo files exist in the specified month directory

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
- Check existing PDFs are in `output/YYYY/lang/pdf/print/` directory
- Ensure PDF files follow `YYYYMM.pdf` naming convention

**"No cover photo found for YYYYMM"**
- Check `calendar-production/photos/photo_information.txt` for entries marked with "cover" in 4th column
- Format should be: `YYYYMM\tfilename\tobservation_id\tcover`
- Ensure all 12 months (202601-202612) have cover photos marked
- Cover photos must exist as `.jpg` files in respective month directories
- Run: `python3 scripts/build_calendar.py --cover --year 2026 --no-pdf` to test cover generation

**"Cover page generation failed"**
- Verify location data exists in all month README.md files
- Check that cover photos exist in `photos/YYYY/MM/` directories
- Ensure photo_information.txt uses tab-separated format with cover column
- Test individual components: location reading, photo loading, template rendering

**"Can't find output HTML or PDF files"**
- **Calendar Files**: `output/YYYY/lang/html/YYYYMM.html` and `output/YYYY/lang/pdf/print|web/`
- **Perpetual Files**: `output/perpetual/lang/html/MM.html` and `output/perpetual/lang/pdf/`
- **Cover Files**: `output/YYYY/lang/html/cover_YYYY.html` or `output/perpetual/lang/html/cover_perpetual.html`
- **Cover PDFs**: `portioid_calendar_cover_YYYY_lang_print.pdf` and `portioid_calendar_cover_YYYY_lang_web.pdf`
- **Check current directory**: Run commands from `calendar-production/` directory
- **Verify build success**: Look for "✅ Generated HTML:" and "🎉 Successfully built" messages

---

## 📞 Support & Development

### Current Status
✅ **Production-ready workflow with complete build system including cover pages**  
✅ **Professional cover page system with 12-photo showcase grid**  
✅ **Multi-language cover page support (English, German, Spanish)**
✅ **Cover page integration in complete build workflow (--complete includes cover)**  
✅ **Dedicated --cover option for standalone cover page generation**  
✅ **Cover page PDF generation (both print and web formats)**  
✅ **Complete 12-month cover photo system (all months 1-12 have cover photos)**  
✅ **Dynamic row layout system - eliminates empty rows completely**  
✅ **Enhanced photo presentation: Variable dimensions (42.4mm vs 34.7mm height)**  
✅ **Smart QR integration: flexible hash parameters for month/date navigation**  
✅ **Auto-location reading from README.md files**  
✅ **Dual-format PDF generation: Print and Web-optimized modes**  
✅ **Complete build workflow: Single command generates everything**  
✅ **Dual PDF binding: Separate print and web-optimized bound versions**  
✅ **Landing page with hash parameter support implemented**  
✅ **Perpetual calendar landing page integration - handles #01-#12 parameters**  
✅ **Clean header design with integrated elements**  
✅ **Enhanced print media CSS for PDF consistency**  
✅ **Cross-year photo support: YYYYMM format with seamless overflow**

### Next Steps
1. ✅ **Professional cover page system with 12-photo showcase grid**
2. ✅ **Multi-language cover page support with localized titles**
3. ✅ **Cover page integration in complete build workflow**
4. ✅ **Dedicated --cover option for standalone generation**
5. ✅ **Cover page PDF generation (print and web formats)**
6. ✅ **Complete 12-month cover photo system**
7. ✅ **Dynamic calendar layout system - NO MORE EMPTY ROWS!**
8. ✅ **Enhanced QR code integration with smart landing page**
9. ✅ **Complete build workflow with dual-format PDF generation**
10. ✅ **Full internationalization with German and Spanish support**
11. ⏳ **Generate remaining months for 2027+ calendar years**

### Contact
- **Project Repository**: This calendar system
- **Documentation**: This file (`CLAUDE.md`)
- **Issue Tracking**: Document issues encountered during testing