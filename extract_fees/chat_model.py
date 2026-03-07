from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
import torch
from transformers import pipeline
from typing import Literal

# Generates a format instruction to produce json result

def format_instruction_prompt():

# Using pydantic BaseModel, define a list of fields and dtype
    class fee_name(BaseModel):
        fee_name:str = Field(description = "The name of the interchange fee or scheme fee")
        new_rate:float | None = Field(description = "The new interchange fee rate or new scheme fee rate. Contains only numbers without %")
        effective_date:str = Field(description = "The effective start date or end date of the fee. STRICTLY in YYYY-MM-DD format.")
        country:str | None = Field(description = "The name of the country or countries affecte. For example, Malaysia, Singapore, etc.")
        change_type: Literal["new_fee", "updated_fee"] = Field(description = "The type of fee change. The only values allowed are new_fee and updated_fee.")

    # Enables a list of fee_name
    class fee_name_list(BaseModel):
        fee_names: List[fee_name]


    # Defines json format
    pydantic_parser = PydanticOutputParser(pydantic_object=fee_name_list)

    format_instructions = pydantic_parser.get_format_instructions()

    # Generates the instruction
    format_instruction_prompt = ChatPromptTemplate.from_messages(
        [
        ("system", """
        \nYou are a data analyst with good knowledge in the payments industry working at Stripe. Your role is to extract all relevant acquirer fees into a json format to enable further processing by another agent.
        
        \n{format_instructions}

        \nSTRICTLY generate ONLY raw JSON, do not include markdown code fences, backticks, or any conversational text.The context given are new fees, eventhough the effective date is set in the past.
        """
        ),
        ("user", "Context:\n{context}. \n\nQuestion:\n{query}")  
        ]
    ).partial(format_instructions=format_instructions)

    return format_instruction_prompt, pydantic_parser


def chat_model(prompt:str, question:str, context:str, pydantic_parser):

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
    chain = prompt | chat_model  | pydantic_parser

    response = chain.invoke({"query": question, "context": context})

    ###
    # In the future might want to use smart chain
    # # Define two chains
    # primary_chain = prompt | llm | parser
    # fallback_chain = retry_prompt | stronger_llm | parser

    # # Combine them
    # smart_chain = primary_chain.with_fallbacks([fallback_chain])

    # try:
    #     result = smart_chain.invoke({"query": "your data query"})
    # except Exception as e:
    #     print("Both primary and fallback failed.")
    ###
    
    response = response.model_dump()

    return response 
