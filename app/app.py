import streamlit as st
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# --- 1. Environment & Path Setup ---
load_dotenv() 

if not os.getenv("GROQ_API_KEY"):
    st.error("❌ GROQ_API_KEY not found! Check your .env file.")
    st.stop()

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# --- 2. Project Imports ---
from Core.Global_Workflow import build_unified_graph
from Core.Unifiedstate import IndigoMasterState 

# --- 3. Page Config ---
st.set_page_config(page_title="Indigo AI 2.0", layout="wide", page_icon="🚀")

# --- 4. Session State Initialization ---
if "graph_app" not in st.session_state:
    st.session_state.graph_app = build_unified_graph()
    st.session_state.thread_id = "indigo_user_session_v1"
    st.session_state.messages = [] 
    st.session_state.logs = [] 

def add_log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({"time": timestamp, "level": level, "msg": msg})

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# --- 5. Sidebar: Profile & Context ---
with st.sidebar:
    st.title("🚀 Indigo v2.0")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    if uploaded_file:
        temp_path = os.path.join(current_dir, "temp_resume.pdf")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if "CandidateProfile" not in st.session_state:
            with st.spinner("Extracting Profile..."):
                add_log("Starting Resume Extraction...", "PROCESS")
                st.session_state.graph_app.invoke({"file": temp_path}, config)
                state = st.session_state.graph_app.get_state(config)
                st.session_state.CandidateProfile = state.values.get("CandidateProfile")
                add_log("Profile extraction completed.")
                st.success("Profile Loaded!")

    if "CandidateProfile" in st.session_state and st.session_state.CandidateProfile:
        st.divider()
        st.subheader("👤 Candidate Profile")
        profile = st.session_state.CandidateProfile
        st.write(f"**Current Role:** {profile.get('jobTitle', 'Unknown')}")
        st.write(f"**Exp Level:** {profile.get('jobLevel', 'N/A')}")
        with st.expander("Detected Skills"):
            st.write(", ".join(profile.get("skills", [])))

# --- 6. Main Layout ---
col_chat, col_dash = st.columns([1, 1.2])

with col_chat:
    st.subheader("🤖 Strategy Assistant")
    chat_container = st.container(height=500)
    
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ex: 'I want to be a Cloud Architect'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        p_lower = prompt.lower()
        target_action = None
        if any(word in p_lower for word in ["goal", "target", "become"]): target_action = "goal"

        with chat_container.chat_message("assistant"):
            if target_action == "goal":
                import re
                clean_goal = re.sub(r'(?i)^(set goal to|set goal|goal is|goal|target is|target|become a|become)\s*:?\s*', '', prompt).strip()
                st.markdown(f"Setting target to: **{clean_goal}**. Initiating live market research...")
                
                st.session_state.graph_app.update_state(config, {"target_goal": clean_goal, "entry_type": "goal"})
                
                with st.status("🕵️ Researching via Tavily & AI...", expanded=True) as status:
                    try:
                        for event in st.session_state.graph_app.stream(None, config, stream_mode="updates"):
                            if event:
                                node_name = list(event.keys())[0]
                                add_log(f"Agent '{node_name}' completed.", "GRAPH")
                                st.write(f"✅ {node_name.replace('_', ' ').title()} finished.")
                        status.update(label="Research Complete!", state="complete")
                    except Exception as e:
                        add_log(f"Critical Error: {str(e)}", "ERROR")
                        st.error(f"Search failed: {str(e)}")
                
                st.rerun()
            else:
                st.markdown("I'm ready to help. Try setting a specific career goal!")

with col_dash:
    st.subheader("📊 Execution Dashboard")
    
    current_state = st.session_state.graph_app.get_state(config)
    state_vals = current_state.values if current_state and current_state.values else {}
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Goal Path", "🔄 Pivot Strategies", "📋 State Data", "📜 Activity Log"])

    with tab1:
        st.write("### 🎯 Professional Goal Analysis")
        col_inp, col_btn = st.columns([3, 1])
        current_goal_text = state_vals.get("target_goal", "")
        manual_goal = col_inp.text_input("Active Goal:", value=current_goal_text, key="manual_goal_input", label_visibility="collapsed", placeholder="Enter goal here...")
        
        if col_btn.button("Run Analysis", use_container_width=True):
            with st.spinner("Triggering Agents..."):
                st.session_state.graph_app.update_state(config, {"target_goal": manual_goal, "entry_type": "goal"})
                st.session_state.graph_app.invoke(None, config)
                st.rerun()

        st.divider()
        
        # Skill Requirements Display
        reqs = state_vals.get("market_requirements", [])
        if reqs:
            # Detection of fallback
            is_fallback = any(r.get('skill') == "Strategic Planning" for r in reqs)
            if is_fallback:
                st.error("⚠️ **NODE ERROR**: The Search Agent failed to return dynamic data and triggered a fallback. Please check your Tavily API key and LLM formatting.")
            
            st.write(f"#### Growth Pillars for: **{state_vals.get('target_goal', 'Your Goal')}**")
            for req in reqs:
                with st.expander(f"🛠️ {req.get('skill', 'Requirement')}", expanded=True):
                    lvl = req.get('complexity', 0)
                    st.progress(lvl / 5.0)
                    desc = req.get('description') or req.get('reasoning') or "Market requirement identified by analysis agent."
                    st.write(f"**Analysis:** {desc}")
        elif state_vals.get("target_goal"):
            st.warning("Analysis in progress. Try refreshing if it stays blank.")
        else:
            st.info("No goal data found. Please set a goal in the chat.")

        # Reality Check / Timeline
        truth = state_vals.get("baseline_truth", "")
        if truth:
            st.write("#### 📅 Expected Timeline & Effort")
            if isinstance(truth, dict):
                for k, v in truth.items(): st.markdown(f"**{k}**: {v}")
            else: st.info(truth)

    with tab2:
        paths = state_vals.get("suggested_paths", [])
        if paths:
            for p in paths:
                p_data = p.model_dump() if hasattr(p, 'model_dump') else p
                with st.expander(f"✨ {p_data.get('title', 'Path Strategy')}"):
                    st.write(p_data.get('description', 'No description available.'))
        else:
            st.info("No pivot paths found yet.")

    with tab3:
        st.write("### 🔍 Live State Inspector")
        if state_vals: st.json(state_vals)
        else: st.write("Graph state is empty.")
            
    with tab4:
        st.write("### 🛠️ Execution History")
        for log in reversed(st.session_state.logs):
            st.markdown(f"**[{log['time']}]** {log['msg']}")