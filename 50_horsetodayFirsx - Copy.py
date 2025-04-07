import re
import time
import pandas as pd

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from datetime import datetime
from datetime import datetime, timedelta


url = "https://www.odds.com.au/horse-racing/"

# Set Firefox options for headless mode
options = Options()
options.headless = True

# Launch the web browser (Firefox) in headless mode
driver = webdriver.Firefox(executable_path='./geckodriver', options=options)

# Navigate to the webpage
driver.get(url)

# Wait for the date selectors to be visible
wait = WebDriverWait(driver,20)
date_selectors = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".date-selectors .date-selector")))

aus_nz_horse_racing_section = driver.find_element(By.XPATH, "//h2[contains(text(), 'Australia & New Zealand Horse Racing')]/following-sibling::div[@class='racing-meeting-rows__main']")

# Find the event locations
event_locations = aus_nz_horse_racing_section.find_elements(By.CSS_SELECTOR, ".racing-meeting-rows__right-inner a")

race_links = []

# Loop through each event location
for location in event_locations:
    # Scroll to the element using JavaScript
    driver.execute_script("arguments[0].scrollIntoView();", location)
    # time.sleep(10)

    race_url = location.get_attribute('href')
    race_links.append(race_url)

# Close the browser
driver.quit()

# Set Firefox options for headless mode
options = Options()
options.headless = True

# Launch the web browser (Firefox) in headless mode
driver = webdriver.Firefox(executable_path='./geckodriver', options=options)


 # Loop through each race URL
for url in race_links:
    # Navigate to the webpage
    driver.get(url)

    # Wait for the page to load
    wait = WebDriverWait(driver,20)

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
                show_more_button = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "octd-show-more-btn")))
            except:
                break

    # Get the page source after the page has fully loaded
    html_content = driver.page_source

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the required information within the 'ul' tag with class 'hero-racing-info'
    hero_racing_info = soup.find("ul", class_="hero-racing-info")

    # Extract the event name
    event_name_tag = soup.find("p", class_="hero-racing__event-name")
    event_name = event_name_tag.get_text(strip=True)

    # # Extract the event location and race number
    # event_location_tag = soup.find("h2", class_="hero-racing__event-title")
    # event_location_race_number = event_location_tag.get_text(strip=True)
    #
    # # Extract the event location and race number from the combined text
    # event_location, race_number = re.search(r'(.*) Race (\d+)', event_location_race_number).groups()
    # race_number = f"R{race_number}"  # Attach "R" in front of the race number

    #way to extract event name and race no from url
    pattern = r"/([^/]+)/race-(\d+)/"

    # Use re.search to find the pattern in the URL
    match = re.search(pattern, url)

    # Extract the track name and race number from the matched groups
    event_location = match.group(1)
    race_number = f"R{match.group(2)}

    # Extract the timestamp using regular expressions
    timestamp_pattern = r'(\d{1,2}:\d{2}(?:am|pm)) (\w{3}) (\d{1,2} \w{3} \d{4})'
    timestamp_match = re.search(timestamp_pattern, html_content)
    event_time, day, date = timestamp_match.groups() if timestamp_match else ("N/A", "N/A", "N/A")

    # Add 10 hours to the event_time
    event_time = datetime.strptime(event_time, "%I:%M%p")
    event_time += timedelta(hours=00)
    event_time = event_time.strftime("%I:%M%p")

    # Find the horse names
    horse_names = []
    horse_tags = soup.select("span.competitor-details a[data-analytics-event-name='Link']")
    for tag in horse_tags:
        horse_name = tag.get_text(strip=True)
        horse_names.append(horse_name)


    # Find all <a> tags with the specified data-analytics attribute
    bookie_name_link_tag = soup.find_all('a', attrs={'data-analytics': 'Form Guide : Odds Comparison : Win Odds'})

    # Extract link from href attribute and text from data-analytics attribute
    for tag in bookie_name_link_tag:
        bookie_link = f"https://www.odds.com.au{tag['href']}"
        bookie_name = tag['data-analytics'].split(':')[-1].strip()

    # Find the oddvalue tag tag with the specified class
    odds_values_tag = soup.find('div', class_='octd-right__odds-value-cell')

    # Extract the oddvalue content from the oddvalue>
    odds_value = odds_values_tag.text

    #data input
    horse_data = []
    odds_data = []
    odds_data.append({"bookmaker": bookie_name, "odds": odds_value, "link": bookie_link})
    for hr_name in horse_names:
        horse_data.append({"name": hr_name, "odds_data": odds_data})

    if hero_racing_info and event_name:
        # Extract the distance and track information from the 'li' tags
        distance_tag = hero_racing_info.find("li", class_="hero-racing-info__item")
        track_tag = distance_tag.find_next("li", class_="hero-racing-info__item")

        # Extract the text content from the tags and split by comma
        distance = track_tag.get_text(strip=True).split(",")[0].strip()
        track = track_tag.get_text(strip=True).split(",")[1].strip() if len(track_tag.get_text(strip=True).split(",")) > 1 else ""

        # Print the extracted information
        print("Event Name:", event_name)
        print("Time:", event_time)
        print("Day:", day)
        print("Date:", date)
        print("Distance:", distance)
        print("Track:", track)

        # Print the horse names without index numbers
        # print("\nHorse Names:")
        # for horse_name in horse_names:
        #     print(horse_name)

        # Print the win odds and bookie links for each horse
        for horse in horse_data:
            print(f"\nHorse Name: {horse['name']}")
            for odds_info in horse['odds_data']:
                bookmaker = odds_info['bookmaker']
                odds = odds_info['odds']
                link = odds_info['link']
                print(f"  Bookmaker: {bookmaker}, Odds: {odds}, Link: {link}")


        # Insert data into the "HorseData" table
        for horse in horse_data:
            horse_name = horse['name']
            horse_name_parts = horse_name.split('(')
            name_with_index = horse_name_parts[0].strip()
            index, name = re.search(r'(\d*)\s*(.*)', name_with_index).groups() if re.search(r'(\d*)\s*(.*)', name_with_index) else ("", name_with_index)
            number = horse_name_parts[1].replace(')', '').strip() if len(horse_name_parts) > 1 else ''
            if number:
                horse_name = f"{index} {name}({number})"
            else:
                horse_name = f"{index} {name}"



            odds_values = [odds_info['odds'] for odds_info in horse['odds_data']]
            link_values = [odds_info['link'] for odds_info in horse['odds_data']]
            odds_values.insert(5, 0)  # Insert 0 as the 6th odd
            link_values.insert(5, '')  # Insert empty string as the 6th reflink

            # Adjust odds_values and link_values to have a length of 16
            odds_values = odds_values[:16]
            odds_values += [0] * (16 - len(odds_values))
            link_values = link_values[:16]
            link_values += [''] * (16 - len(link_values))



        print("\n\nHorse Today's Data inserted successfully into the database!")
driver.quit()