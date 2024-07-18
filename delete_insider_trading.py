import streamlit as st
from datetime import datetime as dt
import requests

# data
api_key = st.secrets["API_KEY"]

# helper functions
def fetch():
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get("https://sectors-news-endpoint.vercel.app/insider-trading", headers = headers)

    if response.status_code == 200:
        return response.json()
    else:
        # Handle error
        st.error(f"Error fetching insider trading data. Please reload the app.")
data = fetch()

def delete():
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    deleted = {
        "id_list": st.session_state.ids
    }
    response = requests.delete(f"https://sectors-news-endpoint.vercel.app/insider-trading", headers = headers, json=deleted)

    if response.status_code != 200:
        # Handle error
        st.error(f"Error deleting insider trading data. Please try again.")
    else:
        st.toast("Selected insider trading are successfully deleted!")
    st.rerun()

@st.experimental_dialog("Delete Insider Trading")
def dialog():
    st.write(f"Are you sure you want to delete insider trading with the following id(s): {st.session_state.ids}?")
    if st.button("Yes", type="primary"):
        delete()

# app
st.title("Sectors News")

st.subheader("Delete Insider Trading")

if (len(data) > 0):
    form = st.form("edit")
    selected_ids = form.multiselect("Select id(s)", [i['id'] for i in data], key="ids")
    if form.form_submit_button("Delete", type="primary"):
        if len(selected_ids) > 0:
            dialog()
        else:
            st.toast("Please select at least 1 id.")

    st.dataframe(data, 
        column_order=["id", "title", "body", "source", "timestamp", "sector", "subsector", "tags", "tickers", "transaction_type", "holding_before", "holding_after", "amount_transaction", "holder_type"],
        selection_mode="single-row"
    )
else: 
    st.info("There is no insider trading in the database.")
    st.page_link("create_news.py", label="Create Insider Trading", icon=":material/arrow_back:")