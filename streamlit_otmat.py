import streamlit as st
import time
import toml
import pandas as pd
import os
from azure.storage.filedatalake import DataLakeServiceClient
import json
import io

# URL of the publicly published Power BI dashboard
# power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiNmVhY2M3ODktNTM4Zi00YTk1LTk4OTItN2Q0NWUyNzJmOWRkIiwidCI6ImRjMjQwNWJjLTI2MDAtNDc3ZC04YjhlLTM5OTRmNWI1MzdhMyIsImMiOjl9"  # Replace with your actual URL
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
file_system_users = st.secrets["File_System2"]["file_system_users"]
sas_token_users = st.secrets["SAS_token2"]["sas_token_users"]
file = st.secrets["File"]["file"]
file_json = st.secrets["File_JSON"]["file_json"]



# Construct the account URL with the SAS token
account_url = f"https://{storage_account_name}.dfs.core.windows.net?{sas_token_users}"
service_client = DataLakeServiceClient(account_url=account_url)
# Get a list of files in your Data Lake directory (root of the container)
file_system_client = service_client.get_file_system_client(file_system=file_system_users)
paths = file_system_client.get_paths() 
files = [os.path.basename(path.name) for path in paths if not path.is_directory]

# --- Function to list files in a directory ---
def list_files_in_directory(file_system_client, directory):
    try:
        paths = file_system_client.get_paths(path=directory)
        return [path.name for path in paths if not path.is_directory]
    except Exception as e:
        st.error(f"Error listing files: {e}")
        return []


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


# Function to read user data from CSV in ADLS2
def get_user_data(file_system_client, filename=file):
    try:
        # Get the file client
        file_client = file_system_client.get_file_client(filename)

        # Download the file content
        download = file_client.download_file()
        downloaded_bytes = download.readall()

        # Read the CSV data into a Pandas DataFrame
        df = pd.read_csv(io.BytesIO(downloaded_bytes))
        return df

    except Exception as e:
        st.error(f"Error reading user data: {e}")
        return None

# Get user data
user_df = get_user_data(file_system_client)


# Function to check user authentication and get user's site
def authenticate(username, password, user_df):
    if user_df is not None:
        user = user_df.loc[user_df['username'] == username]
        if not user.empty and user['password'].values[0] == password:
            return user['site'].values[0]  # Return the user's site
    return None  # Authentication fails or site not found


# Function to read Power BI URLs from JSON in ADLS2
def get_powerbi_urls(file_system_client, filename=file_json):
    try:
        # Get the file client
        file_client = file_system_client.get_file_client(filename)

        # Download the file content
        download = file_client.download_file()
        downloaded_bytes = download.readall()

        # Read the JSON data
        powerbi_urls = json.loads(downloaded_bytes.decode('utf-8'))
        return powerbi_urls

    except Exception as e:
        st.error(f"Error reading Power BI URLs: {e}")
        return None

# Get Power BI URLs
powerbi_urls = get_powerbi_urls(file_system_client)
print(powerbi_urls)


def main():
    # Initialize session state 
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "show_title_page" not in st.session_state:
        st.session_state.show_title_page = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "site" not in st.session_state:  # Initialize 'site' in session state
        st.session_state.site = None

    # Authentication page
    if not st.session_state.authenticated:
        st.title("Login")
        username = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate(username, password_input, user_df):
                st.session_state.authenticated = True
                st.session_state.show_title_page = True
                st.session_state.username = username
                st.session_state.site = site  # Store the user's site
                st.rerun()
            else:
                st.error("Invalid username or password")

    # Title page (shown for 5 seconds after successful login)
    elif st.session_state.show_title_page:
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
        # st.title("Welcome!")
        time.sleep(5)
        st.session_state.show_title_page = False
        st.rerun()

# Power BI dashboard page (user-specific)
    else:
        st.title("Power BI Dashboard")

        # Get the Power BI URL for the logged-in user from the JSON data
        username = st.session_state.username
        site = st.session_state.site  # Get the user's site
        if powerbi_urls:
            powerbi_url = powerbi_urls.get(username)
            if powerbi_url:
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
                                                             
        # Logout button
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
            
        # # Construct the account URL with the SAS token
        # account_url_dnl = f"https://{storage_account_name}.dfs.core.windows.net?{sas_token}"
        # service_client_dnl = DataLakeServiceClient(account_url=account_url_dnl)   
         
        # # Get a list of files in your Data Lake directory (root of the container)
        # file_system_client_dnl = service_client_dnl.get_file_system_client(file_system=file_system_name)
        # paths = file_system_client_dnl.get_paths() 
        # files_dnl = [os.path.basename(path.name) for path in paths if not path.is_directory]

        # Create the selectbox
        with st.sidebar:
            try:
                # Create a DataLakeServiceClient (for public access, no credentials are needed)
                service_client = DataLakeServiceClient(account_url=f"https://{storage_account_name}.dfs.core.windows.net")

                # Get the file system client
                file_system_client = service_client.get_file_system_client(file_system=file_system_name)

                # List files in the specified directory (using site from session state)
                site = st.session_state.site
                files = list_files_in_directory(file_system_client, site)
                
                # Select file to download
                selected_file = st.sidebar.selectbox("Select a file", files)

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
            except Exception as e:
                st.sidebar.error(f"Error connecting to ADLS: {e}")
if __name__ == "__main__":
    main()