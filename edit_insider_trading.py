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
def fetch():
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get("https://sectors-news-endpoint.fly.dev/insider-trading", headers = headers)

    if response.status_code == 200:
        return response.json()
    else:
        # Handle error
        st.error(f"Error fetching insider trading data. Please reload the app.")
data = fetch()

def format_option(option):
    return option.replace("-", " ").title()

def edit():
    selected_id = st.session_state.pdf_edit_id
    if selected_id != None:
        st.session_state.pdf_edit_view = "view2"
        prev_data = next((item for item in data if item["id"] == selected_id), None)
        if prev_data:
            try:
                timestamp = dt.strptime(prev_data["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                timestamp = dt.strptime(prev_data["timestamp"], "%Y-%m-%dT%H:%M:%S")
            st.session_state.pdf_edit_source=prev_data["source"]
            st.session_state.pdf_edit_title=prev_data["title"]
            st.session_state.pdf_edit_body=prev_data["body"]
            st.session_state.pdf_edit_date=timestamp.date()
            st.session_state.pdf_edit_time=timestamp.time()
            st.session_state.pdf_edit_holder_name=prev_data["holder_name"]
            st.session_state.pdf_edit_holder_type=prev_data["holder_type"]
            st.session_state.pdf_edit_holding_before=prev_data["holding_before"]
            st.session_state.pdf_edit_amount=prev_data["amount_transaction"]
            st.session_state.pdf_edit_transaction_type=prev_data["transaction_type"]
            st.session_state.pdf_edit_holding_after=prev_data["holding_after"]
            st.session_state.pdf_edit_subsector=prev_data["sub_sector"]
            st.session_state.pdf_edit_tags=', '.join(prev_data["tags"])
            st.session_state.pdf_edit_tickers=', '.join(prev_data["tickers"])
            st.session_state.pdf_edit_price_transaction = prev_data["price_transaction"]
            st.session_state.pdf_edit_price = prev_data["price"]
            st.session_state.pdf_edit_trans_value = prev_data["transaction_value"]
            st.session_state.pdf_edit_view = "view2"
    else:
        st.toast("Please select 1 id.")

def post():
    if not st.session_state.pdf_edit_source or not st.session_state.pdf_edit_title or not st.session_state.pdf_edit_body or not st.session_state.pdf_edit_date or not st.session_state.pdf_edit_time or not st.session_state.pdf_edit_holder_name or not st.session_state.pdf_edit_holder_type or not st.session_state.pdf_edit_transaction_type or not st.session_state.pdf_edit_subsector or not st.session_state.pdf_edit_tags or not st.session_state.pdf_edit_tickers or not st.session_state.pdf_edit_price_transaction:
        st.toast("Please fill out the required fields.")
    else:
        tags_list = [tag.strip() for tag in st.session_state.pdf_edit_tags.split(',') if tag.strip()]
        tickers_list = [ticker.strip() for ticker in st.session_state.pdf_edit_tickers.split(',') if ticker.strip()]

        final_t = {"amount_transacted": [], "prices": []}
        for i in range(len(st.session_state.pdf_edit_price_transaction["amount_transacted"])):
            final_t["amount_transacted"].append(st.session_state[f"amount_{i}"])
            final_t["prices"].append(st.session_state[f"price_{i}"])

        data = {
            'id': st.session_state.pdf_edit_id,
            'source': st.session_state.pdf_edit_source,
            'title': st.session_state.pdf_edit_title,
            'body': st.session_state.pdf_edit_body,
            'timestamp': dt.combine(st.session_state.pdf_edit_date, st.session_state.pdf_edit_time).strftime("%Y-%m-%d %H:%M:%S"),
            'holder_name': st.session_state.pdf_edit_holder_name,
            'holder_type': st.session_state.pdf_edit_holder_type,
            'holding_before': st.session_state.pdf_edit_holding_before,
            'amount_transaction': st.session_state.pdf_edit_amount,
            'transaction_type': st.session_state.pdf_edit_transaction_type,
            'holding_after': st.session_state.pdf_edit_holding_after,
            'sub_sector': st.session_state.pdf_edit_subsector,
            'tags': tags_list,
            'tickers': tickers_list,
            'price_transaction': final_t
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.patch("https://sectors-news-endpoint.fly.dev/insider-trading", headers = headers, json=data)

        if response.status_code == 200:
            st.toast("Insider trading editted successfully! 🎉")
            st.session_state.pdf_edit_source=""
            st.session_state.pdf_edit_title=""
            st.session_state.pdf_edit_body=""
            st.session_state.pdf_edit_date=dt.today()
            st.session_state.pdf_edit_time=dt.now()
            st.session_state.pdf_edit_holder_name=""
            st.session_state.pdf_edit_holder_type="insider"
            st.session_state.pdf_edit_holding_before=0
            st.session_state.pdf_edit_amount=0
            st.session_state.pdf_edit_transaction_type="buy"
            st.session_state.pdf_edit_holding_after=0
            st.session_state.pdf_edit_subsector=available_subsectors[0]
            st.session_state.pdf_edit_tags=""
            st.session_state.pdf_edit_tickers=""
            st.session_state.pdf_edit_view = "view1"
            st.session_state.pdf_edit_price_transaction = None
            st.session_state.pdf_edit_price = ""
            st.session_state.pdf_edit_trans_value = ""
        else:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")

def back():
    st.session_state.pdf_edit_view = "view1"

# app
if 'pdf_edit_view' not in st.session_state:
    st.session_state.pdf_edit_view = 'view1'

st.title("Sectors News")

# file submission
if st.session_state.pdf_edit_view == "view1":
    st.subheader("Edit Insider Trading")

    if (len(data) > 0):
        form = st.form("edit")
        selected_id = form.selectbox("Select id", [i['id'] for i in sorted(data, key=lambda x: x["id"])], key="pdf_edit_id")
        form.form_submit_button("Edit", type="primary", on_click=edit)

        st.dataframe(sorted(data, key=lambda x: x["id"], reverse=True), 
            column_order=["id", "title", "body", "source", "timestamp", "holder_name", "holder_type", "holding_before", "amount_transaction", "transaction_type", "holding_after", "price_transaction", "price", "transaction_value", "sector", "sub_sector", "tags", "tickers"],
            selection_mode="single-row"
        )
    else: 
        st.info("There is no insider tradings in the database.")
        st.page_link("insider_trading_pdf.py", label="Add Insider Trading", icon=":material/arrow_back:")

elif st.session_state.pdf_edit_view == "view2":
    insider = st.form('insider')

    insider.subheader("Edit Insider Trading")
    back_button = insider.form_submit_button("< Back", on_click=back)
    insider.caption(":red[*] _required_")
    id = insider.text_input("ID*", value= st.session_state.get("pdf_edit_id", ""), disabled=True, key="pdf_edit_id")
    source = insider.text_input("Source:red[*]", value= st.session_state.get("pdf_edit_source", ""), placeholder="Enter URL", key="pdf_edit_source")
    title = insider.text_input("Title:red[*]", value= st.session_state.get("pdf_edit_title", ""), placeholder="Enter title", key="pdf_edit_title")
    body = insider.text_area("Body:red[*]", value= st.session_state.get("pdf_edit_body", ""), placeholder="Enter body", key="pdf_edit_body")
    date = insider.date_input("Created Date (GMT+7):red[*]", value= st.session_state.get("pdf_edit_date", dt.today()), max_value=dt.today(), format="YYYY-MM-DD", key="pdf_edit_date")
    time = insider.time_input("Created Time (GMT+7)*:red[*]", value= st.session_state.get("pdf_edit_time", dt.now().time()), key="pdf_edit_time", step=60)
    holder_name = insider.text_input("Holder Name:red[*]", value= st.session_state.get("pdf_edit_holder_name", ""), placeholder="Enter holder name", key="pdf_edit_holder_name")
    holder_type = insider.selectbox("Holder Type:red[*]", index= ["insider", "institution"].index(st.session_state.get("pdf_edit_holder_type", "insider")), options = ["insider", "institution"], format_func=format_option, key="pdf_edit_holder_type")
    holding_before = insider.number_input("Stock Holding before Transaction:red[*]", value= st.session_state.get("pdf_edit_holding_before", 0), placeholder="Enter stock holding before transaction", key="pdf_edit_holding_before", min_value=0)
    amount_transaction = insider.number_input("Amount Transaction:red[*]", value= st.session_state.get("pdf_edit_amount_transaction", 0), placeholder="Enter amount transaction", key="pdf_edit_amount")
    trans_type = insider.selectbox("Transaction Type:red[*]", options = ["buy", "sell"],  index= ["buy", "sell"].index(st.session_state.get("pdf_edit_transaction_type", "buy")), format_func=format_option, key="pdf_edit_transaction_type")
    holding_after = insider.number_input("Stock Holding after Transaction:red[*]", value= st.session_state.get("pdf_edit_holding_after", 0), placeholder="Enter stock holding after transaction", key="pdf_edit_holding_after", min_value=0)
    subsector = insider.selectbox("Subsector:red[*]", index = available_subsectors.index(st.session_state.get("subsector", available_subsectors[0])), options = available_subsectors, format_func=format_option, key="pdf_edit_subsector")
    tags = insider.text_area("Tags:red[*]", value=st.session_state.get("pdf_edit_tags", ""), placeholder="Enter tags separated by commas, e.g. idx, market-cap", key="pdf_edit_tags")
    tickers = insider.text_area("Tickers:red[*]", value=st.session_state.get("pdf_edit_tickers", ""), placeholder="Enter tickers separated by commas, e.g. BBCA.JK, BBRI.JK", key="pdf_edit_tickers")

    price_transaction = st.session_state.get("pdf_edit_price_transaction", {"amount_transacted": [], "prices": []})
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

    st.session_state.pdf_edit_price_transaction = price_transaction

    price = insider.number_input("Price*", value= st.session_state.get("pdf_edit_price", 0), disabled=True, key="pdf_edit_price")
    transaction_value = insider.number_input("Transaction Value*", value= st.session_state.get("pdf_edit_trans_value", 0), disabled=True, key="pdf_edit_trans_value")

    submit = insider.form_submit_button("Submit", on_click=post)