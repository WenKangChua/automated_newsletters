from pathlib import Path
from pipeline.generate import generate_fee_markdown_table, generate_newsletter
from pipeline.extraction import raw_fee_extract
from pipeline.review import review_raw_extract, review_newsletter, save_raw_extract_example, save_newsletter_example
from utils.logger import get_logger 
from utils.config import base_path, config, datetime_now

logger = get_logger(__name__)

_input_file_name:str = "mock_gri_bulletin_1.pdf"
_output_file_name:str = "output_mock_gri_bulletin_1"
_input_file_dir:Path = base_path / config["queues"]["input"]["pending_process_dir"] / _input_file_name # Folder where pdf file to be processed    

def run_extraction():
    raw_fee_extract(_input_file_dir, _output_file_name)

def run_review_raw_extract():
    review_raw_extract()

def run_generate():
    fee_table_markdown = generate_fee_markdown_table(_output_file_name)
    generate_newsletter(_input_file_name, fee_table_markdown, _output_file_name)

def run_review_newsletter():
    review_newsletter()

def run_save_examples():
    save_raw_extract_example()
    save_newsletter_example()

def run_full_pipeline():
    run_extraction()
    run_review_raw_extract()
    run_generate()
    run_review_newsletter()
    run_save_examples()