from algoliasearch.search_client import SearchClient
import json


ALGOLIA_APP_ID = 'OQ9LS22UHK'
ALGOLIA_API_KEY = '74c8af5cf891cdc0f11e95ba29a9a2ee'

INDEX_NAME = "companies"

# Initialize Algolia client
client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
index = client.init_index(INDEX_NAME)


merged_file_path = "scraper/data/merged_companies.json"
with open(merged_file_path, "r") as f:
    companies = json.load(f)


for idx, company in enumerate(companies):
    company["objectID"] = str(idx)  # Assign a unique identifier which will be visible and what pops up first in aglio, and is good for keeping track of duplicates and seeing which is from your latest indexing run

# Upload data to Algolia
index.save_objects(companies, {"autoGenerateObjectIDIfNotExist": True})

print(f"✅ Successfully indexed {len(companies)} companies to Algolia!")
