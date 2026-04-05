# app/entrypoints/view_store.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # points to app/

from domain.retrieval.example_store import _get_raw_extract_example_store, add_raw_extract_example
from domain.retrieval.example_store import _get_newsletter_example_store, add_newsletter_example

"""
Run this script to add and view examples into example stores
"""

def run_raw_extract_example():
    _get_raw_extract_example_store().reset_collection()
    add_raw_extract_example()
    store = _get_raw_extract_example_store()
    return print(store.get())

"""Vector Store example - raw extract
{
    "ids": [
        "2de44b3c-eb22-40d0-a93f-23eb66210171",
        "9d79ed85-ea8c-4b0d-81e5-815eabfc861a",
    ],
    "embeddings": None,
    "documents": [
        "GRI-2025-SG-001 General Rate Increase for Domestic\nDelivery Services in Singapore\nType:\nBulletin Announcement\nPublished:\n1 March 2025\nCategory:\nPricing / Fees\nEffective:\n1 June 2025\nAudience:\nShipper / Merchant / Processor\nFirst Billing:\n9 June 2025\nRegion:\nAsia / Pacific\nBrand:\nSwiftFreight\nCountry:\nSingapore\nAction:\nFinancial\nExecutive Overview\nSwiftFreight is revising the delivery surcharge rates for domestic parcel services in Singapore, effective 1 June 2025.\nThis General Rate Increase (GRI) applies to standard ground and express air delivery services to reflect rising\noperational and fuel costs.\nEffective Date Details\nDate\nDetails\n1 June 2025\nRevised pricing becomes effective\n9 June 2025\nFirst billing date under new rates\nWhat SwiftFreight is Doing\nSwiftFreight is revising the surcharge rates for domestic parcel delivery services in Singapore. This revision reflects\nincreases in operational costs, including last-mile logistics and handling. The revised rates apply to all domestic\nshipments billed weekly. Refer to the Billing and Pricing Information section below for the updated rate table.\nVersion History\nDate\nDescription of Change\n1 March 2025\nInitial publication date\nBilling and Pricing Information\nSwiftFreight will revise the fees in the Billing and Pricing table effective 1 June 2025 and will bill the fees weekly with\nthe first billing occurring on 9 June 2025.\nShipper / Merchant Fees\nWeekly Domestic Parcel Delivery\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-001\nStandard Ground Delivery Surcharge\nSG-GND\n2.75\nGRI-SG-002\nExpress Air Delivery Surcharge\nSG-AIR\n3.30\nGRI-SG-003\nResidential Address Surcharge\nSG-RES\n1.50\n© 2025 SwiftFreight Logistics Pte. Ltd. Proprietary. All rights reserved.\nGRI-2025-SG-001 General Rate Increase for Domestic Delivery Services in Singapore \x7f 1 March 2025",
        "GRI-2025-SG-001 General Rate Increase for Parcel Delivery\nServices in Singapore\nType:\nBulletin Announcement\nPublished:\n1 March 2025\nCategory:\nPricing / Fees\nEffective:\n1 June 2025\nAudience:\nShipper / Merchant / Processor\nFirst Billing:\n9 June 2025\nRegion:\nAsia / Pacific\nBrand:\nSwiftFreight\nCountry:\nSingapore\nAction:\nFinancial\nExecutive Overview\nSwiftFreight is revising surcharge rates across its full parcel delivery service portfolio in Singapore, effective 1 June\n2025. This General Rate Increase (GRI) covers destination delivery charges, origin handling charges, and specialised\ncargo surcharges, reflecting rising operational, fuel, and compliance costs across the delivery network.\nEffective Date Details\nDate\nDetails\n1 June 2025\nRevised pricing becomes effective\n9 June 2025\nFirst billing date under new rates\nWhat SwiftFreight is Doing\nSwiftFreight is revising surcharge rates across three charge categories: destination charges applied at the point of\ndelivery, origin charges applied at the point of dispatch, and specialised cargo surcharges for shipments requiring\nadditional handling. All revised rates apply to weekly billing cycles commencing 9 June 2025. Refer to the Billing and\nPricing Information section below for the full rate tables.\nVersion History\nDate\nDescription of Change\n1 March 2025\nInitial publication date\nBilling and Pricing Information\nSwiftFreight will revise the fees in the Billing and Pricing tables below effective 1 June 2025, with the first billing\noccurring on 9 June 2025. All rates are expressed as a percentage of the shipment value unless otherwise stated.\nSection 1: Destination Charges\nDestination charges apply at the point of delivery in Singapore. These surcharges cover last-mile delivery costs\nincluding fuel and remote area access, and are passed through to merchants and shippers.\nWeekly Destination Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-001\nStandard Ground Delivery Surcharge\nSG-GND\n2.75\nGRI-SG-002\nRemote Area Delivery Surcharge\nSG-REM\n3.10\nSection 2: Origin Charges\nOrigin charges apply at the point of dispatch and cover export documentation and origin port handling. These charges\nare borne at the origin country prior to SwiftFreight's involvement in the delivery journey.\nWeekly Origin Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-010\nOrigin Port Handling Fee\nSG-OPH\n1.20\nGRI-SG-011\nExport Documentation Fee\nSG-EXP\n0.65\nSection 3: Specialised Cargo Surcharges\nSpecialised cargo surcharges apply to shipments requiring additional handling outside of SwiftFreight's standard\nparcel service. This includes hazardous materials and refrigerated cold-chain cargo. These surcharges are applied at\nthe carrier's discretion and are subject to cargo classification at the time of booking.\nWeekly Specialised Cargo Surcharges\nBilling Event No.\nBilling Event Name\nService ID\nNew Rate (%)\nGRI-SG-020\nHazardous Materials Handling Surcharge\nSG-HAZ\n4.50\nGRI-SG-021\nRefrigerated Cold-Chain Surcharge\nSG-COLD\n5.50\n© 2025 SwiftFreight Logistics Pte. Ltd. Proprietary. All rights reserved.\nGRI-2025-SG-001 General Rate Increase for Parcel Delivery Services in Singapore \x7f 1 March 2025",
    ],
    "uris": None,
    "included": ["metadatas", "documents"],
    "data": None,
    "metadatas": [
        {
            "file_name": "mock_gri_bulletin_1.pdf",
            "csv_output": '"billing_id","service_id","fee_name","new_rate","effective_date","country","currency","change_type","charge_category"\n"GRI-SG-001","SG-GND","Standard Ground Delivery Surcharge","2.75","2025-06-01","Singapore","SGD","revised_fee","destination"\n"GRI-SG-002","SG-AIR","Express Air Delivery Surcharge","3.30","2025-06-01","Singapore","SGD","revised_fee","destination"\n"GRI-SG-003","SG-RES","Residential Address Surcharge","1.50","2025-06-01","Singapore","SGD","revised_fee","destination"',
            "created_datetime": "2026-04-03 12:04:11",
        },
        {
            "created_datetime": "2026-04-03 12:04:11",
            "csv_output": '"billing_id","service_id","fee_name","new_rate","effective_date","country","currency","change_type","charge_category"\n"GRI-SG-001","SG-GND","Standard Ground Delivery Surcharge","2.75","2025-06-01","Singapore","SGD","revised_fee","destination"\n"GRI-SG-002","SG-REM","Remote Area Delivery Surcharge","3.10","2025-06-01","Singapore","SGD","revised_fee","destination"',
            "file_name": "mock_gri_bulletin_2_example_store.pdf",
        },
    ],
}
"""

def run_newsletter_example():
    _get_newsletter_example_store().reset_collection()
    add_newsletter_example()
    store = _get_newsletter_example_store()
    return print(store.get())

"""Vector Store example - newsletter
error: cannot format : Cannot parse: 1:47: 'ids': ['b3431e1d-b072-4ef9-8ede-58e4eb1bcec1'], 'embeddings': None, 'documents': ['| Country  | Effective Date | Fee Name                       | Current Rate | New Rate | Change      |\n|:---------|:---------------|:-------------------------------|-------------:|---------:|:------------|\n| Singapore| 2025-06-01     | Ground Delivery Surcharge      | 2.6          | 2.75     | Updated Fee |\n| Singapore| 2025-06-01     | Remote Area Delivery Surcharge | 3.0          | 3.1      | Updated Fee |'], 'uris': None, 'included': ['metadatas', 'documents'], 'data': None, 'metadatas': [{'created_datetime': '2026-04-05 20:41:44', 'newsletter_output': '# SwiftFreight Announces Revised Delivery Surcharges in Singapore\n\nEffective 1 June 2025, SwiftFreight will be revising its delivery surcharge rates in Singapore. This adjustment reflects rising operational and fuel costs across our delivery network.\n\n| Country  | Effective Date | Fee Name                       | Current Rate | New Rate | Change      |\n|:---------|:---------------|:-------------------------------|-------------:|---------:|:------------|\n| Singapore| 2025-06-01     | Ground Delivery Surcharge      | 2.6          | 2.75     | Updated Fee |\n| Singapore| 2025-06-01     | Remote Area Delivery Surcharge | 3.0          | 3.1      | Updated Fee |\n\nAll applicable fees and surcharges will be passed through accordingly. \nShould you have any questions regarding these rate adjustments, please feel free to reach out to your Account Manager or contact the LastMile Support team', 'file_name': 'mock_gri_bulletin_2.pdf'}]}
"""

if __name__ == "__main__":
    run_newsletter_example()
    # run_raw_extract_example()