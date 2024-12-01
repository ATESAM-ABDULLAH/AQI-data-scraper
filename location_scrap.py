import logging
from glob import glob
from time import sleep
import pandas as pd
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Setup logger for tracking the script's execution
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_file = ".location_scrap.log"
fh = logging.FileHandler(log_file)
fh.setFormatter(logging.Formatter(fmt="%(asctime)s - %(message)s"))
logger.addHandler(fh)

# Constants
CHROMEDRIVER_PATH = r"/home/atesam/Documents/Projects/AQI-data-scraper/chromedriver-linux64/chromedriver"
stations = [s.split("/")[-1][:-16] for s in glob("data/india-aqi/*.csv")]

# ChromeDriver service setup
service = Service(executable_path=CHROMEDRIVER_PATH)

# Chrome options configuration
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=options)


def get_directions_info(driver: webdriver.Chrome, stations: list) -> pd.DataFrame:
    """
    Takes a list of stations and returns a dataframe with information about coordinates,
    and location (address, zipcode, city, county, state, country) using the geocode finder tool
    (https://www.mapdevelopers.com/geocode_tool.php).
    """

    directions_info = defaultdict(list)
    for i, station in enumerate(stations):
        if i % 100 == 0 or i == 0:  # Reload page every 100 stations
            driver.get("https://www.mapdevelopers.com/geocode_tool.php")
            sleep(10)  # Allow time for the page to load
            text_field = driver.find_element(By.CLASS_NAME, "form-control")
            find_button = driver.find_element(
                By.XPATH, "//*[contains(text(), 'Find Address')]"
            )

        # Enter station into the text field and click "Find Address"
        text_field.clear()
        text_field.send_keys(station)
        find_button.click()
        sleep(2)

        try:
            # Extract data from the page
            lat = driver.find_element(By.ID, "display_lat").text
            lon = driver.find_element(By.ID, "display_lng").text
            directions_info["address"].append(
                driver.find_element(By.ID, "display_address").text
            )
            directions_info["state"].append(
                driver.find_element(By.ID, "display_state").text
            )
            directions_info["city"].append(
                driver.find_element(By.ID, "display_city").text
            )
            directions_info["zipcode"].append(
                driver.find_element(By.ID, "display_zip").text
            )
            directions_info["county"].append(
                driver.find_element(By.ID, "display_county").text
            )
            directions_info["country"].append(
                driver.find_element(By.ID, "display_country").text
            )
            directions_info["coordinates"].append((lat, lon))
            logger.info(f"Location for {station} scrapped successfully.")
        except Exception as e:
            logger.error(f"Error processing station {station} location: {e}")
            # Append placeholders in case of failure
            directions_info["address"].append("N/A")
            directions_info["state"].append("N/A")
            directions_info["city"].append("N/A")
            directions_info["zipcode"].append("N/A")
            directions_info["county"].append("N/A")
            directions_info["country"].append("N/A")
            directions_info["coordinates"].append(("N/A", "N/A"))

    driver.quit()
    return pd.DataFrame(directions_info)


# Process stations and save data to CSV
directions_info = get_directions_info(driver, stations)
output_path = "data/location_info.csv"
directions_info.to_csv(output_path, index=False)
logger.info(f"Location information saved to {output_path}")
