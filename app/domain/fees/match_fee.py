import pandas as pd
from rapidfuzz import process, fuzz
from pathlib import Path
from utils.config import config, base_path
from utils.logger import get_logger

logger = get_logger(__name__)
_fee_database = base_path / config["database"]["csv"]["fee_database_csv"]

def _get_fuzzy_match(fee_name:str, choices:list[str], threshold:int = 85) -> str|None:
    """
    Fuzzy match a string and a list of string.
    Returns the first matched string in the list if above threshold.
    """
    match:tuple[str, float, int]|None = process.extractOne(fee_name, choices, scorer = fuzz.token_sort_ratio) # extractOne returns (match, score, index)
    if match and match[1] >= threshold:
        return match[0]
    return None

def _query_fee_database() -> pd.DataFrame:
    df = pd.read_csv(_fee_database)
    return df

def _query_destination_fees() -> pd.DataFrame:
    
    fee_database:pd.DataFrame = _query_fee_database()
    fee_database = fee_database[fee_database["is_deprecated"] == False]
    fee_database = fee_database[fee_database["charge_category"] == "destination"]
    
    return fee_database

def update_fee_database(raw_extract:pd.DataFrame) -> pd.DataFrame:
    """
    Updates fee database with new fees from raw extract.
    """
    # fee database columns
    # billing_id,service_id,fee_name,currency,current_rate,start_date,region,charge_category,is_deprecated
    
    # raw extract columns
    # "billing_id","service_id","fee_name","new_rate","effective_date","country","currency","change_type","charge_category"
    new_fees = raw_extract[raw_extract["change_type"] == "new_fees"]
    new_fees.rename(
        columns = {
            "new_rate":"current_rate",
            "effective_date":"start_date",
            "country":"region"
                 }, inplace = True
    )
    new_fees['is_deprecated'] = False
    column_order:list[str] = ["billing_id", "service_id", "fee_name", "currency","current_rate", "start_date", "region","charge_category", "is_deprecated"]
    new_fees = new_fees[column_order]

    new_fees.to_csv(_fee_database, 
                mode='a', 
                index=False, 
                header=False)

    return None

def fee_lookup(database_file_path:Path, raw_extract:pd.DataFrame) -> pd.DataFrame:
    """
    Takes a dataframe of new fees and fuzzy matches them against the internal fee database.
    Returns a markdown-formatted table with matched fee names, old rates(if applicable), new rates, and change types.
    """

    fee_database = _query_destination_fees()

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
        suffixes=("_extract", "_database")
    )

    logger.info(f"Dropping Columns... Renaming Columns.... Ordering Column...")
    matched_fees = matched_fees.dropna(subset=["current_rate"])
    # matched_fees = matched_fees[matched_fees["charge_category"] == "destination"]
    matched_fees = matched_fees.rename(columns={"fee_name_database":"fee_name", "currency_database":"currency"})
    column_order:list[str] = ["country", "currency", "effective_date", "fee_name","current_rate", "new_rate", "change_type"]
    matched_fees = matched_fees[column_order]

    # matched_fees = matched_fees.to_markdown(index=False)
    return matched_fees
