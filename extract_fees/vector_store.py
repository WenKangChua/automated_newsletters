from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# This file is used for embedding a pdf file, running similarity search and returning the result

def vector_store(file_path:str=None, rag_query:str=None):

    if file_path is None:
        raise ValueError("Please include a valid file path")
        exit()
    if rag_query is None:
        raise ValueError("Please input a valid query for similiarty search")
        exit()

    # Load and split
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        strip_whitespace=True
        )
    chunks = splitter.split_documents(docs)

    # Embed and store
    embeddings = HuggingFaceEmbeddings(
        model = "jinaai/jina-embeddings-v5-text-small-retrieval",
        model_kwargs = {'device': 'mps'} #set mps for macbook M chip
    )

    vectorstore = Chroma(embedding_function = embeddings, collection_name="pdf_input")
    vectorstore = vectorstore.from_documents(chunks)

    results = vectorstore.similarity_search(rag_query, k=3)
    context = "\n".join([r.page_content for r in results])

    return context
