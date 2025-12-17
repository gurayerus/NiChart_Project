import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

def set_global_style():
    st.markdown(
        """
        <style>
        html, body, [class*="css"]  {
            font-size: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def config_page() -> None:
    nicon = Image.open("../resources/nichart1.png")
    st.set_page_config(
        page_title="NiChart",
        page_icon=nicon,
        layout="wide",
        #layout="centered",
        menu_items={
            "Get help": "https://neuroimagingchart.com/",
            "Report a bug": "https://github.com/CBICA/NiChart_Project/issues/new?assignees=&labels=&projects=&template=bug_report.md&title=%5BBUG%5D+",
            "About": "https://neuroimagingchart.com/",
        },
    )

def add_sidebar_options():
    with st.sidebar:

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(
                "[![GitHub](https://img.shields.io/badge/GitHub-Repo-8DA1EE?style=for-the-badge&logo=github&logoColor=white)](https://github.com/CBICA/NiChart_Project)"
            )
        with col2:
            st.markdown(
                "[![ISTAGING](https://img.shields.io/badge/NiChart-Web-C744C2?style=for-the-badge&logoColor=white)](https://neuroimagingchart.com)"
            )
