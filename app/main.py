from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from algoliasearch.search_client import SearchClient
from fuzzywuzzy import fuzz
import os

# Initialize FastAPI app
app = FastAPI()

# Algolia credentials
ALGOLIA_APP_ID = os.getenv("ALGOLIA_APP_ID", "OQ9LS22UHK")
ALGOLIA_API_KEY = os.getenv("ALGOLIA_API_KEY", "74c8af5cf891cdc0f11e95ba29a9a2ee")
INDEX_NAME = "companies"

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
index = client.init_index(INDEX_NAME)

# Request model, so basically the model we will use for the search function
class SearchQuery(BaseModel):
    name: str = ""
    website: str = ""
    phone_number: str = ""
    facebook_profile: str = ""

# Search function
def best_match(query, results):
    best_score = 0
    best_result = None
    
    for result in results:
        score = 0
        
        # Exact matches
        if query.website and query.website in result.get("url", ""):
            score += 30
        if query.phone_number and query.phone_number in result.get("phone_numbers", []):
            score += 25
        if query.facebook_profile and query.facebook_profile in result.get("social_links", []):
            score += 20
        
        # Fuzzy matching for company name
        if query.name and "company_name" in result:
            name_similarity = fuzz.partial_ratio(query.name.lower(), result["company_name"].lower())
            score += name_similarity // 2  # Weight name matching lower
        
        if score > best_score:
            best_score = score
            best_result = result
    
    return best_result

@app.post("/search")
def search_company(query: SearchQuery):
    try:
        search_query = query.name or query.website or query.phone_number or query.facebook_profile

        #Debugging Output: Print the query before sending, needed because of the issues we faced with getting a lot of 500 errors or 404 company not found error
        print(f"📤 Sending query to Algolia: {search_query}")
        print(f"🔍 Using hitsPerPage: 10")

        
        response = index.search(search_query, {"hitsPerPage": 10})

        #Debugging Output: Print what Algolia returns
        print("🔍 Algolia API Response:", response)

        best_result = best_match(query, response["hits"])

        if best_result:
            return best_result
        else:
            raise HTTPException(status_code=404, detail="No matching company found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




print("✅ API updated to return best-matching company profiles!")
