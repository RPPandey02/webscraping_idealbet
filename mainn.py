import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import mysql.connector
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Function to scrape and insert data for a single race
def scrape_and_insert_race_data(url, cursor, greyhounds_names=None):
    # Set up Selenium
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
    driver.get(url)

    # Wait for the page to load (you may need to adjust the timeout)
    time.sleep(5)  # Adjust the sleep time as needed

    # Parse the HTML content using BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find and print the horse names (first 3)
    greyhounds_names = soup.find_all('h4', class_='selection-result__info-competitor-name')
    event_loc_bundle = soup.find_all('h1', class_='class="meeting-selector__meeting-name')

    # Check if there are enough horse names
    if len(greyhounds_names) < 7:
        print(f"Not enough horse names found for race: {url}")
    else:
        # Extract event location, race number, and horse names
        event_location = event_loc_bundle[12222222222222222222222222].text.strip()
        race_number = "R" + url.split('-')[-1]
        first_place = greyhounds_names[1].text.strip()
        second_place = greyhounds_names[2].text.strip()
        third_place = greyhounds_names[3].text.strip()

        # Close the driver when done
        driver.quit()

        # Define the query to insert data into your table
        insert_query = "INSERT INTO HorseResults (event_location, race_number, 1st_place, 2nd_place, 3rd_place) VALUES (%s, %s, %s, %s, %s)"
        values = (event_location, race_number, first_place, second_place, third_place)

        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="idealbet_online",
            password="LtiqFiDy2-xuA",
            database="idealbet_online"
        )

        cursor = connection.cursor()

        # Execute the query
        cursor.execute(insert_query, values)

        # Commit the changes and close the connection
        connection.commit()
        connection.close()


# Set up Selenium for the main page with race links
main_url = "https://www.racenet.com.au/results/greyhounds"
options = Options()
options.headless = True
driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
driver.get(main_url)

# Find and click the "Today" button
# Wait for the "Today" tab to be clickable and then click it
today_tab = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-analytics="Results : Tab Group : Today"]'))
)
today_tab.click()

# Wait for the page to load (you may need to adjust the timeout)
time.sleep(5)  # Adjust the sleep time as needed

# Parse the HTML content using BeautifulSoup
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Locate the race links within the specified structure
race_links = []

# Find all anchor tags with href attributes containing "/results/greyhounds/"
for a_tag in soup.find_all('a', href=True):
    if "/results/greyhounds/" in a_tag['href']:
        race_links.append(a_tag['href'])

# Close the driver when done
driver.quit()

# Connect to the MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="idealbet_online",
    password="LtiqFiDy2-xuA",
    database="idealbet_online"
)

cursor = connection.cursor()

# Iterate through race links, scrape, and insert data into the database
for race_url in race_links:
    full_race_url = f"https://www.racenet.com.au{race_url}"
    print(f"Scraping data for race: {full_race_url}")
    scrape_and_insert_race_data(full_race_url, cursor)

# Close the connection to the MySQL database
connection.close()
