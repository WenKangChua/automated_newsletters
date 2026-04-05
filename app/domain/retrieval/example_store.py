from langchain_chroma import Chroma
from langchain_core.documents import Document
from pathlib import Path
from datetime import datetime
from domain.retrieval.vector_store import embeddings
from utils.config import config, base_path, datetime_now
import re
from utils.logger import get_logger

logger = get_logger(__name__)

_raw_extract_example_store_dir:Path = base_path / config["database"]["store"]["raw_extract_example_store_dir"] # contains raw extract examples
_raw_extract_add_example_path:Path = base_path / config["database"]["store"]["add_example_raw_extract_dir"] # dir to add new raw extract examples in

_newsletter_example_store_dir:Path = base_path / config["database"]["store"]["newsletter_example_store_dir"] # contains newsletter examples
_newsletter_add_example_path:Path = base_path / config["database"]["store"]["add_example_newsletter_dir"] # dir to add new newsletter examples in

def _get_raw_extract_example_store() -> Chroma:
    """
    Return ChromaDB raw extract example store used to feed in examples into the model for more consistent responses.
    """
    return Chroma(
        persist_directory = _raw_extract_example_store_dir,
        embedding_function = embeddings,
        collection_name = "few_shot_examples_raw_extract"
    )

def _get_newsletter_example_store() -> Chroma:
    """
    Return ChromaDB newsletter example store used to feed in examples into the model for more consistent responses.
    """
    return Chroma(
        persist_directory = _newsletter_example_store_dir,
        embedding_function = embeddings,
        collection_name = "few_shot_examples_newsletter"
    )

def add_raw_extract_example() -> None:
    """
    To add raw extract examples to raw extract example store. The file must contain a context and a csv code block.
    """
    vectorstore:Chroma = _get_raw_extract_example_store()
    raw_extract_file:list[Path] = [f for f in _raw_extract_add_example_path.iterdir() if f.is_file() and f.suffix in {".txt", ".csv", ".md"}]

    for each in raw_extract_file:
        raw_extract:str = each.read_text(encoding = 'utf-8')        
        raw_extract_csv:str = re.search(r"```csv(.*?)```", raw_extract, re.DOTALL).group(1).strip()
        raw_extract_context = re.search(r"```context(.*?)```", raw_extract, re.DOTALL).group(1).strip()
        file_name = re.search(r"```bulletin(.*?)```", raw_extract, re.DOTALL).group(1).strip()
        doc = Document(
            page_content = raw_extract_context, #input example
            metadata = {
                "created_datetime": datetime_now,
                "csv_output": raw_extract_csv, #output example
                "file_name": file_name
                }
        )
        vectorstore.add_documents([doc])

def retrieve_raw_extract_examples(query:str, k:int = 1) -> list[dict]:
    """
    Retrieve raw extract examples from example store.
    """
    vectorstore:Chroma = _get_raw_extract_example_store()
    results:list[Document] = vectorstore.similarity_search(query, k = k)
    return [
        {
            "context": r.page_content,
            "csv_output": r.metadata["csv_output"],
            "file_name": r.metadata["file_name"]
        }
        for r in results
    ]

def add_newsletter_example() -> None:
    """
    To add raw extract examples to raw extract example store. The file must contain a context and a csv code block.
    """
    vectorstore:Chroma = _get_newsletter_example_store()
    raw_extract_file:list[Path] = [f for f in _newsletter_add_example_path.iterdir() if f.is_file() and f.suffix in {".txt", ".csv", ".md"}]

    for each in raw_extract_file:
        raw_extract:str = each.read_text(encoding = 'utf-8')
        fee_markdown_table:str = re.search(r"```markdown_table(.*?)```", raw_extract, re.DOTALL).group(1).strip()
        newsletter_context = re.search(r"```newsletter(.*?)```", raw_extract, re.DOTALL).group(1).strip()
        file_name = re.search(r"```file_name(.*?)```", raw_extract, re.DOTALL).group(1).strip()  
        doc = Document(
            page_content = fee_markdown_table, #input example
            metadata = {
                "created_datetime": datetime_now, 
                "newsletter_output": newsletter_context, #output example
                "file_name": file_name
                }
        )
        vectorstore.add_documents([doc])

def retrieve_newsletter_examples(query: str, k: int = 1) -> list[dict]:
    """
    Retrieve newsletter examples from example store.
    """
    vectorstore:Chroma = _get_newsletter_example_store()
    results:list[Document] = vectorstore.similarity_search(query, k = k)
    return [
        {
            "markdown_table": r.page_content,
            "newsletter_output": r.metadata["newsletter_output"],
            "file_name": r.metadata["file_name"]
        }
        for r in results
    ]