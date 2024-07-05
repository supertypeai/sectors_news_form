import streamlit as st

pages = {
    "Sectors News": [
        st.Page("create_news.py", title="Post News", icon="📋"),
        st.Page("insider_trading.py", title="Post Insider Trading", icon="📂"),
        st.Page("edit_news.py", title="Edit News", icon="✏️")
    ]
}


pg = st.navigation(pages)
pg.run()