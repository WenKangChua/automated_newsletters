from customer_notification_generator.app.domain.retrieval.vector_store import build_vector_store, query_vector_store
from domain.llm.local_llm import run_mini_instruct_model, _load_chat_model
from domain.llm.prompt_templates import *
import pandas as pd
from datetime import datetime
from pathlib import Path
from domain.retrieval.example_store import add_example
from domain.fees.match_fee import fee_lookup
from domain.llm.llm_validation import validate_output, strip_markdown_fences
from utils.config import config
from io import StringIO
from utils.logger import get_logger
from utils.system_commands import open_file

logger = get_logger(__name__)
base_path = Path(__file__).parent.parent # ~/Documents/GitHub/customer_notification_generator/
datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
output_file_name:str = datetime_now + "_model_csv_output.txt"
output_folder_path = base_path / config["output"]["output_notification_path"]
output_md_path:Path = output_folder_path / output_file_name

def stage_1():
    """
    From PDF files in a input folder, a model will extract all relevant acquirer fees and return
    the results in a text file into the output folder.
    """
    ## Start of stage 1
    # initialise file paths and variables
    logger.info("Stage 1: Start extract fee details from input")
    input_file_path = config["input"]["input_pdf_path"]
    rag_query ="Please find all relevant acquirer fees, rates, country, effective date, currency."
    max_retries = 3

    # From my PDF, get relevant context through similiarity search
    # Format instruction prompt with system user tag to ensure json output
    # Pass the prompt and context into phi4 chat model from huggingface
    logger.info(f"Reading file from: {input_file_path}")
    logger.info(f"Query for RAG: {rag_query}")

    vector_store = build_vector_store(file_path = input_file_path)
    pdf_context = query_vector_store(vector_store, rag_query = rag_query)

    raw_fee_extract_prompt = raw_fee_extract_prompt_template(example_query = rag_query)
    logger.info(f"Invoking Prompt...")

    extract_fees_kwargs = {"prompt":raw_fee_extract_prompt, "query":rag_query, "context":pdf_context}

    for attempt in range(max_retries):
        csv_output = run_mini_instruct_model(**extract_fees_kwargs)
        csv_output = strip_markdown_fences(csv_output)
        valid, result = validate_output(csv_output)
        if valid:
            logger.info(f"Valid output on attempt {attempt + 1}")
            break
        else:
            logger.warning(f"Attempt {attempt + 1} failed: {result} Output: {csv_output}")
            if attempt < max_retries - 1:
                logger.info("Repairing prompt...")
                # repair_prompt = repair_prompt_template()
                repair_kwargs = {"prompt":repair_prompt_template(), "previous_output":csv_output, "error":result, "query":rag_query, "context":pdf_context}
                extract_fees_kwargs = repair_kwargs
    else:
        logger.error(f"Failed to get valid output after {max_retries} attempts. Last error: {result}")

    model_csv_output = f"""
    ```context
    {pdf_context}
    ```
    -------
    ```csv
    {csv_output}
    ```
    """
    model_csv_output = ("\n".join(line.strip() for line in model_csv_output.strip().splitlines()))
    
    output_md_path.write_text(model_csv_output, encoding = "utf-8")

    logger.info(f"Output:\n {csv_output}")
    logger.info("Stage 1: Finish extract fee details from input")

    return csv_output, pdf_context
    ### End of stage 1

if __name__ == "__main__":
    stage_1()