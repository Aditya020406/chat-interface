import streamlit as st
import os
import json
import psutil

# Page Config
st.set_page_config(page_title="Star AI", page_icon="⭐", layout="centered")

st.title("⭐ Star — Personal Assistant")
st.caption("Online & fully operational, Boss.")

# Tool definitions
def get_workspace_status():
    """Returns system storage and status details."""
    try:
        # Cross-platform disk usage check
        usage = psutil.disk_usage('/')
        free_gb = round(usage.free / (1024**3), 2)
        total_gb = round(usage.total / (1024**3), 2)
        used_gb = round(usage.used / (1024**3), 2)
        
        return json.dumps({
            "status": "online",
            "workspace_directory": os.getcwd(),
            "storage_used_gb": f"{used_gb} GB",
            "storage_free_gb": f"{free_gb} GB",
            "storage_total_gb": f"{total_gb} GB"
        })
    except Exception as e:
        return json.dumps({"status": "online", "message": str(e)})

# Initialize chat history with Star's greeting
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello Boss. Star is online. How can I assist you with your systems or workspace today?"}
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input handling
if prompt := st.chat_input("What is your command, Boss?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Logic for processing commands (like checking workspace status)
    if "status" in prompt.lower() or "workspace" in prompt.lower() or "storage" in prompt.lower():
        raw_status = get_workspace_status()
        response = f"System diagnostics retrieved, Boss:\n```json\n{raw_status}\n```"
    else:
        response = f"Command received, Boss: '{prompt}'. I am processing your request."

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
