from pathlib import Path
from domain.llm.local_llm import run_mini_instruct_model
from domain.llm.prompt_templates import *
from domain.fees.match_fee import fee_lookup
from utils.config import config, base_path, datetime_now
from io import StringIO
from utils.logger import get_logger
import pandas as pd

logger = get_logger(__name__)

def generate_fee_markdown_table(file_name:str) -> str:
    """
    Look up fee database for existing rates and map it against new rates from raw extract.
    Returns a markdown table from a pandas dataframe.
    """
    file_name = file_name + ".txt"
    raw_extract:Path = base_path / config["queues"]["output"]["raw_extract_dir"] / file_name
    database_file_path:Path = base_path / config["database"]["csv"]["fee_database_csv"]
    
    raw_extract:str = raw_extract.read_text(encoding = 'utf-8')
    raw_extract:str = re.search(r"```csv(.*?)```", raw_extract, re.DOTALL).group(1).strip()
    raw_extract:pd.DataFrame = pd.read_csv(StringIO(raw_extract))
    
    updated_fee_table = fee_lookup(database_file_path, raw_extract)
    updated_fee_table_markdown = updated_fee_table.to_markdown(index = False)

    return updated_fee_table_markdown

def generate_newsletter(input_file_name:str, fee_table_markdown:str, output_file_name:str) -> None:

    output_file_name = output_file_name + "_results.md"
    complete_queue_dir = base_path / config["queues"]["review"]["newsletter_dir"] / output_file_name
    
    prompt = newsletter_prompt_template(updated_fee_table_markdown = fee_table_markdown)
    newsletter = run_mini_instruct_model(prompt = prompt)
    
    review_content = f"""
    Bulletin:\n
    ```file_name
    {input_file_name}
    ```
    ---
    Markdown Table:\n
    ```markdown_table
    {fee_table_markdown}
    ```
    ---
    Newsletter:\n
    ```newsletter
    {newsletter}
    ```
    """
    review_content = ("\n".join(line.strip() for line in review_content.strip().splitlines()))

    logger.info(f"Saving System notification to '{complete_queue_dir}'")
    complete_queue_dir.write_text(review_content, encoding = "utf-8")

    logger.info(f"Completed generating system notification: {output_file_name}")
    # return complete_queue_dir, output_file_name, review_content
    return None