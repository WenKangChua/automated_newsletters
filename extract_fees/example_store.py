from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from pathlib import Path
from datetime import datetime
import json

from vector_store import *
from config import config
from langchain_community.document_loaders import PyPDFLoader

base_path = Path(__file__).parent.parent
example_store_dir = base_path / "database/chroma_db/example_store"
datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'mps'}
)

def get_example_store():
    return Chroma(
        persist_directory = example_store_dir,
        embedding_function = embeddings,
        collection_name = "few_shot_examples_pdf_input"
    )

def add_example(context: str, csv_output: str):
    vectorstore = get_example_store()
    doc = Document(
        page_content = context,  # embedded for similarity search
        metadata = {
            "created_datetime": datetime_now,
            "csv_output": csv_output
            }
    )
    vectorstore.add_documents([doc])

def retrieve_examples(query: str, k: int = 1) -> list[dict]:
    vectorstore = get_example_store()
    results = vectorstore.similarity_search(query, k = k)
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
    
    input_file_path = config["input"]["input_pdf_path"]
    
    data = get_example_store()
    data.reset_collection()

    loader = PyPDFLoader(input_file_path)
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        strip_whitespace=True
    )

    rag_query = "Please find all relevant acquirer fees, rates, country, effective date, currency."
    sample_output = """
    "fee_name","new_rate","effective_date","region","currency","change_type"
    "Digital Assurance Acquirer Fee – Non-Tokenized (Debit)","0.04","2025-10-13","Australia","AUD","updated_fee"
    "Digital Assurance Acquirer Fee – Non-Tokenized (Credit)","0.04","2025-10-13","Australia","AUD","updated_fee"
    """
    chunks = splitter.split_documents(docs)
    temp_vector_store = Chroma.from_documents(chunks, embedding = embeddings)
    temp_document = temp_vector_store.similarity_search(rag_query, k = 3)
    context = "\n".join([r.page_content for r in temp_document]) # from a list of documents, join page_content into a single list
    add_example(context, sample_output)

    print(data.get())
    print(data._collection.name)

    
    




    
