import streamlit as st

pages = {
    "Sectors News": [
        st.Page("create_news.py", title="Create News", icon="📋"),
        st.Page("edit_news.py", title="Edit News", icon="✏️")
    ]
}


pg = st.navigation(pages)
pg.run()