import os
from typing import List, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Sheets Configuration
SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
SHEET_NAMES: List[str] = os.getenv("SHEET_NAMES", "").split(",")

# Google Auth Files
TOKEN_FILE: str = os.getenv("TOKEN_FILE", "token.pickle")
CREDENTIALS_FILE: str = os.getenv("CREDENTIALS_FILE", "credentials.json")
SCOPES: List[str] = ["https://www.googleapis.com/auth/spreadsheets"]

# Performance Thresholds
GLOBAL_THRESHOLD: int = int(os.getenv("GLOBAL_THRESHOLD", "8"))

# Scraper Settings
RUN_SCRAPER: bool = os.getenv("RUN_SCRAPER", "True").lower() == "true"

# Output Files
COMBINED_CSV: str = os.getenv("COMBINED_CSV", "combined_results.csv")

# Contest Configuration
# Format: (contest_name, contest_url, individual_threshold)
# Set individual_threshold to None if no specific threshold for that contest
CONTESTS: List[Tuple[str, str, Optional[int]]] = [
    (
        "Contest1",
        "https://codeforces.com/group/3MTZPM7hsC/contest/651191/standings",
        None,
    ),
    (
        "Contest2",
        "https://codeforces.com/group/3MTZPM7hsC/contest/652764/standings",
        None,
    ),
]

# Scraper Delays (in seconds)
MIN_PAGE_DELAY: float = 1.0
MAX_PAGE_DELAY: float = 2.0
MIN_CLICK_DELAY: float = 0.5
MAX_CLICK_DELAY: float = 1.0
CLOUDFLARE_WAIT: int = 5

MAX_PAGES: int = 100


def validate_config() -> bool:
    """Validate that all required configuration is present"""
    if not SPREADSHEET_ID:
        print("❌ ERROR: SPREADSHEET_ID not set in .env file")
        return False

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ ERROR: {CREDENTIALS_FILE} not found")
        return False

    if not CONTESTS:
        print("❌ ERROR: No contests configured")
        return False

    return True
