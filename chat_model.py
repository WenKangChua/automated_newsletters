from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
import torch
from transformers import pipeline
from output_notification.fee_info import updated_fee_markdown
from extract_fees.vector_store import vector_store
 
file_path = "/Users/wenkangchua/Documents/GitHub/customer_notification_generator/extract_fees/input/m_an11539_en-us 2025-04-15.pdf"
question = "Give me details on what had change and the retional behind it."
context = vector_store(file_path=file_path, rag_query=question)

# Generates the instruction
prompt = ChatPromptTemplate.from_messages(
    [
    ("system", 
    """
    You are a professional financial communications expert from stripe. Your task is to write a detailed, article-style announcement you have received regarding fee changes.

    LOGICAL RULES FOR THE ARTICLE:
    1. NARRATIVE SOURCE: Use the "Context" extracted from the PDF to explain the business rationale.
    2. ACTION IDENTIFIER: 
    - If `fee_change` is "updated_fee", describe it as a REVISION of an existing fee.
    - If `fee_change` is "new_fee", describe it as the INTRODUCTION of a new fee.
    3. DATA HANDLING:
    - For REVISIONS, include both the Current Rate and New Rate.
    - For INTRODUCTIONS, list the Current Rate as "N/A" or "-" and state that this is a new billing event.
    4. TONE: Maintain a professional, corporate tone suitable for an official customer notification.

    REQUIRED STRUCTURE:
    1. Headline: A clear, professional title.
    2. BODY:
        - 1-2 paragraphs summarizing the effective date, the region, and the business purpose.
        - A clean Markdown table with columns | Fee Name | Current Rate | New Rate |. DO NOT include fee_change column.
        - A brief closing mentioning that if there are any other questions, please contact us.
    """
    ),
    ("user", 
     """
    ###Context:
    {context}
    ###Fee Table:
    {updated_fee_markdown}
     """
     )  
    ]
)

# Initialize the local Transformers Pipeline
model_id = "microsoft/Phi-4-mini-instruct"

pipe = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={
        "dtype": torch.bfloat16, 
        "device_map": "mps"
    },
    max_new_tokens=1024,
    do_sample=False,
    return_full_text=False
)

# Wrap it in LangChain's HuggingFacePipeline
llm = HuggingFacePipeline(pipeline=pipe)

# Use ChatHuggingFace to handle the <|system|> and <|user|> tags automatically
chat_model = ChatHuggingFace(llm=llm)

# Create and Invoke the Chain
chain = prompt | chat_model

response = chain.invoke({"updated_fee_markdown": updated_fee_markdown, "context": context})

response = response.content

with open("./results.md", "w", encoding="utf-8") as f:
    f.write(response)
