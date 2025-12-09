import time
import random
import pandas as pd
from typing import List, Dict, Set, Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scraper.driver import DriverManager
from utils.logger import logger
import config


class CodeforcesScraperError(Exception):
    """Custom exception for scraper errors"""

    pass


class CodeforcesScraper:

    def __init__(self):
        self.participants: Dict[str, Set[str]] = {}

    def extract_page_data(self, driver: DriverManager) -> List[Dict[str, any]]:
        """
        Extract participant data from current standings page

        Args:
            driver: DriverManager instance

        Returns:
            List of dictionaries containing handle and solved problems
        """
        try:
            WebDriverWait(driver.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.standings"))
            )
            time.sleep(0.5)

            rows = driver.driver.find_elements(
                By.CSS_SELECTOR, "table.standings tbody tr"
            )
            data = []

            for row in rows:
                try:
                    row_class = row.get_attribute("class") or ""
                    if "header" in row_class:
                        continue

                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 5:
                        continue

                    handle = cells[1].text.strip().replace("*", "").strip()
                    if not handle:
                        continue

                    solved = []
                    for i in range(4, len(cells)):
                        cell = cells[i]
                        cell_class = cell.get_attribute("class") or ""

                        if "accepted" in cell_class.lower() or "+" in cell.text:
                            problem_letter = chr(65 + i - 4)
                            solved.append(problem_letter)

                    data.append({"Handle": handle, "Solved": solved})

                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue

            return data

        except Exception as e:
            logger.error(f"Failed to extract page data: {e}")
            raise CodeforcesScraperError(f"Data extraction failed: {e}")

    def scrape_page(self, url: str, page_num: int) -> Optional[List[Dict[str, any]]]:
        """
        Scrape a single page of contest standings

        Args:
            url: Contest standings URL
            page_num: Page number to scrape

        Returns:
            List of participant data or None if failed
        """
        with DriverManager() as driver:
            try:
                page_url = url if page_num == 1 else f"{url}/page/{page_num}"

                logger.info(f"[PAGE {page_num}] Loading...")
                driver.driver.get(page_url)

                time.sleep(random.uniform(config.MIN_PAGE_DELAY, config.MAX_PAGE_DELAY))

                driver.wait_for_cloudflare()

                driver.click_unofficial_checkbox()

                if driver.check_access_denied():
                    raise CodeforcesScraperError("Access denied by Cloudflare")

                page_data = self.extract_page_data(driver)
                logger.info(
                    f"[PAGE {page_num}] Extracted {len(page_data)} participants"
                )

                return page_data

            except Exception as e:
                logger.error(f"[PAGE {page_num}] Error: {e}")
                return None

    def scrape_contest(
        self, contest_name: str, contest_url: str
    ) -> Tuple[pd.DataFrame, str]:
        """
        Scrape entire contest standings (all pages)

        Args:
            contest_name: Name of the contest
            contest_url: Contest standings URL

        Returns:
            Tuple of (DataFrame with results, CSV filename)
        """
        logger.info("=" * 60)
        logger.info(f"SCRAPING: {contest_name}")
        logger.info("=" * 60)

        self.participants = {}
        page = 1

        while page <= config.MAX_PAGES:
            page_data = self.scrape_page(contest_url, page)

            if not page_data:
                break

            # Update participants dictionary and track if any new data was found
            new_count = 0
            any_new_data = False

            for entry in page_data:
                handle = entry["Handle"]
                solved = set(entry["Solved"])

                if handle in self.participants:
                    old_solved = self.participants[handle]
                    new_solved = old_solved.union(solved)

                    # Check if there are any new problems solved
                    if len(new_solved) > len(old_solved):
                        self.participants[handle] = new_solved
                        any_new_data = True
                    else:
                        self.participants[handle] = new_solved
                else:
                    self.participants[handle] = solved
                    new_count += 1
                    any_new_data = True

            logger.info(f"[INFO] New: {new_count} | Total: {len(self.participants)}")

            # Stop if no new data (no new handles AND no additional problems solved)
            if not any_new_data:
                logger.info("[INFO] No new data found. Stopping scrape.")
                break

            time.sleep(random.uniform(config.MIN_PAGE_DELAY, config.MAX_PAGE_DELAY))
            page += 1

        df = pd.DataFrame(
            [
                {
                    "Handle": handle,
                    "Solved_Problems": ",".join(sorted(problems)),
                    "Total_Solved": len(problems),
                }
                for handle, problems in self.participants.items()
            ]
        )

        df = df.sort_values("Total_Solved", ascending=False).reset_index(drop=True)

        csv_file = f"{contest_name}_standings.csv"
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")

        logger.info(f"\n✅ Scraped {len(df)} participants")
        logger.info(f"✅ Saved to: {csv_file}\n")

        return df, csv_file

    @staticmethod
    def scrape_all_contests() -> Dict[str, Tuple[pd.DataFrame, str]]:
        """
        Scrape all configured contests

        Returns:
            Dictionary mapping contest_name -> (DataFrame, CSV filename)
        """
        logger.info("\n" + "=" * 60)
        logger.info("STEP 1: SCRAPING ALL CONTESTS")
        logger.info("=" * 60)

        results = {}
        scraper = CodeforcesScraper()

        for contest_config in config.CONTESTS:
            contest_name = contest_config[0]
            contest_url = contest_config[1]

            df, csv_file = scraper.scrape_contest(contest_name, contest_url)
            results[contest_name] = (df, csv_file)

        return results
