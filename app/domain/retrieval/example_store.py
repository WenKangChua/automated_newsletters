from langchain_chroma import Chroma
from langchain_core.documents import Document
from pathlib import Path
from datetime import datetime
from vector_store import embeddings
from utils.config import config
import re
from utils.logger import get_logger

logger = get_logger(__name__)
base_path:Path = Path(__file__).parent.parent
datetime_now:str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
example_store_path:Path = base_path / config["database"]["example_store_path"]
add_example_path:Path = base_path / config["input"]["add_example_path"]

def get_example_store() -> Chroma:
    """
    Return ChromaDB example store used to feed in examples into the model for more consistent responses.
    Collection name = "few_shot_examples_pdf_input"
    """
    return Chroma(
        persist_directory = example_store_path,
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
    raw_extract_path:list[Path] = [f for f in add_example_path.iterdir() if f.is_file() and f.suffix in {".txt", ".csv", ".md"}]
    for each in raw_extract_path:
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

def retrieve_examples(query: str, k: int = 1) -> list[dict]:
    """
    Retrieve examples from the example_store. Using query for similarity search.
    Primarily used in prompt template to enable more concise responses.
    """
    vectorstore:Chroma = get_example_store()
    results:list[Document] = vectorstore.similarity_search(query, k = k)
    return [
        {
            "context": r.page_content,
            "csv_output": r.metadata["csv_output"]
        }
        for r in results
    ]

if __name__ == "__main__":
    """
    One time to reset or build input/output examples for fee json extraction.
    """ 
    # input_file_path = config["input"]["input_pdf_path"]
    
    data = get_example_store()
    data.reset_collection()
    add_example()
    # print(data.get())
    
    # data = get_example_store()

    # loader = PyPDFLoader(input_file_path)
    # docs = loader.load()
    
    # splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=500,
    #     chunk_overlap=50,
    #     strip_whitespace=True
    # )

    rag_query = "Please find all relevant acquirer fees, rates, country, effective date, currency."
    result = retrieve_examples(rag_query, k = 2)
    logger.info(f"Results:\n {result}")

    # sample_output = """
    # "fee_name","new_rate","effective_date","region","currency","change_type"
    # "Digital Assurance Acquirer Fee – Non-Tokenized (Debit)","0.04","2025-10-13","Australia","AUD","updated_fee"
    # "Digital Assurance Acquirer Fee – Non-Tokenized (Credit)","0.04","2025-10-13","Australia","AUD","updated_fee"
    # """
    # chunks = splitter.split_documents(docs)
    # temp_vector_store = Chroma.from_documents(chunks, embedding = embeddings)
    # temp_document = temp_vector_store.similarity_search(rag_query, k = 3)
    # context = "\n".join([r.page_content for r in temp_document]) # from a list of documents, join page_content into a single list
    # add_example(context, sample_output)

    # print(data.get())
    # print(data._collection.name)

    
    




    
