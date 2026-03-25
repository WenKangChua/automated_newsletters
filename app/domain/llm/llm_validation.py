from pydantic import BaseModel, Field
from typing import Literal
import re
import pandas as pd
from io import StringIO

# Using pydantic BaseModel, define a list of fields and dtype
class fee_name(BaseModel):
    fee_name:str = Field(description = "The name of the interchange fee or scheme fee")
    new_rate:float | None = Field(description = "The new fee rate as express in percentage.")
    effective_date:str = Field(description = "The effective start date or end date of the fee. STRICTLY in YYYY-MM-DD format.")
    region:str | None = Field(description = "The region in which the fee is for.")
    currency:str = Field(description = "The currency of the fees.")
    change_type: Literal["new_fee", "updated_fee", "deleted_fee"] = Field(description = "The only values allowed are new_fee and updated_fee.")

def validate_output(output:str, pydantic_base_model:BaseModel) -> tuple[bool, str]:
    """
    validates the model output against a pydantic base model class.
    It test for dataframe conversion and validates value against a pydantic base model.
    If there is an error, return False and the error message else, it will return true.
    """
    try:
        df_output = pd.read_csv(StringIO(output))
        for i, row in df_output.iterrows():
            pydantic_base_model(**row.to_dict())
        return True, output
    except Exception as e:
        return False, str(e)
    
def strip_markdown_fences(text:str) -> str:
    """
    Returns a string with backticks striped.
    """
    text = text.strip()
    text = re.sub(r"^```(?:csv)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

    
