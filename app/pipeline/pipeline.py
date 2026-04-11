from pathlib import Path
from pipeline.generate import generate_fee_markdown_table, generate_newsletter
from pipeline.extraction import raw_fee_extract
from pipeline.review import review_raw_extract, review_newsletter, save_raw_extract_example, save_newsletter_example
from utils.logger import get_logger 
from utils.config import base_path, config, datetime_now

logger = get_logger(__name__)

def run_extraction():
    input_file_dir:Path = base_path / config["queues"]["input"]["pending_process_dir"]
    pending_process_files:list[Path] = [f for f in input_file_dir.iterdir() if f.is_file() and f.suffix in {".pdf"}]
    for each in pending_process_files:
        raw_fee_extract(each)

def run_review_raw_extract():
    review_raw_extract()

def run_generate():
    output_file_dir:Path = base_path / config["queues"]["output"]["raw_extract_dir"]
    output_files:list[Path] = [f for f in output_file_dir.iterdir() if f.is_file() and f.suffix in {".txt"}]
    for each in output_files:
        fee_table_markdown = generate_fee_markdown_table(each.name)
        generate_newsletter(fee_table_markdown, each.stem)

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