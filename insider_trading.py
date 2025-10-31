from datetime import datetime

from insider_non_idx_helper.single_filing_helper import main_ui_single
from insider_non_idx_helper.pair_filing_helper import main_ui_pair
# from insert_trading_function import insert_insider_trading_supabase

import streamlit as st
import requests

# data
API_KEY = st.secrets["API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

def post(form_number: int = None):
    is_pair_filings = form_number is not None
    
    # Add suffix for pair filings
    suffix = f"_{form_number}" if form_number else ""
    
    final_uuid = st.session_state.uuid if st.session_state.uuid else st.session_state.get("uuid_field_manual", "")

    required_fields = [
        "source", "date", "time", "doc_number", "company_name",
        "holder_name", "ticker", "purpose", "holder_type"
    ]

    # Check with suffix
    missing_fields = [field for field in required_fields if not st.session_state.get(field + suffix)]
    
    if missing_fields:
        msg = f"Please fill out required fields (Filing #{form_number if form_number else ''}): " + ", ".join(missing_fields)
        try:
            st.toast(msg)
        except Exception:
            st.warning(msg)
        return False  
    
    # Get price_transaction with suffix
    pt_key = f"price_transaction{suffix}" if suffix else "price_transaction"
    
    if pt_key not in st.session_state or not st.session_state[pt_key]["amount_transacted"]:
        st.toast(f"Please add at least one transaction (Filing #{form_number if form_number else ''})")
        return False  
    
    final_transaction = {"amount_transacted": [], "prices": [], "types": [], 'dates': []}
    length_price_transaction = len(st.session_state[pt_key]["amount_transacted"])
    
    for index in range(length_price_transaction):
        final_transaction["amount_transacted"].append(st.session_state[f"amount{suffix}_{index}"])
        final_transaction["prices"].append(st.session_state[f"price{suffix}_{index}"])
        final_transaction['types'].append(st.session_state[f"types{suffix}_{index}"])
        # final_transaction['dates'].append(st.session_state[f'date{suffix}_{index}'])
        date_value = st.session_state[f'date{suffix}_{index}']
        final_transaction['dates'].append(
                    date_value.strftime("%Y-%m-%d") if hasattr(date_value, 'strftime') else str(date_value)
                )
        
    data = {
        "document_number": st.session_state.get(f"doc_number{suffix}"),
        "company_name": st.session_state.get(f"company_name{suffix}"),
        "shareholder_name": st.session_state.get(f"holder_name{suffix}"),
        "source": st.session_state.get(f"source{suffix}"),
        "UID": final_uuid,
        "ticker": st.session_state.get(f"ticker{suffix}"),
        "holding_before": st.session_state.get(f"holding_before{suffix}"), 
        "share_percentage_before": st.session_state.get(f"share_percentage_before{suffix}"),
        "holding_after": st.session_state.get(f"holding_after{suffix}"),
        "share_percentage_after": st.session_state.get(f"share_percentage_after{suffix}"),
        "sub_sector": st.session_state.get(f"subsector{suffix}", ""),
        "purpose": st.session_state.get(f"purpose{suffix}"),
        "holder_type": st.session_state.get(f"holder_type{suffix}"),
        'tags': st.session_state.get(f"tags{suffix}", ""),
        "date_time": datetime.combine(
            st.session_state.get(f"date{suffix}"), 
            st.session_state.get(f"time{suffix}")
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "price_transaction": final_transaction,
    }
    
    try:
        # Log data being sent
        with st.expander("🔍 Debug - Request Data"):
            st.json(data)

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        response = requests.post(
            "https://sectors-news-endpoint.fly.dev/insider-trading", 
            headers = headers, json=data
        )
        
        if response.status_code == 200:
            if not is_pair_filings:
                st.toast("Single filing submitted successfully!")
                reset_form()
            return True
        else:
            # Handle non-200 responses
            st.error(f"❌ API Error {response.status_code} for Filing #{form_number if form_number else ''}")
            
            with st.expander(f"🔍 Error Details (Filing #{form_number if form_number else ''})"):
                st.write("**Status Code:**", response.status_code)
                st.write("**Response Headers:**", dict(response.headers))
                
                try:
                    error_json = response.json()
                    st.write("**Error Response (JSON):**")
                    st.json(error_json)
                except:
                    st.write("**Error Response (Text):**")
                    st.code(response.text)
            
            return False
        
    except Exception as error:
        st.error(f"Error submitting Filing #{form_number}: {str(error)}")
        return False 

def reset_form():
    """Reset all form fields after successful submission"""
    st.session_state.doc_number = ""
    st.session_state.company_name = ""
    st.session_state.holder_name = ""
    st.session_state.source = ""
    st.session_state.uuid = ""
    st.session_state.ticker = ""
    st.session_state.holding_before = 0
    st.session_state.share_percentage_before = 0.0
    st.session_state.holding_after = 0
    st.session_state.share_percentage_after = 0.0
    st.session_state.subsector = ""
    st.session_state.purpose = ""
    st.session_state.holder_type = "insider"
    st.session_state.date = datetime.today()
    st.session_state.time = datetime.now().time()
    st.session_state.tags = ""
    st.session_state.price_transaction = {
        "amount_transacted": [],
        "prices": [], 
        "types": [], 
        "dates": []
    }
    st.session_state.standalone_uuid = False

def main_ui():
    st.title("Sectors Filings")

    if 'filing_type' not in st.session_state:
        st.session_state.filing_type = None

    st.subheader("📋 Select Filing Type")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        if st.button(
            "**Single Filings**\n\n📄 One filing per submission",
            key="single_filing",
            use_container_width=True,
            type="primary" if st.session_state.filing_type == "Single Filings" else "secondary"
        ):
            st.session_state.filing_type = "Single Filings"
            st.rerun()
    
    with col2:
        if st.button(
            "**Pair Filings**\n\n📑 Two identical filings",
            key="pair_filing",
            use_container_width=True,
            type="primary" if st.session_state.filing_type == "Par Filings" else "secondary"
        ):
            st.session_state.filing_type = "Par Filings"
            st.rerun()
    
    if st.session_state.filing_type == 'Single Filings':
        st.write("---")
        main_ui_single(lambda: post(form_number=None))
    elif st.session_state.filing_type == 'Par Filings':
        st.write('---')
        main_ui_pair(post)
    else:
        st.info("👆 Please select a filing type above to continue.")      


if __name__ == '__main__':
    main_ui()