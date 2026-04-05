# app/entrypoints/view_store.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # points to app/

from pipeline.generate import generate_fee_markdown_table
from utils.logger import get_logger 
import pandas as pd
from io import StringIO

logger = get_logger(__name__)

csv = """
"billing_id","service_id","fee_name","new_rate","effective_date","country","currency","change_type","charge_category"
"GRI-SG-001","SG-GND","Standard Ground Delivery Surcharge","2.75","2025-06-01","Singapore","SGD","updated_fee","destination"
"GRI-SG-002","SG-REM","Remote Area Delivery Surcharge","3.10","2025-06-01","Singapore","SGD","updated_fee","destination"
"GRI-SG-010","SG-OPH","Origin Port Handling Fee","1.20","2025-06-01","Singapore","SGD","updated_fee","origin"
"GRI-SG-011","SG-EXP","Export Documentation Fee","0.65","2025-06-01","Singapore","SGD","updated_fee","origin"
"GRI-SG-020","SG-HAZ","Hazardous Materials Handling Surcharge","4.50","2025-06-01","Singapore","SGD","updated_fee","specialised"
"GRI-SG-021","SG-COLD","Refrigerated Cold-Chain Surcharge","5.50","2025-06-01","Singapore","SGD","updated_fee","specialised"
"""



_fee_table_markdown = generate_fee_markdown_table(csv)
print(_fee_table_markdown)
