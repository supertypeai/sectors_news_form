import streamlit as st

pages = {
    "Sectors News": [
        st.Page("create_news.py", title="Add News", icon="📋"),
        st.Page("edit_news.py", title="Edit News", icon="🖊️"),
        st.Page("delete_news.py", title="Delete News", icon="❗"),
        st.Page("insider_trading_pdf.py", title="Add Insider Trading (IDX Format)", icon="📂"),
        st.Page("insider_trading.py", title="Add Insider Trading (Non-IDX Format)", icon="✒️"),
        st.Page("edit_insider_trading.py", title="Edit Insider Trading", icon="🖊️"),
        st.Page("delete_insider_trading.py", title="Delete Insider Trading", icon="❕")
    ]
}


pg = st.navigation(pages)
pg.run()