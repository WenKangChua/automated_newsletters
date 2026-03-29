import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # points to app/

from langchain_chroma import Chroma
from pathlib import Path
from utils.config import config, base_path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from pathlib import Path
from datetime import datetime
from domain.retrieval.vector_store import embeddings
from utils.config import config, base_path, datetime_now
import re
from utils.logger import get_logger

_example_store_dir:Path = base_path / config["database"]["example_store_dir"]
_add_example_path:Path = base_path / config["input"]["add_example_dir"]

# Embed and store
embeddings = HuggingFaceEmbeddings(
    model_name = "BAAI/bge-m3",
    model_kwargs={'device': 'mps'}
)

def get_example_store() -> Chroma:
    """
    Return ChromaDB example store used to feed in examples into the model for more consistent responses.
    Collection name = "few_shot_examples_pdf_input"
    """
    return Chroma(
        persist_directory = _example_store_dir,
        embedding_function = embeddings,
        collection_name = "few_shot_examples_pdf_input"
    )

def add_example() -> None:
    """
    To add example(s) from text files in database/example_store/add_example.
    The file must contain a context and a csv code block.
    The context is the result from a vector store similarty search.
    The csv is the response from the SLM as defined in a pydantic class - fee_name.
    """
    vectorstore:Chroma = get_example_store()
    raw_extract_file:list[Path] = [f for f in _add_example_path.iterdir() if f.is_file() and f.suffix in {".txt", ".csv", ".md"}]

    for each in raw_extract_file:
        raw_extract:str = each.read_text(encoding = 'utf-8')        
        raw_extract_csv:str = re.search(r"```csv(.*?)```", raw_extract, re.DOTALL).group(1).strip()
        raw_extract_context = re.search(r"```context(.*?)```", raw_extract, re.DOTALL).group(1).strip()       
        doc = Document(
            page_content = raw_extract_context,
            metadata = {
                "created_datetime": datetime_now,
                "csv_output": raw_extract_csv
                }
        )
        vectorstore.add_documents([doc])

# add_example()
data = get_example_store()
print(data.get())
