## General
+ consider using sunday first for US/Canada/Mexico/Australia
  + add that info to pdf filenames
  + needs to be part of i18n somehow…
+ improve QR code layout
  + rounder
  + fitting better into frame
  + slightly more transparent (hence more green)

## PDF version
+ make sure spiral binding does not ruin title elements

## Landing page
+ improve page layout (laptop/mobile)
+ if applicable: show today's photo with short explanation
  + or if full date given in URL
  + need to add species names for that (i18n!)

## HTML version
+ check if we really need hardcoded html for each language
+ website: make calendar html mobile ready
+ remove crop marks and bleed
+ able to navigate to next/previous month

## Perpetual calendar ✅ COMPLETED
+ ✅ consider changing qr code #202601 etc. url parameter - implemented simple #MM format for perpetual
+ ✅ perpetual calendar (no weekdays or week numbers) - implemented with day-only layout
+ ✅ scrap previous/next month overflow - perpetual uses simple consecutive day layout
+ ✅ save under folder "perpetual" instead of year - output/perpetual/ structure implemented
+ ✅ multi-language support - German and Spanish QR codes with language-specific URLs
+ ✅ add 0229 - February 29th support implemented with photo from 2026 collection
+ ✅ **ENHANCED**: Dynamic grid system - 6x5 for short months, 7x5 for long months
+ ✅ **ENHANCED**: Wider photos in 6-column layout (63mm vs 54mm width)
+ ✅ **ENHANCED**: Complete CLAUDE.md documentation with usage examples

## Sunday-first calendar option
+ add --sunday-first option to build_calendar.py
+ modify week_calculator.py to support Sunday as first day
+ update calendar templates to handle both Monday and Sunday start
+ add language/region support for different week start preferences

## Title page
+ 12 photos with country names
+ title?

## Workflow

## Title bar
+ consider moving title bar to bottom

## Hosting
+ free webhosting of several 300mb and 30mb files

## Photos

## World map
+ coordinates are sometimes off, needed to tweak them to the right for some maps
+ we probably don't need to create the maps in the assets folder of each language. use one common folder instead?
