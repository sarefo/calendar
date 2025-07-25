// Global variables
let currentLanguage = 'en';
let translations = {};
let photoObservations = {};
let currentDate = new Date();

// DOM elements
const todayInput = document.getElementById('todayDate');
const currentDateDisplay = document.getElementById('currentDateDisplay');
const pickDateBtn = document.getElementById('pickDateBtn');

// Load JSON data
async function loadData() {
    try {
        // Load translations
        const translationsResponse = await fetch('data/translations.json');
        translations = await translationsResponse.json();
        
        // Load photo observations
        const observationsResponse = await fetch('data/photo-observations.json');
        photoObservations = await observationsResponse.json();
        
        // Initialize the app after data is loaded
        initializeApp();
    } catch (error) {
        console.error('Error loading data:', error);
        // Fallback to default language if data loading fails
        initializeApp();
    }
}

// Check for URL parameters (e.g., ?lang=de)
function checkUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    
    if (langParam && ['en', 'de', 'es'].includes(langParam)) {
        updateLanguage(langParam);
    }
}

// Initialize the application
function initializeApp() {
    // Ensure language is always explicitly set
    if (!currentLanguage || currentLanguage === '') {
        currentLanguage = 'en';
    }
    
    // Check for URL parameters first
    checkUrlParameters();
    
    // Always update to the current language (even if it's 'en')
    updateLanguage(currentLanguage);
    
    // Initialize date and language
    if (!setDateFromHash()) {
        updateDateDisplay(new Date());
    }

    // Initialize month links with current language
    updateMonthLinks(currentLanguage);

    // Initialize DuoNat link based on device
    updateDuoNatLink();

    // Listen for hash changes
    window.addEventListener('hashchange', setDateFromHash);

    // Event listeners
    currentDateDisplay.addEventListener('click', openCurrentObservation);
    
    // Add window resize listener to readjust font size
    window.addEventListener('resize', function() {
        if (currentDateDisplay) {
            adjustFontSize(currentDateDisplay);
        }
    });

    let isDatePickerOpen = false;

    pickDateBtn.addEventListener('click', function () {
        // Prevent multiple rapid clicks
        if (isDatePickerOpen) return;

        isDatePickerOpen = true;

        // Temporarily make input focusable but still invisible
        todayInput.style.position = 'fixed';
        todayInput.style.left = '50%';
        todayInput.style.top = '50%';
        todayInput.style.transform = 'translate(-50%, -50%)';
        todayInput.style.opacity = '0';
        todayInput.style.pointerEvents = 'none';
        todayInput.style.zIndex = '1000';

        // Focus and open picker
        setTimeout(() => {
            todayInput.focus();
            if (typeof todayInput.showPicker === 'function') {
                todayInput.showPicker();
            }
        }, 10);
    });

    // Function to reset the picker state and hide input
    function resetDatePickerState() {
        // Return input to completely hidden state
        todayInput.style.position = 'absolute';
        todayInput.style.left = '-9999px';
        todayInput.style.top = 'auto';
        todayInput.style.transform = 'none';
        todayInput.style.opacity = '0';
        todayInput.style.zIndex = '-1';

        isDatePickerOpen = false;
    }

    // Handle date selection
    todayInput.addEventListener('change', function () {
        const selectedDate = this.valueAsDate;
        if (selectedDate) {
            updateDateDisplay(selectedDate);
            resetDatePickerState();
            openCurrentObservation();
        }
    });

    // Reset picker state when user clicks away or cancels
    todayInput.addEventListener('blur', function () {
        if (isDatePickerOpen) {
            setTimeout(() => {
                // Double-check that the date picker should still be closed
                if (isDatePickerOpen && document.activeElement !== todayInput) {
                    resetDatePickerState();
                }
            }, 300);
        }
    });
}

// Detect Android devices
function isAndroid() {
    return /Android/i.test(navigator.userAgent);
}

// Update DuoNat link based on device
function updateDuoNatLink() {
    const duonatLink = document.querySelector('.duonat-link');
    if (duonatLink) {
        if (isAndroid()) {
            duonatLink.href = 'https://play.google.com/store/apps/details?id=app.duo_nat';
        } else {
            duonatLink.href = 'https://duo-nat.web.app/';
        }
    }
}

// Update UI language
function updateLanguage(language) {
    currentLanguage = language;
    document.documentElement.lang = language;

    const t = translations[language] || translations.en || {};

    // Update text content
    const titleElement = document.querySelector('h1');
    if (titleElement && t.title) titleElement.textContent = t.title;
    
    const subtitleElement = document.querySelector('.subtitle');
    if (subtitleElement && t.subtitle) subtitleElement.textContent = t.subtitle;
    
    const dateQuestionElement = document.querySelector('.date-section h2');
    if (dateQuestionElement && t.dateQuestion) dateQuestionElement.textContent = t.dateQuestion;
    
    const dateHelpElement = document.querySelector('.date-help');
    if (dateHelpElement && t.dateHelp) dateHelpElement.textContent = t.dateHelp;
    
    const pickDateBtnElement = document.getElementById('pickDateBtn');
    if (pickDateBtnElement && t.pickDateBtn) pickDateBtnElement.textContent = t.pickDateBtn;
    
    const calendarSectionElement = document.querySelector('.calendar-section h3');
    if (calendarSectionElement && t.viewCalendar) calendarSectionElement.textContent = t.viewCalendar;
    
    const duonatTitleElement = document.querySelector('.duonat-title');
    if (duonatTitleElement && t.duonatTitle) duonatTitleElement.textContent = t.duonatTitle;
    
    const duonatDescriptionElement = document.querySelector('.duonat-description');
    if (duonatDescriptionElement && t.duonatDescription) duonatDescriptionElement.textContent = t.duonatDescription;
    
    const footerElement = document.querySelector('.footer');
    if (footerElement && t.footerText && t.onINaturalist) {
        footerElement.innerHTML = t.footerText + ' <a href="https://www.inaturalist.org/observations?place_id=any&user_id=portioid&verifiable=any" target="_blank" style="color: #74ac00; text-decoration: none; font-weight: 600;">portioid</a> ' + t.onINaturalist;
    }

    // Update calendar month links
    updateMonthLinks(language);

    // Update DuoNat link based on device
    updateDuoNatLink();

    // Update date display
    updateDateDisplay(currentDate);
}

// Update month links based on language
function updateMonthLinks(language) {
    const monthsGrid = document.getElementById('monthsGrid');
    if (!monthsGrid) return;
    
    monthsGrid.innerHTML = '';

    // Generate month links for the specified language
    for (let month = 1; month <= 12; month++) {
        const monthStr = month.toString().padStart(2, '0');
        const yearMonth = `2026${monthStr}`;
        const link = document.createElement('a');
        link.href = `calendar-production/output/2026/${language}/html/${yearMonth}.html`;
        link.className = 'month-link';
        link.textContent = month.toString();
        monthsGrid.appendChild(link);
    }
}

// Format date for display
function formatDateForDisplay(date) {
    const t = translations[currentLanguage] || translations.en || {};
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };

    // Use appropriate locale for date formatting
    let locale = 'en-US';
    if (currentLanguage === 'de') locale = 'de-DE';
    else if (currentLanguage === 'es') locale = 'es-ES';

    return date.toLocaleDateString(locale, options);
}

// Format date for observation lookup (YYYY-MM-DD)
function formatDateForLookup(date) {
    return date.toISOString().split('T')[0];
}

// Update the displayed date
function updateDateDisplay(date) {
    currentDate = date;
    if (currentDateDisplay) {
        currentDateDisplay.textContent = formatDateForDisplay(date);
        adjustFontSize(currentDateDisplay);
    }
    if (todayInput) {
        todayInput.valueAsDate = date;
    }
}

// Dynamically adjust font size to fill the button
function adjustFontSize(element) {
    const maxFontSize = 1.3; // em
    const minFontSize = 0.8; // em
    
    // Start with a reasonable font size
    let fontSize = maxFontSize;
    element.style.fontSize = fontSize + 'em';
    
    // Check if text overflows and reduce font size if needed
    let iterations = 0;
    while (element.scrollWidth > element.clientWidth && fontSize > minFontSize && iterations < 10) {
        fontSize -= 0.05;
        element.style.fontSize = fontSize + 'em';
        iterations++;
    }
    
    // If text is much smaller than container, try to increase font size
    const textWidth = element.scrollWidth;
    const containerWidth = element.clientWidth;
    
    if (textWidth < containerWidth * 0.8 && fontSize < maxFontSize) {
        while (element.scrollWidth < containerWidth * 0.9 && fontSize < maxFontSize && iterations < 20) {
            fontSize += 0.02;
            element.style.fontSize = fontSize + 'em';
            if (element.scrollWidth > containerWidth) {
                fontSize -= 0.02;
                element.style.fontSize = fontSize + 'em';
                break;
            }
            iterations++;
        }
    }
}

// Open observation for current date
function openCurrentObservation() {
    let dateString = formatDateForLookup(currentDate);
    let observationId = photoObservations[dateString];

    // If no observation found for current date, try 2026 equivalent for perpetual calendar
    if (!observationId || observationId === '0') {
        const currentDateObj = new Date(currentDate);
        const month = currentDateObj.getMonth() + 1; // 1-12
        const day = currentDateObj.getDate();
        
        // Create 2026 equivalent date
        const year2026DateString = `2026-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        observationId = photoObservations[year2026DateString];
    }

    if (observationId && observationId !== '0') {
        const url = `https://www.inaturalist.org/observations/${observationId}`;
        window.open(url, '_blank');
    } else {
        const t = translations[currentLanguage] || translations.en || {};
        const message = t.noObservation || 'No observation available for this date yet.';
        alert(message);
    }
}

// Check for hash parameter like #202601 or #20260115 or #202601&lang=de or #01 (perpetual)
function setDateFromHash() {
    const hash = window.location.hash.substring(1); // Remove #

    // Parse hash to extract date and language parameters
    let dateString = hash;
    let language = 'en';

    if (hash.includes('&lang=')) {
        const parts = hash.split('&lang=');
        dateString = parts[0];
        language = parts[1];

        // Validate language and update UI
        if (['en', 'de', 'es'].includes(language)) {
            updateLanguage(language);
        }
    }

    // Check for YYYYMMDD format (8 digits)
    if (dateString && dateString.match(/^\d{8}$/)) {
        // Parse YYYYMMDD format
        const year = parseInt(dateString.substring(0, 4));
        const month = parseInt(dateString.substring(4, 6));
        const day = parseInt(dateString.substring(6, 8));

        if (year >= 2000 && year <= 3000 && month >= 1 && month <= 12 && day >= 1 && day <= 31) {
            const targetDate = new Date(year, month - 1, day);
            // Verify the date is valid (handles leap years and month lengths)
            if (targetDate.getFullYear() === year &&
                targetDate.getMonth() === month - 1 &&
                targetDate.getDate() === day) {
                updateDateDisplay(targetDate);
                return true;
            }
        }
    }
    // Check for YYYYMM format (6 digits)
    else if (dateString && dateString.match(/^\d{6}$/)) {
        // Parse YYYYMM format
        const year = parseInt(dateString.substring(0, 4));
        const month = parseInt(dateString.substring(4, 6));

        if (year >= 2000 && year <= 3000 && month >= 1 && month <= 12) {
            // Check if current date is within that month
            const now = new Date();
            const currentYear = now.getFullYear();
            const currentMonth = now.getMonth() + 1;

            let targetDate;
            if (currentYear === year && currentMonth === month) {
                // Use current date if we're in the target month
                targetDate = now;
            } else {
                // Use first day of the target month
                targetDate = new Date(year, month - 1, 1);
            }

            updateDateDisplay(targetDate);
            return true;
        }
    }
    // Check for perpetual calendar format (MM - 1 or 2 digits)
    else if (dateString && dateString.match(/^\d{1,2}$/)) {
        // Parse MM format for perpetual calendar
        const month = parseInt(dateString);

        if (month >= 1 && month <= 12) {
            const now = new Date();
            const currentYear = now.getFullYear();
            const currentMonth = now.getMonth() + 1;

            let targetDate;
            if (currentMonth === month) {
                // Use current date if we're in the target month
                targetDate = now;
            } else {
                // Use first day of the target month in current year
                targetDate = new Date(currentYear, month - 1, 1);
            }

            updateDateDisplay(targetDate);
            return true;
        }
    }
    return false;
}


// Load data when the page loads
document.addEventListener('DOMContentLoaded', loadData);