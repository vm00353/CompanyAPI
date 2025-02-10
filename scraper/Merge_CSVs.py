import pandas as pd

# Load the scraped company data done in the scraper py code
scraped_file_path = "/Users/moisescuvlad/company_api_project/scraper/data/companies.json"  # Update path if needed
scraped_df = pd.read_json(scraped_file_path)

# Load the company names CSV
company_names_file_path = "/Users/moisescuvlad/Downloads/sample-websites-company-names.csv"
company_names_df = pd.read_csv(company_names_file_path)

# Ensure column names match correctly
company_names_df.rename(columns={"domain": "url"}, inplace=True)  # Align naming

# Select only the necessary columns from company names file as the others are already in the companies.json file
columns_to_merge = ["url", "company_commercial_name", "company_legal_name", "company_all_available_names"]
company_names_df = company_names_df[columns_to_merge]

# Merge scraped data with company names dataset
merged_df = scraped_df.merge(company_names_df, on="url", how="left")

# Rename columns for clarity, and that is how it will show up in aglolia
merged_df.rename(columns={"company_commercial_name": "company_name"}, inplace=True)

# Save the merged data and that is what will run in index py code
merged_file_path = "scraper/data/merged_companies.json"
merged_df.to_json(merged_file_path, orient="records", indent=4)

print(f"✅ Merged data saved to {merged_file_path}")
