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

    response = requests.get("https://sectors-news-endpoint.fly.dev/articles", headers = headers)

    if response.status_code == 200:
        return response.json()
    else:
        # Handle error
        st.error(f"Error fetching news data. Please reload the app.")
data = fetch()

def format_option(option):
    return option.replace("-", " ").title()

def edit():
    selected_id = st.session_state.id
    if selected_id != None:
        st.session_state.view = "view2"
        prev_data = next((item for item in data if item["id"] == selected_id), None)
        if prev_data:
            st.session_state.title=prev_data["title"]
            st.session_state.body=prev_data["body"]
            st.session_state.source=prev_data["source"]
            st.session_state.date=dt.strptime(prev_data["timestamp"], "%Y-%m-%dT%H:%M:%S").date()
            st.session_state.time=dt.strptime(prev_data["timestamp"], "%Y-%m-%dT%H:%M:%S").time()
            st.session_state.subsector=prev_data["sub_sector"]
            st.session_state.tags=", ".join(prev_data["tags"])
            st.session_state.tickers=", ".join(prev_data["tickers"])
    else:
        st.toast("Please select 1 id.")

def post():
    if not st.session_state.source or not st.session_state.date or not st.session_state.time or not st.session_state.subsector or not st.session_state.tags or not st.session_state.tickers:
        st.toast("Please fill out the required fields.")
    else:
        # process form data
        selected_id = st.session_state.id
        tags_list = [tag.strip() for tag in st.session_state.tags.split(',') if tag.strip()]
        tickers_list = [ticker.strip() for ticker in st.session_state.tickers.split(',') if ticker.strip()]

        data = {
            "id": selected_id,
            "title": st.session_state.title,
            "body": st.session_state.body,
            "source": st.session_state.source,
            "timestamp": dt.combine(st.session_state.date, st.session_state.time).strftime("%Y-%m-%d %H:%M:%S"),
            "sub_sector": st.session_state.subsector,
            "tags": tags_list,
            "tickers": tickers_list
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.patch(f"https://sectors-news-endpoint.fly.dev/articles", headers = headers, json=data)

        if response.status_code == 200:
            st.toast("News editted successfully! 🎉")
            st.session_state.title=""
            st.session_state.body=""
            st.session_state.source=""
            st.session_state.date=dt.today()
            st.session_state.time=dt.now()
            st.session_state.subsector=available_subsectors[0]
            st.session_state.tags=""
            st.session_state.tickers=""
            st.session_state.view = 'view1'
        else:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")

def back():
    st.session_state.view = "view1"

# app
if 'view' not in st.session_state:
    st.session_state.view = 'view1'

st.title("Sectors News")

if st.session_state.view == "view1":
    st.subheader("Edit News")

    if (len(data) > 0):
        form = st.form("edit")
        selected_id = form.selectbox("Select id", [i['id'] for i in sorted(data, key=lambda x: x["id"])], key="id")
        form.form_submit_button("Edit", type="primary", on_click=edit)

        st.dataframe(sorted(data, key=lambda x: x["id"], reverse=True), 
            column_order=["id", "title", "body", "source", "timestamp", "sector", "subsector", "tags", "tickers"],
            selection_mode="single-row"
        )
    else: 
        st.info("There is no news in the database.")
        st.page_link("create_news.py", label="Create News", icon=":material/arrow_back:")

elif st.session_state.view == "view2":
    edit_news = st.form('edit_news')

    edit_news.subheader("Edit News")
    back_button = edit_news.form_submit_button("< Back", on_click=back)
    edit_news.caption(":red[*] _required_")
    id = edit_news.text_input("ID*", value= st.session_state.get("id", ""), disabled=True, key="id")
    title = edit_news.text_input("Title", value=st.session_state.get("title", ""), placeholder="Enter title", key="title")
    body = edit_news.text_area("Body", value=st.session_state.get("body", ""), placeholder="Enter body", key="body")
    source = edit_news.text_input("Source:red[*]", value=st.session_state.get("source", ""), placeholder="Enter URL", key="source")
    date = edit_news.date_input("Created Date (GMT+7):red[*]", value=st.session_state.get("date", dt.today()), max_value=dt.today(), format="YYYY-MM-DD", key="date")
    time = edit_news.time_input("Created Time (GMT+7)*:red[*]", value=st.session_state.get("time", dt.now().time()), key="time", step=60)
    subsector = edit_news.selectbox("Subsector:red[*]", options=available_subsectors, index=available_subsectors.index(st.session_state.get("subsector", available_subsectors[0])), format_func=format_option, key="subsector")
    tags = edit_news.text_area("Tags:red[*]", value=st.session_state.get("tags", ""), placeholder="Enter tags separated by commas, e.g. idx, market-cap", key="tags")
    tickers = edit_news.text_area("Tickers:red[*]", value=st.session_state.get("tickers", ""), placeholder="Enter tickers separated by commas, e.g. BBCA.JK, BBRI.JK", key="tickers")

    submit2 = edit_news.form_submit_button("Submit", on_click=post, type="primary")        
