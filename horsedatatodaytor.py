import re
import time
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from concurrent.futures import ThreadPoolExecutor
from stem import Signal
from stem.control import Controller

# Database connection settings
servername = "localhost"
username = "idealbet_online"
password = "LtiqFiDy2-xuA"
dbname = "idealbet_online"
tablename = "HorseDataTorBrowser"

url = 'https://www.odds.com.au/horse-racing/'


def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)


def setup_tor_browser():
    # Set the path to the Tor Browser's GeckoDriver
    tor_driver_path = "/home/idealbet/public_html/idealbet.online/scripts/geckodriver"

    tor_options = Options()
    tor_options.headless = True  # Set to True if you want to run in headless mode

    driver = webdriver.Firefox(executable_path=tor_driver_path, options=tor_options)
    return driver


# Set Firefox options for headless mode
options = Options()
options.headless = True


# Function to scrape data for a single race URL
def scrape_race(url):
    # Launch the web browser (Firefox) in headless mode
    driver = setup_tor_browser()
    setup_tor_browser()

    try:
        # Connect to the MySQL server
        conn = pymysql.connect(
            host=servername,
            user=username,
            password=password,
            database=dbname
        )

        cursor = conn.cursor()

        # Navigate to the race URL
        driver.get(url)

        # Wait for the page to load
        wait = WebDriverWait(driver, 20)

        # Check if the "show more" button is present
        show_more_button = None

        try:
            show_more_button = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "octd-show-more-btn")))

        except:
            pass

        # Click on the "show more" button until all horses are visible
        if show_more_button:
            while True:
                try:
                    # Click on the "show more" button
                    show_more_button.click()
                    time.sleep(20)  # Add a small delay to load the additional horses
                    show_more_button = wait.until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "octd-show-more-btn")))
                except:
                    break

        from bs4 import BeautifulSoup
        import requests

        # Get the page source after the page has fully loaded
        html_content = driver.page_source

        # Parse the HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the required information within the 'ul' tag with class 'hero-racing-info'
        hero_racing_info = soup.find("ul", class_="hero-racing-info")

        # Extract the event name
        event_name_tag = soup.find("p", class_="hero-racing__event-name")
        event_name = event_name_tag.get_text(strip=True)

        # way to extract event name and race no from url
        pattern = r"/([^/]+)/race-(\d+)/"

        # Use re.search to find the pattern in the URL
        match = re.search(pattern, url)

        # Extract the track name and race number from the matched groups
        event_location = match.group(1).capitalize()
        race_number = f"R{match.group(2)}"

        # Extract the timestamp using regular expressions
        timestamp_pattern = r'(\d{1,2}:\d{2}(?:am|pm)) (\w{3}) (\d{1,2} \w{3} \d{4})'
        timestamp_match = re.search(timestamp_pattern, html_content)
        event_time, day, date = timestamp_match.groups() if timestamp_match else ("N/A", "N/A", "N/A")

        soup = BeautifulSoup(html_content, 'html.parser')

        horse_names = []
        horse_tags = soup.select("span.competitor-details a[data-analytics-event-name='Link']")

        for tag in horse_tags:
            horse_name = tag.get_text(strip=True)
            horse_names.append(horse_name)

        horse_rows = soup.select("div.octd-right__main-row")
        horse_data = []

        for idx, row in enumerate(horse_rows):
            odds_data = []
            bookie_tags = row.select("a[data-key]")
            for bookie_idx, bookie_tag in enumerate(bookie_tags, start=1):
                if bookie_idx == 5 or bookie_idx == 6:  # Ignore the 6th odd and reflink6
                    continue
                bookie_name = (bookie_tag['data-key']).split("-")[1]
                bookie_link = bookie_tag['href']
                # Append the desired part before the link
                bookie_link = f"https://www.odds.com.au{bookie_link}"
                odds_value = bookie_tag.find_next("div", class_="octd-right__odds-value-cell").text.strip()
                odds_data.append({"bookmaker": bookie_name, "odds": odds_value, "link": bookie_link})
            horse_data.append({"name": horse_names[idx], "odds_data": odds_data})

        if hero_racing_info and event_name:
            # Extract the distance and track information from the 'li' tags
            distance_tag = hero_racing_info.find("li", class_="hero-racing-info__item")
            track_tag = distance_tag.find_next("li", class_="hero-racing-info__item")

            # Extract the text content from the tags and split by comma
            distance = track_tag.get_text(strip=True).split(",")[0].strip()
            track = track_tag.get_text(strip=True).split(",")[1].strip() if len(
                track_tag.get_text(strip=True).split(",")) > 1 else ""


        else:
            print("Information not found on the page:", url)

        # Insert data into the "HorseData" table
        for horse in horse_data:

            horse_name = horse['name']

            odds_values = [odds_info['odds'] for odds_info in horse['odds_data']]
            link_values = [odds_info['link'] for odds_info in horse['odds_data']]

            while len(odds_values) < 12:
                odds_values.append(0)  # Fill in missing odds with "N/A"

            while len(link_values) < 12:
                link_values.append("")  # Fill in missing links with "N/A

            sql_query = """
            INSERT INTO {0}
            (EventLocation, RaceNumber, EventName, HorseName, Predictor, Time, Day, Date, Distance,Track,
            OddsRef1, Ref1Link, OddsRef2, Ref2Link, OddsRef3, Ref3Link, OddsRef4, Ref4Link, OddsRef5, Ref5Link,
            OddsRef6, Ref6Link, OddsRef7, Ref7Link, OddsRef8, Ref8Link, OddsRef9, Ref9Link, OddsRef10, Ref10Link,
            OddsRef11, Ref11Link, OddsRef12, Ref12Link, OddsRef13, Ref13Link, OddsRef14, Ref14Link, OddsRef15,
            Ref15Link, OddsRef16, Ref16Link)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """.format(tablename)
            # Execute the SQL query with the data
            cursor.execute(sql_query, (
                event_location, race_number, event_name, horse_name, None, event_time, day, date, distance, track,
                odds_values[0], link_values[0], odds_values[1], link_values[1], odds_values[2], link_values[2],
                odds_values[3], link_values[3], odds_values[4], link_values[4], odds_values[5], link_values[5],
                odds_values[6], link_values[6], odds_values[7], link_values[7], odds_values[8], link_values[8],
                odds_values[9], link_values[9], odds_values[10], link_values[10], 0, "",
                0, "", 0, "", 0, "",
                0, ""
            ))
            # Commit the changes to the database
            conn.commit()

    except pymysql.Error as error:
        print("Error connecting to MySQL:", error)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    driver.quit()  # Close the browser after scraping and inserting


# Launch the web browser (Firefox) in headless mode
driver = setup_tor_browser()

# Navigate to the webpage
driver.get(url)

# Wait for the date selectors to be visible
wait = WebDriverWait(driver, 20)
date_selectors = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".date-selectors .date-selector")))

aus_nz_horse_racing_section = driver.find_element(By.XPATH,
                                                  "//h2[contains(text(), 'Australia & New Zealand Horse Racing')]/following-sibling::div[@class='racing-meeting-rows__main']")

# Find the event locations
event_locations_linker = aus_nz_horse_racing_section.find_elements(By.CSS_SELECTOR,
                                                                   ".racing-meeting-rows__right-inner a")
race_links = []

# Loop through each event location
for location in event_locations_linker:
    driver.execute_script("arguments[0].scrollIntoView();", location)
    race_url = location.get_attribute('href')
    race_links.append(race_url)

# Close the browser
driver.quit()

# List of race URLs to scrape
race_urls = race_links

# Number of concurrent threads (adjust as needed)
num_threads = 6

# Use a ThreadPoolExecutor to parallelize scraping
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    # Scrape data for all race URLs concurrently
    executor.map(scrape_race, race_urls)


