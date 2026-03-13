import pandas as pd
from rapidfuzz import process, fuzz
from pathlib import Path
from config import config
from logger import get_logger

logger = get_logger(__name__)

def fee_lookup():
    base_path = Path(__file__).parent.parent

    existing_fee_csv = base_path / config["database"]["fee_database"]
    fee_announcement_csv = base_path /  config["database"]["fee_announcement"]

    existing_fees = pd.read_csv(existing_fee_csv)
    logger.info(f"Reading Fee Database: {existing_fee_csv}")
    fee_announcement = pd.read_csv(fee_announcement_csv)
    logger.info(f"Reading Fee Announcement: {fee_announcement_csv}")

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

    logger.info(f"Starting Fuzzy Match")
    fee_announcement["matched_fee_name"] = fee_announcement["fee_name"].apply(
        lambda x: get_fuzzy_match(x, choices)
    )

    # 4. Merge the tables
    logger.info(f"Mapping rates in fee_database to fee_announcement_database")
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

    updated_fee_markdown = merged_df.to_markdown(index=False)
    logger.info(f"Output\n {updated_fee_markdown}")
    return updated_fee_markdown

if __name__ == "__main__":
    fee_lookup()





