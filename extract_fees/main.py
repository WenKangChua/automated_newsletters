from vector_store import vector_store
from main import format_instruction_prompt, chat_model
import pandas as pd
from datetime import datetime
from pathlib import Path

base_path = Path(__file__).parent.parent
output_file = base_path / "database" / "new_fees_llm_output" / "fee_announcement.csv"

query = "Please extract all relevant acquirer fees that was announced, including the country affected."
input_file_path = "./input/m_an11539_en-us 2025-04-15.pdf"

# From my PDF, get relevant context through similiarity search
context = vector_store(file_path=input_file_path, rag_query=query)

# Format instruction prompt with system user tag to ensure json output
prompt, pydantic_parser = format_instruction_prompt()

# Pass the prompt and context into phi4 chat model from huggingface
response = chat_model(prompt=prompt, question=query, context=context, pydantic_parser=pydantic_parser)

new_fees = pd.DataFrame(response["fee_names"])
datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
new_fees.insert(column="extracted_at", loc=0, value=datetime_now)
new_fees.to_csv(output_file, index=False, mode='a', header=False)

