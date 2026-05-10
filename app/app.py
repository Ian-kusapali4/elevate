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
from components.chat import render_control_interface  # Corrected Import
from components.dashboard import render_dashboard

# --- 2. Page Config ---
st.set_page_config(page_title="Elevate AI 2.0", layout="wide", page_icon="🚀")

# --- 3. Session State Initialization ---
init_keys = {
    "graph_app": None,
    "last_results": {},
    "thread_id": "Elevate_user_session_v2",
    "messages": [],
    "logs": [],
    "CandidateProfile": None,
    "active_pivot_view": None 
}

for key, value in init_keys.items():
    if key not in st.session_state:
        if key == "graph_app":
            st.session_state[key] = build_unified_graph()
        else:
            st.session_state[key] = value

# --- 4. Sync State Before Rendering ---
config = {"configurable": {"thread_id": st.session_state.thread_id}}
current_state = st.session_state.graph_app.get_state(config)

if current_state and current_state.values:
    st.session_state.last_results = current_state.values

# --- 5. Render Layout ---
render_sidebar(current_dir)

# Define columns
col_chat, col_dash = st.columns([1, 1.4])

# Render the components into the columns
with col_chat:
    # Use the new function name we imported
    render_control_interface(col_chat)

with col_dash:
    render_dashboard(col_dash)