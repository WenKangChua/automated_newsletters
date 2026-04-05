from pathlib import Path
from utils.config import config, base_path
from utils.logger import get_logger
from utils.system_commands import open_file

logger = get_logger(__name__)

def review_files(source_dir:Path, target_dir:Path) -> None:
    """
    Prompt user to review the files in source directory. The file will be moved to target directory once approved.
    """
    source_files:list[Path] = [f for f in source_dir.iterdir() if f.is_file() and f.suffix in {".txt",".md",".csv"}]
    if source_files:
        output_file_names:str = "\n".join(f.name for f in source_files)
        logger.warning(f"Please review these output before continuing:\n{output_file_names}")
    
        for each_file in source_files:
            open_file(each_file)
            answer:str = input(f"Approved {each_file.name}? (Y/N) ")
        
            if answer.lower().strip() == "y":
                old_path:Path = source_dir / each_file.name
                new_path:Path = target_dir / each_file.name
                logger.info(f"Moving file from '{Path(*old_path.parts[-3:])}' -> '{Path(*new_path.parts[-3:])}'")
                old_path.rename(new_path)
            else:
                logger.info(f"{each_file.name} not moved.")

    else:
        logger.info("No files to be reivewed")

def review_raw_extract():
    """
    Prompt user to review raw extract and drop into raw extract add example dir when approved.
    """
    _raw_extract_review_queue_dir:Path = base_path / config["queues"]["review"]["raw_extract_dir"]
    _example_dir:Path = base_path / config["queues"]["output"]["raw_extract_dir"]
    review_files(_raw_extract_review_queue_dir, _example_dir)
    return None

def review_newsletter():
    """
    Prompt user to review raw extract and drop into newsletter add example dir when approved.
    """
    _newsletter_review_dir:Path = base_path / config["queues"]["review"]["newsletter_dir"]
    _newsletter_complete_dir:Path = base_path / config["queues"]["output"]["newsletter_dir"]
    review_files(_newsletter_review_dir, _newsletter_complete_dir)
    return None

def save_raw_extract_example():
    raw_extract_add_example_dir:Path = base_path / config["database"]["store"]["add_example_raw_extract_dir"]
    raw_extract_complete_dir:Path = base_path / config["queues"]["output"]["raw_extract_dir"]
    
    source_files:list[Path] = [f for f in raw_extract_complete_dir.iterdir() if f.is_file() and f.suffix in {".txt",".md",".csv"}]
    if source_files:
        output_file_names:str = "\n".join(f.name for f in source_files)
        logger.warning(f"Moving raw extracts into example store:\n{output_file_names}")
    
        for each in source_files:
            each.rename(raw_extract_add_example_dir / each.name)
            logger.info(f"Moved {each.name} from '{Path(*raw_extract_complete_dir.parts[-3:])}' -> '{Path(*raw_extract_add_example_dir.parts[-4:])}'")
    else:
        logger.info(f"No files to moved in {Path(*raw_extract_complete_dir.parts[-3:])}")
    return None

def save_newsletter_example():
    newsletter_add_example_dir:Path = base_path / config["database"]["store"]["add_example_newsletter_dir"]
    newsletter_complete_dir:Path = base_path / config["queues"]["output"]["newsletter_dir"]
    
    source_files:list[Path] = [f for f in newsletter_complete_dir.iterdir() if f.is_file() and f.suffix in {".txt",".md",".csv"}]
    if source_files:
        output_file_names:str = "\n".join(f.name for f in source_files)
        logger.warning(f"Moving newsletter into example store:\n{output_file_names}")
    
        for each in source_files:
            each.rename(newsletter_add_example_dir / each.name)
            logger.info(f"Moved {each.name} from '{Path(*newsletter_complete_dir.parts[-3:])}' -> '{Path(*newsletter_add_example_dir.parts[-4:])}'")
    else:
        logger.info(f"No files to moved in {Path(*newsletter_complete_dir.parts[-3:])}")
    return None