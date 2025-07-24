## General
+ replace tabs in photo_information.txt with commas?

## Perpetual calendar

## Photos

## Cover page

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

## Sunday-first calendar option
+ consider using sunday first for US/Canada/Mexico/Australia
  + add that info to pdf filenames
  + needs to be part of i18n somehow…
+ add --sunday-first option to build_calendar.py
+ modify week_calculator.py to support Sunday as first day
+ update calendar templates to handle both Monday and Sunday start
+ add language/region support for different week start preferences

## Workflow

## Hosting
+ free webhosting of several 300mb and 30mb files
