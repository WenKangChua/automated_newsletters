import pandas as pd
from rapidfuzz import process, fuzz
from pathlib import Path
from utils.config import config, base_path
from utils.logger import get_logger

logger = get_logger(__name__)

def get_fuzzy_match(fee_name:str, choices:list[str], threshold:int = 85) -> str|None:
    """
    Fuzzy match a string and a list of string.
    Returns the first matched string in the list if above threshold.
    """
    match:tuple[str, float, int]|None = process.extractOne(fee_name, choices, scorer = fuzz.token_sort_ratio) # extractOne returns (match, score, index)
    if match and match[1] >= threshold:
        return match[0]
    return None

def fee_lookup(database_file_path:Path, raw_extract:pd.DataFrame) -> str:
    """
    Takes a dataframe of new fees and fuzzy matches them against the internal fee database.
    Returns a markdown-formatted table with matched fee names, old rates(if applicable), new rates, and change types.
    """
    fee_database_csv:Path = database_file_path
    
    logger.info(f"Reading Fee Database: '{fee_database_csv}'")
    fee_database:pd.DataFrame = pd.read_csv(fee_database_csv)
    fee_database = fee_database[fee_database["is_deprecated"] == False]

    # # We map 'old' fee names to the closest 'new' fee names
    # choices:list[str] = fee_database["fee_name"].tolist()
    # raw_extract["matched_fee_name"] = raw_extract["fee_name"].apply(
    #     lambda x: get_fuzzy_match(x, choices)
    # )
    # logger.info(f"Database fuzz match result:\n{raw_extract}")

    #Merge the tables
    matched_fees:pd.DataFrame = pd.merge(
        raw_extract, 
        fee_database,
        left_on=["billing_id","service_id"], 
        right_on=["billing_id","service_id"], 
        how="left",
        suffixes=("_database", "_extract")
    )

    logger.info(f"Dropping Columns... Renaming Columns.... Ordering Column...")
    matched_fees = matched_fees.rename(columns={"fee_name_database":"fee_name"})
    column_order:list[str] = ["country", "effective_date", "fee_name","current_rate", "new_rate", "change_type"]
    matched_fees = matched_fees[column_order]

    matched_fees = matched_fees.to_markdown(index=False)
    logger.info(f"Output\n {matched_fees}")

    return matched_fees

def add_fees(new_fees):
    update_new_fees = new_fees[new_fees["change_type"] == "updated_fee"]
