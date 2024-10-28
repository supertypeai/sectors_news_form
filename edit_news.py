import streamlit as st
from datetime import datetime as dt
import requests
import json

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
    selected_id = st.session_state.edit_id
    if selected_id != None:
        st.session_state.view_edit = "view2"
        prev_data = next((item for item in data if item["id"] == selected_id), None)
        if prev_data:
            st.session_state.edit_title=prev_data["title"]
            st.session_state.edit_body=prev_data["body"]
            st.session_state.edit_source=prev_data["source"]
            st.session_state.edit_date=dt.strptime(prev_data["timestamp"], "%Y-%m-%dT%H:%M:%S").date()
            st.session_state.edit_time=dt.strptime(prev_data["timestamp"], "%Y-%m-%dT%H:%M:%S").time()
            st.session_state.edit_subsector=[option for option in prev_data["sub_sector"] if option in available_subsectors]
            st.session_state.edit_tags=", ".join(prev_data["tags"])
            st.session_state.edit_tickers=", ".join(prev_data["tickers"])
            st.session_state.edit_dimension = json.dumps(prev_data["dimension"])
    else:
        st.toast("Please select 1 id.")

def post():
    if not st.session_state.edit_source or not st.session_state.edit_date or not st.session_state.edit_time or not st.session_state.edit_tags:
        st.toast("Please fill out the required fields.")
    else:
        # process form data
        selected_id = st.session_state.edit_id
        tags_list = [tag.strip() for tag in st.session_state.edit_tags.split(',') if tag.strip()]
        tickers_list = [ticker.strip() for ticker in st.session_state.edit_tickers.split(',') if ticker.strip()] if st.session_state.edit_tickers else []

        data = {
            "id": selected_id,
            "title": st.session_state.edit_title,
            "body": st.session_state.edit_body,
            "source": st.session_state.edit_source,
            "timestamp": dt.combine(st.session_state.edit_date, st.session_state.edit_time).strftime("%Y-%m-%d %H:%M:%S"),
            "sub_sector": st.session_state.edit_subsector,
            "tags": tags_list,
            "tickers": tickers_list,
            "dimension": json.loads(st.session_state.edit_dimension)
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.patch(f"https://sectors-news-endpoint.fly.dev/articles", headers = headers, json=data)

        if response.status_code == 200:
            st.toast("News editted successfully! 🎉")
            st.session_state.edit_title=""
            st.session_state.edit_body=""
            st.session_state.edit_source=""
            st.session_state.edit_date=dt.today()
            st.session_state.edit_time=dt.now()
            st.session_state.edit_subsector=""
            st.session_state.edit_tags=""
            st.session_state.edit_tickers=""
            st.session_state.edit_dimension=""
            st.session_state.view_edit = 'view1'
        else:
            # Handle error
            st.error(f"Error: Something went wrong. Please try again.")

def back():
    st.session_state.view_edit = "view1"

# app
if 'view_edit' not in st.session_state:
    st.session_state.view_edit = 'view1'

st.title("Sectors News")

if st.session_state.view_edit == "view1":
    st.subheader("Edit News")

    if (len(data) > 0):
        form = st.form("edit")
        selected_id = form.selectbox("Select id", [i['id'] for i in sorted(data, key=lambda x: x["id"])], key="edit_id")
        form.form_submit_button("Edit", type="primary", on_click=edit)

        st.dataframe(sorted(data, key=lambda x: x["id"], reverse=True), 
            column_order=["id", "title", "body", "source", "timestamp", "sector", "sub_sector", "tags", "tickers", "dimension", "score"],
            selection_mode="single-row"
        )
    else: 
        st.info("There is no news in the database.")
        st.page_link("create_news.py", label="Create News", icon=":material/arrow_back:")

elif st.session_state.view_edit == "view2":
    edit_news = st.form('edit_news')

    edit_news.subheader("Edit News")
    back_button = edit_news.form_submit_button("< Back", on_click=back)
    edit_news.caption(":red[*] _required_")
    id = edit_news.text_input("ID*", value= st.session_state.get("edit_id", ""), disabled=True, key="edit_id")
    title = edit_news.text_input("Title", value=st.session_state.get("edit_title", ""), placeholder="Enter title", key="edit_title")
    body = edit_news.text_area("Body", value=st.session_state.get("edit_body", ""), placeholder="Enter body", key="edit_body")
    source = edit_news.text_input("Source:red[*]", value=st.session_state.get("edit_source", ""), placeholder="Enter URL", key="edit_source")
    date = edit_news.date_input("Created Date (GMT+7):red[*]", value=st.session_state.get("edit_date", dt.today()), max_value=dt.today(), format="YYYY-MM-DD", key="edit_date")
    time = edit_news.time_input("Created Time (GMT+7)*:red[*]", value=st.session_state.get("edit_time", dt.now().time()), key="edit_time", step=60)
    subsector = edit_news.multiselect("Subsector", options=available_subsectors, default=[option for option in st.session_state.get("edit_subsector", [available_subsectors[0]]) if option in available_subsectors], format_func=format_option, key="edit_subsector")
    tags = edit_news.text_area("Tags:red[*]", value=st.session_state.get("edit_tags", ""), placeholder="Enter tags separated by commas, e.g. idx, market-cap", key="edit_tags")
    tickers = edit_news.text_area("Tickers", value=st.session_state.get("edit_tickers", ""), placeholder="Enter tickers separated by commas, e.g. BBCA.JK, BBRI.JK", key="edit_tickers")
    dimension = edit_news.text_area("Dimension:red[*]", value=st.session_state.get("edit_dimension", ""), placeholder="Enter dimension", key="dimension")
    submit2 = edit_news.form_submit_button("Submit", on_click=post, type="primary")        
