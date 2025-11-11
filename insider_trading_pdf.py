from datetime import datetime as dt, date

import streamlit as st
import requests
import uuid
import traceback

# from generate_article import generate_article_filings, extract_from_pdf
# from edit_insider_trading_function import insert_insider_trading_supabase
# import json 
# import tempfile

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

# helper functions
def format_option(option):
    return option.replace("-", " ").title()

# def save_temp(st_file):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         tmp.write(st_file.read())
#         tmp_path = tmp.name 
#     return tmp_path

def generate():
    if (not st.session_state.pdf_source or not st.session_state.file) or (st.session_state.share_transfer and (not st.session_state.recipient_source or not st.session_state.recipient_file)):
        st.toast("Please fill out the required fields.")
        return
    else:
        files = {
            'file': (st.session_state.file.name, st.session_state.file, 'application/pdf'),
            'source': (None, st.session_state.pdf_source, 'text/plain'),
        }

        if st.session_state.share_transfer:
            recipient_files = {
                'file': (st.session_state.recipient_file.name, st.session_state.recipient_file, 'application/pdf'),
                'source': (None, st.session_state.recipient_source, 'text/plain'),
            }

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        response = requests.post("https://sectors-news-endpoint.fly.dev/pdf", headers = headers, files=files)
        if st.session_state.share_transfer:
            response_recipient = requests.post("https://sectors-news-endpoint.fly.dev/pdf", headers = headers, files=recipient_files)

        if response.status_code == 200: 
            autogen = response.json()
            # with st.expander("🔍 Debug - Request Data"):
            #     st.json(autogen)
            # Handle if type in price transaction is empty
            st.session_state.show_type_notice = False
            price_transaction = autogen["price_transaction"]
            if "types" not in price_transaction or not price_transaction["types"]:
                num_transactions = len(price_transaction.get("prices", []))
                price_transaction["types"] = ["buy"] * num_transactions
                st.session_state.show_type_notice = True
                
            timestamp = dt.strptime(autogen["timestamp"], "%Y-%m-%d %H:%M:%S")
            st.session_state.pdf_source=autogen["source"]
            st.session_state.pdf_subsector=autogen["sub_sector"]
            st.session_state.pdf_title=autogen["title"]
            st.session_state.pdf_body=autogen["body"]
            st.session_state.pdf_date=timestamp.date()
            st.session_state.pdf_time=timestamp.time()
            st.session_state.pdf_company_name=autogen["company_name"]
            st.session_state.pdf_holder_name=autogen["holder_name"]
            st.session_state.pdf_holding_before=autogen["holding_before"]
            st.session_state.pdf_share_percentage_before=autogen["share_percentage_before"]
            st.session_state.pdf_amount=autogen["amount_transaction"]
            st.session_state.pdf_transaction_type=autogen["transaction_type"]
            st.session_state.pdf_holding_after=autogen["holding_after"]
            st.session_state.pdf_share_percentage_after=autogen["share_percentage_after"]
            # st.session_state.pdf_tags=', '.join(autogen["tags"])
            st.session_state.pdf_tags=""
            st.session_state.pdf_tickers=', '.join(autogen["tickers"])
            st.session_state.pdf_price_transaction = autogen["price_transaction"]
            st.session_state.pdf_price = autogen["price"]
            st.session_state.pdf_trans_value = autogen["transaction_value"]
            st.session_state.pdf_flag_tags = autogen.get("flag_tags", "")
            st.session_state.pdf_purpose = autogen.get('purpose', '')

            if not st.session_state.share_transfer:
                st.session_state.pdf_view = "post"
        else:
            # Handle error
            st.error(f"Error: Something went wrong with the transferrer data. Please try again.")

        if st.session_state.share_transfer and response_recipient.status_code == 200:
            autogen_recipient = response_recipient.json()

            st.session_state.show_type_notice_recipient = False
            price_transaction_recipient = autogen_recipient["price_transaction"]
            if "types" not in price_transaction_recipient or not price_transaction_recipient["types"]:
                num_transactions = len(price_transaction_recipient.get("prices", []))
                price_transaction_recipient["types"] = ["buy"] * num_transactions
                st.session_state.show_type_notice = True
            
            timestamp_recipient = dt.strptime(autogen_recipient["timestamp"], "%Y-%m-%d %H:%M:%S")
            st.session_state.recipient_source=autogen_recipient["source"]
            st.session_state.recipient_title=autogen_recipient["title"]
            st.session_state.recipient_body=autogen_recipient["body"]
            st.session_state.recipient_date=timestamp_recipient.date()
            st.session_state.recipient_time=timestamp_recipient.time()
            st.session_state.recipient_company_name=autogen_recipient["company_name"]
            st.session_state.recipient_holder_name=autogen_recipient["holder_name"]
            st.session_state.recipient_holding_before=autogen_recipient["holding_before"]
            st.session_state.recipient_share_percentage_before=autogen_recipient["share_percentage_before"]
            st.session_state.recipient_amount=autogen_recipient["amount_transaction"]
            st.session_state.recipient_transaction_type=autogen_recipient["transaction_type"]
            st.session_state.recipient_holding_after=autogen_recipient["holding_after"]
            st.session_state.recipient_share_percentage_after=autogen_recipient["share_percentage_after"]
            # st.session_state.recipient_tags=', '.join(autogen_recipient["tags"])
            st.session_state.recipient_tags=""
            st.session_state.recipient_subsector=autogen_recipient["sub_sector"]
            st.session_state.recipient_tickers=', '.join(autogen_recipient["tickers"])
            st.session_state.recipient_price_transaction = autogen_recipient["price_transaction"]
            st.session_state.recipient_price = autogen_recipient["price"]
            st.session_state.recipient_trans_value = autogen_recipient["transaction_value"]
            st.session_state.recipient_flag_tags = autogen_recipient.get("flag_tags", "")
            st.session_state.recipient_purpose = autogen_recipient.get('purpose', '')

            if response.status_code == 200:
                st.session_state.pdf_view = "post"
                
        elif st.session_state.share_transfer and not response_recipient.status_code != 200:
            # Handle error
            st.error(f"Error: Something went wrong with the recipient data. Please try again.")

def post():
    # Define required fields
    pdf_required_fields = [
        "pdf_source", "pdf_title", "pdf_body", "pdf_date", "pdf_time",
        "pdf_holder_name", "pdf_holder_type", "pdf_transaction_type",
        "pdf_subsector", "pdf_tickers", "pdf_price_transaction"
    ]

    recipient_required_fields = [
        "recipient_source", "recipient_title", "recipient_body", "recipient_date", "recipient_time",
        "recipient_holder_name", "recipient_holder_type", "recipient_transaction_type",
        "recipient_subsector", "recipient_tickers", "recipient_price_transaction"
    ]

    # Validation
    missing_pdf = not all(st.session_state.get(field) for field in pdf_required_fields)
    missing_recipient = (
        st.session_state.get("share_transfer")
        and not all(st.session_state.get(field) for field in recipient_required_fields)
    )

    if missing_pdf or missing_recipient:
        st.toast("Please fill out the required fields.")

    else:
        # tags_list = [tag.strip() for tag in st.session_state.pdf_tags.split(',') if tag.strip()]
        tickers_list = [ticker.strip() for ticker in st.session_state.pdf_tickers.split(',') if ticker.strip()]
        
        final_transaction = {"amount_transacted": [], "prices": [], "types": [], 'dates': []}

        for idx in range(len(st.session_state.pdf_price_transaction["amount_transacted"])):
            final_transaction["amount_transacted"].append(st.session_state[f"amount_{idx}"])
            final_transaction["prices"].append(st.session_state[f"price_{idx}"])
            final_transaction['types'].append(st.session_state[f"type_{idx}"])
            date_value = st.session_state[f"date_{idx}"]
            final_transaction['dates'].append(
                date_value.strftime("%Y-%m-%d") if hasattr(date_value, 'strftime') else str(date_value)
            )

        if st.session_state.share_transfer:
            flag_share_transfer = st.session_state.share_transfer
        else: 
            flag_share_transfer = None

        data = {
            'source': st.session_state.pdf_source,
            'title': st.session_state.pdf_title,
            'body': st.session_state.pdf_body,
            'timestamp': dt.combine(st.session_state.pdf_date, st.session_state.pdf_time).strftime("%Y-%m-%d %H:%M:%S"),
            'company_name': st.session_state.pdf_company_name,
            'holder_name': st.session_state.pdf_holder_name,
            'holder_type': st.session_state.pdf_holder_type,
            'holding_before': st.session_state.pdf_holding_before,
            'share_percentage_before': st.session_state.pdf_share_percentage_before,
            'amount_transaction': st.session_state.pdf_amount,
            # 'transaction_type': st.session_state.pdf_transaction_type,
            'holding_after': st.session_state.pdf_holding_after,
            'share_percentage_after': st.session_state.pdf_share_percentage_after,
            'sub_sector': st.session_state.pdf_subsector,
            'tags': st.session_state.pdf_tags,
            'tickers': tickers_list,
            'price_transaction': final_transaction,
            "share_transfer":flag_share_transfer,
            'flag_tags': st.session_state.pdf_flag_tags,
            'purpose': st.session_state.pdf_purpose
        }

        if st.session_state.share_transfer:
            uid = str(uuid.uuid4())
            data['UID'] = uid

            recipient_tickers_list = [ticker.strip() for ticker in st.session_state.recipient_tickers.split(',') if ticker.strip()]
            
            recipient_final_transaction = {"amount_transacted": [], "prices": [], 'types': [], 'dates': []}
            
            for idx in range(len(st.session_state.recipient_price_transaction["amount_transacted"])):
                recipient_final_transaction["amount_transacted"].append(st.session_state[f"recipient_amount_{idx}"])  
                recipient_final_transaction["prices"].append(st.session_state[f"recipient_price_{idx}"])             
                recipient_final_transaction['types'].append(st.session_state[f"type_recipient_{idx}"])
                # date_value = st.session_state[f"date_recipient_{idx}"]
                # recipient_final_transaction['dates'].append(date_value.strftime("%Y-%m-%d") if isinstance(date_value, dt.date) else str(date_value))
                date_value = st.session_state[f"date_recipient_{idx}"]
                recipient_final_transaction['dates'].append(
                    date_value.strftime("%Y-%m-%d") if hasattr(date_value, 'strftime') else str(date_value)
                )

            recipient_data = {
                'UID': uid,
                'source': st.session_state.recipient_source,
                'title': st.session_state.recipient_title,
                'body': st.session_state.recipient_body,
                'timestamp': dt.combine(st.session_state.recipient_date, st.session_state.recipient_time).strftime("%Y-%m-%d %H:%M:%S"),
                'company_name': st.session_state.recipient_company_name,
                'holder_name': st.session_state.recipient_holder_name,
                'holder_type': st.session_state.recipient_holder_type,
                'holding_before': st.session_state.recipient_holding_before,
                'share_percentage_before': st.session_state.recipient_share_percentage_before,
                'amount_transaction': st.session_state.recipient_amount,
                # 'transaction_type': st.session_state.recipient_transaction_type,
                'holding_after': st.session_state.recipient_holding_after,
                'share_percentage_after': st.session_state.recipient_share_percentage_after,
                'sub_sector': st.session_state.recipient_subsector,
                'tags': st.session_state.recipient_tags,
                'tickers': recipient_tickers_list,
                'price_transaction': recipient_final_transaction,
                'share_transfer_recipient': st.session_state.share_transfer,
                'flag_tags': st.session_state.recipient_flag_tags,
                'purpose': st.session_state.recipient_purpose
            }
        
        else:
            if st.session_state.pdf_uid:
                data['UID'] = st.session_state.pdf_uid

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        if st.session_state.share_transfer:
            data['tags'] = 'share_transfer'
            recipient_data['tags'] = 'share_transfer'

        try:
            # Log data being sent
            with st.expander("🔍 Debug - Request Data"):
                st.json(data)
            
            res = requests.post(
                "https://sectors-news-endpoint.fly.dev/pdf/post", 
                headers=headers, 
                json=data,
                timeout=30
            )
            
            st.write(f"Primary request status: {res.status_code}")
            
            if st.session_state.share_transfer:
                with st.expander("🔍 Debug - Recipient Request Data"):
                    st.json(recipient_data)
                    
                res_recipient = requests.post(
                    "https://sectors-news-endpoint.fly.dev/pdf/post", 
                    headers=headers, 
                    json=recipient_data,
                    timeout=30
                )
                st.write(f"Recipient request status: {res_recipient.status_code}")

            if res.status_code == 200:
                st.session_state.pdf_source=""
                st.session_state.pdf_title=""
                st.session_state.pdf_body=""
                st.session_state.pdf_date=dt.today()
                st.session_state.pdf_time=dt.now()
                st.session_state.pdf_holder_name=""
                st.session_state.pdf_holder_type="insider"
                st.session_state.pdf_holding_before=0
                st.session_state.pdf_share_percentage_before=0
                st.session_state.pdf_amount=0
                st.session_state.pdf_transaction_type="buy"
                st.session_state.pdf_holding_after=0
                st.session_state.pdf_share_percentage_after=0
                st.session_state.pdf_subsector=AVAILABLE_SUBSECTORS[0]
                st.session_state.pdf_tags=""
                st.session_state.pdf_tickers=""
                st.session_state.pdf_price_transaction = None
                st.session_state.pdf_price = ""
                st.session_state.pdf_trans_value = ""
                st.session_state.pdf_purpose = ""

                st.session_state.pdf_uid = ""
                st.session_state.generate_uid = False

                if not st.session_state.share_transfer:
                    st.toast("Insider trading submitted successfully! 🎉")
                    st.session_state.pdf_view = "file"
            else:
                # Detailed error for main request
                st.error(f"❌ API Error {res.status_code}")
                st.write("**Response:**")
                try:
                    st.json(res.json())
                except:
                    st.code(res.text)
            
            if st.session_state.share_transfer and res_recipient.status_code == 200:
                st.session_state.recipient_source=""
                st.session_state.recipient_title=""
                st.session_state.recipient_body=""
                st.session_state.recipient_date=dt.today()
                st.session_state.recipient_time=dt.now()
                st.session_state.recipient_holder_name=""
                st.session_state.recipient_holder_type="insider"
                st.session_state.recipient_holding_before=0
                st.session_state.recipient_share_percentage_before=0
                st.session_state.recipient_amount=0
                st.session_state.recipient_transaction_type="buy"
                st.session_state.recipient_holding_after=0
                st.session_state.recipient_share_percentage_after=0
                st.session_state.recipient_subsector=AVAILABLE_SUBSECTORS[0]
                st.session_state.recipient_tags=""
                st.session_state.recipient_tickers=""
                st.session_state.recipient_price_transaction = None
                st.session_state.recipient_price = ""
                st.session_state.recipient_trans_value = ""
                st.session_state.recipient_purpose = ""

                if res.status_code == 200:
                    st.toast("Insider trading submitted successfully! 🎉")
                    st.session_state.pdf_view = "file"
                    st.session_state.share_transfer = False
            
            elif st.session_state.share_transfer and res_recipient.status_code != 200:
                st.error(f"❌ Recipient API Error {res_recipient.status_code}")
                st.write("**Response:**")
                try:
                    st.json(res_recipient.json())
                except:
                    st.code(res_recipient.text)

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except requests.exceptions.RequestException as error:
            st.error(f"🌐 Network error: {str(error)}")
        except Exception as error:
            st.error(f"💥 Unexpected error: {str(error)}")
            st.code(traceback.format_exc())


def back():
    st.session_state.pdf_view = "file"
    st.session_state.share_transfer = False

def generate_uid():
    return str(uuid.uuid4())

def on_generate_uid_change():
    if st.session_state.generate_uid:
        # Generate new UID when checkbox is checked
        st.session_state.pdf_uid = generate_uid()
    else:
        # Clear UID when checkbox is unchecked
        st.session_state.pdf_uid = ""

def main_ui():
    # app
    if 'pdf_view' not in st.session_state:
        st.session_state.pdf_view = 'file'

    if 'pdf_edit' not in st.session_state:
        st.session_state.pdf_edit = False

    if 'share_transfer' not in st.session_state:
        st.session_state.share_transfer = False

    if 'generate_uuid' not in st.session_state:
        st.session_state.generate_uuid = False

    if 'pdf_uid' not in st.session_state:
        st.session_state.pdf_uid = None

    if 'pdf_flag_tags' not in st.session_state:
        st.session_state.pdf_flag_tags = ""
    
    if 'recipient_flag_tags' not in st.session_state:
        st.session_state.recipient_flag_tags = ""

    st.title("Sectors News")

    # file submission
    if st.session_state.pdf_view == "file":
        # Share transfer checkbox
        st.checkbox("Pair Filings", key="share_transfer")

        if not st.session_state.share_transfer:
            # UID checkbox
            st.checkbox("Single Filing",
                key="generate_uid", 
                on_change=on_generate_uid_change
            )

        insider = st.form('insider')

        insider.subheader("Add Insider Trading (IDX Format)")
        insider.caption(":red[*] _required_")
        
        # Upload file
        insider.file_uploader(
            "Upload File (.pdf):red[*]", 
            type="pdf", 
            accept_multiple_files=False, 
            key="file"
        )
        
        # Source url
        insider.text_input(
            "Source:red[*]", 
            placeholder="Enter URL", 
            key="pdf_source"
        )
        
        if not st.session_state.share_transfer:
            uid_value = st.session_state.pdf_uid if st.session_state.generate_uid else ""
            uid = insider.text_input("UID", value=uid_value,
                disabled=st.session_state.generate_uid,
                key="pdf_uid_input"
            )
            
            # Update session state if manually edited
            if not st.session_state.generate_uid:
                st.session_state.pdf_uid = uid

        if st.session_state.share_transfer:
            insider.markdown("### Recipient Filing Info")
            
            # Upload file share transfer
            insider.file_uploader(
                "Upload File (.pdf):red[*]", 
                type="pdf", 
                accept_multiple_files=False, 
                key="recipient_file"
            )
            
            # Source url share transfer
            insider.text_input(
                "Source:red[*]", 
                placeholder="Enter URL", 
                key="recipient_source"
            )

        # Submit button to parse pdf
        insider.form_submit_button("Submit", on_click=generate)

    elif st.session_state.pdf_view == "post":
        if st.session_state.show_type_notice:
            st.warning('The document have no type (buy/sell) in price transactions.' \
                        ' Please adjust as needed')

        # Share transfer checkbox disabled
        st.checkbox("Pair Filings", key="share_transfer", disabled=True)
        if not st.session_state.share_transfer:
            # UID checkbox disabled
            st.checkbox("Single Filing", key="generate_uuid", disabled=True)
        
        # Form for insider trading details
        insider = st.form('insider')

        insider.subheader("Add Insider Trading (IDX Format)")
        insider.form_submit_button("< Back", on_click=back)
        insider.caption(":red[*] _required_")

        # Source
        insider.text_input(
            'Source:red[*]', 
            placeholder='Enter URL', 
            key='pdf_source'
        )

        # Title
        insider.text_input(
            'Title:red[*]', 
            placeholder='Enter title', 
            key='pdf_title'
        )

        # Body
        insider.text_area(
            'Body:red[*]', 
            placeholder='Enter body', 
            key='pdf_body'
        )

        # Created Date (GMT+7)
        insider.date_input(
            'Created Date (GMT+7):red[*]', 
            max_value=dt.today(), 
            format='YYYY-MM-DD', 
            key='pdf_date'
        )

        # Created Time (GMT+7)
        insider.time_input(
            'Created Time (GMT+7)*:red[*]', 
            key='pdf_time', 
            step=60
        )

        # Company Name 
        insider.text_input(
            'Company Name:red[*]', 
            placeholder='Enter company name',
            key='pdf_company_name'
        )

        # Holder Name
        insider.text_input(
            'Holder Name:red[*]', 
            placeholder='Enter holder name', 
            key='pdf_holder_name'
        )

        # Holder Type
        insider.selectbox(
            'Holder Type:red[*]', 
            options=['insider', 'institution'], 
            format_func=format_option, 
            key='pdf_holder_type'
        )

        # Holding Before 
        insider.number_input(
            'Stock Holding Before Transaction:red[*]', 
            placeholder='Enter stock holding before transaction', 
            min_value=0, 
            key='pdf_holding_before'
        )

        # Share_percentage_before
        insider.number_input(
            "Stock Ownership Percentage before Transaction:red[*]", 
            placeholder="Enter stock ownership percentage before transaction", 
            key="pdf_share_percentage_before", 
            min_value=0.00000, max_value=100.00000, step=0.00001, 
            format="%.5f"
        )
        
        # Amount_transaction
        insider.number_input(
            "Amount Transaction:red[*]", 
            placeholder="Enter amount transaction", 
            key="pdf_amount"
        )
        
        # Holding after
        insider.number_input(
            "Stock Holding after Transaction:red[*]", 
            placeholder="Enter stock holding after transaction", 
            key="pdf_holding_after", 
            min_value=0
        )
        
        # Share percentage after
        insider.number_input(
            "Stock Ownership Percentage after Transaction:red[*]", 
            placeholder="Enter stock ownership percentage after transaction", 
            key="pdf_share_percentage_after", 
            min_value=0.00000, max_value=100.00000, step=0.00001, 
            format="%.5f"
        )
        
        # Subsector
        insider.selectbox(
            "Subsector:red[*]", 
            options = AVAILABLE_SUBSECTORS, 
            format_func=format_option, 
            index = AVAILABLE_SUBSECTORS.index(st.session_state.pdf_subsector),
            key="pdf_subsector"
        )
        
        # Tags
        insider.text_area("Tags:red[*]", 
                                 placeholder="Filled automatically",
                                 disabled=True,
                                 key="pdf_tags")
        # Tickers
        insider.text_area(
            "Tickers:red[*]", 
            placeholder="Enter tickers separated by commas, e.g. BBCA.JK, BBRI.JK", 
            key="pdf_tickers")
        
        # Purpose
        insider.text_area(
            "Purpose:red[*]", 
            placeholder="Enter purpose", 
            key="pdf_purpose")
        
        # Price transactions PDF
        price_transaction = st.session_state.get("pdf_price_transaction", {"amount_transacted": [], "prices": []})
        if price_transaction is None:
            price_transaction = {"amount_transacted": [], "prices": [], 'types': [], 'dates': []}
        
        transaction_container = insider.expander("Transactions", expanded=True)

        amounts = price_transaction["amount_transacted"]
        prices = price_transaction["prices"]
        types = price_transaction["types"]
        dates = price_transaction["dates"]

        for idx, (amount, price, type, date) in enumerate(zip(amounts, prices, types, dates)):
            col1, col2, col3, col4, col5 = transaction_container.columns([2, 2, 2, 2, 2], vertical_alignment="bottom")
            
            price_transaction["amount_transacted"][idx] = col1.number_input(
                f"Amount Transacted", 
                value=amount, 
                key=f"amount_{idx}"
            )
            price_transaction["prices"][idx] = col2.number_input(
                f"Price", 
                value=price, 
                key=f"price_{idx}"
            )

            type_options = ["buy", "sell", 'others']
            type_index = type_options.index(type.lower()) if type.lower() in type_options else 0
            price_transaction["types"][idx] = col3.selectbox(
                f"Type", 
                options=type_options, 
                index=type_index, 
                format_func=format_option, 
                key=f"type_{idx}"
            )

            price_transaction["dates"][idx] = col4.date_input(
                f"Date", 
                value=date if date else dt.today(), 
                max_value=dt.today(), 
                format="YYYY-MM-DD", 
                key=f"date_{idx}"
            )

            remove_button = col5.form_submit_button(f"Remove Transaction {idx + 1}")
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
        
        st.session_state.pdf_price_transaction = price_transaction

        # Price
        insider.number_input(
            "Price*", disabled=True, key="pdf_price"
        )
        
        # Transaction Value
        insider.number_input(
            "Transaction Value*", disabled=True, key="pdf_trans_value"
        )

        # Recipient section for share transfer
        if st.session_state.share_transfer:
            insider.markdown("### Recipient Filing Info")
            recipient_source = insider.text_input("Source:red[*]", placeholder="Enter URL", key="recipient_source")
            recipient_title = insider.text_input("Title:red[*]", placeholder="Enter title", key="recipient_title")
            recipient_body = insider.text_area("Body:red[*]", placeholder="Enter body", key="recipient_body")
            recipient_date = insider.date_input("Created Date (GMT+7):red[*]", max_value=dt.today(), format="YYYY-MM-DD", key="recipient_date")
            recipient_time = insider.time_input("Created Time (GMT+7)*:red[*]", key="recipient_time", step=60)
            
            # Recipient Company Name 
            insider.text_input(
                'Recipient Company Name:red[*]', 
                placeholder='Enter company name',
                key='recipient_company_name'
            )

            recipient_holder_name = insider.text_input("Holder Name:red[*]", placeholder="Enter holder name", key="recipient_holder_name")
            recipient_holder_type = insider.selectbox("Holder Type:red[*]", options = ["insider", "institution"], format_func=format_option, key="recipient_holder_type")
            recipient_holding_before = insider.number_input("Stock Holding before Transaction:red[*]", placeholder="Enter stock holding before transaction", key="recipient_holding_before", min_value=0)
            recipient_share_percentage_before = insider.number_input("Stock Ownership Percentage before Transaction:red[*]", placeholder="Enter stock ownership percentage before transaction", key="recipient_share_percentage_before", min_value=0.00000, max_value=100.00000, step=0.00001, format="%.5f")
            recipient_amount_transaction = insider.number_input("Amount Transaction:red[*]", placeholder="Enter amount transaction", key="recipient_amount")
            recipient_holding_after = insider.number_input("Stock Holding after Transaction:red[*]", placeholder="Enter stock holding after transaction", key="recipient_holding_after", min_value=0)
            recipient_share_percentage_after = insider.number_input("Stock Ownership Percentage after Transaction:red[*]", placeholder="Enter stock ownership percentage after transaction", key="recipient_share_percentage_after", min_value=0.00000, max_value=100.00000, step=0.00001, format="%.5f")
            
            # Subsector share_transfer
            insider.selectbox(
                "Subsector:red[*]", 
                options = AVAILABLE_SUBSECTORS, 
                format_func=format_option, 
                index=AVAILABLE_SUBSECTORS.index(st.session_state.recipient_subsector),
                key="recipient_subsector")
            
            # Tags share_transfer
            insider.text_area(
                "Tags:red[*]", 
                placeholder="Filled automatically", 
                disabled=True,
                key="recipient_tags")
            
            # Tickers share_transfer
            insider.text_area(
                "Tickers:red[*]",
                  placeholder="Enter tickers separated by commas, e.g. BBCA.JK, BBRI.JK",
                  key="recipient_tickers"
                )
            
            # Purpose
            insider.text_area(
                "Purpose:red[*]", 
                placeholder="Enter recipient purpose", 
                key="recipient_purpose")
            
            # Price transactions share_transfer
            recipient_price_transaction = st.session_state.get("recipient_price_transaction", {"amount_transacted": [], "prices": []})
            if recipient_price_transaction is None:
                recipient_price_transaction = {"amount_transacted": [], "prices": [], "types": [], 'dates': []}

            recipient_transaction_container = insider.expander("Transactions", expanded=True)

            amounts_recipient = recipient_price_transaction["amount_transacted"]
            prices_recipient = recipient_price_transaction["prices"]
            types_recipient = recipient_price_transaction["types"]
            dates_recipient = recipient_price_transaction["dates"]

            for idx, (amount, price, type, date) in enumerate(zip(amounts_recipient, prices_recipient, types_recipient, dates_recipient)):
                col1, col2, col3, col4, col5 = recipient_transaction_container.columns([2, 2, 2, 2, 2], vertical_alignment="bottom")
                
                recipient_price_transaction["amount_transacted"][idx] = col1.number_input(
                    f"Amount Transacted", 
                    value=amount, 
                    key=f"recipient_amount_{idx}"
                )
                recipient_price_transaction["prices"][idx] = col2.number_input(
                    f"Price", 
                    value=price, 
                    key=f"recipient_price_{idx}"
                )

                type_options = ["buy", "sell", 'others']
                type_index = type_options.index(type.lower()) if type.lower() in type_options else 0
                recipient_price_transaction["types"][idx] = col3.selectbox(
                    f"Type", 
                    options=type_options, 
                    index=type_index, 
                    format_func=format_option, 
                    key=f"type_recipient_{idx}"
                )
                recipient_price_transaction['dates'][idx] = col4.date_input(
                    f"Date", 
                    value=date if date else dt.today(), 
                    max_value=dt.today(), 
                    format="YYYY-MM-DD", 
                    key=f"date_recipient_{idx}"
                )

                recipient_remove_button = col5.form_submit_button(f"Remove Recipient Transaction {idx + 1}")
                if recipient_remove_button:
                    recipient_price_transaction["amount_transacted"].pop(idx)
                    recipient_price_transaction["prices"].pop(idx)
                    recipient_price_transaction["types"].pop(idx)
                    st.rerun()

            if recipient_transaction_container.form_submit_button("Add Recipient Transaction"):
                recipient_price_transaction["amount_transacted"].append(0)
                recipient_price_transaction["prices"].append(0)
                recipient_price_transaction["types"].append("buy")
                st.rerun()
        
            st.session_state.recipient_price_transaction = recipient_price_transaction

            # Recipient Price
            insider.number_input(
                "Price*", disabled=True, key="recipient_price"
            )
            
            # Recipient Transaction Value
            insider.number_input(
                "Transaction Value*", disabled=True, key="recipient_trans_value"
            )

        # Submit button
        insider.form_submit_button("Submit", on_click=post)

if __name__ == "__main__":
    main_ui()