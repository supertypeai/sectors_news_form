import streamlit as st 
from datetime import datetime as dt
from typing import Callable

import streamlit as st
import uuid 

def uuid_on_change():
    if st.session_state.get('standalone_uuid'):
        st.session_state.uuid = str(uuid.uuid4())  
    else:
        st.session_state.uuid = ""

def format_option(option):
    return option.replace("-", " ").title()

# app
def main_ui_single(post: Callable):
    if 'uuid' not in st.session_state:
        st.session_state.uuid = None

    if "price_transaction" not in st.session_state:
        st.session_state.price_transaction = {
            "amount_transacted": [],
            "prices": [], 
            "types": [], 
            "dates": []
        }

    price_transaction = st.session_state.price_transaction

    if "types" not in price_transaction:
        price_transaction["types"] = []
    if "amount_transacted" not in price_transaction:
        price_transaction["amount_transacted"] = []
    if "prices" not in price_transaction:
        price_transaction["prices"] = []
    if "dates" not in price_transaction:
        price_transaction["dates"] = []

    # Chechbox to generate uid
    checkbox_uuid = st.checkbox("Generate UID", 
                                key="standalone_uuid", 
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

    # Tags form Optional
    insider.text_input(
        "Tags", 
        placeholder="Enter tags separated by commas, Optional", 
        key="tags"
    )

    transaction_container = insider.expander("Transactions", expanded=True)

    amount_transacted = price_transaction["amount_transacted"]
    prices = price_transaction["prices"]
    types = price_transaction["types"]
    dates = price_transaction["dates"]

    for idx, (amount, price, type, date) in enumerate(zip(amount_transacted, prices, types, dates)):
        col1, col2, col3, col4, col5 = transaction_container.columns([2, 2, 2, 2, 1], vertical_alignment="bottom")
        
        price_transaction["amount_transacted"][idx] = col1.number_input(
            f"Amount Transacted {idx + 1}", 
            value=amount, 
            key=f"amount_{idx}"
        )
        price_transaction["prices"][idx] = col2.number_input(
            f"Price {idx + 1}", 
            value=price, 
            key=f"price_{idx}"
        )
        price_transaction["types"][idx] = col3.selectbox(
            f"Type {idx + 1}",
            options=["buy", "sell", 'other'], 
            index=0 if type == "buy" else 1, 
            format_func=format_option,
            key=f"types_{idx}"
        )
        price_transaction["dates"][idx] = col4.date_input(
            f"Date {idx + 1}", 
            value=date if date else dt.today(), 
            max_value=dt.today(), 
            format="YYYY-MM-DD", 
            key=f"date_{idx}"
        )
        
        remove_button = col5.form_submit_button(f"❌ {idx + 1}")
        if remove_button:
            price_transaction["amount_transacted"].pop(idx)
            price_transaction["prices"].pop(idx)
            price_transaction["types"].pop(idx)
            st.rerun()

    if transaction_container.form_submit_button("➕ Add Transaction"):
        price_transaction["amount_transacted"].append(0)
        price_transaction["prices"].append(0)
        price_transaction["types"].append("buy")
        price_transaction['dates'].append(dt.today().date())
        st.rerun()

    st.session_state.price_transaction = price_transaction

    # Submit button to indert the data
    insider.form_submit_button("Submit", on_click=post)
