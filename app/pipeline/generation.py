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

def fee_markdown_table(raw_extract:str) -> str:
    """
    Look up fee database for existing rates and map it against new rates from raw extract.
    Returns a markdown table from a pandas dataframe.
    """
    ## Start of Stage 2
    ### To look up fees in database for old rates
    logger.info("Stage 2: Finding existing fees")

    logger.info(f"Dataframe output:\n\n {raw_extract}")
    
    raw_extract = pd.read_csv(StringIO(raw_extract))
    database_file_path = base_path / config["database"]["fee_database_csv"]
    updated_fee_table_markdown = fee_lookup(database_file_path ,raw_extract)

    logger.info("Stage 2: End finding existing fees")

    return updated_fee_table_markdown

def generate_newsletter(pdf_context, file_name, fee_table_markdown):
    ## Start of Stage 3
    ### Generate the notification
    logger.info("Stage 3: Start generating system notification")
    output_file_name = datetime_now + "_results.md"
    complete_queue_dir = base_path / config["review"]["newsletter_dir"] / output_file_name
    
    logger.info("Generating system notification")
    prompt = newsletter_prompt_template(context = pdf_context, updated_fee_table_markdown = fee_table_markdown)
    kwargs = {"prompt":prompt}
    newsletter = run_mini_instruct_model(**kwargs)
    review_content = f"""
    Bulletin:\n
    ```bulletin
    {file_name}
    ```
    ---
    {newsletter}
    """
    review_content = ("\n".join(line.strip() for line in review_content.strip().splitlines()))

    logger.info(f"Saving System notification in {complete_queue_dir}")
    complete_queue_dir.write_text(review_content, encoding = "utf-8")

    logger.info(f"Completed generating system notification: {output_file_name}")
    # return complete_queue_dir, output_file_name, review_content
    return None

    ### End of Stage 3

def stage_4(output_file_path, output_file_name, pdf_context):
    ## Start of Stage 4
    ### To add the csv and notification into example_store
    system_notificaton_dir = config["database"]["completed_dir"]
    open_file(output_file_path)
    while True:
        logger.info("Please review and edit the notification before continuing.")
        save = input("Save csv output to vector store? It may be used as an example in the future. (Y/N) ").strip().lower()
        if save == "y":
            system_notificaton_dir.write_text(pdf_context, encoding = "utf-8")
            output_file_path.rename(base_path / system_notificaton_dir /  output_file_name)
            logger.info(f"{output_file_path} have been added to example store")
            break
        elif save == "n":
            logger.info("Quiting...")
            break
        else:
            logger.info("Please enter either Y or N")