# app/entrypoints/cli.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # points to app/

from pipeline.pipeline import (
    run_full_pipeline,
    run_extraction,
    run_review_raw_extract,
    run_generate,
    run_review_newsletter,
    run_save_examples,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Single source of truth
MENU_ITEMS = [
    ("1", "Run full pipeline", run_full_pipeline),
    ("2", "Extract fees from PDF", run_extraction),
    ("3", "Review raw extract", run_review_raw_extract),
    ("4", "Generate newsletter", run_generate),
    ("5", "Review newsletter", run_review_newsletter),
    ("6", "Save examples to store", run_save_examples),
    ("0", "Exit", exit),
]

# Generate MENU
MENU = "\n".join(
    ["========================================",
     "  Automated Newsletters - Pipeline CLI",
     "========================================"]
    + [f"  {key}. {label}" for key, label, _ in MENU_ITEMS]
    + ["========================================"]
)

# Generate ACTIONS
ACTIONS = {key: (label, action) for key, label, action in MENU_ITEMS}

def main():
    while True:
        print(MENU)
        choice = input("Select an option: ").strip()

        if choice == "0":
            logger.info("Exiting CLI.")
            break
        elif choice in ACTIONS:
            label, fn = ACTIONS[choice]
            logger.info(f"Running: {label}")
            fn()
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()