import streamlit as st 
from datetime import datetime as dt
from typing import Callable

import streamlit as st
import uuid 
import time

def format_option(option):
    return option.replace("-", " ").title()

def reset_pair_forms():
    """Reset both pair filing forms after successful submission"""
    # Reset shared UUID
    st.session_state.uuid = ""
    
    # Reset both forms
    for form_num in [1, 2]:
        suffix = f"_{form_num}"
        
        # Clear all form fields
        for key in list(st.session_state.keys()):
            if key.endswith(suffix):
                del st.session_state[key]
        
        # Reset price_transaction for each form
        pt_key = f"price_transaction{suffix}"
        st.session_state[pt_key] = {
            "amount_transacted": [],
            "prices": [], 
            "types": [], 
            "dates": []
        }

def main_ui_pair(post: Callable):
    """Show two stacked forms for pair filings"""
    
    # Auto-generate shared UUID
    if 'uuid' not in st.session_state or not st.session_state.uuid:
        st.session_state.uuid = str(uuid.uuid4())

    st.info(f"🔗 Shared UUID: `{st.session_state.uuid}`")
    
    # First form
    with st.container(border=True):
        st.subheader("📄 Filing #1")
        render_single_form(form_number=1)
    
    st.write("---")
    
    # Second form
    with st.container(border=True):
        st.subheader("📄 Filing #2")
        render_single_form(form_number=2)
    
    st.write("---")
    st.warning("⚠️ Make sure both filings above are filled out correctly before submitting!")
    
    # Single submit button for both filings
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if st.button("📤 Submit Both Filings", type="primary", use_container_width=True):
            # Submit filing #1
            success_1 = post(form_number=1)
            # Submit filing #2  
            success_2 = post(form_number=2)
            
            if success_1 and success_2:
                st.success("✅ Both filings submitted successfully!")
                reset_pair_forms()
                time.sleep(3.5)
                st.rerun()


def render_single_form(form_number: int):
    """Render a single form WITHOUT st.form wrapper"""
    
    suffix = f"_{form_number}"
    
    # Initialize price_transaction
    pt_key = f"price_transaction{suffix}"
    if pt_key not in st.session_state or not isinstance(st.session_state[pt_key], dict):
        st.session_state[pt_key] = {
            "amount_transacted": [],
            "prices": [], 
            "types": [], 
            "dates": []
        }

    # NO st.form() wrapper
    st.caption(":red[*] _required_")
    
    # All fields with unique keys - use st.xxx directly instead of insider.xxx
    st.text_input("Source:red[*]", placeholder="Enter URL", key=f"source{suffix}")
    
    st.text_input("UUID", 
        value=st.session_state.uuid, 
        disabled=True,
        key=f"uuid_display{suffix}"  # Add a key even for disabled fields
    )

    st.date_input(
        "Created Date (GMT+7):red[*]", 
        max_value=dt.today(), 
        format="YYYY-MM-DD",
        key=f"date{suffix}"
    )
    
    st.time_input(
        "Created Time (GMT+7):red[*]", 
        key=f"time{suffix}", 
        step=60
    )
    
    st.text_input(
        "Document Number:red[*]", 
        placeholder="Enter document number", 
        key=f"doc_number{suffix}"
    )
    
    st.text_input(
        "Company Name:red[*]", 
        placeholder="Enter company name", 
        key=f"company_name{suffix}"
    )
    
    st.text_input(
        "Holder Name:red[*]", 
        placeholder="Enter holder name", 
        key=f"holder_name{suffix}"
    )
    
    st.text_input(
        "Ticker:red[*]", 
        placeholder="Enter ticker", 
        key=f"ticker{suffix}"
    )
    
    st.text_input(
        "Subsector", 
        placeholder="Filled automatically",
        disabled=True,
        key=f'subsector{suffix}'
    )

    st.number_input(
        "Stock Holding before:red[*]", 
        key=f"holding_before{suffix}", 
        min_value=0
    )
    
    st.number_input(
        "Stock Holding after:red[*]", 
        key=f"holding_after{suffix}", 
        min_value=0
    )
    
    st.number_input(
        "% before:red[*]", 
        key=f"share_percentage_before{suffix}", 
        min_value=0.00000, max_value=100.00000, 
        step=0.00001, format="%.5f"
    )
    
    st.number_input(
        "% after:red[*]", 
        key=f"share_percentage_after{suffix}", 
        min_value=0.00000, max_value=100.00000, 
        step=0.00001, format="%.5f"
    )
    
    st.text_input(
        "Purpose:red[*]", 
        placeholder="Enter transaction purpose", 
        key=f"purpose{suffix}"
    )
    
    st.selectbox(
        "Holder Type:red[*]", 
        options=["insider", "institution"], 
        format_func=format_option, 
        key=f"holder_type{suffix}"
    )

    st.text_input(
        "Tags", 
        placeholder="Optional", 
        key=f"tags{suffix}"
    )

    # Transactions
    transaction_container = st.expander("Transactions", expanded=True)
    price_transaction = st.session_state[pt_key]
    
    for idx in range(len(price_transaction["amount_transacted"])):
        c1, c2, c3, c4, c5 = transaction_container.columns([2, 2, 2, 2, 1])
        
        c1.number_input(
            f"Amount {idx + 1}", 
            value=price_transaction["amount_transacted"][idx], 
            key=f"amount{suffix}_{idx}",
            min_value=0
        )
        c2.number_input(
            f"Price {idx + 1}", 
            value=price_transaction["prices"][idx], 
            key=f"price{suffix}_{idx}",
            min_value=0
        )

        current_type = price_transaction['types'][idx].lower()
        if current_type == "buy":
            type_index = 0
        elif current_type == "sell":
            type_index = 1
        else:  
            type_index = 2

        c3.selectbox(
            f"Type {idx + 1}",
            options=["buy", "sell", 'other'], 
            index=type_index, 
            format_func=format_option,
            key=f"types{suffix}_{idx}"
        )
        c4.date_input(
            f"Date", 
            value=price_transaction["dates"][idx] if price_transaction["dates"][idx] else dt.today(), 
            max_value=dt.today(), 
            format="YYYY-MM-DD", 
            key=f"date{suffix}_{idx}"
        )
        
        if c5.button(f"❌", key=f"remove{suffix}_{idx}"):
            price_transaction["amount_transacted"].pop(idx)
            price_transaction["prices"].pop(idx)
            price_transaction["types"].pop(idx)
            price_transaction["dates"].pop(idx)
            st.rerun()

    if transaction_container.button(f"➕ Add Transaction", key=f"add{suffix}"):
        price_transaction["amount_transacted"].append(0)
        price_transaction["prices"].append(0)
        price_transaction["types"].append("buy")
        price_transaction["dates"].append(dt.today())
        st.rerun()

    st.session_state[pt_key] = price_transaction
