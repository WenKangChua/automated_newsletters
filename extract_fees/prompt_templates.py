from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from validation import fee_name_list

def fee_names_json_prompt_instructions():

    # Defines json format
    pydantic_parser = PydanticOutputParser(pydantic_object=fee_name_list)
    # Generates the instruction
    format_instructions = pydantic_parser.get_format_instructions()
    format_instruction_prompt = ChatPromptTemplate.from_messages(
        [
        ("system", """
        \nYour role is to extract all relevant acquirer fees to enable further processing by another agent.
        
        \n{format_instructions}

        """
        ),
        ("user", "Context:\n{context}. \n\nQuestion:\n{query}")  
        ]
    ).partial(format_instructions=format_instructions)

    return format_instruction_prompt

def repair_prompt():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
             You are a system that fixes invalid JSON outputs.
             STRICTLY generate ONLY raw JSON, do not include markdown code fences, backticks, or any conversational text.
             """
             ),
            (
            "user","""
            Previous Output:
            {previous_output}

            Error:
            {error}
            """)
        ]
    )
    return prompt

def notification_article_prompt_template(updated_fee_table_markdown:str, context:str):
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
        5. Do not include these information
        - Anything about Technical Resource Center or Pricing Guide

        REQUIRED STRUCTURE:
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
    ).partial(context=context, updated_fee_table_markdown=updated_fee_table_markdown )

    return prompt
