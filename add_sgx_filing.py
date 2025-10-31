from supabase import create_client

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
                
                # Validate it's a list
                if not isinstance(data, list):
                    st.error("❌ JSON must contain an array of objects")
                    return
                
                st.success(f"✅ File loaded successfully! Found {len(data)} records")
                
                # Preview section
                with st.expander("👁️ Preview Data", expanded=True):
                    st.json(data[:3] if len(data) > 3 else data, expanded=False)
                    if len(data) > 3:
                        st.info(f"Showing first 3 of {len(data)} records")
                
                st.session_state['json_data'] = data
                
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