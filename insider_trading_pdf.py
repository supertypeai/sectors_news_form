import streamlit as st
from datetime import datetime as dt
import requests
import uuid

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
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post("https://sectors-news-endpoint.fly.dev/pdf", headers = headers, files=files)
        if st.session_state.share_transfer:
            response_recipient = requests.post("https://sectors-news-endpoint.fly.dev/pdf", headers = headers, files=recipient_files)

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
            st.session_state.pdf_share_percentage_before=autogen["share_percentage_before"]
            st.session_state.pdf_amount=autogen["amount_transaction"]
            st.session_state.pdf_transaction_type=autogen["transaction_type"]
            st.session_state.pdf_holding_after=autogen["holding_after"]
            st.session_state.pdf_share_percentage_after=autogen["share_percentage_after"]
            st.session_state.pdf_tags=', '.join(autogen["tags"])
            st.session_state.pdf_tickers=', '.join(autogen["tickers"])
            st.session_state.pdf_price_transaction = autogen["price_transaction"]
            st.session_state.pdf_price = autogen["price"]
            st.session_state.pdf_trans_value = autogen["transaction_value"]
            if not st.session_state.share_transfer:
                st.session_state.pdf_view = "post"
        else:
            # Handle error
            st.error(f"Error: Something went wrong with the transferrer data. Please try again.")

        if st.session_state.share_transfer and response_recipient.status_code == 200:
            autogen_recipient = response_recipient.json()
            timestamp_recipient = dt.strptime(autogen_recipient["timestamp"], "%Y-%m-%d %H:%M:%S")
            st.session_state.recipient_source=autogen_recipient["source"]
            st.session_state.recipient_title=autogen_recipient["title"]
            st.session_state.recipient_body=autogen_recipient["body"]
            st.session_state.recipient_date=timestamp_recipient.date()
            st.session_state.recipient_time=timestamp_recipient.time()
            st.session_state.recipient_holder_name=autogen_recipient["holder_name"]
            st.session_state.recipient_holding_before=autogen_recipient["holding_before"]
            st.session_state.recipient_share_percentage_before=autogen_recipient["share_percentage_before"]
            st.session_state.recipient_amount=autogen_recipient["amount_transaction"]
            st.session_state.recipient_transaction_type=autogen_recipient["transaction_type"]
            st.session_state.recipient_holding_after=autogen_recipient["holding_after"]
            st.session_state.recipient_share_percentage_after=autogen_recipient["share_percentage_after"]
            st.session_state.recipient_tags=', '.join(autogen_recipient["tags"])
            st.session_state.recipient_tickers=', '.join(autogen_recipient["tickers"])
            st.session_state.recipient_price_transaction = autogen_recipient["price_transaction"]
            st.session_state.recipient_price = autogen_recipient["price"]
            st.session_state.recipient_trans_value = autogen_recipient["transaction_value"]
            if response.status_code == 200:
                st.session_state.pdf_view = "post"
        elif st.session_state.share_transfer and response_recipient.status_code != 200:
            # Handle error
            st.error(f"Error: Something went wrong with the recipient data. Please try again.")


def post():
    if (not st.session_state.pdf_source or not st.session_state.pdf_title or not st.session_state.pdf_body or not st.session_state.pdf_date or not st.session_state.pdf_time or not st.session_state.pdf_holder_name or not st.session_state.pdf_holder_type or not st.session_state.pdf_transaction_type or not st.session_state.pdf_subsector or not st.session_state.pdf_tags or not st.session_state.pdf_tickers or not st.session_state.pdf_price_transaction) or (st.session_state.share_transfer and (not st.session_state.recipient_source or not st.session_state.recipient_title or not st.session_state.recipient_body or not st.session_state.recipient_date or not st.session_state.recipient_time or not st.session_state.recipient_holder_name or not st.session_state.recipient_holder_type or not st.session_state.recipient_transaction_type or not st.session_state.recipient_subsector or not st.session_state.recipient_tags or not st.session_state.recipient_tickers or not st.session_state.recipient_price_transaction)):
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
            'share_percentage_before': st.session_state.pdf_share_percentage_before,
            'amount_transaction': st.session_state.pdf_amount,
            'transaction_type': st.session_state.pdf_transaction_type,
            'holding_after': st.session_state.pdf_holding_after,
            'share_percentage_after': st.session_state.pdf_share_percentage_after,
            'sub_sector': st.session_state.pdf_subsector,
            'tags': tags_list,
            'tickers': tickers_list,
            'price_transaction': final_t,
        }

        if st.session_state.share_transfer:
            uid = str(uuid.uuid4())
            data['UID'] = uid
            recipient_tags_list = [tag.strip() for tag in st.session_state.recipient_tags.split(',') if tag.strip()]
            recipient_tickers_list = [ticker.strip() for ticker in st.session_state.recipient_tickers.split(',') if ticker.strip()]
            recipient_final_t = {"amount_transacted": [], "prices": []}
            for i in range(len(st.session_state.recipient_price_transaction["amount_transacted"])):
                recipient_final_t["amount_transacted"].append(st.session_state[f"amount_{i}"])
                recipient_final_t["prices"].append(st.session_state[f"price_{i}"])

            recipient_data = {
                'UID': uid,
                'source': st.session_state.recipient_source,
                'title': st.session_state.recipient_title,
                'body': st.session_state.recipient_body,
                'timestamp': dt.combine(st.session_state.recipient_date, st.session_state.recipient_time).strftime("%Y-%m-%d %H:%M:%S"),
                'holder_name': st.session_state.recipient_holder_name,
                'holder_type': st.session_state.recipient_holder_type,
                'holding_before': st.session_state.recipient_holding_before,
                'share_percentage_before': st.session_state.recipient_share_percentage_before,
                'amount_transaction': st.session_state.recipient_amount,
                'transaction_type': st.session_state.recipient_transaction_type,
                'holding_after': st.session_state.recipient_holding_after,
                'share_percentage_after': st.session_state.recipient_share_percentage_after,
                'sub_sector': st.session_state.recipient_subsector,
                'tags': recipient_tags_list,
                'tickers': recipient_tickers_list,
                'price_transaction': recipient_final_t,
            }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        res = requests.post("https://sectors-news-endpoint.fly.dev/pdf/post", headers = headers, json=data)
        if st.session_state.share_transfer:
            res_recipient = requests.post("https://sectors-news-endpoint.fly.dev/pdf/post", headers = headers, json=recipient_data)

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
            st.session_state.pdf_subsector=available_subsectors[0]
            st.session_state.pdf_tags=""
            st.session_state.pdf_tickers=""
            st.session_state.pdf_price_transaction = None
            st.session_state.pdf_price = ""
            st.session_state.pdf_trans_value = ""
            if not st.session_state.share_transfer:
                st.toast("Insider trading submitted successfully! 🎉")
                st.session_state.pdf_view = "file"

        else:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")
        
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
            st.session_state.recipient_subsector=available_subsectors[0]
            st.session_state.recipient_tags=""
            st.session_state.recipient_tickers=""
            st.session_state.recipient_price_transaction = None
            st.session_state.recipient_price = ""
            st.session_state.recipient_trans_value = ""
            if res.status_code == 200:
                st.toast("Insider trading submitted successfully! 🎉")
                st.session_state.pdf_view = "file"
                st.session_state.share_transfer = False
        elif st.session_state.share_transfer and res_recipient.status_code != 200:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")

def back():
    st.session_state.pdf_view = "file"
    st.session_state.share_transfer = False

# app
if 'pdf_view' not in st.session_state:
    st.session_state.pdf_view = 'file'

if 'pdf_edit' not in st.session_state:
    st.session_state.pdf_edit = False

if 'share_transfer' not in st.session_state:
    st.session_state.share_transfer = False

st.title("Sectors News")

# file submission
if st.session_state.pdf_view == "file":
    is_share_transfer = st.checkbox("Share Transfer", key="share_transfer")

    insider = st.form('insider')

    insider.subheader("Add Insider Trading (IDX Format)")
    insider.caption(":red[*] _required_")

    file = insider.file_uploader("Upload File (.pdf):red[*]", type="pdf", accept_multiple_files=False, key="file")
    source = insider.text_input("Source:red[*]", placeholder="Enter URL", key="pdf_source")

    recipient_file = None
    recipient_link = None
    if st.session_state.share_transfer:
        insider.markdown("### Recipient Filing Info")
        recipient_file = insider.file_uploader("Upload File (.pdf):red[*]", type="pdf", accept_multiple_files=False, key="recipient_file")
        recipient_link = insider.text_input("Source:red[*]", placeholder="Enter URL", key="recipient_source")

    submit = insider.form_submit_button("Submit", on_click=generate)

elif st.session_state.pdf_view == "post":
    is_share_transfer = st.checkbox("Share Transfer", key="share_transfer", disabled=True)
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
    share_percentage_before = insider.number_input("Stock Ownership Percentage before Transaction:red[*]", placeholder="Enter stock ownership percentage before transaction", key="pdf_share_percentage_before", min_value=0.00000, max_value=100.00000, step=0.00001, format="%.5f")
    amount_transaction = insider.number_input("Amount Transaction:red[*]", placeholder="Enter amount transaction", key="pdf_amount")
    trans_type = insider.selectbox("Transaction Type:red[*]", options = ["buy", "sell"], format_func=format_option, key="pdf_transaction_type")
    holding_after = insider.number_input("Stock Holding after Transaction:red[*]", placeholder="Enter stock holding after transaction", key="pdf_holding_after", min_value=0)
    share_percentage_after = insider.number_input("Stock Ownership Percentage after Transaction:red[*]", placeholder="Enter stock ownership percentage after transaction", key="pdf_share_percentage_after", min_value=0.00000, max_value=100.00000, step=0.00001, format="%.5f")
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

    if st.session_state.share_transfer:
        insider.markdown("### Recipient Filing Info")
        recipient_source = insider.text_input("Source:red[*]", placeholder="Enter URL", key="recipient_source")
        recipient_title = insider.text_input("Title:red[*]", placeholder="Enter title", key="recipient_title")
        recipient_body = insider.text_area("Body:red[*]", placeholder="Enter body", key="recipient_body")
        recipient_date = insider.date_input("Created Date (GMT+7):red[*]", max_value=dt.today(), format="YYYY-MM-DD", key="recipient_date")
        recipient_time = insider.time_input("Created Time (GMT+7)*:red[*]", key="recipient_time", step=60)
        recipient_holder_name = insider.text_input("Holder Name:red[*]", placeholder="Enter holder name", key="recipient_holder_name")
        recipient_holder_type = insider.selectbox("Holder Type:red[*]", options = ["insider", "institution"], format_func=format_option, key="recipient_holder_type")
        recipient_holding_before = insider.number_input("Stock Holding before Transaction:red[*]", placeholder="Enter stock holding before transaction", key="recipient_holding_before", min_value=0)
        recipient_share_percentage_before = insider.number_input("Stock Ownership Percentage before Transaction:red[*]", placeholder="Enter stock ownership percentage before transaction", key="recipient_share_percentage_before", min_value=0.00000, max_value=100.00000, step=0.00001, format="%.5f")
        recipient_amount_transaction = insider.number_input("Amount Transaction:red[*]", placeholder="Enter amount transaction", key="recipient_amount")
        recipient_trans_type = insider.selectbox("Transaction Type:red[*]", options = ["buy", "sell"], format_func=format_option, key="recipient_transaction_type")
        recipient_holding_after = insider.number_input("Stock Holding after Transaction:red[*]", placeholder="Enter stock holding after transaction", key="recipient_holding_after", min_value=0)
        recipient_share_percentage_after = insider.number_input("Stock Ownership Percentage after Transaction:red[*]", placeholder="Enter stock ownership percentage after transaction", key="recipient_share_percentage_after", min_value=0.00000, max_value=100.00000, step=0.00001, format="%.5f")
        recipient_subsector = insider.selectbox("Subsector:red[*]", options = available_subsectors, format_func=format_option, key="recipient_subsector")
        recipient_tags = insider.text_area("Tags:red[*]", placeholder="Enter tags separated by commas, e.g. idx, market-cap", key="recipient_tags")
        recipient_tickers = insider.text_area("Tickers:red[*]", placeholder="Enter tickers separated by commas, e.g. BBCA.JK, BBRI.JK", key="recipient_tickers")

        recipient_price_transaction = st.session_state.get("recipient_price_transaction", {"amount_transacted": [], "prices": []})
        if recipient_price_transaction is None:
            recipient_price_transaction = {"amount_transacted": [], "prices": []}

        recipient_transaction_container = insider.expander("Transactions", expanded=True)

        for idx, (amount, price) in enumerate(zip(recipient_price_transaction["amount_transacted"], recipient_price_transaction["prices"])):
            col1, col2, col3 = recipient_transaction_container.columns([2, 2, 2], vertical_alignment="bottom")
            recipient_price_transaction["amount_transacted"][idx] = col1.number_input(f"Amount Transacted {idx + 1}", value=amount, key=f"recipient_amount_{idx}")
            recipient_price_transaction["prices"][idx] = col2.number_input(f"Price {idx + 1}", value=price, key=f"recipient_price_{idx}")
            recipient_remove_button = col3.form_submit_button(f"Remove Recipient Transaction {idx + 1}")
            if recipient_remove_button:
                recipient_price_transaction["amount_transacted"].pop(idx)
                recipient_price_transaction["prices"].pop(idx)
                st.rerun()

        if recipient_transaction_container.form_submit_button("Add Recipient Transaction"):
            recipient_price_transaction["amount_transacted"].append(0)
            recipient_price_transaction["prices"].append(0)
            st.rerun()

        st.session_state.recipient_price_transaction = recipient_price_transaction

        recipient_price = insider.number_input("Price*", disabled=True, key="recipient_price")
        recipient_transaction_value = insider.number_input("Transaction Value*", disabled=True, key="recipient_trans_value")

    submit = insider.form_submit_button("Submit", on_click=post)
