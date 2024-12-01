import os
import shutil
import logging
import requests
import re
from time import sleep
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Setup logger for tracking the script's execution
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_file = ".data_scrap.log"
fh = logging.FileHandler(log_file)
fh.setFormatter(logging.Formatter(fmt="%(asctime)s - %(message)s"))
logger.addHandler(fh)

# Constants
INDIA_STATIONS_URL = "https://aqicn.org/map/india/"
DOWNLOAD_FOLDER = "tmp_downloads"
DATA_FOLDER = "data/india-aqi"
CHROMEDRIVER_PATH = r"/home/atesam/Documents/Projects/AQI-data-scraper/chromedriver-linux64/chromedriver"
num_stations = 10


# Ensure download and data directories exist
if os.path.exists(DOWNLOAD_FOLDER):
    shutil.rmtree(DOWNLOAD_FOLDER)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Fetch the station list from the website
response = requests.get(INDIA_STATIONS_URL)
soup = BeautifulSoup(response.content, "html.parser")

# Extract station names and clean up by removing leading numbers
stations_list = [
    re.sub(r"^\d+\s+", "", station.text.split(" (")[0])
    for station in soup.find(id="map-station-list").find_all("a")
]
stations_list = stations_list[:num_stations]

# ChromeDriver service setup
service = Service(executable_path=CHROMEDRIVER_PATH)

# Chrome options configuration
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Chrome preferences for automatic downloads
prefs = {
    "download.default_directory": os.path.join(os.getcwd(), DOWNLOAD_FOLDER),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_settings.popups": 0,
    "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
    "profile.default_content_setting_values.automatic_downloads": 1,
}
options.add_experimental_option("prefs", prefs)

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=options)


def download_station_data(driver: webdriver, station: str, sleep_time: int = 4):
    """
    Downloads AQI data for a given station.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        station (str): Name of the station to search and download data for.
        sleep_time (int): Time in seconds to wait between actions.
    """
    try:
        # Open the AQICN data platform page
        driver.get("https://aqicn.org/data-platform/register/")
        w, h = driver.get_window_size().values()

        # Locate and scroll to the historic data section
        historic_div = driver.find_element(By.ID, "historic-aqidata")
        driver.execute_script("return arguments[0].scrollIntoView();", historic_div)
        driver.execute_script(f"window.scrollBy(0, -{h / 2});")

        # Clean station name and input it into the search prompt
        station_cleaned = station.encode("ascii", "ignore").decode()
        station_prompt = historic_div.find_element(By.CLASS_NAME, "prompt")
        station_prompt.send_keys(station_cleaned)
        sleep(sleep_time)

        # Click on the search result
        search_result = historic_div.find_element(By.CLASS_NAME, "result")
        driver.execute_script("return arguments[0].scrollIntoView();", search_result)
        driver.execute_script(f"window.scrollBy(0, -{h / 2});")
        search_result.click()
        sleep(sleep_time)

        # Click the download button
        download_button = driver.find_element(
            By.CLASS_NAME, "histui.ui.basic.primary.button"
        )
        driver.execute_script("return arguments[0].scrollIntoView();", download_button)
        driver.execute_script(f"window.scrollBy(0, -{h / 2});")
        download_button.click()
        sleep(sleep_time * 2)

        # Agree to terms if prompted
        agree_button = driver.find_element(
            By.CLASS_NAME, "histui.ui.large.primary.button"
        )
        driver.execute_script("return arguments[0].scrollIntoView();", agree_button)
        driver.execute_script(f"window.scrollBy(0, -{h / 2});")
        agree_button.click()
        sleep(sleep_time * 3)

    except Exception as e:
        logger.error(f"Failed to download data for station {station}: {e}")
        raise


# Download data for each station
for station in stations_list:
    try:
        logger.info(f"Starting data download for station: {station}")
        download_station_data(driver, station)
        logger.info(f"Data for {station} downloaded successfully.")
    except Exception as e:
        logger.warning(
            f"Retrying download for station {station} with extended wait time."
        )
        try:
            download_station_data(driver, station)
            logger.info(f"Data for {station} downloaded successfully on retry.")
        except Exception as retry_error:
            logger.error(f"Final failure for station {station}: {retry_error}")

# Move downloaded files to the data folder
for file in os.listdir(DOWNLOAD_FOLDER):
    shutil.move(os.path.join(DOWNLOAD_FOLDER, file), os.path.join(DATA_FOLDER, file))

# Clean up WebDriver
driver.quit()

logger.info("Data download process completed.")
