from pydantic import BaseModel, Field, ConfigDict, ValidationError
from typing import Literal
import re
import pandas as pd
from io import StringIO

# Using pydantic BaseModel, define a list of fields and dtype
class fee_name(BaseModel):
    billing_id:str = Field(description="The billing event ID")
    service_id:str = Field(description="The service ID")
    fee_name:str = Field(description = "The name of the fee or surcharge")
    new_rate:float | None = Field(description = "The new fee rate as express in percentage")
    effective_date:str = Field(description = "The effective start date or end date of the fee. STRICTLY in YYYY-MM-DD format")
    country:str | None = Field(description = "The country applicable")
    currency:str = Field(description = "The currency of the fees")
    change_type: Literal["new_fee", "updated_fee", "deleted_fee"] = Field(description = "Contains either new_fee, updated_fee or deleted_fee")
    model_config = ConfigDict(extra='forbid')

def validate_output(output:str, pydantic_base_model:BaseModel) -> tuple[bool, str]:
    """
    validates the model output against a pydantic base model class.
    It test for dataframe conversion and validates value against a pydantic base model.
    If there is an error, return False and the error message else, it will return true.
    """
    # Validate if csv can be converted into pandas dataframe
    try:
        df_output = pd.read_csv(StringIO(output))
    except Exception as e:
        return False, str(e)
    
    # Validate values against a pydantic BaseModel
    error_message = []
    for i, row in df_output.iterrows():
        try:
            pydantic_base_model(**row.to_dict())
            return True, output
        except ValidationError as e:
            for error in e.errors():
                error_message.append(f"Row {i} | Field: {error['loc']} | Error Message: {error['msg']} | Wrong Value: {error['input']}")
    return False, ("\n".join(error_message))

def strip_markdown_fences(text:str) -> str:
    """
    Returns a string with backticks striped.
    """
    text = text.strip()
    text = re.sub(r"^```(?:csv)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

if __name__ == "__main__":
    _csv = """
"fee_name","new_rate","effective_date","country","currency","change_type"
"Standard Ground Delivery Surcharge","2.75","2025-06-01","Singapore","SGD","updated_fee"
"Express Air Delivery Surcharge","3.30","2025-06-01","Singapore","SGD","updated_fee"
"Residential Address Surcharge","1.50","2025-06-01","Singapore","SGD","updated_fee"
"""
    validate_output(_csv, fee_name)
