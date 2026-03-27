from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.domain.retrieval.example_store import retrieve_examples
from app.domain.llm.llm_validation import fee_name
from app.utils.logger import get_logger

logger = get_logger(__name__)

def raw_fee_extract_prompt_template(example_query:str = None) -> ChatPromptTemplate:
    """
    Returns a prompt with instructions to extract the fees from a pdf.
    It includes headers and column description from a pydantic model.
    There is also an option to add in examples to improve model consistency.
    """

    # initalise csv headers and descriptions from pydantic base model
    model_fields:dict[str, any] = fee_name.model_fields
    headers:str = ",".join(model_fields.keys())
    column_description:str = "\n".join([f"{k}: {v.description}" for k,v in model_fields.items()])

    # intialise messages
    messages:list[str] = [
        (
        "system", 
        """
        Analyse the context given and extract the fees information according to the rules and provide only csv output without conversation text.
        
        ### Rules:
        1. There can be more than one rows.\n
        2. Enclose all fields in quotes.\n
        3. Use only these csv headers - {headers}\n
        4. Adhere to these field descriptions when extracting fees information - {column_description}
        """
        )
    ]

    # Retrieve example and append to message
    examples:list[dict] = retrieve_examples(query = example_query)
    for example in examples:
        messages.append(("user", f"Example Context:\n{example["context"]} \n\nExample Question: {example_query}"))
        messages.append(("assistant", example["csv_output"]))

    messages.append(("user", "Context:\n{context}. \n\nQuestion:\n{query}"))

    # Generates the instruction
    prompt:ChatPromptTemplate = ChatPromptTemplate.from_messages(messages).partial(
        headers = headers,
        column_description = column_description
    )

    logger.info("\n" + str(prompt))
    return prompt

def repair_prompt_template() -> ChatPromptTemplate:
    """
    Returns a prompt containing the previous output and python error to fix any invalid output.
    """
    prompt:ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [
            ("system", "Please read the previous output and the error message. Fix the error."),
            ("user", "Context:\n{context}\n\nQuestion:\n{query}"),
            ("assistant","{previous_output}")
            ("user","Please fix this error:\n{error}")
        ]
    )
    return prompt

def notification_article_prompt_template(updated_fee_table_markdown:str, context:str) -> ChatPromptTemplate:
    """
    Returns a prompt with a set of instruction to generate the article style fee announcement.
    """
    prompt:ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [
        ("system", 
        """
        You are a professional financial communications expert. Your task is to write a detailed, article-style announcement you have received regarding fee changes.

        ### LOGICAL RULES FOR THE ARTICLE:
        1. NARRATIVE SOURCE: Use the "Context" extracted from the PDF to explain the business rationale.
        2. ACTION IDENTIFIER: 
        - If `fee_change` is "updated_fee", describe it as a REVISION of an existing fee.
        - If `fee_change` is "new_fee", describe it as the INTRODUCTION of a new fee.
        3. DATA HANDLING:
        - For REVISIONS, include both the Current Rate and New Rate.
        - For INTRODUCTIONS, list the Current Rate as "N/A" or "-" and state that this is a new billing event.
        4. TONE: Maintain a professional, corporate tone suitable for an official customer notification.
        5. DO NOT INCLUDE anything about Technical Resource Center or Pricing Guide.

        ### REQUIRED STRUCTURE:
        1. Headline: A clear, professional title.
        2. BODY:
            - Always start the paragraph with effective date, the region or country, and the business purpose. Keep it to one short paragraph.
            - A clean Markdown table with columns | Country | Effective Date | | Fee Name | Current Rate | New Rate |. DO NOT include fee_change column.
            - A brief closing mentioning that if there are any other questions, please contact us.
        """
        ),
        ("user", 
        """
        ###Context:
        {context}
        ###Fee Table:
        {updated_fee_table_markdown}
        """
        )  
        ]
    ).partial(context = context, updated_fee_table_markdown = updated_fee_table_markdown)

    return prompt
