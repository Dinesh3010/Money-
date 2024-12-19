import streamlit as st
import pandas as pd
import requests
import json
from io import StringIO

# GitHub Configuration
GITHUB_REPO = "your-username/your-repo-name"
GITHUB_FILE = "expenditure_data.csv"
GITHUB_TOKEN = "your_personal_access_token"

def load_data():
    """Load data from GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        file_content = content['content']
        decoded = StringIO(file_content.encode('ascii'))
        return pd.read_csv(decoded)
    else:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

def save_data(data):
    """Save data to GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    existing_data = load_data()

    # Append new data
    if not existing_data.empty:
        data = pd.concat([existing_data, data])

    csv_content = data.to_csv(index=False)
    encoded_content = csv_content.encode('ascii')

    # Check if the file exists
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()['sha']
        payload = {
            "message": "Update expenditure data",
            "content": encoded_content.decode(),
            "sha": sha
        }
    else:
        payload = {
            "message": "Create expenditure data",
            "content": encoded_content.decode()
        }

    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code not in [200, 201]:
        st.error("Failed to save data to GitHub.")
    else:
        st.success("Data saved successfully to GitHub.")

# Streamlit App
st.title("Money Expenditure Tracker")

# Input Form
with st.form("expenditure_form"):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Other"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    description = st.text_area("Description")
    submitted = st.form_submit_button("Submit")

    if submitted:
        new_data = pd.DataFrame({
            "Date": [date],
            "Category": [category],
            "Amount": [amount],
            "Description": [description]
        })
        save_data(new_data)

# Display Data
st.subheader("Expenditure Data")
data = load_data()
st.dataframe(data)
