import streamlit as st
from datetime import datetime as dt
import requests

# data
api_key = st.secrets["API_KEY"]

available_subsectors = [
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

def generate():
    if not st.session_state.pdf_source or not st.session_state.file:
        st.toast("Please fill out the required fields.")
    else:
        files = {
            'file': (st.session_state.file.name, st.session_state.file, 'application/pdf'),
            'source': (None, st.session_state.pdf_source, 'text/plain'),
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post("https://sectors-news-endpoint.fly.dev/pdf", headers = headers, files=files)

        if response.status_code == 200:
            autogen = response.json()
            timestamp = dt.strptime(autogen["timestamp"], "%Y-%m-%d %H:%M:%S")
            st.session_state.pdf_source=autogen["source"]
            st.session_state.pdf_title=autogen["title"]
            st.session_state.pdf_body=autogen["body"]
            st.session_state.pdf_date=timestamp.date()
            st.session_state.pdf_time=timestamp.time()
            st.session_state.pdf_holder_name=autogen["holder_name"]
            st.session_state.pdf_holding_before=autogen["holding_before"]
            st.session_state.pdf_amount=autogen["amount_transaction"]
            st.session_state.pdf_transaction_type=autogen["transaction_type"]
            st.session_state.pdf_holding_after=autogen["holding_after"]
            st.session_state.pdf_tags=', '.join(autogen["tags"])
            st.session_state.pdf_tickers=', '.join(autogen["tickers"])
            st.session_state.pdf_price_transaction = autogen["price_transaction"]
            st.session_state.pdf_price = autogen["price"]
            st.session_state.pdf_trans_value = autogen["transaction_value"]
            st.session_state.pdf_view = "post"
        else:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")
  
def post():
    if not st.session_state.pdf_source or not st.session_state.pdf_title or not st.session_state.pdf_body or not st.session_state.pdf_date or not st.session_state.pdf_time or not st.session_state.pdf_holder_name or not st.session_state.pdf_holder_type or not st.session_state.pdf_transaction_type or not st.session_state.pdf_subsector or not st.session_state.pdf_tags or not st.session_state.pdf_tickers or not st.session_state.pdf_price_transaction:
        st.toast("Please fill out the required fields.")
    else:
        tags_list = [tag.strip() for tag in st.session_state.pdf_tags.split(',') if tag.strip()]
        tickers_list = [ticker.strip() for ticker in st.session_state.pdf_tickers.split(',') if ticker.strip()]
        final_t = {"amount_transacted": [], "prices": []}
        for i in range(len(st.session_state.pdf_price_transaction["amount_transacted"])):
            final_t["amount_transacted"].append(st.session_state[f"amount_{i}"])
            final_t["prices"].append(st.session_state[f"price_{i}"])

        data = {
            'source': st.session_state.pdf_source,
            'title': st.session_state.pdf_title,
            'body': st.session_state.pdf_body,
            'timestamp': dt.combine(st.session_state.pdf_date, st.session_state.pdf_time).strftime("%Y-%m-%d %H:%M:%S"),
            'holder_name': st.session_state.pdf_holder_name,
            'holder_type': st.session_state.pdf_holder_type,
            'holding_before': st.session_state.pdf_holding_before,
            'amount_transaction': st.session_state.pdf_amount,
            'transaction_type': st.session_state.pdf_transaction_type,
            'holding_after': st.session_state.pdf_holding_after,
            'sub_sector': st.session_state.pdf_subsector,
            'tags': tags_list,
            'tickers': tickers_list,
            'price_transaction': final_t,
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post("https://sectors-news-endpoint.fly.dev/pdf/post", headers = headers, json=data)

        if response.status_code == 200:
            st.toast("Insider trading submitted successfully! 🎉")
            st.session_state.pdf_source=""
            st.session_state.pdf_title=""
            st.session_state.pdf_body=""
            st.session_state.pdf_date=dt.today()
            st.session_state.pdf_time=dt.now()
            st.session_state.pdf_holder_name=""
            st.session_state.pdf_holder_type="insider"
            st.session_state.pdf_holding_before=0
            st.session_state.pdf_amount=0
            st.session_state.pdf_transaction_type="buy"
            st.session_state.pdf_holding_after=0
            st.session_state.pdf_subsector=available_subsectors[0]
            st.session_state.pdf_tags=""
            st.session_state.pdf_tickers=""
            st.session_state.pdf_view = "file"
            st.session_state.pdf_price_transaction = None
            st.session_state.pdf_price = ""
            st.session_state.pdf_trans_value = ""
        else:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")

def back():
    st.session_state.pdf_view = "file"

# app
if 'pdf_view' not in st.session_state:
    st.session_state.pdf_view = 'file'

if 'pdf_edit' not in st.session_state:
    st.session_state.pdf_edit = False

st.title("Sectors News")

# file submission
if st.session_state.pdf_view == "file":
    insider = st.form('insider')

    insider.subheader("Add Insider Trading (IDX Format)")
    insider.caption(":red[*] _required_")

    file = insider.file_uploader("Upload File (.pdf):red[*]", type="pdf", accept_multiple_files=False, key="file")
    source = insider.text_input("Source:red[*]", placeholder="Enter URL", key="pdf_source")
    submit = insider.form_submit_button("Submit", on_click=generate)

elif st.session_state.pdf_view == "post":
    insider = st.form('insider')

    insider.subheader("Add Insider Trading (IDX Format)")
    back_button = insider.form_submit_button("< Back", on_click=back)
    insider.caption(":red[*] _required_")
    source = insider.text_input("Source:red[*]", placeholder="Enter URL", key="pdf_source")
    title = insider.text_input("Title:red[*]", placeholder="Enter title", key="pdf_title")
    body = insider.text_area("Body:red[*]", placeholder="Enter body", key="pdf_body")
    date = insider.date_input("Created Date (GMT+7):red[*]", max_value=dt.today(), format="YYYY-MM-DD", key="pdf_date")
    time = insider.time_input("Created Time (GMT+7)*:red[*]", key="pdf_time", step=60)
    holder_name = insider.text_input("Holder Name:red[*]", placeholder="Enter holder name", key="pdf_holder_name")
    holder_type = insider.selectbox("Holder Type:red[*]", options = ["insider", "institution"], format_func=format_option, key="pdf_holder_type")
    holding_before = insider.number_input("Stock Holding before Transaction:red[*]", placeholder="Enter stock holding before transaction", key="pdf_holding_before", min_value=0)
    amount_transaction = insider.number_input("Amount Transaction:red[*]", placeholder="Enter amount transaction", key="pdf_amount")
    trans_type = insider.selectbox("Transaction Type:red[*]", options = ["buy", "sell"], format_func=format_option, key="pdf_transaction_type")
    holding_after = insider.number_input("Stock Holding after Transaction:red[*]", placeholder="Enter stock holding after transaction", key="pdf_holding_after", min_value=0)
    subsector = insider.selectbox("Subsector:red[*]", options = available_subsectors, format_func=format_option, key="pdf_subsector")
    tags = insider.text_area("Tags:red[*]", placeholder="Enter tags separated by commas, e.g. idx, market-cap", key="pdf_tags")
    tickers = insider.text_area("Tickers:red[*]", placeholder="Enter tickers separated by commas, e.g. BBCA.JK, BBRI.JK", key="pdf_tickers")

    price_transaction = st.session_state.get("pdf_price_transaction", {"amount_transacted": [], "prices": []})
    if price_transaction is None:
        price_transaction = {"amount_transacted": [], "prices": []}
    
    transaction_container = insider.expander("Transactions", expanded=True)

    for idx, (amount, price) in enumerate(zip(price_transaction["amount_transacted"], price_transaction["prices"])):
        col1, col2, col3 = transaction_container.columns([2, 2, 2], vertical_alignment="bottom")
        price_transaction["amount_transacted"][idx] = col1.number_input(f"Amount Transacted {idx + 1}", value=amount, key=f"amount_{idx}")
        price_transaction["prices"][idx] = col2.number_input(f"Price {idx + 1}", value=price, key=f"price_{idx}")
        remove_button = col3.form_submit_button(f"Remove Transaction {idx + 1}")
        if remove_button:
            price_transaction["amount_transacted"].pop(idx)
            price_transaction["prices"].pop(idx)
            st.rerun()

    if transaction_container.form_submit_button("Add Transaction"):
        price_transaction["amount_transacted"].append(0)
        price_transaction["prices"].append(0)
        st.rerun()

    st.session_state.pdf_price_transaction = price_transaction

    price = insider.number_input("Price*", disabled=True, key="pdf_price")
    transaction_value = insider.number_input("Transaction Value*", disabled=True, key="pdf_trans_value")
    
    
    submit = insider.form_submit_button("Submit", on_click=post)
