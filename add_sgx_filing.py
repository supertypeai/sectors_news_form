from supabase import create_client

from utils.add_sgx_filings_helper import generate_title_and_body

import streamlit as st 
import json
import time
import requests
import traceback


API_KEY = st.secrets["API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

CREATE_CLIENT_SUPABASE = create_client(
    supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY
)


def push_data(payload: list[dict[str, any]], table_name: str):
    try:
        response = (
            CREATE_CLIENT_SUPABASE
            .table(table_name)
            .insert(payload)
            .execute()
        )

        if response.data:
            return True, "Data pushed successfully!"
        
        return False, 'Data pushed failed!'
    
    except Exception as error:
        return False, f"Error: {str(error)}"


def run_generate_title_and_body(records: list[dict]) ->list[dict]:
    for record in records:
        holder_name = record.get('holder_name')
        issuer_name = record.get('issuer_name')
        tx_type = record.get('transaction_type')
        amount = record.get('amount_transaction')
        holding_before = record.get('holding_before')
        holding_after = record.get('holding_after')

        title, body = generate_title_and_body(
            holder_name=holder_name, 
            company_name=issuer_name, 
            tx_type=tx_type, 
            amount=amount, 
            holding_before=holding_before, 
            holding_after=holding_after,
            purpose_en=None
        )

        record['title'] = title
        record['body'] = body 
    
    return records 


def main_ui():
    st.set_page_config(
        page_title="SGX Filing Uploader",
        page_icon="📤",
        layout="centered"
    )
    
    st.title("📤 SGX Filing Uploader")
    
    st.divider()
    
    with st.container(border=True):
        st.subheader("📁 Upload JSON File")
        st.caption("no need to remove any keys in the json")
        
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=['json'],
            help="Upload a JSON file containing an array of objects"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read()
                data = json.loads(content)
                
                headers = {"Authorization": f"Bearer {API_KEY}"}

                response = requests.post(
                    "https://sectors-news-endpoint.fly.dev/sgx-insider-trading",
                    headers=headers,
                    json=data,
                    timeout=60
                )

                if not response.ok:
                    try:
                        st.error(f"❌ API {response.status_code}: {response.json()}")
                    
                    except Exception:
                        st.error(f"❌ API {response.status_code}: {response.text}")
                    
                    st.stop()

                payload_news = response.json()['data']

                payload = run_generate_title_and_body(data)

                payload_filing = [
                    {
                        key: value for key, value in record.items()
                        if key not in {'reasons', 'issuer_name', 'circumstances_desc'}
                    }
                    for record in payload
                ]

                if not isinstance(payload_filing, list):
                    st.error("❌ JSON must contain an array of objects")
                    return
                
                st.success(f"✅ File loaded successfully! Found {len(payload_filing)} records")

                with st.expander("Preview Data to sgx_filings", expanded=True):
                    st.json(payload_filing[:3] if len(data) > 3 else payload_filing, expanded=False)
                    if len(payload_filing) > 3:
                        st.info(f"Showing first 3 of {len(payload_filing)} records")

                with st.expander("Preview Data to sgx_News", expanded=True):
                    st.json(payload_news[:3] if len(payload_news) > 3 else payload_news, expanded=False)
                    if len(payload_news) > 3:
                        st.info(f"Showing first 3 of {len(payload_news)} records")

                st.session_state['json_data_filing'] = payload_filing
                st.session_state['json_data_news'] = payload_news
                
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format. Please upload a valid JSON file.")

            except Exception as error:
                st.error(f"❌ {type(error).__name__}: {str(error)}")
                st.code(traceback.format_exc(), language="text")
    
    st.divider()
    
    if 'json_data_filing' in st.session_state and 'json_data_news' in st.session_state:
        _, col2, _ = st.columns([1, 2, 1])

        with col2:
            if st.button(
                "📤 Submit to Database",
                type="primary",
                use_container_width=True
            ):
                with st.spinner("Pushing data to database..."):
                    success_filing, message_filing = push_data(st.session_state.json_data_filing, "sgx_filings")
                    success_news, message_news = push_data(st.session_state.json_data_news, "sgx_news")

                    if success_filing and success_news:
                        st.success("✅ Both sgx_filings and sgx_news pushed successfully!")
                        
                        del st.session_state['json_data_filing']
                        del st.session_state['json_data_news']
                        
                        time.sleep(3.5)
                        st.rerun()

                    else:
                        if not success_filing:
                            st.error(f"❌ sgx_filings: {message_filing}")
                        
                        if not success_news:
                            st.error(f"❌ sgx_news: {message_news}")
    else:
        st.info("👆 Please upload a JSON file to continue")


if __name__ == '__main__':
    main_ui()