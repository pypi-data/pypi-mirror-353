<h1 align="center">🎓 BUBT RoutinePy</h1>
<p align="center"><b>Part of Project "Harukaze🍃"</b></p>

[![BUBT](https://img.shields.io/badge/BUBT-University-002E5D?style=flat&logo=shield&logoColor=FFD700&color=FFD700&labelColor=002E5D)](https://www.bubt.edu.bd/)
[![Support Chat](https://img.shields.io/badge/Telegram-Join_Chat-2CA5E0?logo=telegram&logoColor=white)](https://t.me/harukaze_bubt)

[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-%23B20000?logo=gnu&logoColor=white)](https://opensource.org/licenses/GPL-3.0)
[![PyPI](https://img.shields.io/pypi/v/bubt-routinepy?color=blue&label=PyPI)](https://pypi.org/project/bubt-routinepy/)

## Overview

An unofficial Python wrapper of the BUBT Routine API, seamlessly integrated with a robust web scraper and PDF extractor for getting routine data.

## 🌟 Features

- **Unofficial & Reverse-Engineered**: Built through reverse-engineering of BUBT Routine API endpoints

- **Robust Web Scraper**: Extracts routine data directly from the BUBT 
website, supporting both HTML and PDF formats.

- **Command-Line Interface (CLI)**: Offers a CLI version for easy routine data retrieval from the terminal (with different outputs like `table`, `text`,`json`).

- **Caching Mechanism**: Caches HTML and PDF files to optimize performance and reduce overhead on Annex (it's already slow enough).

- **Data Normalization**: Consistent output format across all sources (API/HTML/PDF)

## ⚡ Installation

### Stable Version (Recommended)
```bash
uv add bubt-routinepy
```

Or the usual
```bash
pip install bubt-routinepy
```

### Development Version
```bash
pip install git+https://github.com/kurtnettle/bubt-routinepy.git@master
```

## 📝 Usage

### CLI

```bash
routinepy --routine-type class --program-code 006 --intake 50 --section 1
```
**output (default):**
```bash
+------------------------------------------------------------------------+
|                          Class Routine (50-1)                          |
+----------------------+---------+---------+---------+---------+---------+
|         Time         |   sun   |   mon   |   tues  |  wednes |  thurs  |
+----------------------+---------+---------+---------+---------+---------+
| 08:00 AM to 09:15 AM | CSE 320 |         |         |         |         |
|                      |   WMO   |         |         |         |         |
|                      |  B2/416 |         |         |         |         |
| 09:15 AM to 10:30 AM | CSE 320 |         | CSE 328 |         |         |
|                      |   WMO   |         |   MRG   |         |         |
|                      |  B2/416 |         |  B2/518 |         |         |
| 10:30 AM to 11:45 AM | CSE 351 |         | CSE 407 |         |         |
|                      |   SAM   |         |   NMP   |         |         |
|                      |  B2/710 |         |  B2/710 |         |         |
| 11:45 AM to 01:00 PM |         | CSE 327 | CSE 417 | CSE 417 |         |
|                      |         |   MRG   |   ADSK  |   ADSK  |         |
|                      |         |  B2/709 |  B2/710 |  B2/909 |         |
| 01:30 PM to 02:45 PM |         | CSE 418 |         | CSE 352 |         |
|                      |         |   ADSK  |         |   SAM   |         |
|                      |         |  B2/417 |         |  B2/420 |         |
| 02:45 PM to 04:00 PM |         | CSE 418 |         | CSE 352 | CSE 319 |
|                      |         |   ADSK  |         |   SAM   |   WMO   |
|                      |         |  B2/417 |         |  B2/420 |  B2/709 |
| 04:00 PM to 05:15 PM |         | CSE 319 |         | CSE 327 | CSE 407 |
|                      |         |   WMO   |         |   MRG   |   NMP   |
|                      |         |  B2/318 |         |  B2/710 |  B2/709 |
| 05:15 PM to 06:30 PM |         |         |         |         | CSE 351 |
|                      |         |         |         |         |   SAM   |
|                      |         |         |         |         |  B2/709 |
+----------------------+---------+---------+---------+---------+---------+
```
### Or if you prefer JSON
```bash
routinepy --routine-type class --program-code 006 --intake 50 --section 1 --format json
```
**Output:**
```json
[{"week_day": "sun", "period_time": "08:00 AM to 09:15 AM", "intake": "50", "section": "1", "faculty_code": "WMO", "building": "2", "room": "416", "course_code": "CSE 320", "shift_time": "Day"},
... , 
... , 
... , 
{"week_day": "thurs", "period_time": "05:15 PM to 06:30 PM", "intake": "50", "section": "1", "faculty_code": "SAM", "building": "2", "room": "709", "course_code": "CSE 351", "shift_time": "Day"}]
```

> [!TIP]
> Check documentation for complete CLI reference

### As a Library 

**1. Initializing Clients**

```py
# For scraping functionality
from routinepy.lib import ScraperClient
scraper = ScraperClient()

# For API functionality
from routinepy.lib import ApiClient
api = ApiClient()
```

**2. Let's get the routine of `CSE` Dept Intake `50` and Section `1`**

```py
from routinepy.lib.enums import ProgramCode

# Using Scraper or API
data = await client.get_class_routine(
    program_code=ProgramCode.CSE_Day,
    intake="50",
    section="1",
)
```

**Output:**
```py
[ClassPeriod(week_day=<Weekday.SUNDAY: 'sun'>, period_time='08:00 AM to 09:15 AM', intake='50', section='1', faculty_code='WMO', faculty_name=None, building='2', room='416', course_code='CSE 320', course_name=None, shift_time=<ShiftTime.DAY: 'Day'>),
...
...
...
 ClassPeriod(week_day=<Weekday.THURSDAY: 'thurs'>, period_time='05:15 PM to 06:30 PM', intake='50', section='1', faculty_code='SAM', faculty_name=None, building='2', room='709', course_code='CSE 351', course_name=None, shift_time=<ShiftTime.DAY: 'Day'>)]
 ```

> [!NOTE]  
> A list of class periods containing information of each periods. Some fields like `faculty_name` are empty because the `ApiClient` doesn't have that information but the `ScraperClient` does!


## 📄 Documentation

https://bubt-routinepy.readthedocs.io


## 🤝 Contributing

Contributions are welcome! If you'd like to improve the tool or fix bugs, feel free to submit a pull request. Please ensure your changes align with the project's coding standards and include appropriate tests.

## 📜 License

This project is licensed under the GPLv3 License. See the [LICENSE](./LICENSE) file for full details.

By contributing to this project, you agree that your contributions will be licensed under the GPLv3 License as well.