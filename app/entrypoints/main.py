from domain.retrieval.vector_store import build_vector_store, query_vector_store
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

def stage_1_1() -> None:
    logger.info("Checking for model output to be reviewed...")
    ouput_files = [f for f in output_folder_path.iterdir() if f.is_file() and f.suffix == ".txt" ]
    if ouput_files:
        output_file_names = "\n".join(f.name for f in ouput_files)
        logger.warning(f"Please review these output before continuing:\n{output_file_names}")
    for each_file in ouput_files:
        answer = input(f"Move {each_file.name} from review queue to the fee extract queue? (Y/N) ")
        if answer.lower().strip() == "y":
            old_path = output_folder_path / each_file.name
            new_path = base_path / config["database"]["model_output"] / each_file.name
            logger.info(f"Moving file from '{old_path}' -> '{new_path}'")
            old_path.rename(new_path)
        else:
            logger.info(f"{each_file.name} not moved.")
    return None

def stage_2(csv_output):
    ## Start of Stage 2
    ### To look up fees in database for old rates
    logger.info("Stage 2: Finding existing fees")

    new_fees = csv_output
    logger.info(f"Dataframe output:\n\n {new_fees}")

    updated_fee_table_markdown = fee_lookup(new_fees)

    logger.info("Stage 2: End finding existing fees")

    return updated_fee_table_markdown
    ### End of Stage 2

def stage_3(pdf_context, updated_fee_table_markdown, csv_output):
    ## Start of Stage 3
    ### Generate the notification
    logger.info("Stage 3: Start generating system notification")
    output_file_name = datetime_now + "_results.md"
    output_file_path = base_path / config["output"]["output_notification_path"] / output_file_name
    
    logger.info("Generating system notification")
    prompt = notification_article_prompt_template(context = pdf_context, updated_fee_table_markdown = updated_fee_table_markdown)
    system_notification = mini_instruct_model(prompt = prompt)
    review_content = f"""Review Section, do not edit anything outside the csv block.

    ```csv
    {csv_output}
    ```

    ---

    {system_notification}

    """
    review_content = ("\n".join(line.strip() for line in review_content.strip().splitlines()))

    logger.info(f"Saving System notification in {output_file_path}")
    output_file_path.write_text(review_content, encoding = "utf-8")

    logger.info(f"Completed generating system notification: {output_file_name}")
    return output_file_path, output_file_name, review_content

    ### End of Stage 3

def stage_4(output_file_path, output_file_name, pdf_context, review_content):
    ## Start of Stage 4
    ### To add the csv and notification into example_store
    system_notificaton_dir = config["database"]["model_output"]
    open_file(output_file_path)
    while True:
        logger.info("Please review and edit the notification before continuing.")
        save = input("Save csv output to vector store? It may be used as an example in the future. (Y/N) ").strip().lower()
        if save == "y":
            # output_file = output_file_path.read_text()
            # csv_output = re.search(r"```csv(.*?)```", output_file, re.DOTALL).group(1).strip()
            system_notificaton_dir.write_text(pdf_context, encoding = "utf-8")
            output_file_path.rename(base_path / system_notificaton_dir /  output_file_name)
            # add_example(context = pdf_context, csv_output = csv_output)
            logger.info(f"{output_file_path} have been added to example store")
            break
        elif save == "n":
            logger.info("Quiting...")
            break
        else:
            logger.info("Please enter either Y or N ")
    ### End of stage 4

if __name__ == "__main__":
    logger.info("Start of process")
    # csv_output, pdf_context = stage_1()
    stage_1_1()
    
    # updated_fee_table_markdown = stage_2(csv_output)
    
    # output_file_path, output_file_name, review_content = stage_3(pdf_context, updated_fee_table_markdown, csv_output)
    # _load_chat_model.cache_clear()
    # torch.mps.empty_cache()
    
    # stage_4(output_file_path, output_file_name, pdf_context, review_content)
    # logger.info("End of process")
