from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
import torch
from transformers import pipeline
from functools import lru_cache
from langchain_core.prompts import ChatPromptTemplate
from config import config

# model_id = "microsoft/Phi-4-mini-instruct"
model_id = "mistralai/Ministral-3-3B-Instruct-2512"

@lru_cache(maxsize=1)
def _load_chat_model():
  
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

    return chat_model

def mini_instruct_model(prompt:ChatPromptTemplate, **kwargs):
    # loads chat_model for the first time
    chat_model = _load_chat_model()  # Cached — only loads on first call
    
    # Create and Invoke the Chain
    chain = prompt | chat_model

    response = chain.invoke(kwargs or {})

    return response.content
