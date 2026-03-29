import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # points to app/

from pipeline.generation import fee_markdown_table, generate_newsletter
from pipeline.extraction import raw_fee_extract
from pipeline.review import review_raw_extract, review_newsletter
from utils.logger import get_logger 
from utils.config import base_path, config

logger = get_logger(__name__)

_raw_extract_review_queue_path:Path = base_path / config["review"]["raw_extract_dir"]
_newsletter_review_queue_path:Path = base_path / config["review"]["newsletter_dir"]
_example_path:Path = base_path / config["database"]["example_store_dir"]

if __name__ == "__main__":
    logger.info("Start of process")
    review_raw_extract()
    breakpoint()
    raw_extract, pdf_context, file_name = raw_fee_extract()
    review_raw_extract()
    fee_table_markdown = fee_markdown_table(raw_extract)
    generate_newsletter(pdf_context, file_name, fee_table_markdown)
    review_newsletter()