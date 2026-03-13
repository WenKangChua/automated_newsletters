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

### Start of stage 1
# initialise file paths and variables
logger.info("Stage 1: Start extract fee details from input")
input_file_path = config["input"]["input_pdf_path"]
rag_query = config["input"]["fee_extract_query"]
max_retries = 3

# From my PDF, get relevant context through similiarity search
# Format instruction prompt with system user tag to ensure json output
# Pass the prompt and context into phi4 chat model from huggingface
logger.info(f"Reading file from: {input_file_path}")
logger.info(f"Query for RAG: {rag_query}")

context = vector_store(file_path = input_file_path, rag_query = rag_query)

logger.info(f"RAG Context Output:\n {context}")

prompt = fee_names_json_prompt_instructions()
logger.info(f"Invoking Prompt: {prompt}")
extract_fees_kwargs = {"prompt":prompt, "query":rag_query, "context":context}

for attempt in range(max_retries):
    response = mini_instruct_model(**extract_fees_kwargs)
    response = strip_markdown_fences(response)
    valid, result = validate_output(response)
    if valid:
        logger.info(f"Valid output on attempt {attempt + 1}")
        break
    else:
        logger.warning(f"Attempt {attempt + 1} failed: {result} Output: {response}")
        if attempt < max_retries - 1:
            logger.info("Repairing prompt...")
            prompt = repair_prompt()
            repair_kwargs = {"prompt":prompt, "previous_output":response, "error":result}
            extract_fees_kwargs = repair_kwargs
else:
    logger.error(f"Failed to get valid output after {max_retries} attempts. Last error: {result}")

response = json.loads(response)["fee_names"]
logger.info(f"Output:\n {response}")
logger.info("Stage 1: Finish extract fee details from input")
### End of stage 1

### Start of Stage 2
logger.info("Stage 2: Start update fee database")

output_file = base_path / config["output"]["output_path_fee_announcement_csv"]
new_fees = pd.DataFrame(response)
new_fees.insert(column="extracted_at", loc=0, value=datetime_now)
logger.info(f"Inserting data: {new_fees.head()}")

new_fees.to_csv(output_file, index=False, mode='a', header=False)
logger.info("Data added to fee_announcement.csv\n")
logger.info("Stage 2: Finish update fee database")
### End of Stage 2

### Start of Stage 3
logger.info("Stage 3: Start generating system notification")
updated_fee_table_markdown = fee_lookup()
file_path = "/Users/wenkangchua/Documents/GitHub/customer_notification_generator/extract_fees/input/m_an11539_en-us 2025-04-15.pdf"
question = "Give me details on what had change and the retional behind it."
context = vector_store(file_path=file_path, rag_query=question)

prompt = notification_article_prompt_template(context=context, updated_fee_table_markdown=updated_fee_table_markdown)
response = mini_instruct_model(prompt=prompt)

article_notification = response

output_file_name = datetime_now + "_results.md"

with open(base_path / config["output"]["output_notification_path"] / output_file_name, "w", encoding="utf-8") as f:
    f.write(article_notification)
### End of Stage 3
