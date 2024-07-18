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

def post():
    if not st.session_state.source or not st.session_state.date or not st.session_state.time or not st.session_state.doc_number or not st.session_state.company_name or not st.session_state.shareholder_name or not st.session_state.subsector or not st.session_state.ticker or not st.session_state.category or not st.session_state.control_status or not st.session_state.holding_before or not st.session_state.holding_after or not st.session_state.purpose or not st.session_state.holder_type:
        st.toast("Please fill out the required fields.")
    else:
        data = {
            "document_number": st.session_state.doc_number,
            "company_name": st.session_state.company_name,
            "shareholder_name": st.session_state.shareholder_name,
            "source": st.session_state.source,
            "ticker": st.session_state.ticker,
            "category": st.session_state.category,
            "control_status": st.session_state.control_status,
            "holding_before": st.session_state.holding_before, 
            "holding_after": st.session_state.holding_after,
            "sub_sector": st.session_state.subsector,
            "purpose": st.session_state.purpose,
            "holder_type": st.session_state.holder_type,
            "date_time": dt.combine(st.session_state.date, st.session_state.time).strftime("%Y-%m-%d %H:%M:%S")
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post("https://sectors-news-endpoint.vercel.app/insider-trading", headers = headers, json=data)

        if response.status_code == 200:
            st.toast("Insider Trading submitted successfully! 🎉")
            st.session_state.doc_number = ""
            st.session_state.company_name = ""
            st.session_state.shareholder_name = ""
            st.session_state.source = ""
            st.session_state.ticker = ""
            st.session_state.category = ""
            st.session_state.control_status = ""
            st.session_state.holding_before = 0
            st.session_state.holding_after = 0
            st.session_state.subsector = available_subsectors[0]
            st.session_state.purpose = ""
            st.session_state.holder_type="insider"
            st.session_state.date = dt.today()
            st.session_state.time = dt.now()
        else:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")
  
# app
st.title("Sectors News")

insider = st.form('insider')

insider.subheader("Add Insider Trading (Non-IDX Format)")
insider.caption(":red[*] _required_")
source = insider.text_input("Source:red[*]", placeholder="Enter URL", key="source")
date = insider.date_input("Created Date (GMT+7):red[*]", max_value=dt.today(), format="YYYY-MM-DD", key="date")
time = insider.time_input("Created Time (GMT+7)*:red[*]", key="time", step=60)
doc_number = insider.text_input("Document Number:red[*]", placeholder="Enter document number", key="doc_number")
company_name = insider.text_input("Company Name:red[*]", placeholder="Enter company name", key="company_name")
shareholder_name = insider.text_input("Shareholder Name:red[*]", placeholder="Enter shareholder name", key="shareholder_name")
subsector = insider.selectbox("Subsector:red[*]", options = available_subsectors, format_func=format_option, key="subsector")
ticker = insider.text_input("Ticker:red[*]", placeholder="Enter ticker", key="ticker")
category = insider.text_input("Category:red[*]", placeholder="Enter category", key="category")
control_status = insider.text_input("Control Status:red[*]", placeholder="Enter control status", key="control_status")
holding_before = insider.number_input("Stock Holding before Transaction:red[*]", placeholder="Enter stock holding before transaction", key="holding_before", min_value=0)
holding_after = insider.number_input("Stock Holding after Transaction:red[*]", placeholder="Enter stock holding after transaction", key="holding_after", min_value=0)
purpose = insider.text_input("Transaction Purpose:red[*]", placeholder="Enter transaction purpose", key="purpose")
holder_type = insider.selectbox("Holder Type:red[*]", options = ["insider", "institution"], format_func=format_option, key="holder_type")
submit = insider.form_submit_button("Submit", on_click=post)