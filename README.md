
A Python-based web scraper that extracts race data from [odds.com.au](https://www.odds.com.au/). It uses Selenium with Tor Browser for anonymous scraping, stores data in a MySQL database, and supports multi-threaded processing for efficiency.

## Features
- **Web Scraping**: Extracts race details (event name, location, race number, time, date) from racing pages.
- **Competitor Data**: Scrapes competitor names, win odds, and bookmaker links for each race.
- **Anonymity**: Uses Tor Browser with IP renewal for anonymous scraping.
- **Database Storage**: Stores scraped data in a MySQL database (`RacesTomorrowTorBrowser` table).
- **Multi-Threaded Processing**: Employs `ThreadPoolExecutor` for concurrent scraping of multiple race URLs.
- **Headless Mode**: Runs Firefox in headless mode for efficient scraping without a GUI.

## Technologies
- **Python**: Core programming language.
- **Selenium**: For browser automation and web scraping.
- **Tor Browser**: Ensures anonymity during scraping via Tor network.
- **pymysql**: For connecting to and interacting with a MySQL database.
- **BeautifulSoup**: For parsing HTML content.
- **Stem**: To control Tor and renew IP addresses.
- **ThreadPoolExecutor**: For parallel scraping of race URLs.

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/RPPandey02/RaceDataScraper.git
   cd RaceDataScraper
   ```

2. **Set Up Tor Browser**:
   - Install Tor Browser on your system.
   - Ensure Tor is running on port `9051` (default for Tor control port).
   - Download `geckodriver` for Firefox and place it in the specified path (`/home/idealbet/public_html/idealbet.online/scripts/geckodriver` or adjust the path in the script).

3. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Dependencies**:
   Ensure you have Python 3.8+ installed. Create a `requirements.txt` file with the following:
   ```
   selenium==4.21.0
   pymysql==1.1.1
   beautifulsoup4==4.12.3
   stem==1.8.3
   requests==2.32.3
   ```
   Then install:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure MySQL Database**:
   - Set up a MySQL database named `idealbet_online`.
   - Create a table named `RacesTomorrowTorBrowser` with the following schema (based on the script’s `INSERT` query):
     ```sql
     CREATE TABLE RacesTomorrowTorBrowser (
         id INT AUTO_INCREMENT PRIMARY KEY,
         EventName VARCHAR(255),
         EventLocation VARCHAR(255),
         RaceNumber VARCHAR(50),
         Time VARCHAR(50),
         Day VARCHAR(50),
         Date VARCHAR(50),
         HorseName VARCHAR(255),
         OddsRef1 FLOAT, Ref1Link TEXT,
         OddsRef2 FLOAT, Ref2Link TEXT,
         OddsRef3 FLOAT, Ref3Link TEXT,
         OddsRef4 FLOAT, Ref4Link TEXT,
         OddsRef5 FLOAT, Ref5Link TEXT,
         OddsRef6 FLOAT, Ref6Link TEXT,
         OddsRef7 FLOAT, Ref7Link TEXT,
         OddsRef8 FLOAT, Ref8Link TEXT,
         OddsRef9 FLOAT, Ref9Link TEXT,
         OddsRef10 FLOAT, Ref10Link TEXT,
         OddsRef11 FLOAT, Ref11Link TEXT,
         OddsRef12 FLOAT, Ref12Link TEXT,
         OddsRef13 FLOAT, Ref13Link TEXT,
         OddsRef14 FLOAT, Ref14Link TEXT,
         OddsRef15 FLOAT, Ref15Link TEXT,
         OddsRef16 FLOAT, Ref16Link TEXT
     );
     ```
   - Update the database credentials in the script (`servername`, `username`, `password`, `dbname`, `tablename`) to match your setup.

6. **Run the Script**:
   ```bash
   python scripts/scrape_races.py
   ```

## Usage
- The script scrapes race data for events scheduled "Tomorrow" on [odds.com.au](https://www.odds.com.au/).
- It navigates to each race URL, extracts event details, competitor names, odds, and bookmaker links, and stores them in the MySQL database.
- Multi-threading (`ThreadPoolExecutor`) is used to scrape multiple races concurrently (default: 6 threads).
- Tor Browser ensures anonymity by renewing the IP address for each scrape.

## Notes
- **Tor Configuration**: Ensure Tor is running and accessible on port `9051`. The script uses `stem` to renew the Tor IP for each scrape.
- **GeckoDriver**: The script assumes `geckodriver` is located at `/home/idealbet/public_html/idealbet.online/scripts/geckodriver`. Update the path if necessary.
- **Headless Mode**: The script runs Firefox in headless mode to improve performance. Set `tor_options.headless = False` in the script if you want to see the browser UI.
- **Error Handling**: The script includes basic error handling for MySQL connections and Selenium timeouts. Monitor logs for issues during scraping.

## Future Enhancements
- Add support for scraping races on other dates (beyond "Tomorrow").
- Implement retry logic for failed scrapes due to network issues.
- Add data validation before inserting into the database.
- Include logging to track scraping progress and errors.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details (if applicable).

