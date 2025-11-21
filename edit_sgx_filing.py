from supabase import create_client

import streamlit as st


# Setup env
API_KEY = st.secrets["API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


def fetch_data_fillings() -> list[dict]:
    supabase_client = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)
    try:
        response = supabase_client.table("sgx_filings").select("*").execute()
        if response.data is not None:
            return response.data
        else:
            st.error("Error fetching data insider trading. Please reload the app.")
            return None
        
    except Exception as error:
        st.error(f"Exception while fetching data insider trading: {error}")
        return None


def upsert_data(data):
    try:
        supabase_client = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)
        response = (
            supabase_client
            .table('sgx_filings')
            .upsert(data, on_conflict='id')
            .execute()
        )
        return {"success": True, "data": response.data}
    except Exception as error:
        return {"success": False, "error": str(error)}


@st.cache_data
def get_data():
    return fetch_data_fillings()


def back():
    st.session_state.edit_view = "view1"


def edit():
    selected_id = st.session_state.sgx_edit_id

    if selected_id is not None:
        st.session_state.edit_view = "view2" 

    data = get_data()
    prev_data = next((item for item in data if item["id"] == selected_id), None)
    if prev_data:
        st.session_state.edit_data = prev_data


def submit():
    updated_data = {
        "id": st.session_state.sgx_edit_id,
        "url": st.session_state.edit_url,
        "symbol": st.session_state.edit_symbol,
        "transaction_date": str(st.session_state.edit_transaction_date),
        "shareholder_name": st.session_state.edit_shareholder_name,
        "transaction_type": st.session_state.edit_transaction_type,
        "number_of_stock": st.session_state.edit_number_of_stock,
        "value": st.session_state.edit_value,
        "price_per_share": st.session_state.edit_price_per_share,
        "shares_before": st.session_state.edit_shares_before,
        "shares_before_percentage": st.session_state.edit_shares_before_percentage,
        "shares_after": st.session_state.edit_shares_after,
        "shares_after_percentage": st.session_state.edit_shares_after_percentage,
    }
    
    result = upsert_data(updated_data)

    if result["success"]:
        st.session_state.submit_result = {
            "success": True,
            "data": updated_data
        }
        st.cache_data.clear()
        st.session_state.edit_view = "view1"
        st.session_state.pop("edit_data", None)
    else:
        st.session_state.submit_result = {
            "success": False,
            "error": result["error"],
            "data": updated_data
        }


def main_ui():
    if 'edit_view' not in st.session_state:
        st.session_state.edit_view = 'view1' 

    if st.session_state.get("submit_result"):
        result = st.session_state.submit_result
        
        if result["success"]:
            st.success(f"Successfully updated Filing #{result['data']['id']}")
            with st.expander("Data Sent"):
                st.json(result["data"])
            st.session_state.pop("submit_result", None)
        else:
            st.error(f"Failed to update Filing #{result['data']['id']}")
            with st.expander("Error Details"):
                st.write("**Error:**", result["error"])
                st.write("**Data Attempted:**")
                st.json(result["data"])
            st.session_state.pop("submit_result", None)

    data = get_data()

    if st.session_state.edit_view == 'view1':
        if (len(data) > 0):
            form = st.form("edit")
            form.selectbox(
                "Select id", 
                [index['id'] for index in sorted(data, key=lambda x: x["id"])], 
                key="sgx_edit_id"
            )
            form.form_submit_button("Edit", type="primary", on_click=edit)

            st.dataframe(sorted(data, key=lambda x: x["id"], reverse=True), 
            column_order = [
                "id", 
                "url", 
                "symbol", 
                "transaction_date", 
                "transaction_type", 
                "value", 
                "price_per_share",
                "number_of_stock",           
                "shares_before",             
                "shares_before_percentage",  
                "shares_after",              
                "shares_after_percentage",   
                "shareholder_name"           
            ],
            selection_mode="single-row"
            )
        else: 
            st.info("There is no insider tradings in the database.")
            st.page_link("add_sgx_filings.py", label="Add SGX Filings", icon=":material/arrow_back:")

    elif st.session_state.edit_view == 'view2':
        prev = st.session_state.get("edit_data", {})
        
        sgx_filing = st.form('insider') 
        sgx_filing.form_submit_button("< Back", on_click=back)

        # ID form
        sgx_filing.text_input(
            "ID*", 
            value= st.session_state.get("sgx_edit_id", ""), 
            disabled=True, 
            key="sgx_edit_id"
        )

        sgx_filing.text_input(
            "URL*",
            value=prev.get("url", ""),
            key="edit_url"
        )

        sgx_filing.text_input(
            "Symbol*",
            value=prev.get("symbol", ""),
            key="edit_symbol"
        )

        sgx_filing.date_input(
            "Transaction Date*",
            value=prev.get("transaction_date"),
            key="edit_transaction_date"
        )

        sgx_filing.text_input(
            "Shareholder Name*",
            value=prev.get("shareholder_name", ""),
            key="edit_shareholder_name"
        )

        sgx_filing.selectbox(
            "Transaction Type",
            options=['others', "buy", "sell", "transfer", "award"],
            index=['others', "buy", "sell", "transfer", "award"].index(prev.get("transaction_type", "").lower())
                if prev.get("transaction_type", "").lower() in ['others', "buy", "sell", "transfer", "award"] else 0,
            key="edit_transaction_type"
        )
        
        sgx_filing.number_input(
            "Number of Stock",
            value=prev.get("number_of_stock") or 0.0,
            key="edit_number_of_stock"
        )

        sgx_filing.number_input(
            "Value",
            value=prev.get("value") or 0.0,
            key="edit_value"
        )

        sgx_filing.number_input(
            "Price per Share",
            value=prev.get("price_per_share") or 0.0,
            format="%.5f",
            key="edit_price_per_share"
        )

        sgx_filing.number_input(
            "Shares Before",
            value=prev.get("shares_before") or 0.0,
            key="edit_shares_before"
        )

        sgx_filing.number_input(
            "Shares Before Percentage",
            value=prev.get("shares_before_percentage") or 0.0,
            format="%.5f",
            key="edit_shares_before_percentage"
        )

        sgx_filing.number_input(
            "Shares After",
            value=prev.get("shares_after") or 0.0,
            key="edit_shares_after"
        )

        sgx_filing.number_input(
            "Shares After Percentage",
            value=prev.get("shares_after_percentage") or 0.0,
            format="%.5f",
            key="edit_shares_after_percentage"
        )

        sgx_filing.form_submit_button('Submit', type='primary', on_click=submit)


if __name__ == '__main__':
    main_ui()
