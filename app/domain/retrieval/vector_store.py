from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from utils.logger import get_logger

logger = get_logger(__name__)

# This file is used for embedding a pdf file, running similarity search and returning the result

# Embed and store
embeddings = HuggingFaceEmbeddings(
    model_name = "BAAI/bge-m3",
    model_kwargs={'device': 'mps'}
)

_collection_name = "pdf_temp_store"

def build_vector_store(pdf_file:str, max_page:str = 5) -> Chroma:
    """
    Build a vector store only using PDF as an input.
    Documents more than 5 pages will not be chunked.
    """
    # Load and split
    loader = PyPDFLoader(pdf_file)
    docs = loader.load()
    pages = len(docs)
    if pages > max_page:
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 100,
            strip_whitespace = True
            )
        chunks = splitter.split_documents(docs)
        logger.info(f"Chunking documents. {pages} => {max_page}")
        return Chroma.from_documents(chunks, embedding = embeddings, collection_name = _collection_name) 
    else:
        logger.info(f"Skip chunking documents. {pages} <= {max_page}")
        return Chroma.from_documents(docs, embedding = embeddings, collection_name = _collection_name)

def query_vector_store(vectorstore:Chroma, rag_query:str, k:int = 3) -> str:
    """
    Does a similiarty search on the vectore store. Returning top K results.
    """
    results = vectorstore.similarity_search(rag_query, k = k)
    results.sort(key = lambda d: d.metadata["page"])
    context = "\n".join([r.page_content for r in results])
    return context

def reset_vector_store() -> None:
    """
    To clear pdf_temp_store cache data
    """
# "Get" the store by referencing the same collection name
    vector_store = Chroma(
        collection_name = _collection_name,
        embedding_function = embeddings
    )
    
    # Delete it
    logger.info(f"Resetting collection: {_collection_name}")
    vector_store.delete_collection()

    return None


"""Document Object Sample:
[
    Document(
        metadata={
            "producer": "ReportLab PDF Library - (opensource)",
            "creator": "(unspecified)",
            "creationdate": "2026-03-30T13:32:11+00:00",
            "author": "(anonymous)",
            "keywords": "",
            "moddate": "2026-03-30T13:32:11+00:00",
            "subject": "(unspecified)",
            "title": "(anonymous)",
            "trapped": "/False",
            "source": "/Users/wenkangchua/Documents/GitHub/automated_newsletters/app/infrastructure/queues/pending_process/mock_gri_bulletin_2.pdf",
            "total_pages": 2,
            "page": 0,
            "page_label": "1",
        },
        page_content="GRI-2025-SG-001 General Rate Increase for Parcel Delivery\n Services in Singapore\nType:\nBulletin Announcement\nPublished:\n1 March 2025\nCategory:\nPricing / Fees\nEffective:\n1 June 2025\nAudience:\nShipper / Merchant / Processor\nFirst Billing:\n9 June 2025\nRegion:\nAsia / Pacific\nBrand:\nSwiftFreight\nCountry:\nSingapore\nAction:\nFinancial\nExecutive Overview\nSwiftFreight is revising surcharge rates across its full parcel delivery service portfolio in Singapore, effective 1 June\n2025. This General Rate Increase (GRI) covers destination delivery charges, origin handling charges, and specialised\ncargo surcharges, reflecting rising operational, fuel, and compliance costs across the delivery network.\nEffective Date Details\nDate\nDetails\n1 June 2025\nRevised pricing becomes effective\n9 June 2025\nFirst billing date under new rates\nWhat SwiftFreight is Doing\nSwiftFreight is revising surcharge rates across three charge categories: destination charges applied at the point of\ndelivery, origin charges applied at the point of dispatch, and specialised cargo surcharges for shipments requiring\nadditional handling. All revised rates apply to weekly billing cycles commencing 9 June 2025. Refer to the Billing and\nPricing Information section below for the full rate tables.\nVersion History\nDate\nDescription of Change\n1 March 2025\nInitial publication date\nBilling and Pricing Information\nSwiftFreight will revise the fees in the Billing and Pricing tables below effective 1 June 2025, with the first billing\noccurring on 9 June 2025. All rates are expressed as a percentage of the shipment value unless otherwise stated.\nSection 1: Destination Charges\nDestination charges apply at the point of delivery in Singapore. These surcharges cover last-mile delivery costs\nincluding fuel and remote area access, and are passed through to merchants and shippers.\nWeekly Destination Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-001\nStandard Ground Delivery Surcharge\nSG-GND\n2.75",
    ),
    Document(
        metadata={
            "producer": "ReportLab PDF Library - (opensource)",
            "creator": "(unspecified)",
            "creationdate": "2026-03-30T13:32:11+00:00",
            "author": "(anonymous)",
            "keywords": "",
            "moddate": "2026-03-30T13:32:11+00:00",
            "subject": "(unspecified)",
            "title": "(anonymous)",
            "trapped": "/False",
            "source": "/Users/wenkangchua/Documents/GitHub/automated_newsletters/app/infrastructure/queues/pending_process/mock_gri_bulletin_2.pdf",
            "total_pages": 2,
            "page": 1,
            "page_label": "2",
        },
        page_content="GRI-SG-002\nRemote Area Delivery Surcharge\nSG-REM\n3.10\nSection 2: Origin Charges\nOrigin charges apply at the point of dispatch and cover export documentation and origin port handling. These charges\nare borne at the origin country prior to SwiftFreight's involvement in the delivery journey.\nWeekly Origin Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-010\nOrigin Port Handling Fee\nSG-OPH\n1.20\nGRI-SG-011\nExport Documentation Fee\nSG-EXP\n0.65\nSection 3: Specialised Cargo Surcharges\nSpecialised cargo surcharges apply to shipments requiring additional handling outside of SwiftFreight's standard\nparcel service. This includes hazardous materials and refrigerated cold-chain cargo. These surcharges are applied at\nthe carrier's discretion and are subject to cargo classification at the time of booking.\nWeekly Specialised Cargo Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-020\nHazardous Materials Handling Surcharge\nSG-HAZ\n4.50\nGRI-SG-021\nRefrigerated Cold-Chain Surcharge\nSG-COLD\n5.50\n© 2025 SwiftFreight Logistics Pte. Ltd. Proprietary. All rights reserved.\nGRI-2025-SG-001 General Rate Increase for Parcel Delivery Services in Singapore \x7f 1 March 2025",
    ),
]
"""

"""Vector Store Sample - No Chunking
[
    Document(
        id="fb6e172b-d7e9-4e79-9e9c-dc1a4775477c",
        metadata={
            "source": "/Users/wenkangchua/Documents/GitHub/automated_newsletters/app/infrastructure/queues/pending_process/mock_gri_bulletin_2.pdf",
            "author": "(anonymous)",
            "keywords": "",
            "subject": "(unspecified)",
            "creator": "(unspecified)",
            "producer": "ReportLab PDF Library - (opensource)",
            "total_pages": 2,
            "title": "(anonymous)",
            "page": 1,
            "moddate": "2026-03-30T13:32:11+00:00",
            "page_label": "2",
            "trapped": "/False",
            "creationdate": "2026-03-30T13:32:11+00:00",
        },
        page_content="GRI-SG-002\nRemote Area Delivery Surcharge\nSG-REM\n3.10\nSection 2: Origin Charges\nOrigin charges apply at the point of dispatch and cover export documentation and origin port handling. These charges\nare borne at the origin country prior to SwiftFreight's involvement in the delivery journey.\nWeekly Origin Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-010\nOrigin Port Handling Fee\nSG-OPH\n1.20\nGRI-SG-011\nExport Documentation Fee\nSG-EXP\n0.65\nSection 3: Specialised Cargo Surcharges\nSpecialised cargo surcharges apply to shipments requiring additional handling outside of SwiftFreight's standard\nparcel service. This includes hazardous materials and refrigerated cold-chain cargo. These surcharges are applied at\nthe carrier's discretion and are subject to cargo classification at the time of booking.\nWeekly Specialised Cargo Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-020\nHazardous Materials Handling Surcharge\nSG-HAZ\n4.50\nGRI-SG-021\nRefrigerated Cold-Chain Surcharge\nSG-COLD\n5.50\n© 2025 SwiftFreight Logistics Pte. Ltd. Proprietary. All rights reserved.\nGRI-2025-SG-001 General Rate Increase for Parcel Delivery Services in Singapore \x7f 1 March 2025",
    ),
    Document(
        id="87491bb0-8d0a-4b3f-99cc-d53cc67acb9a",
        metadata={
            "author": "(anonymous)",
            "page_label": "1",
            "page": 0,
            "creator": "(unspecified)",
            "creationdate": "2026-03-30T13:32:11+00:00",
            "source": "/Users/wenkangchua/Documents/GitHub/automated_newsletters/app/infrastructure/queues/pending_process/mock_gri_bulletin_2.pdf",
            "moddate": "2026-03-30T13:32:11+00:00",
            "keywords": "",
            "subject": "(unspecified)",
            "producer": "ReportLab PDF Library - (opensource)",
            "total_pages": 2,
            "trapped": "/False",
            "title": "(anonymous)",
        },
        page_content="GRI-2025-SG-001 General Rate Increase for Parcel Delivery\n Services in Singapore\nType:\nBulletin Announcement\nPublished:\n1 March 2025\nCategory:\nPricing / Fees\nEffective:\n1 June 2025\nAudience:\nShipper / Merchant / Processor\nFirst Billing:\n9 June 2025\nRegion:\nAsia / Pacific\nBrand:\nSwiftFreight\nCountry:\nSingapore\nAction:\nFinancial\nExecutive Overview\nSwiftFreight is revising surcharge rates across its full parcel delivery service portfolio in Singapore, effective 1 June\n2025. This General Rate Increase (GRI) covers destination delivery charges, origin handling charges, and specialised\ncargo surcharges, reflecting rising operational, fuel, and compliance costs across the delivery network.\nEffective Date Details\nDate\nDetails\n1 June 2025\nRevised pricing becomes effective\n9 June 2025\nFirst billing date under new rates\nWhat SwiftFreight is Doing\nSwiftFreight is revising surcharge rates across three charge categories: destination charges applied at the point of\ndelivery, origin charges applied at the point of dispatch, and specialised cargo surcharges for shipments requiring\nadditional handling. All revised rates apply to weekly billing cycles commencing 9 June 2025. Refer to the Billing and\nPricing Information section below for the full rate tables.\nVersion History\nDate\nDescription of Change\n1 March 2025\nInitial publication date\nBilling and Pricing Information\nSwiftFreight will revise the fees in the Billing and Pricing tables below effective 1 June 2025, with the first billing\noccurring on 9 June 2025. All rates are expressed as a percentage of the shipment value unless otherwise stated.\nSection 1: Destination Charges\nDestination charges apply at the point of delivery in Singapore. These surcharges cover last-mile delivery costs\nincluding fuel and remote area access, and are passed through to merchants and shippers.\nWeekly Destination Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-001\nStandard Ground Delivery Surcharge\nSG-GND\n2.75",
    ),
]
"""

"""Vector Store Sample - Chunking
[
    Document(
        id="8634ac5f-d5a1-4909-a590-dc1f659db7a0",
        metadata={
            "source": "/Users/wenkangchua/Documents/GitHub/automated_newsletters/app/infrastructure/queues/pending_process/mock_gri_bulletin_2.pdf",
            "total_pages": 2,
            "creator": "(unspecified)",
            "trapped": "/False",
            "page": 1,
            "moddate": "2026-03-30T13:32:11+00:00",
            "subject": "(unspecified)",
            "title": "(anonymous)",
            "page_label": "2",
            "author": "(anonymous)",
            "keywords": "",
            "producer": "ReportLab PDF Library - (opensource)",
            "creationdate": "2026-03-30T13:32:11+00:00",
        },
        page_content="GRI-SG-002\nRemote Area Delivery Surcharge\nSG-REM\n3.10\nSection 2: Origin Charges\nOrigin charges apply at the point of dispatch and cover export documentation and origin port handling. These charges\nare borne at the origin country prior to SwiftFreight's involvement in the delivery journey.\nWeekly Origin Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-010\nOrigin Port Handling Fee\nSG-OPH\n1.20\nGRI-SG-011\nExport Documentation Fee\nSG-EXP\n0.65",
    ),
    Document(
        id="3cc22ff1-3bf7-4f5d-9aca-0096c30da44b",
        metadata={
            "source": "/Users/wenkangchua/Documents/GitHub/automated_newsletters/app/infrastructure/queues/pending_process/mock_gri_bulletin_2.pdf",
            "trapped": "/False",
            "moddate": "2026-03-30T13:32:11+00:00",
            "title": "(anonymous)",
            "creationdate": "2026-03-30T13:32:11+00:00",
            "page_label": "2",
            "producer": "ReportLab PDF Library - (opensource)",
            "keywords": "",
            "subject": "(unspecified)",
            "creator": "(unspecified)",
            "author": "(anonymous)",
            "total_pages": 2,
            "page": 1,
        },
        page_content="GRI-SG-011\nExport Documentation Fee\nSG-EXP\n0.65\nSection 3: Specialised Cargo Surcharges\nSpecialised cargo surcharges apply to shipments requiring additional handling outside of SwiftFreight's standard\nparcel service. This includes hazardous materials and refrigerated cold-chain cargo. These surcharges are applied at\nthe carrier's discretion and are subject to cargo classification at the time of booking.\nWeekly Specialised Cargo Surcharges\nBilling Event No.\nBilling Event Name\nService ID",
    ),
    Document(
        id="58e7f525-0070-428d-91c6-cfd45cde0ce8",
        metadata={
            "page_label": "1",
            "creator": "(unspecified)",
            "title": "(anonymous)",
            "keywords": "",
            "trapped": "/False",
            "page": 0,
            "subject": "(unspecified)",
            "creationdate": "2026-03-30T13:32:11+00:00",
            "moddate": "2026-03-30T13:32:11+00:00",
            "total_pages": 2,
            "source": "/Users/wenkangchua/Documents/GitHub/automated_newsletters/app/infrastructure/queues/pending_process/mock_gri_bulletin_2.pdf",
            "producer": "ReportLab PDF Library - (opensource)",
            "author": "(anonymous)",
        },
        page_content="delivery, origin charges applied at the point of dispatch, and specialised cargo surcharges for shipments requiring\nadditional handling. All revised rates apply to weekly billing cycles commencing 9 June 2025. Refer to the Billing and\nPricing Information section below for the full rate tables.\nVersion History\nDate\nDescription of Change\n1 March 2025\nInitial publication date\nBilling and Pricing Information",
    ),
]
"""