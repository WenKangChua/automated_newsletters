from pydantic import BaseModel, Field
from typing import List
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
import torch
from transformers import pipeline

def mini_instruct_model(system_prompt:str, query:str):

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
    chain = system_prompt | chat_model
    response = chain.invoke({"query": query})
    
    return response


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

