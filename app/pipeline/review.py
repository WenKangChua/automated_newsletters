from pathlib import Path
from utils.config import config, base_path
from utils.logger import get_logger
from utils.system_commands import open_file

logger = get_logger(__name__)

def review_files(source_dir:Path, target_dir:Path) -> None:
    """
    Prompt user to review the files in source directory. The file will be moved to target directory once approved.
    """
    logger.info("Checking documents to be reviewed...")
    source_files:list[Path] = [f for f in source_dir.iterdir() if f.is_file() and f.suffix in {".txt",".md",".csv"}]
    if source_files:
        output_file_names:str = "\n".join(f.name for f in source_files)
        logger.warning(f"Please review these output before continuing:\n{output_file_names}")
    for each_file in source_files:
        open_file(each_file)
        answer:str = input(f"Move {each_file.name} from review queue to the fee extract queue? (Y/N) ")
        if answer.lower().strip() == "y":
            old_path:Path = source_dir / each_file.name
            new_path:Path = target_dir / each_file.name
            logger.info(f"Moving file from '{old_path}' -> '{new_path}'")
            old_path.rename(new_path)
        else:
            logger.info(f"{each_file.name} not moved.")
    else:
        logger.info("No files to be reivewed")

def review_raw_extract():
    _raw_extract_review_queue_dir:Path = base_path / config["review"]["raw_extract_dir"]
    _example_dir:Path = base_path / config["database"]["example_store_dir"]
    review_files(_raw_extract_review_queue_dir, _example_dir)
    return None

def review_newsletter():
    _newsletter_review_dir:Path = base_path / config["review"]["newsletter_dir"]
    _newsletter_complete_dir:Path = base_path / config["output"]["newsletter_dir"]
    review_files(_newsletter_review_dir, _newsletter_complete_dir)
    return None