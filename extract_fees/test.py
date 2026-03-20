import textwrap
import re

csv_output = """
"fee_name","new_rate","effective_date","region","currency","change_type"
"Digital Assurance Acquirer Fee – Non-Tokenized (Debit)","0.04","2025-10-13","Australia","AUD","updated_fee"
"Digital Assurance Acquirer Fee – Non-Tokenized (Credit)","0.04","2025-10-13","Australia","AUD","updated_fee"
    """

review_content = f"""Review Section, do not edit anything outside the csv block.
```csv
    {csv_output}
    
```
some_text
"""

# # print(review_content)
csv_output = ("\n".join(line.strip() for line in review_content.strip().splitlines()))
# csv_match = re.search(r"```csv\s*(.*?)```", csv_output, re.DOTALL)
# print(csv_output)

csv_match = re.search(r"```csv(.*?)```", csv_output, re.DOTALL).group(1).strip()
print(csv_match.group(1).strip())
