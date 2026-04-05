from langchain_core.prompts import ChatPromptTemplate
from domain.retrieval.example_store import *
from domain.llm.llm_validation import fee_name
from utils.logger import get_logger

logger = get_logger(__name__)

def _get_fee_csv_format() -> tuple[str, str]:
    """
    Returns (headers, column_description) derived from the fee_name pydantic model.
    """
    model_fields:dict[str, any] = fee_name.model_fields
    headers:str = ",".join(model_fields.keys())
    column_description: str = "\n".join([f"{k}: {v.description}" for k, v in model_fields.items()])
    return headers, column_description

def raw_fee_extract_prompt_template(context:str, query:str) -> ChatPromptTemplate:
    """
    Returns a prompt with instructions to extract the fees from a pdf.
    It includes headers and column description from a pydantic model.
    There is also an option to add in examples to improve model consistency.
    """

    # initalise csv headers and descriptions from pydantic base model
    headers, column_description = _get_fee_csv_format()

    # intialise messages
    messages:list[tuple[str]] = [
        (
        "system",
        """
        Analyse the context given and extract the fees information according to the rules and provide only csv output without conversation text.

        ### Rules:
        1. There can be more than one rows.
        2. Enclose all fields in quotes.
        3. Use only these csv headers - {headers}
        4. Adhere to these field descriptions when extracting fees information - {column_description}
        5. Key words like revised indicates an update rather than new fees.
        """
        )
    ]

    # Retrieve example and append to message
    logger.info("Start retrieving examples")
    examples:list[dict] = retrieve_raw_extract_examples(context)
    for example in examples:
        logger.info(f"Append context example:{example["file_name"]}")
        messages.append(("user", f"Example Context:\n{example["context"]} \n\nExample Question: {query}"))
        messages.append(("assistant", example["csv_output"]))
        logger.info(f"Append output example:{example["csv_output"]}")
    
    messages.append(("user", "Context:\n{context}. \n\nQuestion:\n{query}"))

    # Generates the instruction
    prompt:ChatPromptTemplate = ChatPromptTemplate.from_messages(messages).partial(
        headers = headers,
        column_description = column_description,
        context = context,
        query = query
    )

    return prompt

def repair_prompt_template(context:str, query:str, previous_output:str, error:str) -> ChatPromptTemplate:
    """
    Returns a prompt containing the previous output and python error to fix any invalid output.
    """
    headers, column_description = _get_fee_csv_format()
    prompt:ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Your previous CSV output contains an error. Fix it and return only corrected CSV output with no conversation text.

                ### Rules:
                1. There can be more than one row.
                2. Enclose all fields in quotes.
                3. Use only these csv headers - {headers}
                4. Adhere to these field descriptions - {column_description}
                """
            ),
            ("user", "Context:\n{context}\n\nQuestion:\n{query}"),
            ("assistant","{previous_output}"),
            ("user","This error was raised:\n{error}\n\nnReturn the corrected CSV only")
        ]
    ).partial(
        headers = headers, 
        column_description = column_description,
        context = context,
        query = query,
        previous_output = previous_output,
        error = error
        )
    return prompt

def newsletter_prompt_template(updated_fee_table_markdown:str) -> ChatPromptTemplate:
    """
    Returns a prompt with a set of instruction to generate the article style fee announcement.
    """
    # intialise messages
    messages:list[tuple[str]] = [
        (
        "system",
        """
        Your task is to write an article-style fee change notification for merchants.

        ### RULES:
        1. FEE TABLE: Reproduce the "Fee Table" exactly as provided. Do not add, remove, or change any rows or values.
        2. NARRATIVE: Derive the effective date, country, and region from the "Fee Table" data only.
        3. TONE: Professional and corporate, suitable for an official merchant notification.

        ### REQUIRED STRUCTURE:
        1. Headline: A clear, professional title.
        2. BODY:
            - Always start the paragraph with effective date, the region or country, and the business purpose. Keep it to one short paragraph.
            - A clean Markdown table with columns | Country | Effective Date | Fee Name | Current Rate | New Rate
        3. Ending: A brief closing mentioning that if there are any other questions, please contact us.
        """
        )
    ]

    # Retrieve example and append to message
    logger.info("Start retrieving examples")
    examples:list[dict] = retrieve_newsletter_examples(updated_fee_table_markdown)
    for example in examples:
        logger.info(f"Append markdown table example:{example["file_name"]}")
        messages.append(("user", f"Example markdown table:\n{example["markdown_table"]}"))
        messages.append(("assistant", example["newsletter_output"]))
        logger.info(f"Append output example:{example["newsletter_output"]}")

    messages.append(("user", f"Markdown Table: {updated_fee_table_markdown}"))

    prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(messages).partial(
        updated_fee_table_markdown = updated_fee_table_markdown
        )

    return prompt
