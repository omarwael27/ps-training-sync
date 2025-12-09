import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from typing import Optional

from utils.logger import logger
import config


class DriverManager:

    def __init__(self):
        self.driver: Optional[uc.Chrome] = None

    def init_driver(self) -> uc.Chrome:
        
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = uc.Chrome(options=options, version_main=None, use_subprocess=True)

        return self.driver

    def click_unofficial_checkbox(self) -> None:
        """
        Click the 'Show unofficial' checkbox on Codeforces standings page
        Uses human-like scrolling and timing to avoid detection
        """
        if not self.driver:
            raise RuntimeError("Driver not initialized")

        try:
            time.sleep(random.uniform(config.MIN_CLICK_DELAY, config.MAX_CLICK_DELAY))

            self.driver.execute_script("window.scrollTo(0, 200);")
            time.sleep(0.2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.2)

            checkbox = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, "showUnofficial"))
            )

            if not checkbox.is_selected():
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", checkbox
                )
                time.sleep(0.3)

                actions = ActionChains(self.driver)
                actions.move_to_element(checkbox).pause(0.1).click().perform()

                time.sleep(
                    random.uniform(config.MIN_CLICK_DELAY, config.MAX_CLICK_DELAY)
                )
                logger.info("✓ Clicked 'Show unofficial' checkbox")

        except Exception as e:
            logger.error(f"Failed to click checkbox: {e}")
            raise

    def wait_for_cloudflare(self) -> None:
        """Wait if Cloudflare challenge is detected"""
        if not self.driver:
            return

        if "cloudflare" in self.driver.page_source.lower():
            logger.warning("⚠️  Cloudflare detected, waiting...")
            time.sleep(config.CLOUDFLARE_WAIT)

    def check_access_denied(self) -> bool:
        """
        Check if access was denied by Cloudflare

        Returns:
            True if access denied, False otherwise
        """
        if not self.driver:
            return False

        return "access denied" in self.driver.page_source.lower()

    def quit(self) -> None:
        """Close the driver safely"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.error(f"Error closing driver: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.quit()
