import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import os

# Ensure data directory exists before I start
os.makedirs('/Users/moisescuvlad/company_api_project/scraper/data', exist_ok=True)

# Load websites from CSV
websites_df = pd.read_csv('/Users/moisescuvlad/Downloads/sample-websites.csv')
websites = websites_df['domain'].dropna().unique()

def extract_company_data(url):
    for protocol in ["http://", "https://"]:
        try:
            response = requests.get(f'{protocol}{url}', timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # ✅ Improved phone number extraction with standard formatting mentioned in Step 2
            phone_pattern = re.compile(r'\+?\d{1,3}?[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}')
            potential_numbers = phone_pattern.findall(soup.text)

            # Convert to numeric-only format, Challemge mentioned in Step2 and 5
            phone_numbers = [
                re.sub(r'\D', '', num) for num in potential_numbers
                if 7 <= len(re.sub(r'\D', '', num)) <= 15  # Keep only numbers between 7 and 15 digits
            ]

    
            social_links = [
                link['href'] for link in soup.find_all('a', href=True)
                if any(platform in link['href'] for platform in ['facebook.com', 'linkedin.com', 'twitter.com'])
            ]

            # ✅ Improved address extraction with stricter filters, first challenge faced with this code problem
            address_pattern = re.compile(
                r'(\d{1,5}\s\w+(?:\s\w+)*\s(?:Street|St\.|Road|Rd\.|Avenue|Ave\.|Boulevard|Blvd\.|Drive|Dr\.|Lane|Ln\.|Court|Ct\.|Parkway|Pkwy\.|Plaza|Plz\.|Square|Sq\.|Highway|Hwy\.|Suite|Building|Office|Unit)(?:,\s*\w+(?:\s\w+)*,?\s*\d{5})?)',
                re.IGNORECASE
            )
            potential_addresses = address_pattern.findall(soup.get_text())

            valid_addresses = [
                addr for addr in potential_addresses
                if not re.search(r'\b000\b|homes|unit\s*\d{0,2}', addr, re.IGNORECASE)
                and len(addr.split()) >= 3
            ]

            address = valid_addresses[0] if valid_addresses else "No valid address found"

            return {
                'url': url,
                'phone_numbers': list(set(phone_numbers)),  # Store numeric-only phone numbers
                'social_links': list(set(social_links)),
                'address': address
            }

        except requests.RequestException as e:
            print(f"Skipping {url}: {e}")
            with open('scraper/failed_domains.txt', 'a') as error_log:
                error_log.write(f"{url} - {e}\n")
            continue

    return None


# Scrape data
company_data = []
for website in websites:
    data = extract_company_data(website)
    if data:
        company_data.append(data)

# Save scraped data for the merge py code
with open('/Users/moisescuvlad/company_api_project/scraper/data/companies.json', 'w') as f:
    json.dump(company_data, f, indent=4)
