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
    if not st.session_state.source or not st.session_state.subsector or not st.session_state.file:
        st.toast("Please fill out the required fields.")
    else:
        files = {
            'file': (st.session_state.file.name, st.session_state.file, 'application/pdf'),
            'source': (None, st.session_state.source, 'text/plain'),
            'sub_sector': (None, st.session_state.subsector, 'text/plain'),
            'holder_type': (None, st.session_state.holder_type, 'text/plain')
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post("https://sectors-news-endpoint.vercel.app/pdf", headers = headers, files=files)

        if response.status_code == 200:
            st.toast("Insider trading submitted successfully! 🎉")
            st.session_state.source=""
            st.session_state.subsector=available_subsectors[0]
            st.session_state.holder_type="insider"
        else:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")
  
# app
st.title("Sectors News")

insider = st.form('insider')

insider.subheader("Add Insider Trading (IDX Format)")
insider.caption(":red[*] _required_")

file = insider.file_uploader("Upload File (.pdf):red[*]", type="pdf", accept_multiple_files=False, key="file")
source = insider.text_input("Source:red[*]", placeholder="Enter URL", key="source")
subsector = insider.selectbox("Subsector:red[*]", options = available_subsectors, format_func=format_option, key="subsector")
holder_type = insider.selectbox("Holder Type:red[*]", options = ["insider", "institution"], format_func=format_option, key="holder_type")
submit = insider.form_submit_button("Submit", on_click=post)