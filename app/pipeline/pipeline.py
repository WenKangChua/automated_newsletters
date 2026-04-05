from pathlib import Path
from pipeline.generate import generate_fee_markdown_table, generate_newsletter
from pipeline.extraction import raw_fee_extract
from pipeline.review import review_raw_extract, review_newsletter, save_raw_extract_example, save_newsletter_example
from utils.logger import get_logger 
from utils.config import base_path, config, datetime_now

logger = get_logger(__name__)

_input_file_name:str = "mock_gri_bulletin_1.pdf"
_output_file_name:str = datetime_now + "_mock_gri_bulletin_1"
_input_file_dir:Path = base_path / config["queues"]["input"]["pending_process_dir"] / _input_file_name # Folder where pdf file to be processed    

_raw_extract_review_queue_path:Path = base_path / config["queues"]["review"]["raw_extract_dir"] # Folder where raw extract are to be reviewed
_newsletter_review_queue_path:Path = base_path / config["queues"]["review"]["newsletter_dir"]

_complete_queue_dir = base_path / config["queues"]["review"]["newsletter_dir"]
_raw_extract_complete_queue_dir = base_path / config["queues"]["output"]["raw_extract_dir"]

_raw_extract_example_store_dir:Path = base_path / config["database"]["store"]["raw_extract_example_store_dir"]

_database_file_path = base_path / config["database"]["csv"]["fee_database_csv"]

def main():
    review_raw_extract()
    # breakpoint()
    raw_fee_extract(_input_file_dir, _output_file_name)
    # review_raw_extract()
    # # breakpoint()
    fee_table_markdown = generate_fee_markdown_table(_output_file_name)
    generate_newsletter(_input_file_name, fee_table_markdown, _output_file_name)
    # # breakpoint()
    review_newsletter()
    save_raw_extract_example()
    save_newsletter_example()
    return None