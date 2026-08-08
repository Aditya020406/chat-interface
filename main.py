import streamlit as st
import os
import json
import psutil
from openai import OpenAI

# Page Config
st.set_page_config(page_title="Star AI", page_icon="⭐", layout="centered")

st.title("⭐ Star — Personal Assistant")
st.caption("Online & fully operational, Boss.")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Tool definitions
def get_workspace_status():
    """Returns system storage and status details."""
    try:
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

# Initialize chat history with Star's FRIDAY personality prompt
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "You are Star, an advanced personal AI assistant modeled after FRIDAY from Iron Man. You address the user as 'Boss' and speak with a sharp, professional, highly capable, and loyal tone."
        },
        {"role": "assistant", "content": "Hello Boss. Star is online. How can I assist you with your systems or workspace today?"}
    ]

# Display chat history (skip system prompt in UI)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input handling
if prompt := st.chat_input("What is your command, Boss?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if the user is asking for system status tool
    if any(keyword in prompt.lower() for keyword in ["status", "workspace", "storage", "diagnostics"]):
        raw_status = get_workspace_status()
        response = f"System diagnostics retrieved, Boss:\n```json\n{raw_status}\n```"
    else:
        # Generate response using the AI model
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            response = completion.choices[0].message.content
        except Exception as e:
            response = f"Communication error with core systems, Boss: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
