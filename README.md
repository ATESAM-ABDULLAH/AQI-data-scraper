# AQI Data Scraper

This repository contains scripts to scrape Air Quality Index (AQI) data and related location information for various stations. It automates the data retrieval process using **Selenium** and processes data efficiently.

---

## Features

- **AQI Data Scraping:** Downloads AQI data for stations from [aqicn.org](https://aqicn.org).
- **Location Extraction:** Extracts location details (coordinates, city, state, and country) using the Geocode Finder Tool.
- **Logging:** Tracks execution details with logs for easy debugging.
- **Headless Automation:** Utilizes headless Chrome for faster and more efficient scraping.

---

## Prerequisites

### 1. Install Google Chrome
Download and install the latest version of Google Chrome:
- [Google Chrome Download](https://www.google.com/chrome/)

### 2. Install ChromeDriver
ChromeDriver is required for Selenium to control the Chrome browser.

Identify your Chrome version:
```bash
google-chrome --version
```

Download the corresponding version of ChromeDriver from:

- [ChromeDriver Downloads](https://sites.google.com/chromium.org/driver/downloads?authuser=0)

Extract and move the chromedriver binary to a directory in your PATH:
```bash
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
```

### 3. Install Poetry
Poetry is used for dependency management.

Install Poetry:
```
pip install poetry
poetry --version
```

### 4. Setup Instructions
Clone the Repository
```
git clone https://github.com/your-username/aqi-data-scraper.git
cd aqi-data-scraper
```

Install Dependencies Use Poetry to install the required dependencies:
```
poetry install
```

Activate the Virtual Environment
```
poetry shell
```

## Usage
### 1. Scraping AQI Data
Run the script to scrape AQI data for all stations:

```
python data_scraper.py
```
This will:
1. Download AQI data for various stations.
2. Save the data in the data/india-aqi directory.

### 2. Extracting Location Information
Run the script to extract location details:
```
python location_scraper.py
```

This will:
1. Extract location details for each station.
2. Save the data as location_info.csv in the data/india-aqi directory.

## File Structure
```txt
.
├── data/                     # Data directory for storing 
│   ├── india-aqi/            # Subdirectory for AQI and 
│   └── location_info.csv     # Extracted location 
├── tmp_downloads/            # Temporary directory for downloads
├── data_scraper.py           # Script to scrape AQI data
├── location_scraper.py       # Script to extract location details
├── poetry.lock               # Poetry lock file for dependencies
├── pyproject.toml            # Poetry configuration file
└── README.md                 # This README file
```

