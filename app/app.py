import streamlit as st
import os
import sys
from dotenv import load_dotenv

# --- 1. Environment & Path Setup ---
load_dotenv() 
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from Core.Global_Workflow import build_unified_graph
from components.sidebar import render_sidebar
from components.chat import render_chat_interface
from components.dashboard import render_dashboard

# --- 2. Page Config ---
st.set_page_config(page_title="Indigo AI 2.0", layout="wide", page_icon="🚀")

# --- 3. Strict Session State Initialization ---
init_keys = {
    "graph_app": None,
    "last_results": {},
    "thread_id": "indigo_user_session_v2",
    "messages": [],
    "logs": [],
    "CandidateProfile": None,
    "active_pivot_view": None  # Added to prevent UnboundLocalError in Pivots
}

for key, value in init_keys.items():
    if key not in st.session_state:
        if key == "graph_app":
            st.session_state[key] = build_unified_graph()
        else:
            st.session_state[key] = value

# --- 4. Sync State Before Rendering ---
# This ensures that if the graph is waiting at an interrupt (like after fetch_jobs),
# the dashboard can see the jobs currently sitting in the graph's memory.
config = {"configurable": {"thread_id": st.session_state.thread_id}}
current_state = st.session_state.graph_app.get_state(config)

if current_state and current_state.values:
    # Synchronize the persistent graph state with the UI session state
    st.session_state.last_results = current_state.values

# --- 5. Render Layout ---
render_sidebar(current_dir)

col_chat, col_dash = st.columns([1, 1.4])

# Pass the columns into the component functions
render_chat_interface(col_chat)
render_dashboard(col_dash)