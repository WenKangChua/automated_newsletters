import pandas as pd
from rapidfuzz import process, fuzz
from pathlib import Path

base_path = Path(__file__).parent.parent
fee_database_path = base_path / "database"

existing_fee_csv = fee_database_path / "fee_framework/fee_database.csv"
fee_announcement_csv = fee_database_path / "new_fees_llm_output/fee_announcement.csv"

# def update_existing_rate():

existing_fees = pd.read_csv(existing_fee_csv)
fee_announcement = pd.read_csv(fee_announcement_csv)

# 2. Define a function to find the best match
def get_fuzzy_match(fee_name, choices, threshold=85):
    # extractOne returns (match, score, index)
    match = process.extractOne(fee_name, choices, scorer=fuzz.token_sort_ratio)
    if match and match[1] >= threshold:
        return match[0]
    return None

# 3. Apply matching
# We map 'old' fee names to the closest 'new' fee names
choices = existing_fees["fee_name"].tolist()

fee_announcement["matched_fee_name"] = fee_announcement["fee_name"].apply(
    lambda x: get_fuzzy_match(x, choices)
)

# existing_fees["lookup_key"] = existing_fees["fee_name"] + existing_fees["country"]
# fee_announcement["lookup_key"] = fee_announcement["matched_fee_name"] + fee_announcement["country"]

# 4. Merge the tables
merged_df = pd.merge(
    fee_announcement, 
    existing_fees,
    left_on=["matched_fee_name","country"], 
    right_on=["fee_name","country"], 
    how="left",
    suffixes=("_existing", "_announcement")
)

merged_df = merged_df.drop(["extracted_at","matched_fee_name","fee_name_announcement","start_date"], axis=1)
merged_df = merged_df.rename(columns={"fee_name_existing":"fee_name"})
column_order = ["country", "effective_date", "fee_name","current_rate", "new_rate", "fee_change"]
merged_df = merged_df[column_order]
# print(merged_df)
updated_fee_markdown = merged_df.to_markdown(index=False)
# print(updated_fee_markdown)
# updated_rates_markdown = updated_rates.to_markdown(index=False)
# fee_announcement_markdown = fee_announcement.to_markdown(index=False)

# print(updated_rates_markdown)
# print("------------------")
# print(fee_announcement_markdown)
# print(fee_announcement)
# update_new_rates_df.to_csv(fee_database_path / "fee_framework/existing_fees.csv", index=False, mode='a', header=False)





