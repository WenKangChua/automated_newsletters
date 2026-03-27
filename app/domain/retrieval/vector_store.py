from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.utils.logger import get_logger

logger = get_logger(__name__)

# This file is used for embedding a pdf file, running similarity search and returning the result

# Embed and store
embeddings = HuggingFaceEmbeddings(
    model_name = "BAAI/bge-m3",
    model_kwargs={'device': 'mps'}
)

def build_vector_store(file:str, embeddings = embeddings) -> Chroma:
    """
    Build a vector store using PDF as an input.
    """
    # Load and split
    loader = PyPDFLoader(file)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
        strip_whitespace = True
        )
    chunks = splitter.split_documents(docs)
    return Chroma.from_documents(chunks, embedding = embeddings)


def query_vector_store(vectorstore, rag_query:str, k:int = 3) -> str:
    """
    Does a similiarty search on the vectore store. Returning top K results.
    """
    results = vectorstore.similarity_search(rag_query, k = k)
    context = "\n".join([r.page_content for r in results])
    logger.info("\nRAG Context:\n" + str(context))
    return context
