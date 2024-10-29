import streamlit as st
import time

# URL of the publicly published Power BI dashboard
power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiNmVhY2M3ODktNTM4Zi00YTk1LTk4OTItN2Q0NWUyNzJmOWRkIiwidCI6ImRjMjQwNWJjLTI2MDAtNDc3ZC04YjhlLTM5OTRmNWI1MzdhMyIsImMiOjl9"  # Replace with your actual URL
font = "Linkin Park"
font2 = "Calibri"
title_text = "Puna Wells Monitoring"

# Initialize session state variable if it doesn't exist
if "show_title" not in st.session_state:
    st.session_state.show_title = True

# Display the initial title
if st.session_state.show_title:
    st.markdown(
    """
    <style>
    body {  /* Apply to the entire page */
        background-color: lightgrey;
    .title-container {
        text-align: center; /* Center the title */
        margin-bottom: 20px; /* Add space below the title */
        margin-top: 200px
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    st.markdown(
        f"""
        <div class="title-container">
            <h1 style='
                font-size: 46px; 
                color: #767675; /* Steel Grey */
                font-family: {font},{font2};
                font-weight: bold;
                text-decoration: underline;
                line-height: 1.2;
                letter-spacing: 1px;
                text-shadow: 2px 2px 4px grey;
            '>
            <u>{title_text}</u>
            </h1>
        </div>
        """,
        # """
        # <title style='text-align: center; color: grey; font-family: {font}; font: italic bold 45px; text-shadow: 2px 2px 4px gray;'>
        # {title_text}
        # </title>  
        # """,
        unsafe_allow_html=True,
    )
    time.sleep(4)
    st.session_state.show_title = False  # Update session state
    st.rerun()

# Display the Power BI dashboard in an iframe
st.markdown(
    f"""  
    <style>
        .iframe-container {{
            position: fixed; 
            top: 6%; 
            left: 0; 
            width: 100vw; 
            height: 94vh; 
            z-index: 9999; 
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .iframe-container iframe {{
            width: 100%; 
            height: 100%; 
        }}
    </style>
    <div class="iframe-container">
       <iframe title="Power BI Dashboard" src="{power_bi_url}" frameborder="0" allowFullScreen="true"></iframe>
    </div>
    """,
    unsafe_allow_html=True,
)