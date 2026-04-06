from pathlib import Path
from domain.retrieval.vector_store import build_vector_store, query_vector_store
from domain.llm.local_llm import run_mini_instruct_model
from domain.llm.prompt_templates import *
from domain.llm.llm_validation import validate_output, strip_markdown_fences
from utils.config import datetime_now
from utils.logger import get_logger

logger = get_logger(__name__)

def raw_fee_extract(input_file:Path, _output_file_name:str) -> tuple[str]:
    """
    From PDF files in a input folder, a model will extract all relevant fees and return
    the results in a text file into a output folder.
    """
    logger.info(f"Reading file from '{input_file}'")

    # Build store and retrieve file context
    rag_query = "Extract all fees and surcharges information."
    vector_store = build_vector_store(pdf_file = input_file)
    pdf_context = query_vector_store(vector_store, rag_query = rag_query, k = 3)
    
    # Extract raw fee extract from file using SLM
    llm_query = "Generate a csv output according to system prompt."
    raw_fee_extract_prompt = raw_fee_extract_prompt_template(query = llm_query, context = pdf_context)

    # Validate SLM results
    max_retries = 3
    for attempt in range(max_retries):
        raw_extract = run_mini_instruct_model(prompt = raw_fee_extract_prompt)
        raw_extract = strip_markdown_fences(raw_extract)
        valid, result = validate_output(output = raw_extract, pydantic_base_model = fee_name)
        if valid:
            logger.info(f"Valid output on attempt {attempt + 1}")
            break
        else:
            logger.warning(f"Attempt {attempt + 1} failed: {result} Output: {raw_extract}")
            if attempt < max_retries - 1:
                logger.info("Repairing prompt...")
                raw_fee_extract_prompt = repair_prompt_template(context = pdf_context, query = rag_query, previous_output = raw_extract, error = result)
    else:
        logger.exception("Unexpected failure during extraction")

    # Building SLM raw_extract report
    model_raw_extract = f"""
    Bulletin
    ```bulletin
    {input_file.name}
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

    # Write report to review queue
    raw_extract_review_queue_dir:Path = base_path / config["queues"]["review"]["raw_extract_dir"] # Folder where raw extract are to be reviewed
    raw_extract_review_queue_file = raw_extract_review_queue_dir / f"{_output_file_name}.txt"
    raw_extract_review_queue_file.write_text(model_raw_extract, encoding = "utf-8")
    logger.info(f"Created SLM raw_extract report in: '{Path(*raw_extract_review_queue_file.parts[-3:])}'")

    # return raw_extract, pdf_context
    return None