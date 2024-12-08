import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# Database setup
def init_db():
    try:
        conn = sqlite3.connect('listings.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS listings (
                            id TEXT PRIMARY KEY,
                            title TEXT,
                            region TEXT,
                            price TEXT,
                            url TEXT,
                            date_scraped TEXT)''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# Fetch the HTML content
def fetch_listings():
    try:
        url = 'https://www.ss.com/lv/electronics/computers/search-result/?q=1050ti'
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

# Parse the HTML to extract data
def parse_listings(soup):
    if soup is None:
        return []

    listings = []
    for row in soup.find_all('tr', id=lambda x: x and x.startswith('tr_')):
        try:
            listing_id = row['id'].split('_')[1]
            title_tag = row.find('a', class_='am')
            title = title_tag.get_text(strip=True)
            url = "https://www.ss.com" + title_tag['href']
            region = row.find('div', class_='ads_region').get_text(strip=True)
            price = row.find('td', class_='msga2-o').get_text(strip=True)
            listings.append((listing_id, title, region, price, url, time.strftime('%Y-%m-%d %H:%M:%S')))
        except AttributeError:
            continue  # Skip rows with missing data
    return listings

# Save listings to the database
def save_listings(listings):
    try:
        conn = sqlite3.connect('listings.db')
        cursor = conn.cursor()

        for listing in listings:
            cursor.execute('''INSERT OR REPLACE INTO listings (id, title, region, price, url, date_scraped)
                              VALUES (?, ?, ?, ?, ?, ?)''', listing)

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# Check for new or removed listings
def check_for_updates():
    conn = sqlite3.connect('listings.db')
    cursor = conn.cursor()

    # Get all the current listing IDs from the database
    cursor.execute('SELECT id FROM listings')
    old_ids = {row[0] for row in cursor.fetchall()}

    soup = fetch_listings()
    if soup is None:
        print("Failed to fetch listings.")
        return

    new_listings = parse_listings(soup)
    new_ids = {listing[0] for listing in new_listings}

    # New listings
    added = new_ids - old_ids
    removed = old_ids - new_ids

    print(f"Added listings: {len(added)}")
    print(f"Removed listings: {len(removed)}")

    save_listings(new_listings)
    conn.close()

# Main function to run the scraper
def main():
    init_db()
    check_for_updates()

if __name__ == '__main__':
    main()
