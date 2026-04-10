from supabase import create_client

from utils.add_sgx_filings_helper import generate_title_and_body

import streamlit as st 
import json 
import time

API_KEY = st.secrets["API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

CREATE_CLIENT_SUPABASE = create_client(
    supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY
)


def push_data(payload: list[dict[str, any]]):
    try:
        response = (
            CREATE_CLIENT_SUPABASE
            .table('sgx_filings')
            .insert(payload)
            .execute()
        )
        if response.data:
            return True, "Data pushed successfully!"
        return False, 'Data pushed failed!'
    
    except Exception as error:
        return False, f"Error: {str(error)}"


def sanitize_data(records: list[dict]) ->list[dict]:
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
        
        record.pop("reasons", None)
        record.pop("issuer_name", None)
    
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
        
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=['json'],
            help="Upload a JSON file containing an array of objects"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read()
                data = json.loads(content)
                
                sanitized_data = sanitize_data(data)

                # Validate it's a list
                if not isinstance(sanitized_data, list):
                    st.error("❌ JSON must contain an array of objects")
                    return
                
                st.success(f"✅ File loaded successfully! Found {len(sanitized_data)} records")
                
                # Preview section
                with st.expander("👁️ Preview Data", expanded=True):
                    st.json(sanitized_data[:3] if len(data) > 3 else sanitized_data, expanded=False)
                    
                    if len(sanitized_data) > 3:
                        st.info(f"Showing first 3 of {len(sanitized_data)} records")
                
                st.session_state['json_data'] = sanitized_data
                
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format. Please upload a valid JSON file.")
            except Exception as error:
                st.error(f"❌ Error reading file: {str(error)}")
    
    st.divider()
    
    if 'json_data' in st.session_state and st.session_state.json_data:
        _, col2, _ = st.columns([1, 2, 1])
        
        with col2:
            if st.button(
                "📤 Submit to Database",
                type="primary",
                use_container_width=True
            ):
                with st.spinner("Pushing data to database..."):
                    success, message = push_data(st.session_state.json_data)
                    
                    if success:
                        st.success(message)
                        # Clear session state after successful submission
                        del st.session_state['json_data']
                        time.sleep(3.5)
                        st.rerun()
                    else:
                        st.error(message)
    else:
        st.info("👆 Please upload a JSON file to continue")


if __name__ == '__main__':
    main_ui()