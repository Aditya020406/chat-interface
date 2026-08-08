cat << 'EOF' > app.py
import json
import os
import urllib.request
import urllib.parse
import urllib.error
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="STAR AI Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BACKEND TOOLS ---

def web_search(query):
    """Searches the live web for real-time information."""
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = []
            if data.get("AbstractText"):
                results.append(f"Summary: {data['AbstractText']}")
            if data.get("Answer"):
                results.append(f"Instant Answer: {data['Answer']}")
            topics = data.get("RelatedTopics", [])
            for topic in topics[:5]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append(f"- {topic['Text']}")

            if not results:
                return json.dumps({"status": "info", "message": f"No instant answer box found for '{query}'. Synthesizing with core knowledge."})
            return json.dumps({"status": "success", "search_results": results})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def get_workspace_status():
    """Returns storage details for the workspace."""
    try:
        stat = os.statvfs('.')
        free_gb = round((stat.f_bavail * stat.f_frsize) / (1024**3), 2)
        total_gb = round((stat.f_blocks * stat.f_frsize) / (1024**3), 2)
        used_gb = round(total_gb - free_gb, 2)
        return json.dumps({
            "status": "online",
            "workspace_directory": os.getcwd(),
            "storage_used_gb": f"{used_gb} GB",
            "storage_free_gb": f"{free_gb} GB",
            "storage_total_gb": f"{total_gb} GB"
        })
    except Exception as e:
        return json.dumps({"status": "online", "message": str(e)})

def list_workspace_files():
    """Lists files and directories in current workspace."""
    try:
        items = os.listdir('.')
        files_info = []
        for item in items:
            is_dir = os.path.isdir(item)
            size_kb = round(os.path.getsize(item) / 1024, 2) if not is_dir else 0
            files_info.append({
                "name": item,
                "type": "directory" if is_dir else "file",
                "size_kb": f"{size_kb} KB" if not is_dir else "-"
            })
        return json.dumps({"status": "success", "workspace_contents": files_info})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def create_file(filename, content):
    """Creates a new file in workspace."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return json.dumps({"status": "success", "message": f"File '{filename}' created successfully."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def read_file(filename):
    """Reads content from workspace file."""
    try:
        if not os.path.exists(filename):
            return json.dumps({"status": "error", "message": f"File '{filename}' does not exist."})
        with open(filename, "r", encoding="utf-8") as f:
            data = f.read()
        return json.dumps({"status": "success", "content": data})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def append_to_file(filename, content):
    """Appends content to file."""
    try:
        if not os.path.exists(filename):
            return json.dumps({"status": "error", "message": f"File '{filename}' does not exist."})
        with open(filename, "a", encoding="utf-8") as f:
            f.write("\n" + content)
        return json.dumps({"status": "success", "message": f"Appended content to '{filename}'."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def delete_file(filename):
    """Deletes file from workspace."""
    try:
        if not os.path.exists(filename):
            return json.dumps({"status": "error", "message": f"File '{filename}' does not exist."})
        os.remove(filename)
        return json.dumps({"status": "success", "message": f"File '{filename}' deleted."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

# --- TOOL SCHEMA ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for real-time facts, news, definitions, or general web topics.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query"}},
                "required": ["query"]
            }
        }
    },
    {"type": "function", "function": {"name": "get_workspace_status", "description": "Fetch real workspace storage and directory status."}},
    {"type": "function", "function": {"name": "list_workspace_files", "description": "List all files and subdirectories inside the workspace folder."}},
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a file in the workspace with specific text content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the file"},
                    "content": {"type": "string", "description": "The text content"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a workspace file.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "Target filename"}},
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "append_to_file",
            "description": "Append text to an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Target filename"},
                    "content": {"type": "string", "description": "Text to append"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file from the workspace.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "Target filename"}},
                "required": ["filename"]
            }
        }
    }
]

SYSTEM_PROMPT = """
You are STAR (System Task & Assistance Resource), an advanced personal AI assistant. 
Address the user as 'boss' or 'sir'. Be direct, intelligent, witty, and highly capable. 
You have access to real workspace management tools and web search capabilities.
"""

def call_groq_api(api_key, messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.5,
        "tools": TOOLS,
        "tool_choice": "auto"
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP Error {e.code}: {error_body}")

# --- STREAMLIT UI SETUP ---

st.sidebar.title("⚡ STAR AI Dashboard")
st.sidebar.caption("System Task & Assistance Resource")

api_key = st.sidebar.text_input("Groq API Key:", type="password", key="api_key_input")

st.sidebar.markdown("---")
st.sidebar.subheader("📁 Workspace Explorer")

if st.sidebar.button("Refresh Workspace Files"):
    st.rerun()

try:
    files = [f for f in os.listdir('.') if not f.startswith('.')]
    for f in sorted(files):
        icon = "📁" if os.path.isdir(f) else "📄"
        st.sidebar.text(f"{icon} {f}")
except Exception as e:
    st.sidebar.error(f"Error reading directory: {str(e)}")

st.title("🤖 STAR Command Center")
st.caption("Integrated Autonomous AI Operating Core")

# Session state initialization
if "conversation" not in st.session_state:
    st.session_state.conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

if "display_history" not in st.session_state:
    st.session_state.display_history = []

# Display message log
for msg in st.session_state.display_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Chat Input
user_input = st.chat_input("Enter command or question for STAR...")

if user_input:
    if not api_key:
        st.error("Please enter your Groq API Key in the left sidebar to activate STAR!")
    else:
        # Render User Message
        st.session_state.display_history.append({"role": "user", "content": user_input})
        st.session_state.conversation.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("STAR thinking & processing..."):
                try:
                    response = call_groq_api(api_key, st.session_state.conversation)
                    message = response['choices'][0]['message']

                    if message.get("tool_calls"):
                        st.session_state.conversation.append(message)

                        for tool_call in message["tool_calls"]:
                            fn_name = tool_call["function"]["name"]
                            fn_args = json.loads(tool_call["function"]["arguments"]) if tool_call["function"].get("arguments") else {}

                            st.status(f"⚡ STAR Executing Tool: `{fn_name}`", state="running")

                            if fn_name == "web_search":
                                result = web_search(fn_args.get("query"))
                            elif fn_name == "get_workspace_status":
                                result = get_workspace_status()
                            elif fn_name == "list_workspace_files":
                                result = list_workspace_files()
                            elif fn_name == "create_file":
                                result = create_file(fn_args.get("filename"), fn_args.get("content"))
                            elif fn_name == "read_file":
                                result = read_file(fn_args.get("filename"))
                            elif fn_name == "append_to_file":
                                result = append_to_file(fn_args.get("filename"), fn_args.get("content"))
                            elif fn_name == "delete_file":
                                result = delete_file(fn_args.get("filename"))
                            else:
                                result = json.dumps({"error": "Unknown function"})

                            st.session_state.conversation.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": result
                            })

                        final_response = call_groq_api(api_key, st.session_state.conversation)
                        reply = final_response['choices'][0]['message']['content']
                    else:
                        reply = message['content']

                    st.markdown(reply)
                    st.session_state.display_history.append({"role": "assistant", "content": reply})
                    st.session_state.conversation.append({"role": "assistant", "content": reply})

                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")
EOF