from typing import List
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time
import random


def scrape_to_csv(
        urls: List[str], tags: List[str], write_to_csv: bool = True, output_file: str = "scraped_data.csv",
        return_structured_data: bool = False, headless: bool = True, proxies: List[str] = None,
        max_retries: int = 3):
    """
    Scrapes data from multiple URLs using rotating proxies and randomized user-agents.
    Includes retry logic for robustness. Returns DataFrame and optionally writes to CSV.

    Args:
        urls: A list of URLs to scrape.
        tags: A list of CSS selectors to extract data from.
        write_to_csv: Save results to CSV.
        output_file: CSV file path.
        return_structured_data: Print nested output in addition to DataFrame.
        headless: Use headless Chrome.
        proxies: List of proxy servers to rotate through (http://ip:port).
        max_retries: Number of retries per URL if scraping fails.
    """
    ua = UserAgent()
    results = []

    for url in urls:
        print(f"Scraping: {url}")
        success = False

        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1}/{max_retries}")

            # Select user-agent and proxy
            user_agent = ua.random
            proxy = random.choice(proxies) if proxies and len(proxies) > 0 else None

            # Setup Chrome options
            options = Options()
            if headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920x1080")

            options.add_argument(f'user-agent={user_agent}')
            if proxy:
                print(f"    Using proxy: {proxy}")
                options.add_argument(f'--proxy-server={proxy}')

            # Anti-detection flags
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Start WebDriver
            service = Service(ChromeDriverManager().install())
            driver = None
            try:
                driver = webdriver.Chrome(service=service, options=options)
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                       Object.defineProperty(navigator, 'webdriver', {
                         get: () => undefined
                       })
                    """
                })

                driver.get(url)

                # Wait and parse
                row = {'url': url}
                for tag in tags:
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, tag))
                        )
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        elements = soup.select(tag)
                        row[tag] = [el.get_text(strip=True) for el in elements]
                    except Exception as e:
                        print(f"    Error with tag '{tag}': {e}")
                        row[tag] = []

                results.append(row)
                success = True
                break

            except Exception as e:
                print(f"Attempt failed: {e}")
                time.sleep(random.uniform(2, 4))  # Backoff delay

            finally:
                if driver:
                    driver.quit()

        if not success:
            print(f"Skipping {url} after {max_retries} failed attempts")
            failed_row = {'url': url}
            for tag in tags:
                failed_row[tag] = ['<FAILED>']
            results.append(failed_row)

        time.sleep(random.uniform(1, 4))

    # Flatten data
    grouped_data = []
    for row in results:
        grouped_row = {'url': row['url']}
        for tag in tags:
            grouped_row[tag] = ', '.join(row.get(tag, []))
        grouped_data.append(grouped_row)

    df = pd.DataFrame(grouped_data)
    if write_to_csv:
        df.to_csv(output_file, index=False)
        print(f"Data written to {output_file}")
    else:
        print(df)

    if return_structured_data:
        print("Raw structured data:")
        print(results)
