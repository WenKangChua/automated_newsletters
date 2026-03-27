from pathlib import Path
from app.domain.retrieval.vector_store import build_vector_store, query_vector_store
from app.domain.llm.local_llm import run_mini_instruct_model, _load_chat_model
from app.domain.llm.prompt_templates import *
from app.domain.retrieval.example_store import add_example
from app.domain.fees.match_fee import fee_lookup
from app.domain.llm.llm_validation import validate_output, strip_markdown_fences
from app.utils.config import config, base_path, datetime_now
from io import StringIO
from app.utils.logger import get_logger
from app.utils.system_commands import open_file
import pandas as pd

logger = get_logger(__name__)



def stage_1():
    """
    From PDF files in a input folder, a model will extract all relevant acquirer fees and return
    the results in a text file into the output folder.
    """
    raw_extract_filepath:Path = base_path / config["output"]["raw_extract_path"] # Folder where raw extract are to be reviewed
    input_file:Path = base_path / config["input"]["pdf_input_path"] / "Sample test file.pdf" # Folder where pdf file to be processed

    ## Start of stage 1
    # initialise file paths and variables
    logger.info("Stage 1: Start extract fee details from input")
    
    rag_query ="Please find all relevant acquirer fees, rates, country, effective date, currency."
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
        csv_output = run_mini_instruct_model(**extract_fees_kwargs)
        csv_output = strip_markdown_fences(csv_output)
        valid, result = validate_output(output = csv_output, pydantic_base_model = fee_name)
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
    Contains the context used to generate the extract.
    ```context
    {pdf_context}
    ```
    -------
    The extract that was generated based on the context above.
    ```csv
    {csv_output}
    ```
    """
    model_csv_output = ("\n".join(line.strip() for line in model_csv_output.strip().splitlines()))

    # Write raw extract to review queue
    raw_extract_filepath = raw_extract_filepath / f"{datetime_now} + _model_csv_output.txt"
    raw_extract_filepath.write_text(model_csv_output, encoding = "utf-8")

    logger.info(f"Output:\n {csv_output}")
    logger.info("Stage 1: Finish extract fee details from input")

    return csv_output, pdf_context
    ### End of stage 1

if __name__ == "__main__":
    stage_1()