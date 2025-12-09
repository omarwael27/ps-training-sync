# Codeforces private Contest data scraping

**Automated system for aggregating and managing Codeforces private contest results across multiple events**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Problem

Managing multiple Codeforces contests and aggregating results is time-consuming and error-prone. Previously, this required:

- Manual data entry from multiple contest pages
- 4-5 hours of work to aggregate and filter results
- Frequent human errors in data collection
- Manual spreadsheet updates across multiple sheets
- Tedious filtering and formatting
- Difficulty tracking performance across contests

### Note: Private Contests Only

This tool is designed specifically for **private Codeforces contests** (group contests). Public contests can use the official [Codeforces API](https://codeforces.com/apiHelp) for easier automation. Private contests don't have API access, making web scraping the only practical solution.

## Solution

**Fully automated pipeline** that:

- Scrapes real-time standings from Codeforces
- Aggregates performance across multiple contests
- Automatically filters participants based on thresholds
- Updates Google Sheets with zero human intervention
- Generates comprehensive analytics reports
- Saves 4-5 hours per automation run
- Eliminates human error completely

---

## Features

### 1. Web Scraping for Private Contests

- Scrapes private Codeforces group contests (no API access needed)
- Bypasses Cloudflare protection using undetected-chromedriver
- Handles pagination automatically
- Extracts participant handles and solved problems
- Robust error handling and retry logic

### 2. Multi-Contest Aggregation

- Tracks performance across unlimited contests
- Individual and global performance thresholds
- Comprehensive scoring system

### 3. Google Sheets Integration

- OAuth 2.0 authentication
- Automatic row deletion based on thresholds
- Professional cell formatting
- Multi-sheet support

### 4. Analytics & Reporting

- Combined CSV with all contest data
- Per-contest breakdown
- Total performance metrics
- Easy-to-read summary reports

---

## Installation

### Prerequisites

- Python 3.13+
- Google Cloud Project with Sheets API enabled
- Chrome/Chromium browser

### Setup Steps

1. **Clone the repository**

```bash
git clone https://github.com/omarwael27/Codeforces-private-Contest-data-scraping.git
cd Codeforces-private-Contest-data-scraping
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Google Sheets API**

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Sheets API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` to project root

5. **Set up environment variables**

Create a `.env` file in the project root with the following variables:

```env
# Google Sheets Configuration
SPREADSHEET_ID=your_google_sheets_id_here
SHEET_NAMES=Sheet1,Sheet2,Sheet3
TOKEN_FILE=token.pickle
CREDENTIALS_FILE=credentials.json

# Performance Thresholds
GLOBAL_THRESHOLD=8

# Scraper Settings
RUN_SCRAPER=True

# Output Files
COMBINED_CSV=combined_results.csv
```

6. **Configure contests** (in `config.py`)

```python
CONTESTS = [
    # (name, url, individual_threshold)
    ("Contest1", "https://...", None),  # No individual threshold
    ("Contest2", "https://...", 5),     # Must solve 5+ problems
]
```

---

## Project Structure

```
Codeforces-private-Contest-data-scraping/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── requirements.txt
├── config.py
├── main.py
├── Contest1_standings.csv
├── Contest2_standings.csv
├── combined_results.csv
├── acm_tracker.log
├── scraper/
│   ├── __init__.py
│   ├── driver.py
│   └── codeforces.py
├── sheets/
│   ├── __init__.py
│   ├── auth.py
│   └── operations.py
└── utils/
    ├── __init__.py
    └── logger.py
```

### Directory Descriptions

- `scraper/` - Web scraping functionality

  - `driver.py` - WebDriver management and configuration
  - `codeforces.py` - Codeforces scraper implementation

- `sheets/` - Google Sheets integration

  - `auth.py` - OAuth 2.0 authentication
  - `operations.py` - Sheet operations (CRUD)

- `utils/` - Utility modules
  - `logger.py` - Logging configuration

---

## Workflow

The system operates in three main phases:

**Scraping Phase**: Retrieves standings from all configured Codeforces contests

**Filtering Phase**: Removes participants below performance thresholds

**Google Sheets Update**: Automatically updates spreadsheets with filtered data

**Report Generation**: Creates combined analytics CSV with aggregate results

### Output Files

- `Contest1_standings.csv` - Individual contest results
- `Contest2_standings.csv` - Individual contest results
- `combined_results.csv` - Aggregated results across all contests
- `acm_tracker.log` - Detailed execution log

---

## Configuration

### Environment Variables (`.env`)

| Variable           | Description                            | Default  |
| ------------------ | -------------------------------------- | -------- |
| `SPREADSHEET_ID`   | Google Sheets ID                       | Required |
| `GLOBAL_THRESHOLD` | Minimum total problems across contests | 8        |
| `SHEET_NAMES`      | Comma-separated sheet names            | Required |
| `RUN_SCRAPER`      | Run scraper or load existing CSVs      | True     |

### Contest Configuration (`config.py`)

```python
CONTESTS = [
    # (name, url, individual_threshold)
    ("Contest1", "https://...", None),  # No individual threshold
    ("Contest2", "https://...", 5),     # Must solve 5+ problems
]
```

### Threshold Logic

A participant is removed if:

- They fail to meet any individual contest threshold (if set), OR
- Their total across all contests is less than GLOBAL_THRESHOLD

---

## Security Notes

**Never commit these files:**

- `credentials.json` - Google API credentials
- `token.pickle` - Authentication token
- `.env` - Environment variables

These are already in `.gitignore` for your protection.

---

## Impact Metrics

| Metric            | Before Automation | After Automation |
| ----------------- | ----------------- | ---------------- |
| Time per cycle    | 4-5 hours         | 5-10 minutes     |
| People required   | 30+ mentors       | 0                |
| Human errors      | Frequent          | Zero             |
| Data accuracy     | ~85-90%           | 100%             |
| Annual time saved | -                 | 200+ hours       |

---

## Troubleshooting

### Common Issues

**1. "Cloudflare blocked access"**

Solution: The scraper waits 15 seconds for Cloudflare challenges. If persistent, increase `CLOUDFLARE_WAIT` in `config.py`.

**2. "credentials.json not found"**

Solution: Download OAuth credentials from Google Cloud Console.

**3. "SPREADSHEET_ID not set"**

Solution: Add your Google Sheets ID to `.env` file.

**4. Rate limiting**

Solution: Random delays are built in; adjust delays in `config.py`.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Omar Wael Mohamed**

- GitHub: [@omarwael27](https://github.com/omarwael27)
- LinkedIn: [omar wael](https://linkedin.com/in/omar-wael-b30a86364/)
- Email: owael2207@gmail.com

---

## Acknowledgments

- Built for acmASCIS Student Chapter at Ain Shams University
- Saves countless hours on data aggregation

---

## Tech Stack

- Python 3.13 - Core language
- Selenium + undetected-chromedriver - Web scraping
- pandas - Data processing
- Google Sheets API - Spreadsheet automation
- OAuth 2.0 - Secure authentication
