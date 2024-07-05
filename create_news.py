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
    if not st.session_state.source or not st.session_state.date or not st.session_state.time or not st.session_state.subsector or not st.session_state.tags or not st.session_state.tickers:
        st.toast("Please fill out the required fields.")
    else:
        # process form data
        tags_list = [tag.strip() for tag in st.session_state.tags.split(',') if tag.strip()]
        tickers_list = [ticker.strip() for ticker in st.session_state.tickers.split(',') if ticker.strip()]

        data = {
            "title": st.session_state.title,
            "body": st.session_state.body,
            "source": st.session_state.source,
            "timestamp": dt.combine(st.session_state.date, st.session_state.time).strftime("%Y-%m-%d %H:%M:%S"),
            "subsector": st.session_state.subsector,
            "tags": tags_list,
            "tickers": tickers_list
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post("https://sectors-news-endpoint.vercel.app/articles", headers = headers, json=data)

        if response.status_code == 200:
            st.toast("News submitted successfully! 🎉")
            st.session_state.title=""
            st.session_state.body=""
            st.session_state.source=""
            st.session_state.date=dt.today()
            st.session_state.time=dt.now()
            st.session_state.subsector=available_subsectors[0]
            st.session_state.tags=""
            st.session_state.tickers=""
        else:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")
  
# app
st.title("Sectors News")

news = st.form('news')

news.subheader("Post News")
news.caption(":red[*] _required_")
title = news.text_input("Title", placeholder="Enter title", key="title")
body = news.text_area("Body", placeholder="Enter body", key="body")
source = news.text_input("Source:red[*]", placeholder="Enter URL", key="source")
date = news.date_input("Created Date (GMT+7):red[*]", max_value=dt.today(), format="YYYY-MM-DD", key="date")
time = news.time_input("Created Time (GMT+7)*:red[*]", key="time", step=60)
subsector = news.selectbox("Subsector:red[*]", options = available_subsectors, format_func=format_option, key="subsector")
tags = news.text_area("Tags:red[*]", placeholder="Enter tags seperated by commas, e.g. idx, market-cap", key="tags")
tickers = news.text_area("Tickers:red[*]", placeholder="Enter tickers seperated by commas, e.g. BBCA.JK, BBRI.JK", key="tickers")
submit = news.form_submit_button("Submit", on_click=post)