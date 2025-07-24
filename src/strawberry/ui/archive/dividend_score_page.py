from src.ui.page import Page
import streamlit as st

class DividendScorePage(Page):
    def render(self):
        # header area
        header_cols = st.columns([2, 1, 1])
        with header_cols[0]:
            st.header("💰 Dividend Score Page")

            
        st.write("Lettuces are leafy greens—great for salads!")