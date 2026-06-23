import streamlit as st
from navbar import show_navbar

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

show_navbar()

st.markdown("""
<h1 style='text-align:center;'>
    Pitch Perfect Buzz
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    background: linear-gradient(to right, #1e1b4b, #311042);
    padding: 30px;
    border-radius: 15px;
    border-left: 5px solid #ff4b4b;
    color: white;
">
    <h2>Welcome to the Cricket Analytics Dashboard! 🏏</h2>
    <p>
        Track live matches, explore player statistics, uncover SQL-powered insights,
        visualize performance trends, and manage cricket data through an interactive platform.
    </p>
</div>
""", unsafe_allow_html=True)