from pathlib import Path
from domain.retrieval.vector_store import build_vector_store, query_vector_store
from domain.llm.local_llm import run_mini_instruct_model, _load_chat_model
from domain.llm.prompt_templates import *
from domain.retrieval.example_store import add_example
from domain.fees.match_fee import fee_lookup
from domain.llm.llm_validation import validate_output, strip_markdown_fences
from utils.config import config, base_path, datetime_now
from io import StringIO
from utils.logger import get_logger
from utils.system_commands import open_file
import pandas as pd

logger = get_logger(__name__)

def raw_fee_extract() -> tuple[str]:
    """
    From PDF files in a input folder, a model will extract all relevant fees and return
    the results in a text file into a output folder.
    """
    file_name:str = "mock_gri_bulletin_1.pdf"
    raw_extract_review_queue_path:Path = base_path / config["review"]["raw_extract_dir"] # Folder where raw extract are to be reviewed
    input_file:Path = base_path / config["input"]["pdf_input_dir"] / file_name # Folder where pdf file to be processed

    ## Start of stage 1
    # initialise file paths and variables
    logger.info("Stage 1: Start extract fee details from input")
    
    rag_query ="Please generate a csv output of billing event, service id, surcharges, rates, country, effective date, currency."
    max_retries = 3

    # From my PDF, get relevant context through similiarity search
    # Format instruction prompt with system user tag to ensure json output
    # Pass the prompt and context into phi4 chat model from huggingface
    logger.info(f"Reading file from: {input_file}")
    logger.info(f"Query for RAG: {rag_query}")

    vector_store = build_vector_store(file = input_file)
    pdf_context = query_vector_store(vector_store, rag_query = rag_query)

    raw_fee_extract_prompt = raw_fee_extract_prompt_template(example_query = rag_query)
    logger.info(f"Invoking Prompt...")

    extract_fees_kwargs = {"prompt":raw_fee_extract_prompt, "query":rag_query, "context":pdf_context}

    for attempt in range(max_retries):
        raw_extract = run_mini_instruct_model(**extract_fees_kwargs)
        raw_extract = strip_markdown_fences(raw_extract)
        valid, result = validate_output(output = raw_extract, pydantic_base_model = fee_name)
        if valid:
            logger.info(f"Valid output on attempt {attempt + 1}")
            break
        else:
            logger.warning(f"Attempt {attempt + 1} failed: {result} Output: {raw_extract}")
            if attempt < max_retries - 1:
                logger.info("Repairing prompt...")
                repair_prompt = repair_prompt_template()
                repair_kwargs = {"prompt":repair_prompt, "previous_output":raw_extract, "error":result, "query":rag_query, "context":pdf_context}
                extract_fees_kwargs = repair_kwargs
    else:
        logger.error(f"Failed to get valid output after {max_retries} attempts. Last error: {result}")

    model_raw_extract = f"""
    Bulletin
    ```bulletin
    {file_name}
    ```
    ---
    Contains the context used to generate the extract
    ```context
    {pdf_context}
    ```
    ---
    The extract that was generated based on the context above
    ```csv
    {raw_extract}
    ```
    """
    model_raw_extract = ("\n".join(line.strip() for line in model_raw_extract.strip().splitlines()))

    # Write raw extract to review queue
    raw_extract_review_queue_file = raw_extract_review_queue_path / f"{datetime_now}_model_raw_extract.txt"
    raw_extract_review_queue_file.write_text(model_raw_extract, encoding = "utf-8")

    logger.info(f"Output:\n {raw_extract}")
    logger.info("Stage 1: Finish extract fee details from input")

    return raw_extract, pdf_context, file_name
    ### End of stage 1