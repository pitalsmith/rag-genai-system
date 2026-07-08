import streamlit as st
import requests
import os
import pandas as pd
import datetime

# --- Helper Function to Get File Info ---
def get_file_list():
# Go up one level from 'frontend' to find 'temp_files'
    folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "temp_files")
    
    # Debug: See where it's looking in your terminal
    print(f"DEBUG: Looking for files in: {folder_path}")
    
    if not os.path.exists(folder_path):
        return pd.DataFrame(columns=["FILE NAME", "SIZE", "ADDED"])
    
    files_data = []
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            # Get file size in KB
            size_kb = round(os.path.getsize(filepath) / 1024, 2)
            # Get last modified time
            mtime = os.path.getmtime(filepath)
            date_added = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            
            files_data.append({
                "FILE NAME": filename,
                "SIZE": f"{size_kb} KB",
                "ADDED": date_added
            })
    
    return pd.DataFrame(files_data)

# Page Configuration
st.set_page_config(layout="wide", page_title="AI Assistant")

# --- Sidebar ---
with st.sidebar:
    st.title("Mike Taylor")
    st.markdown("---")
    st.subheader("WORKSPACE")
    st.write("🏠 Home")
    st.write("👤 Team")
    st.subheader("PROJECTS")
    st.write("📂 Design System")
    st.write("📊 Marketing")
    st.markdown("---")
    st.subheader("TAGS")
    st.write("● Urgent")
    st.write("● Reviewed")

# --- Layout: Main Content (2 Columns) ---
col1, col2 = st.columns([1, 2])



# Left Column: File Management
with col1:
    st.header("Upload Knowledge")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
    
    if uploaded_file is not None:
        if st.button("Index File"):
            files = {"file": (uploaded_file.name, uploaded_file)}
            try:
                response = requests.post("http://127.0.0.1:8000/upload", files=files)
                if response.status_code == 200:
                    st.success(f"Successfully indexed {uploaded_file.name}")
                    st.rerun()
                else:
                    # THIS IS THE KEY: Display the error from the backend
                    st.error(f"Failed! Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
    
    st.subheader("Knowledge Base")
    # This calls the helper function we defined earlier
    df = get_file_list()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No files indexed yet.")

# Right Column: AI Assistant Chat
with col2:
    st.header("AI Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Connect to your backend
        with st.chat_message("assistant"):
            try:
                response = requests.post("http://127.0.0.1:8000/ask", json={"question": prompt})
                answer = response.json().get("answer", "Error: No response from backend.")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error("Could not connect to the backend.")