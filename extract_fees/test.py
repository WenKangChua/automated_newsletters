from vector_store import vector_store
from local_llm import mini_instruct_model
from prompt_templates import fee_names_json_prompt_instructions, notification_article_prompt_template, repair_prompt
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
from fee_lookup import fee_lookup
from validation import validate_output, strip_markdown_fences
from config import config
from logger import get_logger

logger = get_logger(__name__)
base_path = Path(__file__).parent.parent    
datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

output_file_name = datetime_now + "_results.md"
print(output_file_name)