from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
import torch
from transformers import pipeline
from functools import lru_cache
from langchain_core.prompts import ChatPromptTemplate
from app.utils.config import config

model_id = config["model_id"]["phi4"]

@lru_cache(maxsize=1)
def _load_chat_model(max_new_tokens:int = 1024, do_sample:bool = False, return_full_text:bool = False) -> ChatHuggingFace:
    """
    Loads the chat model from huggingface through langchain.
    Returns a chat model which can be invoked.
    """
    pipe = pipeline(
        "text-generation",
        model = model_id,
        model_kwargs = {
            "dtype": torch.bfloat16,
            "device_map": "mps"
        },
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        return_full_text=return_full_text
    )
    # Wrap it in LangChain's HuggingFacePipeline
    llm = HuggingFacePipeline(pipeline = pipe)

    # Use ChatHuggingFace to handle the <|system|> and <|user|> tags automatically
    chat_model = ChatHuggingFace(llm = llm)

    return chat_model

def run_mini_instruct_model(prompt:ChatPromptTemplate, **kwargs:dict[any]) -> str:
    """
    Invoke the chat model with a prompt. kwargs used populate variables in prompt.
    Returns the content of the response.
    """
    # loads chat_model for the first time
    chat_model = _load_chat_model()  # Cached — only loads on first call
    
    # Create and Invoke the Chain
    chain = prompt | chat_model
    response = chain.invoke(kwargs or {})

    return response.content
