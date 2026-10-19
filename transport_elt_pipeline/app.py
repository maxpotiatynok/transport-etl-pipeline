import streamlit as st
from transport_elt_pipeline.analytics import AnalyticsClient

analytics = AnalyticsClient()

st.title("London Underground Dashboard", text_alignment="center")
st.subheader(f":gray[*Total Poll Coverage: {round(analytics.total_poll_coverage(), 2)}%*]", text_alignment="center")

