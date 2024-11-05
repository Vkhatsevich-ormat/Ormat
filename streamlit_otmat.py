import streamlit as st
import time
from azure.storage.filedatalake import DataLakeServiceClient
import toml
import os

# URL of the publicly published Power BI dashboard
power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiNmVhY2M3ODktNTM4Zi00YTk1LTk4OTItN2Q0NWUyNzJmOWRkIiwidCI6ImRjMjQwNWJjLTI2MDAtNDc3ZC04YjhlLTM5OTRmNWI1MzdhMyIsImMiOjl9"  # Replace with your actual URL
font = "Linkin Park"
font2 = "Calibri"
title_text = "Puna Wells Monitoring"
# toml_path = "C://Users//vladislav_k//Documents//Python_Scripts//Ormat//secrets.toml"

# Azure Data Lake Storage Gen2 credentials
# Load secrets from the toml file
# secrets = toml.load(toml_path)

# Access secrets
storage_account_name = st.secrets["Storage_Account"]["storage_account_name"]
file_system_name = st.secrets["File_System"]["file_system_name"]
sas_token = st.secrets["SAS_token"]["sas_token"]
# file_path = st.secrets["File_path"]["file_path"]



def download_file_from_datalake(storage_account_name, file_system_name, sas_token, file_path):
    try:
        account_url = f"https://{storage_account_name}.dfs.core.windows.net?{sas_token}"
        service_client = DataLakeServiceClient(account_url=account_url)
        file_client = service_client.get_file_client(file_system=file_system_name, file_path=file_path)
        download = file_client.download_file()
        return download.readall()
    except Exception as e:
        st.error(f"Error downloading file: {e}")
        return None
    
def main():
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
            unsafe_allow_html=True
        )
        time.sleep(4)
        st.session_state.show_title = False  # Update session state
        # st.rerun()

        # Display the Power BI dashboard in an iframe
    with st.container():
        st.markdown(
            f"""
            <style>
                .main .block-container {{
                    overflow-y: auto; /* Enable vertical scrolling */
                    height: 100vh;   /* Set the height of the content area */
                }}
                .iframe-container {{
                    position: fixed; 
                    top: 6%; 
                    left: 10px; 
                    width: 100vw; 
                    height: 90vh; 
                    z-index: 1; 

                }}
                .iframe-container iframe {{
                    width: 75%; 
                    height: 100%; 
                }}

            </style>
            <div class="iframe-container">
                <iframe title="Power BI Dashboard" src="{power_bi_url}" frameborder="0" allowFullScreen="true"></iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # Display the Power BI dashboard in an iframe
    with st.container():
        st.markdown(
            f"""
            <style>
                .main .block-container {{
                    overflow-y: auto; /* Enable vertical scrolling */
                    height: 100vh;   /* Set the height of the content area */
                }}
                .iframe-container {{
                    position: fixed; 
                    top: 6%; 
                    left: 20%; 
                    width: 100vw; 
                    height: 90vh; 
                    z-index: 1; 

                }}
                .iframe-container iframe {{
                    width: 75%; 
                    height: 100%; 
                }}

            </style>
            <div class="iframe-container">
                <iframe title="Power BI Dashboard" src="{power_bi_url}" frameborder="0" allowFullScreen="true"></iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
     # Construct the account URL with the SAS token
    account_url = f"https://{storage_account_name}.dfs.core.windows.net?{sas_token}"
    service_client = DataLakeServiceClient(account_url=account_url)

    # Get a list of files in your Data Lake directory (root of the container)
    file_system_client = service_client.get_file_system_client(file_system=file_system_name)
    paths = file_system_client.get_paths() 
    files = [os.path.basename(path.name) for path in paths if not path.is_directory]

    # Create the selectbox
    with st.sidebar:
        selected_file = st.selectbox("Select a file to download", files)

        if selected_file:
            file_bytes = download_file_from_datalake(
                storage_account_name, file_system_name, sas_token, selected_file
            )
            if file_bytes:
                st.download_button(
                    label=f"Download {selected_file}",
                    data=file_bytes,
                    file_name=selected_file,
                    mime="application/octet-stream",  # Adjust MIME type if needed
                )
            
            
if __name__ == "__main__":
    main()