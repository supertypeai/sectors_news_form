from datetime import datetime as dt
from supabase import create_client 

from insider_idx_helper.parser_idx_helper import parser_new_document

import streamlit as st
import requests
import uuid
import traceback
import tempfile
import time


# data
API_KEY = st.secrets["API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

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


def format_option(option):
    return option.replace("-", " ").title()


def save_temp(st_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(st_file.read())
        tmp_path = tmp.name 
    return tmp_path


def post_data_filling(payload: dict[str, any]):
    supabase_client = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)
    try:
        response = (
            supabase_client
            .table("idx_filings_v2")
            .insert(payload)
            .execute()
        )
        
        if response.data is not None:
            return response.data
        else:
            st.error("Error inserting data insider trading")
            return None
        
    except Exception as error:
        st.error(f"Exception while fetching data insider trading: {error}")
        return None
    

def populate_session_from_data(data: dict, prefix: str):
    """
    Populate session state from parsed data with given prefix
    """
    if data is None:
        return False
    
    timestamp = dt.strptime(data.get("timestamp", dt.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
    
    st.session_state[f"{prefix}_source"] = data.get("source_url", "")
    st.session_state[f"{prefix}_subsector"] = data.get("sub_sector", AVAILABLE_SUBSECTORS[0])
    st.session_state[f"{prefix}_title"] = data.get("title", "")
    st.session_state[f"{prefix}_body"] = data.get("body", "")
    st.session_state[f"{prefix}_date"] = timestamp.date()
    st.session_state[f"{prefix}_time"] = timestamp.time()
    st.session_state[f"{prefix}_company_name"] = data.get("company_name", "")
    st.session_state[f"{prefix}_holder_name"] = data.get("holder_name", "")
    st.session_state[f"{prefix}_holding_before"] = data.get("holding_before", 0)
    st.session_state[f"{prefix}_share_percentage_before"] = data.get("share_percentage_before", 0)
    st.session_state[f"{prefix}_amount"] = data.get("amount_transaction", 0)
    st.session_state[f"{prefix}_transaction_type"] = data.get("transaction_type", "buy")
    st.session_state[f"{prefix}_holding_after"] = data.get("holding_after", 0)
    st.session_state[f"{prefix}_share_percentage_after"] = data.get("share_percentage_after", 0)
    st.session_state[f"{prefix}_tags"] = ""
    st.session_state[f"{prefix}_symbol"] = data.get("symbol", '')
    st.session_state[f"{prefix}_price"] = data.get("price", "")
    st.session_state[f"{prefix}_trans_value"] = data.get("transaction_value", "")
    st.session_state[f"{prefix}_flag_tags"] = data.get("flag_tags", "")
    st.session_state[f"{prefix}_purpose"] = data.get("purpose", "")
    
    # Convert price_transaction from list of dicts to dict of lists
    price_transaction_list = data.get("price_transaction", [])
    converted_transaction = {
        "amount_transacted": [],
        "prices": [],
        "types": [],
        "dates": []
    }
    
    for transaction in price_transaction_list:
        converted_transaction["amount_transacted"].append(transaction.get("amount_transacted", 0))
        converted_transaction["prices"].append(transaction.get("price", 0))
        converted_transaction["types"].append(transaction.get("type", "buy"))
        converted_transaction["dates"].append(transaction.get("date", dt.today().strftime("%Y-%m-%d")))
    
    st.session_state[f"{prefix}_price_transaction"] = converted_transaction
    
    # Handle type notice
    if not converted_transaction["types"] or all(type == "" for type in converted_transaction["types"]):
        num_transactions = len(converted_transaction["prices"])
        st.session_state[f"{prefix}_price_transaction"]["types"] = ["buy"] * num_transactions
        st.session_state[f"{prefix}_show_type_notice"] = True
    else:
        st.session_state[f"{prefix}_show_type_notice"] = False
    
    return True


def generate():
    if (
        (not st.session_state.pdf_source or not st.session_state.file) or 
        (st.session_state.share_transfer and (not st.session_state.recipient_source or not st.session_state.recipient_file))
    ):
        st.toast("Please fill out the required fields")
        return
    
    try:
        # Parse main PDF
        save_temp_path = save_temp(st.session_state.file)
        response_others, response_no_others = parser_new_document(
            save_temp_path, source_url=st.session_state.pdf_source
        )
        
        # Store which data exists for main PDF
        st.session_state.has_pdf_others = response_others is not None
        st.session_state.has_pdf_no_others = response_no_others is not None
        
        # Populate main PDF data
        if response_others:
            populate_session_from_data(response_others, "pdf_others")
        if response_no_others:
            populate_session_from_data(response_no_others, "pdf_no_others")
        
        # Parse recipient PDF if pair filings
        if st.session_state.share_transfer:
            recipient_temp_path = save_temp(st.session_state.recipient_file)
            recipient_response_others, recipient_response_no_others = parser_new_document(
                recipient_temp_path, source_url=st.session_state.recipient_source
            )
            
            # Store which data exists for recipient PDF
            st.session_state.has_recipient_others = recipient_response_others is not None
            st.session_state.has_recipient_no_others = recipient_response_no_others is not None
            
            # Populate recipient PDF data
            if recipient_response_others:
                populate_session_from_data(recipient_response_others, "recipient_others")
            if recipient_response_no_others:
                populate_session_from_data(recipient_response_no_others, "recipient_no_others")
        
        # Initialize submission tracking
        st.session_state.submitted_forms = set()
        
        # Move to post view
        st.session_state.pdf_view = "post"
        
    except Exception as error:
        st.error(f"Error parsing PDF: {str(error)}")
        st.code(traceback.format_exc())


def post_form(prefix: str, form_label: str):
    """
    Submit a single form identified by prefix
    """
    # Define required fields
    required_fields = [
        f"{prefix}_source", f"{prefix}_title", f"{prefix}_body", 
        f"{prefix}_date", f"{prefix}_time", f"{prefix}_holder_name", 
        f"{prefix}_subsector", f"{prefix}_symbol", f"{prefix}_price_transaction"
    ]
    
    # Validation
    if not all(st.session_state.get(field) for field in required_fields):
        st.toast(f"Please fill out required fields for {form_label}")
        return
    
    # Build transaction data
    final_transaction = {"amount_transacted": [], "prices": [], "types": [], 'dates': []}
    
    for idx in range(len(st.session_state[f"{prefix}_price_transaction"]["amount_transacted"])):
        final_transaction["amount_transacted"].append(st.session_state[f"{prefix}_amount_{idx}"])
        final_transaction["prices"].append(st.session_state[f"{prefix}_price_{idx}"])
        final_transaction['types'].append(st.session_state[f"{prefix}_type_{idx}"])
        date_value = st.session_state[f"{prefix}_date_{idx}"]
        final_transaction['dates'].append(
            date_value.strftime("%Y-%m-%d") if hasattr(date_value, 'strftime') else str(date_value)
        )
    
    data = {
        'source': st.session_state[f"{prefix}_source"],
        'title': st.session_state[f"{prefix}_title"],
        'body': st.session_state[f"{prefix}_body"],
        'timestamp': dt.combine(st.session_state[f"{prefix}_date"], st.session_state[f"{prefix}_time"]).strftime("%Y-%m-%d %H:%M:%S"),
        'company_name': st.session_state[f"{prefix}_company_name"],
        'holder_name': st.session_state[f"{prefix}_holder_name"],
        'holder_type': st.session_state.get(f"{prefix}_holder_type", "insider"),
        'holding_before': st.session_state[f"{prefix}_holding_before"],
        'share_percentage_before': st.session_state[f"{prefix}_share_percentage_before"],
        'amount_transaction': st.session_state[f"{prefix}_amount"],
        'holding_after': st.session_state[f"{prefix}_holding_after"],
        'share_percentage_after': st.session_state[f"{prefix}_share_percentage_after"],
        'sub_sector': st.session_state[f"{prefix}_subsector"],
        'tags': st.session_state[f"{prefix}_tags"],
        'symbol': st.session_state[f"{prefix}_symbol"],
        'price_transaction': final_transaction,
        'flag_tags': st.session_state[f"{prefix}_flag_tags"],
        'purpose': st.session_state[f"{prefix}_purpose"]
    }
    
    # Add UID for pair filings
    if st.session_state.share_transfer:
        if 'pair_filing_uid' not in st.session_state:
            st.session_state.pair_filing_uid = str(uuid.uuid4())
        data['UID'] = st.session_state.pair_filing_uid
        data['tags'] = 'share_transfer'
        
        # Determine if this is recipient
        if prefix.startswith('recipient'):
            data['share_transfer_recipient'] = True
        else:
            data['share_transfer'] = True
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        with st.expander(f"Debug - {form_label} Request Data"):
            st.json(data)
        
        res = requests.post(
            "https://sectors-news-endpoint.fly.dev/pdf/post", 
            headers=headers, 
            json=data,
            timeout=60
        )

        st.write(f"{form_label} status: {res.status_code}")

        if res.status_code == 200:
            st.session_state.submitted_forms.add(prefix)
            st.toast(f"{form_label} submitted successfully!")
            time.sleep(1)

            # Check if all forms are submitted
            expected_forms = set()
            if st.session_state.has_pdf_others:
                expected_forms.add("pdf_others")
            if st.session_state.has_pdf_no_others:
                expected_forms.add("pdf_no_others")
            if st.session_state.share_transfer:
                if st.session_state.has_recipient_others:
                    expected_forms.add("recipient_others")
                if st.session_state.has_recipient_no_others:
                    expected_forms.add("recipient_no_others")
            
            if st.session_state.submitted_forms == expected_forms:
                st.success("All forms submitted successfully!")
                st.balloons()

            st.rerun()

        else:
            st.error(f"API Error {res.status_code}")
            try:
                st.json(res.json())
            except:
                st.code(res.text)

    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
    except Exception as error:
        st.error(f"Unexpected error: {str(error)}")
        st.code(traceback.format_exc())


def render_form_fields(prefix: str, form_label: str):
    """
    Render all form fields for a given prefix
    """
    # Show type notice 
    if st.session_state.get(f"{prefix}_show_type_notice", False):
        st.warning(f'{form_label}: Document has no type (buy/sell) in price transactions. Please adjust as needed')
    
    # Source
    st.text_input(
        'Source*', 
        placeholder='Enter URL', 
        key=f'{prefix}_source'
    )
    
    # Title
    st.text_input(
        'Title*', 
        placeholder='Enter title', 
        key=f'{prefix}_title'
    )
    
    # Body
    st.text_area(
        'Body*', 
        placeholder='Enter body', 
        key=f'{prefix}_body'
    )
    
    # Date and Time
    col1, col2 = st.columns(2)
    col1.date_input(
        'Created Date (GMT+7)*', 
        max_value=dt.today(), 
        format='YYYY-MM-DD', 
        key=f'{prefix}_date'
    )
    col2.time_input(
        'Created Time (GMT+7)*', 
        key=f'{prefix}_time', 
        step=60
    )
    
    # Company and Holder
    st.text_input(
        'Company Name*', 
        placeholder='Enter company name',
        key=f'{prefix}_company_name'
    )
    st.text_input(
        'Holder Name*', 
        placeholder='Enter holder name', 
        key=f'{prefix}_holder_name'
    )
    st.selectbox(
        'Holder Type*', 
        options=['insider', 'institution'], 
        format_func=format_option, 
        key=f'{prefix}_holder_type'
    )
    
    # Holdings
    st.number_input(
        'Stock Holding Before Transaction*', 
        min_value=0, 
        key=f'{prefix}_holding_before'
    )
    st.number_input(
        "Stock Ownership % Before Transaction*", 
        key=f"{prefix}_share_percentage_before", 
        min_value=0.00000, max_value=100.00000, step=0.00001, 
        format="%.5f"
    )
    st.number_input(
        "Amount Transaction*", 
        key=f"{prefix}_amount"
    )
    st.number_input(
        "Stock Holding After Transaction*", 
        key=f"{prefix}_holding_after", 
        min_value=0
    )
    st.number_input(
        "Stock Ownership % After Transaction*", 
        key=f"{prefix}_share_percentage_after", 
        min_value=0.00000, max_value=100.00000, step=0.00001, 
        format="%.5f"
    )
    
    # Subsector
    st.selectbox(
        "Subsector*", 
        options=AVAILABLE_SUBSECTORS, 
        format_func=format_option, 
        index=AVAILABLE_SUBSECTORS.index(st.session_state.get(f"{prefix}_subsector", AVAILABLE_SUBSECTORS[0])),
        key=f"{prefix}_subsector"
    )
    
    # Tags and Tickers
    st.text_area(
        "Tags*", 
        placeholder="Filled automatically",
        disabled=True,
        key=f"{prefix}_tags"
    )
    st.text_area(
        "Symbol*", 
        placeholder="Enter tickers separated by commas, e.g. BBCA.JK, BBRI.JK", 
        key=f"{prefix}_symbol"
    )
    
    # Purpose
    st.text_area(
        "Purpose*", 
        placeholder="Enter purpose", 
        key=f"{prefix}_purpose"
    )
    
    # Price transactions
    price_transaction = st.session_state.get(
        f"{prefix}_price_transaction", {"amount_transacted": [], "prices": [], "types": [], "dates": []}
    )
    if price_transaction is None:
        price_transaction = {"amount_transacted": [], "prices": [], "types": [], "dates": []}
    
    transaction_container = st.expander("Transactions", expanded=True)
    
    amounts = price_transaction.get("amount_transacted", [])
    prices = price_transaction.get("prices", [])
    types = price_transaction.get("types", [])
    dates = price_transaction.get("dates", [])
    
    for idx, (amount, price, typ, date) in enumerate(zip(amounts, prices, types, dates)):
        col1, col2, col3, col4, col5 = transaction_container.columns([2, 2, 2, 2, 1], vertical_alignment="bottom")
        
        col1.number_input(
            f"Amount Transacted", 
            value=amount, 
            key=f"{prefix}_amount_{idx}"
        )
        col2.number_input(
            f"Price", 
            value=price, 
            key=f"{prefix}_price_{idx}"
        )
        
        type_options = ["buy", "sell", 'others']
        type_index = type_options.index(typ.lower()) if typ.lower() in type_options else 0
        col3.selectbox(
            f"Type", 
            options=type_options, 
            index=type_index, 
            format_func=format_option, 
            key=f"{prefix}_type_{idx}"
        )
        
        col4.date_input(
            f"Date", 
            value=date if date else dt.today(), 
            max_value=dt.today(), 
            format="YYYY-MM-DD", 
            key=f"{prefix}_date_{idx}"
        )
        
        if col5.button("Remove", key=f"{prefix}_remove_{idx}"):
            st.session_state[f"{prefix}_price_transaction"]["amount_transacted"].pop(idx)
            st.session_state[f"{prefix}_price_transaction"]["prices"].pop(idx)
            st.session_state[f"{prefix}_price_transaction"]["types"].pop(idx)
            st.session_state[f"{prefix}_price_transaction"]["dates"].pop(idx)
            st.rerun()
    
    if transaction_container.button("Add Transaction", key=f"{prefix}_add_transaction"):
        st.session_state[f"{prefix}_price_transaction"]["amount_transacted"].append(0)
        st.session_state[f"{prefix}_price_transaction"]["prices"].append(0)
        st.session_state[f"{prefix}_price_transaction"]["types"].append("buy")
        st.session_state[f"{prefix}_price_transaction"]["dates"].append(dt.today().strftime("%Y-%m-%d"))
        st.rerun()
    
    # Disabled fields
    st.number_input(
        "Price*", disabled=True, key=f"{prefix}_price", value=st.session_state.get(f"{prefix}_price", 0)
    )
    st.number_input(
        "Transaction Value*", disabled=True, key=f"{prefix}_trans_value", value=st.session_state.get(f"{prefix}_trans_value", 0)
    )
    
    # Check if already submitted
    already_submitted = prefix in st.session_state.get('submitted_forms', set())
    
    # Submit button
    if st.button(f"Submit {form_label}", disabled=already_submitted, key=f"{prefix}_submit_btn"):
        post_form(prefix, form_label)

def back():
    st.session_state.pdf_view = "file"
    # st.session_state.share_transfer = False

def generate_uid():
    return str(uuid.uuid4())

def on_generate_uid_change():
    if st.session_state.generate_uid:
        st.session_state.pdf_uid = generate_uid()
    else:
        st.session_state.pdf_uid = ""

def main_ui():
    if 'pdf_view' not in st.session_state:
        st.session_state.pdf_view = 'file'
    if 'share_transfer' not in st.session_state:
        st.session_state.share_transfer = False
    if 'generate_uid' not in st.session_state:
        st.session_state.generate_uid = False
    if 'pdf_uid' not in st.session_state:
        st.session_state.pdf_uid = None
    
    st.title("Sectors News")
    
    # File submission view
    if st.session_state.pdf_view == "file":
        st.checkbox("Pair Filings", key="share_transfer")
        
        if not st.session_state.share_transfer:
            st.checkbox("Single Filing", key="generate_uid", on_change=on_generate_uid_change)
        
        insider = st.form('insider')
        insider.subheader("Add Insider Trading (IDX Format)")
        insider.caption(":red[*] _required_")
        
        insider.file_uploader(
            "Upload File (.pdf):red[*]", 
            type="pdf", 
            accept_multiple_files=False, 
            key="file"
        )
        insider.text_input(
            "Source:red[*]", 
            placeholder="Enter URL", 
            key="pdf_source"
        )
        
        if not st.session_state.share_transfer:
            uid_value = st.session_state.pdf_uid if st.session_state.generate_uid else ""
            uid = insider.text_input(
                "UID", 
                value=uid_value,
                disabled=st.session_state.generate_uid,
                key="pdf_uid_input"
            )
            if not st.session_state.generate_uid:
                st.session_state.pdf_uid = uid
        
        if st.session_state.share_transfer:
            insider.markdown("### Recipient Filing Info")
            insider.file_uploader(
                "Upload File (.pdf):red[*]", 
                type="pdf", 
                accept_multiple_files=False, 
                key="recipient_file"
            )
            insider.text_input(
                "Source:red[*]", 
                placeholder="Enter URL", 
                key="recipient_source"
            )
        
        insider.form_submit_button("Submit", on_click=generate)
    
    # Post view with multiple forms
    elif st.session_state.pdf_view == "post":
        st.checkbox("Pair Filings", key="share_transfer", disabled=True)
        if not st.session_state.share_transfer:
            st.checkbox("Single Filing", key="generate_uid", disabled=True)
        
        st.info("Modify the purpose field so it updates the body's purpose description.")
        
        if st.button("< Back to Upload"):
            back()
        
        st.caption(":red[*] _required_")
        
        # Render forms based on what data exists
        forms_to_render = []
        
        if st.session_state.get('has_pdf_others', False):
            forms_to_render.append(("pdf_others", "Main PDF - Others Transactions"))
        if st.session_state.get('has_pdf_no_others', False):
            forms_to_render.append(("pdf_no_others", "Main PDF - Buy/Sell Transactions"))
        if st.session_state.share_transfer:
            if st.session_state.get('has_recipient_others', False):
                forms_to_render.append(("recipient_others", "Recipient PDF - Others Transactions"))
            if st.session_state.get('has_recipient_no_others', False):
                forms_to_render.append(("recipient_no_others", "Recipient PDF - Buy/Sell Transactions"))
        
        # Render each form in an expander
        for prefix, label in forms_to_render:
            with st.expander(label, expanded=True):
                render_form_fields(prefix, label)

if __name__ == "__main__":
    main_ui()
