from pydantic import BaseModel, Field
from typing import List
from typing import Literal
import re
from langchain_core.output_parsers import PydanticOutputParser


# Using pydantic BaseModel, define a list of fields and dtype
class fee_name(BaseModel):
    fee_name:str = Field(description = "The name of the interchange fee or scheme fee")
    new_rate:float | None = Field(description = "The new fee rate as express in percentage.")
    effective_date:str = Field(description = "The effective start date or end date of the fee. STRICTLY in YYYY-MM-DD format.")
    region:str | None = Field(description = "The region in which the fee is for.")
    currency:str = Field(description = "The currency of the fees.")
    change_type: Literal["new_fee", "updated_fee", "deleted_fee"] = Field(description = "The only values allowed are new_fee and updated_fee.")

# # Enables a list of fee_name
# class fee_name_list(BaseModel):
#     fee_names: List[fee_name]

def validate_output(output):
    try:
        # data = fee_name_list.model_validate_json(output)
        return True, output
    except Exception as e:
        return False, str(e)
    
def strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:csv)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

    
