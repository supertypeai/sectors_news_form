from datetime import datetime as dt
from supabase import create_client

import streamlit as st
import uuid
import requests

# Setup env
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

def fetch_data_fillings() -> list[dict]:
    supabase_client = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)
    try:
        response = supabase_client.table("idx_filings").select("*").execute()
        if response.data is not None:
            return response.data
        else:
            st.error("Error fetching data insider trading. Please reload the app.")
            return None
        
    except Exception as error:
        st.error(f"Exception while fetching data insider trading: {error}")
        return None
    
DATA = fetch_data_fillings()

def edit():
    selected_id = st.session_state.pdf_edit_id
    if selected_id != None:
        st.session_state.pdf_edit_view = "view2"
        prev_data = next((item for item in DATA if item["id"] == selected_id), None)
        if prev_data:
            try:
                timestamp = dt.strptime(prev_data["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                timestamp = dt.strptime(prev_data["timestamp"], "%Y-%m-%dT%H:%M:%S")
            st.session_state.pdf_edit_uid=prev_data["UID"]
            st.session_state.pdf_edit_source=prev_data["source"]
            st.session_state.pdf_edit_title=prev_data["title"]
            st.session_state.pdf_edit_body=prev_data["body"]
            st.session_state.pdf_edit_date=timestamp.date()
            st.session_state.pdf_edit_time=timestamp.time()
            st.session_state.pdf_edit_holder_name=prev_data["holder_name"]
            st.session_state.pdf_edit_holder_type=prev_data["holder_type"]
            st.session_state.pdf_edit_holding_before=prev_data["holding_before"]
            st.session_state.pdf_edit_share_percentage_before=prev_data["share_percentage_before"]
            st.session_state.pdf_edit_amount=prev_data["amount_transaction"]
            st.session_state.pdf_edit_transaction_type=prev_data["transaction_type"]
            st.session_state.pdf_edit_holding_after=prev_data["holding_after"]
            st.session_state.pdf_edit_share_percentage_after=prev_data["share_percentage_after"]
            st.session_state.pdf_edit_subsector=prev_data["sub_sector"]
            st.session_state.pdf_edit_tags=', '.join(prev_data["tags"])
            st.session_state.pdf_edit_tickers=', '.join(prev_data["tickers"]) if prev_data["tickers"] else None
            st.session_state.pdf_edit_price_transaction = prev_data["price_transaction"]
            st.session_state.pdf_edit_price = prev_data["price"]
            st.session_state.pdf_edit_trans_value = prev_data["transaction_value"]
            st.session_state.pdf_edit_view = "view2"

            st.write(f'debug: {st.session_state.pdf_edit_price_transaction}')

            # Check if types key exists in price_transaction
            price_transaction = prev_data["price_transaction"]
            if (price_transaction and 
                len(price_transaction.get("amount_transacted", [])) > 0 and 
                'types' not in price_transaction):
                st.session_state.show_type_notice = True
            else:
                st.session_state.show_type_notice = False
    else:
        st.toast("Please select 1 id.")

def post():
    required_fields = [
        "pdf_edit_source",
        "pdf_edit_title",
        "pdf_edit_body",
        "pdf_edit_date",
        "pdf_edit_time",
        "pdf_edit_holder_name",
        "pdf_edit_holder_type",
        "pdf_edit_subsector",
        "pdf_edit_tags",
        "pdf_edit_tickers",
        "pdf_edit_price_transaction",
    ]

    # Check if any required field is empty/false
    if any(not st.session_state.get(field) for field in required_fields):
        st.toast("Please fill out the required fields.")
    else:
        if st.session_state.pdf_uid:
            final_uid = st.session_state.pdf_uid
        else:
            manual_uid = st.session_state.get("uuid_field_manual", "")
            final_uid = manual_uid if manual_uid else None

        tags_list = [tag.strip() for tag in st.session_state.pdf_edit_tags.split(',') if tag.strip()]
        tickers_list = [ticker.strip() for ticker in st.session_state.pdf_edit_tickers.split(',') if ticker.strip()]

        final_transactions = {"amount_transacted": [], "prices": [], 'types': []}
        num_entries = len(st.session_state.pdf_edit_price_transaction["amount_transacted"])
        for idx in range(num_entries):
            final_transactions["amount_transacted"].append(st.session_state[f"amount_{idx}"])
            final_transactions["prices"].append(st.session_state[f"price_{idx}"])
            final_transactions['types'].append(st.session_state[f"types_{idx}"])
        
        data = {
            'id': st.session_state.pdf_edit_id,
            'UID': final_uid,
            'source': st.session_state.pdf_edit_source,
            'title': st.session_state.pdf_edit_title,
            'body': st.session_state.pdf_edit_body,
            'timestamp': dt.combine(st.session_state.pdf_edit_date, st.session_state.pdf_edit_time).strftime("%Y-%m-%d %H:%M:%S"),
            'holder_name': st.session_state.pdf_edit_holder_name,
            'holder_type': st.session_state.pdf_edit_holder_type,
            'holding_before': st.session_state.pdf_edit_holding_before,
            'share_percentage_before': st.session_state.pdf_edit_share_percentage_before,
            'amount_transaction': st.session_state.pdf_edit_amount,
            # 'transaction_type': st.session_state.pdf_edit_transaction_type.lower(),
            'holding_after': st.session_state.pdf_edit_holding_after,
            'share_percentage_after': st.session_state.pdf_edit_share_percentage_after,
            'sub_sector': st.session_state.pdf_edit_subsector,
            'tags': tags_list,
            'tickers': tickers_list,
            'price_transaction': final_transactions
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        st.write("Data to be sent for update:", data)  
        
        response = requests.patch(
            "https://sectors-news-endpoint.fly.dev/insider-trading", 
            headers = headers, 
            json=data
        )

        if response.status_code == 200:
            st.toast("Insider trading editted successfully! 🎉")
            st.session_state.pdf_uid=""
            st.session_state.pdf_edit_source=""
            st.session_state.pdf_edit_title=""
            st.session_state.pdf_edit_body=""
            st.session_state.pdf_edit_date=dt.today()
            st.session_state.pdf_edit_time=dt.now()
            st.session_state.pdf_edit_holder_name=""
            st.session_state.pdf_edit_holder_type="insider"
            st.session_state.pdf_edit_holding_before=0
            st.session_state.pdf_edit_share_percentage_before=0
            st.session_state.pdf_edit_amount=0
            # st.session_state.pdf_edit_transaction_type="buy"
            st.session_state.pdf_edit_holding_after=0
            st.session_state.pdf_edit_share_percentage_after=0
            st.session_state.pdf_edit_subsector=AVAILABLE_SUBSECTORS[0]
            st.session_state.pdf_edit_tags=""
            st.session_state.pdf_edit_tickers=""
            st.session_state.pdf_edit_view = "view1"
            st.session_state.pdf_edit_price_transaction = None
            st.session_state.pdf_edit_price = ""
            st.session_state.pdf_edit_trans_value = ""
        else:
            # Handle error
            st.write("Response content:", response.text) 
            st.error(f"Error: Something went wrong. Please try again.")

def back():
    st.session_state.pdf_edit_view = "view1"

def format_option(option):
    return option.replace("-", " ").title()

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
    if 'pdf_edit_view' not in st.session_state:
        st.session_state.pdf_edit_view = 'view1'

    if 'generate_uid' not in st.session_state:
        st.session_state.generate_uid = False

    if 'pdf_uid' not in st.session_state:
        st.session_state.pdf_uid = None

    st.title("Sectors News")

    # file submission
    if st.session_state.pdf_edit_view == "view1":
        st.subheader("Edit Insider Trading")

        if (len(DATA) > 0):
            form = st.form("edit")
            selected_id = form.selectbox("Select id", [i['id'] for i in sorted(DATA, key=lambda x: x["id"])], key="pdf_edit_id")
            form.form_submit_button("Edit", type="primary", on_click=edit)

            st.dataframe(sorted(DATA, key=lambda x: x["id"], reverse=True), 
                column_order=["id", "title", "body", "source", "timestamp", "holder_name", 
                              "holder_type", "holding_before", "share_percentage_before", 
                              "amount_transaction", "transaction_type", "holding_after", 
                              "share_percentage_after", "price_transaction", "price", 
                              "transaction_value", "sector", "sub_sector", "tags", "tickers", "UID"],
                selection_mode="single-row"
            )
        else: 
            st.info("There is no insider tradings in the database.")
            st.page_link("insider_trading_pdf.py", label="Add Insider Trading", icon=":material/arrow_back:")

    elif st.session_state.pdf_edit_view == "view2":
        # Info notice if types were not previously set in db
        if st.session_state.get('show_type_notice', False):
            st.warning("Note: Transaction types were not previously set in db. " \
                    "Defaulting to 'buy' for all entries. " \
                    "Please review and adjust as necessary, because this may affect the calculated price, transaction value, and transaction type")
        
        generate_uid_checkbox = st.checkbox(
            "Generate UID", 
            key="generate_uid", 
            on_change=on_generate_uid_change
        )

        # Edit insider trading form
        insider = st.form('insider')

        insider.subheader("Edit Insider Trading")
        insider.form_submit_button("< Back", on_click=back)
        insider.caption(":red[*] _required_")

        # ID form
        insider.text_input(
            "ID*", 
            value= st.session_state.get("pdf_edit_id", ""), 
            disabled=True, 
            key="pdf_edit_id"
        )
        
        if generate_uid_checkbox:
            insider.text_input(
                "UID*", 
                value= st.session_state.get("pdf_uid", ""), 
                disabled=True, 
                key="pdf_uid"
            )
        else:
            insider.text_input(
                "UID*", 
                disabled=False, 
                value= st.session_state.get("pdf_edit_uid", ""),
                key="uuid_field_manual"
            )

        # Source form
        insider.text_input(
            "Source:red[*]", 
            value= st.session_state.get("pdf_edit_source", ""), 
            placeholder="Enter URL", 
            key="pdf_edit_source"
        )
        
        # Title form
        insider.text_input(
            "Title:red[*]", 
            value= st.session_state.get("pdf_edit_title", ""), 
            placeholder="Enter title", 
            key="pdf_edit_title"
        )
        
        # Body form
        insider.text_area(
            "Body:red[*]", 
            value= st.session_state.get("pdf_edit_body", ""), 
            placeholder="Enter body", 
            key="pdf_edit_body"
        )
        
        # Created date form
        insider.date_input(
            "Created Date (GMT+7):red[*]", 
            value= st.session_state.get("pdf_edit_date", dt.today()),
            max_value=dt.today(), 
            format="YYYY-MM-DD", 
            key="pdf_edit_date"
        )
        
        # Created time form
        insider.time_input(
            "Created Time (GMT+7)*:red[*]", 
            value= st.session_state.get("pdf_edit_time", dt.now().time()), 
            key="pdf_edit_time", step=60
        )  
        
        # Holder name form
        insider.text_input(
            "Holder Name:red[*]", 
            value= st.session_state.get("pdf_edit_holder_name", ""), 
            placeholder="Enter holder name", key="pdf_edit_holder_name"
        )
        
        # Holder type form
        insider.selectbox(
            "Holder Type:red[*]", 
            index= ["insider", "institution"].index(st.session_state.get("pdf_edit_holder_type", "insider")), 
            options = ["insider", "institution"], 
            format_func=format_option, 
            key="pdf_edit_holder_type"
        )
        
        # Holding before form
        insider.number_input("Stock Holding before Transaction:red[*]", 
            value= st.session_state.get("pdf_edit_holding_before"), 
            placeholder="Enter stock holding before transaction", 
            key="pdf_edit_holding_before", min_value=0
        )

        # Share percentage before form    
        insider.number_input(
            "Stock Ownership Percentage before Transaction:red[*]",
            value=st.session_state.get("pdf_edit_share_percentage_before"), 
            placeholder="Enter stock ownership percentage before transaction",
            key="pdf_edit_share_percentage_before", min_value=0.00000,
            max_value=100.00000, 
            step=0.00001,
            format="%.5f"
        )
        
        # Amount transaction form
        insider.number_input(
            "Amount Transaction:red[*]", 
            value= st.session_state.get("pdf_edit_amount"), 
            placeholder="Enter amount transaction", 
            key="pdf_edit_amount"
        )
        
        # Holding after form
        insider.number_input(
            "Stock Holding after Transaction:red[*]", 
            value= st.session_state.get("pdf_edit_holding_after"), 
            placeholder="Enter stock holding after transaction", 
            key="pdf_edit_holding_after", min_value=0
        )
        
        # Share percentage after form  
        insider.number_input(
            "Stock Ownership Percentage after Transaction:red[*]", 
            value=st.session_state.get("pdf_edit_share_percentage_after"),
            placeholder="Enter stock ownership percentage after transaction", 
            key="pdf_edit_share_percentage_after", 
            min_value=0.00000, 
            max_value=100.00000, 
            step=0.00001, 
            format="%.5f"
        )

        # Subsector form
        insider.selectbox(
            "Subsector:red[*]", 
            index = AVAILABLE_SUBSECTORS.index(st.session_state.get("subsector", AVAILABLE_SUBSECTORS[0])),
            options = AVAILABLE_SUBSECTORS, 
            format_func=format_option, 
            key="pdf_edit_subsector")
        
        # Tags form
        insider.text_area(
            "Tags:red[*]", 
            value=st.session_state.get("pdf_edit_tags", ""), 
            placeholder="Enter tags separated by commas, e.g. idx, market-cap", 
            key="pdf_edit_tags")
        
        # Ticker form
        insider.text_area(
            "Tickers:red[*]", 
            value=st.session_state.get("pdf_edit_tickers", ""), 
            placeholder="Enter tickers separated by commas, e.g. BBCA.JK, BBRI.JK", 
            key="pdf_edit_tickers")

        price_transaction = st.session_state.get("pdf_edit_price_transaction", 
                                                {"amount_transacted": [], "prices": [], "types": []})
        if price_transaction is None:
            price_transaction = {"amount_transacted": [], "prices": [], "types": []}

        if 'types' not in price_transaction or not price_transaction.get('types'):
            price_transaction['types'] = ['buy'] * len(price_transaction['amount_transacted'])

        transaction_container = insider.expander("Transactions", expanded=True)

        for idx, (amount, price, type) in enumerate(zip(price_transaction["amount_transacted"], price_transaction["prices"], price_transaction["types"])):
            col1, col2, col3, col4 = transaction_container.columns([2, 2, 2, 2], vertical_alignment="bottom")
            
            col1.number_input(f"Amount Transacted {idx + 1}", value=amount, key=f"amount_{idx}")
            col2.number_input(f"Price {idx + 1}", value=price, key=f"price_{idx}")
            col3.selectbox(f"Type {idx + 1}", 
                            options=['Buy', 'Sell'], 
                            index=0 if type.lower() == "buy" else 1,  
                            format_func=format_option, 
                            key=f"types_{idx}")

            remove_button = col4.form_submit_button(f"Remove Transaction {idx + 1}")
            if remove_button:
                st.session_state.pdf_edit_price_transaction["amount_transacted"].pop(idx)
                st.session_state.pdf_edit_price_transaction["prices"].pop(idx)
                st.session_state.pdf_edit_price_transaction["types"].pop(idx)
                st.rerun()
        
        if transaction_container.form_submit_button("Add Transaction"):
            st.session_state.pdf_edit_price_transaction["amount_transacted"].append(0)
            st.session_state.pdf_edit_price_transaction["prices"].append(0)
            st.session_state.pdf_edit_price_transaction["types"].append("Buy")
            st.rerun()

        # Price form
        insider.number_input(
            "Price*", 
            value= st.session_state.get("pdf_edit_price", 0), 
            disabled=True, 
            key="pdf_edit_price"
        )
        
        # Transaction value form
        insider.number_input(
            "Transaction Value*", 
            value= st.session_state.get("pdf_edit_trans_value", 0), 
            disabled=True, 
            key="pdf_edit_trans_value"
        )

        # Submit button to update the data form
        insider.form_submit_button("Submit", on_click=post)

if __name__ == "__main__":
    main_ui()