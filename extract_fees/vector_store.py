from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# This file is used for embedding a pdf file, running similarity search and returning the result

# Embed and store
embeddings = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-mpnet-base-v2",
    model_kwargs = {'device': 'mps'}
)

def vector_store(file_path:str, rag_query:str, embeddings = embeddings):

    # Load and split
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        strip_whitespace=True
        )
    chunks = splitter.split_documents(docs)

    # vectorstore = Chroma(embedding_function = embeddings, collection_name="pdf_input")
    vectorstore = Chroma.from_documents(chunks, embedding = embeddings)

    results = vectorstore.similarity_search(rag_query, k=3)
    context = "\n".join([r.page_content for r in results])

    return context
