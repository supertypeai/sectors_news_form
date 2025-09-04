from datetime import datetime as dt
from supabase import create_client

import streamlit as st
import requests
import uuid 

# data
API_KEY = st.secrets["API_KEY"]

AVAILABLE_SUBSECTORS = [
  "alternative-energy",
  "apparel-luxury-goods",
  "automobiles-components",
  "banks",
  "basic-materials",
  "consumer-services",
  "financing-service",
  "food-beverage",
  "food-staples-retailing",
  "heavy-constructions-civil-engineering",
  "healthcare-equipment-providers",
  "holding-investment-companies",
  "household-goods",
  "industrial-goods",
  "industrial-services",
  "insurance",
  "investment-service",
  "leisure-goods",
  "logistics-deliveries",
  "media-entertainment",
  "multi-sector-holdings",
  "nondurable-household-products",
  "oil-gas-coal",
  "pharmaceuticals-health-care-research",
  "properties-real-estate",
  "retailing",
  "software-it-services",
  "technology-hardware-equipment",
  "telecommunication",
  "tobacco",
  "transportation",
  "transportation-infrastructure",
  "utilities"
]

def post():
    final_uuid = ""
    if st.session_state.uuid:
        final_uuid = st.session_state.uuid
    else:
        manual_uid = st.session_state.get("uuid_field_manual", "")
        final_uuid = manual_uid if manual_uid else None

    required_fields = [
        "source", "date", "time", "doc_number", "company_name",
        "holder_name", "ticker", "purpose",
        "holder_type", "price_transaction"  # "transaction_type"
    ]

    if any(not st.session_state.get(field) for field in required_fields):
        st.toast("Please fill out the required fields.")
    else:
        final_transaction= {"amount_transacted": [], "prices": [], "types": []}
        length_price_transaction = len(st.session_state.price_transaction["amount_transacted"])
        for index in range(length_price_transaction):
            final_transaction["amount_transacted"].append(st.session_state[f"amount_{index}"])
            final_transaction["prices"].append(st.session_state[f"price_{index}"])
            final_transaction['types'].append(st.session_state[f"types_{index}"])

        data = {
            "document_number": st.session_state.doc_number,
            "company_name": st.session_state.company_name,
            "shareholder_name": st.session_state.holder_name,
            "source": st.session_state.source,
            "UID": final_uuid,
            "ticker": st.session_state.ticker,
            "holding_before": st.session_state.holding_before, 
            "share_percentage_before": st.session_state.share_percentage_before,
            "holding_after": st.session_state.holding_after,
            "share_percentage_after": st.session_state.share_percentage_after,
            "sub_sector": st.session_state.subsector,
            "purpose": st.session_state.purpose,
            "holder_type": st.session_state.holder_type,
            # "transaction_type": st.session_state.transaction_type,
            "date_time": dt.combine(st.session_state.date, st.session_state.time).strftime("%Y-%m-%d %H:%M:%S"),
            "price_transaction": final_transaction
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        response = requests.post("https://sectors-news-endpoint.fly.dev/insider-trading", headers = headers, json=data)

        if response.status_code == 200:
            st.toast("Insider Trading submitted successfully! 🎉")
            st.session_state.doc_number = ""
            st.session_state.company_name = ""
            st.session_state.holder_name = ""
            st.session_state.source = ""
            st.session_state.uuid = ""
            st.session_state.ticker = ""
            st.session_state.holding_before = 0
            st.session_state.share_percentage_before = 0
            st.session_state.holding_after = 0
            st.session_state.share_percentage_after = 0
            st.session_state.subsector = AVAILABLE_SUBSECTORS[0]
            st.session_state.purpose = ""
            st.session_state.holder_type="insider"
            st.session_state.date = dt.today()
            st.session_state.time = dt.now()
            st.session_state.transaction_type = "buy" 
            st.session_state.price_transaction = None
        else:   
            # Handle error
            st.write(response.json())
            st.error(f"Error: Something went wrong. Please try again.")

def uuid_on_change():
    if st.session_state.generate_uuid:
        st.session_state.uuid = str(uuid.uuid4())  
    else:
        st.session_state.uuid = ""

def format_option(option):
    return option.replace("-", " ").title()

# app
def main_ui():
    st.title("Sectors News")

    # Initialize session state variables  
    if 'uuid' not in st.session_state:
        st.session_state.generated_uuid = False

    if 'uuid' not in st.session_state:
        st.session_state.uuid = None

    if "price_transaction" not in st.session_state:
        st.session_state.price_transaction = {
            "amount_transacted": [],
            "prices": [], 
            "types": []
        }

    price_transaction = st.session_state.price_transaction

    if "types" not in price_transaction:
        price_transaction["types"] = []
    if "amount_transacted" not in price_transaction:
        price_transaction["amount_transacted"] = []
    if "prices" not in price_transaction:
        price_transaction["prices"] = []

    # Chechbox to generate uid
    checkbox_uuid = st.checkbox("Generate UUID", 
                                key="generate_uuid", 
                                on_change=uuid_on_change)

    # Form for insider trading input
    insider = st.form('insider')

    insider.subheader("Add Insider Trading (Non-IDX Format)")
    insider.caption(":red[*] _required_")
    
    insider.text_input("Source:red[*]", placeholder="Enter URL", key="source")

    if checkbox_uuid:
        insider.text_input("UUID", 
            value=st.session_state.uuid, 
            key="uuid_field",
            disabled=True,
            help="Auto-generated UUID"
        )
    else:
        # Manual entry mode
        insider.text_input("UUID", 
            placeholder="Enter UUID manually", 
            key="uuid_field_manual",
            help="Enter UUID manually"
        )

    # Date form
    insider.date_input(
        "Created Date (GMT+7):red[*]", 
        max_value=dt.today(), 
        format="YYYY-MM-DD",
        key="date"
    )
    
    # Created date form
    insider.time_input(
        "Created Time (GMT+7)*:red[*]", 
        key="time", 
        step=60
    )
    
    # Document number
    insider.text_input(
        "Document Number:red[*]", 
        placeholder="Enter document number", 
        key="doc_number"
    )
    
    # Company name form
    insider.text_input(
        "Company Name:red[*]", 
        placeholder="Enter company name", 
        key="company_name"
    )
    
    # Holder name form
    insider.text_input(
        "Holder Name:red[*]", 
        placeholder="Enter holder name", 
        key="holder_name"
    )
    
    # Ticker form
    insider.text_input(
        "Ticker:red[*]", 
        placeholder="Enter ticker", 
        key="ticker"
    )
    
    # Subsector form
    insider.text_input(
        "Subsector:red[*]", 
        # options = AVAILABLE_SUBSECTORS, 
        # format_func=format_option, 
        # key="subsector"
        placeholder="Filled automatically based on ticker",
        disabled=True,
        key='subsector'
    )

    # Holding before form
    insider.number_input(
        "Stock Holding before Transaction:red[*]", 
        placeholder="Enter stock holding before transaction", 
        key="holding_before", 
        min_value=0
    )
    
    # Holding after form
    insider.number_input(
        "Stock Holding after Transaction:red[*]", 
        placeholder="Enter stock holding after transaction", 
        key="holding_after", min_value=0
    )
    
    # Share percentage before form
    insider.number_input(
        "Stock Ownership Percentage before Transaction:red[*]", 
        placeholder="Enter stock ownership percentage before transaction", 
        key="share_percentage_before", 
        min_value=0.00000, max_value=100.00000, 
        step=0.00001, format="%.5f"
    )
    
    # Share percentage after form
    insider.number_input(
        "Stock Ownership Percentage after Transaction:red[*]", 
        placeholder="Enter stock ownership percentage after transaction", 
        key="share_percentage_after", 
        min_value=0.00000, max_value=100.00000, 
        step=0.00001, format="%.5f"
    )
    
    # Transaction purpose form
    insider.text_input(
        "Transaction Purpose:red[*]", 
        placeholder="Enter transaction purpose", 
        key="purpose"
    )
    
    # Holder type form
    insider.selectbox(
        "Holder Type:red[*]", 
        options = ["insider", "institution"], 
        format_func=format_option, 
        key="holder_type"
    )

    transaction_container = insider.expander("Transactions", expanded=True)

    for idx, (amount, price, type) in enumerate(zip(price_transaction["amount_transacted"], price_transaction["prices"], price_transaction["types"])):
        col1, col2, col3, col4 = transaction_container.columns([2, 2, 2, 2], vertical_alignment="bottom")
        
        price_transaction["amount_transacted"][idx] = col1.number_input(f"Amount Transacted {idx + 1}", value=amount, key=f"amount_{idx}")
        price_transaction["prices"][idx] = col2.number_input(f"Price {idx + 1}", value=price, key=f"price_{idx}")
        price_transaction["types"][idx] = col3.selectbox(f"Type {idx + 1}",
                                                          options=["buy", "sell"], 
                                                          index=0 if type == "buy" else 1, 
                                                          format_func=format_option,
                                                          key=f"types_{idx}")
        
        remove_button = col4.form_submit_button(f"Remove Transaction {idx + 1}")
        if remove_button:
            price_transaction["amount_transacted"].pop(idx)
            price_transaction["prices"].pop(idx)
            price_transaction["types"].pop(idx)
            st.rerun()

    if transaction_container.form_submit_button("Add Transaction"):
        price_transaction["amount_transacted"].append(0)
        price_transaction["prices"].append(0)
        price_transaction["types"].append("buy")
        st.rerun()

    st.session_state.price_transaction = price_transaction

    # Submit button to indert the data
    insider.form_submit_button("Submit", on_click=post)

if __name__ == "__main__":
    main_ui()