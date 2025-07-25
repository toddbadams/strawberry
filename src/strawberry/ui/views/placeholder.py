import streamlit as st

from strawberry.ui.views.base_view import BasePlaceholderView


class PlaceholderView(BasePlaceholderView):

    def render(self, ticker: str = None):
        st.info("This view is under construction. Please check back later.")
