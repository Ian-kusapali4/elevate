import streamlit as st
import os
import sys
import re
from datetime import datetime
from dotenv import load_dotenv

# --- 1. Environment & Path Setup ---
load_dotenv() 

# Ensure current directory and root are in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from Core.Global_Workflow import build_unified_graph

# --- 2. Page Config ---
st.set_page_config(page_title="Indigo AI 2.0", layout="wide", page_icon="🚀")

# --- 3. Session State Initialization ---
if "graph_app" not in st.session_state:
    st.session_state.graph_app = build_unified_graph()
    st.session_state.thread_id = "indigo_user_session_v2" # Fresh session
    st.session_state.messages = [] 
    st.session_state.logs = [] 
def run_indigo_agent(inputs):
    # This ID keeps the conversation history linked in LangGraph
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    with st.status("🛠️ Indigo Engine: Running Nodes...", expanded=True) as status:
        try:
            # We combine existing data (resume) with the new command (goal/pivot)
            current_vals = st.session_state.get("last_results", {})
            full_inputs = {**current_vals, **inputs}
            
            final_output = {}
            # This 'streams' the graph execution so the UI doesn't freeze
            for event in st.session_state.graph_app.stream(full_inputs, config, stream_mode="values"):
                final_output = event  
            
            status.update(label="Process Complete!", state="complete")
            
            # This is the "Value" it provides: it updates the dashboard state
            st.session_state.last_results = final_output
            return final_output
            
        except Exception as e:
            st.error(f"Graph Error: {str(e)}")
            return st.session_state.last_results

def add_log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({"time": timestamp, "level": level, "msg": msg})

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# --- 4. Sidebar: Profile & Context ---
with st.sidebar:
    st.title("🚀 Indigo v2.0")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    if uploaded_file and "CandidateProfile" not in st.session_state:
        temp_path = os.path.join(current_dir, "temp_resume.pdf")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Analyzing Professional Background..."):
            add_log("Extracting Profile...", "PROCESS")
            st.session_state.graph_app.invoke({"file": temp_path}, config)
            state = st.session_state.graph_app.get_state(config)
            st.session_state.CandidateProfile = state.values.get("CandidateProfile")
            st.success("Profile Analyzed!")

    if st.session_state.get("CandidateProfile"):
        st.divider()
        profile = st.session_state.CandidateProfile
        st.subheader("👤 Current Profile")
        st.write(f"**Role:** {profile.get('jobTitle', 'Unknown')}")
        st.write(f"**Level:** {profile.get('jobLevel', 'N/A')}")
        with st.expander("Detected Skills"):
            st.write(", ".join(profile.get("skills", [])))

# --- 5. Main Layout ---
col_chat, col_dash = st.columns([1, 1.4])

with col_chat:
    st.subheader("🤖 Strategy Assistant")
    chat_container = st.container(height=550)
    
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ex: 'Set goal to CTO' or 'Find me job matches'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        p_lower = prompt.lower()
        
        with chat_container.chat_message("assistant"):
            # INTELLIGENT ROUTING
            if any(w in p_lower for w in ["goal", "target", "become"]):
                # Clean goal extraction
                clean_goal = re.sub(r'(?i)^(set goal to|set goal|goal is|goal|target is|target|become a|become)\s*:?\s*', '', prompt).strip()
                st.write(f"Targeting: **{clean_goal}**. Mapping income drivers & mastery gaps...")
                st.session_state.graph_app.update_state(config, {"target_goal": clean_goal, "entry_type": "goal"})
            
            elif any(w in p_lower for w in ["match", "job", "career"]):
                st.write("Scanning 2026 market for high-salary job matches...")
                st.session_state.graph_app.update_state(config, {"entry_type": "job_match"})
            
            elif any(w in p_lower for w in ["circle", "network", "people"]):
                st.write("Analyzing your strategic professional circle...")
                st.session_state.graph_app.update_state(config, {"entry_type": "circle"})
            
            else:
                st.write("Processing query across all Indigo agents...")

            # STREAM EXECUTION
            with st.status("Indigo Intelligence Engine Running...", expanded=True) as status:
                try:
                    for event in st.session_state.graph_app.stream(None, config, stream_mode="updates"):
                        if event:
                            node_name = list(event.keys())[0]
                            st.write(f"✅ Agent **{node_name.replace('_', ' ').title()}** synchronized.")
                    status.update(label="Strategy Updated!", state="complete")
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")
            
            st.rerun()

with col_dash:
    st.subheader("📊 Execution Dashboard")
    current_state = st.session_state.graph_app.get_state(config)
    vals = current_state.values if current_state and current_state.values else {}
    
    # MULTI-FEATURE TABBED INTERFACE
    tab_goal, tab_match, tab_pivots, tab_circle, tab_raw = st.tabs([
        "🎯 Goal Path", "💼 Job Board", "🔄 Pivots", "⭕ My Circle", "🔍 Live State"
    ])

    with tab_goal:
        if vals.get("target_goal"):
            st.write(f"### Target: {vals.get('target_goal')}")
            reqs = vals.get("market_requirements", [])
            if reqs:
                st.write("#### 🧱 High-Income Pillars (Mastery Gap)")
                for r in reqs:
                    status_icon = {"Missing": "🔴", "Partial": "🟡", "Acquired": "🟢"}.get(r.get('status', 'Missing'), "⚪")
                    with st.expander(f"{status_icon} {r.get('skill')}", expanded=True):
                        comp = r.get('complexity', 1)
                        # The bar now represents Time-to-Mastery
                        st.progress(comp / 5.0)
                        st.caption(f"**Complexity Level:** {comp}/5 | **Status:** {r.get('status')}")
                        st.write(f"**Market Justification:** {r.get('reasoning')}")
            
            st.divider()
            if vals.get("learning_roadmap"):
                st.warning(f"🕒 **Timeline Assessment:** {vals.get('learning_roadmap')}")
        else:
            st.info("Initiate a goal analysis by typing 'Set goal to [Role]' in the chat.")


    with tab_match:
        matches = vals.get("job_matches", [])
        if matches:
            st.write(f"### 💼 Market Matches Found ({len(matches)})")
            for job in matches:
                with st.container(border=True):
                    st.write(f"#### {job.get('title')} at {job.get('company')}")
                    col1, col2 = st.columns(2)
                    col1.caption(f"📍 {job.get('location', 'Remote')}")
                    col2.caption(f"🔗 {job.get('site', 'Direct')}")
        
        if vals.get("resume_suggestions"):
            st.divider()
            st.write("### 📝 Optimization Strategy")
            st.markdown(vals.get("resume_suggestions"))
        elif not matches:
            st.info("No active job matches. Check the 'Internal State Debugger' to see if 'job_matches' is populated.")

    with tab_pivots:
            st.write("### 🔄 Career Pivot Discovery")
            if st.button("Generate Suggested Pivots", type="primary", use_container_width=True):
                st.session_state.last_results = run_indigo_agent({
                    "entry_type": "pivot" # Explicitly tell the graph we want a pivot
                })
                st.rerun()

            pivots = vals.get("suggested_paths", [])
            if pivots:
                st.write(f"Found **{len(pivots)}** potential transition paths:")
                for idx, p in enumerate(pivots):
                    # Handle both Pydantic models and dictionaries
                    p_val = p.model_dump() if hasattr(p, 'model_dump') else p
                    
                    with st.container(border=True):
                        st.write(f"#### ✨ {p_val.get('title')}")
                        st.write(p_val.get('description', 'No description provided.'))
                        
                        # Display bridge skills if they exist
                        skills = p_val.get('bridge_skills', [])
                        if skills:
                            st.caption(f"**Bridge Skills Needed:** {', '.join(skills)}")
                        
                        st.info(f"Potential Salary: {p_val.get('salary_range', 'TBD')}")
                        
                        # --- The Selection Button ---
                        if st.button(f"🎯 Select '{p_val.get('title')}' as Goal", key=f"pivot_sel_{idx}", use_container_width=True):
                            # When clicked, trigger the Goal node using this pivot's title
                            st.session_state.last_results = run_indigo_agent({
                                "target_goal": p_val.get('title'),
                                "entry_type": "goal"
                            })
                            st.success(f"Goal updated to {p_val.get('title')}! Switch to the Goal Path tab to see your roadmap.")
                            st.rerun()
            
            # Debug helper: if the graph ran but returned no pivots
            elif vals.get("entry_type") == "pivot" and not pivots:
                st.warning("The Pivot node ran, but no 'suggested_paths' were returned to the state.")
    with tab_circle:
        circle = vals.get("curated_circles", [])
        if circle:
            st.write("### ⭕ Found Professional Circles")
            for item in circle:
                with st.container(border=True):
                    st.write(f"🔗 **{item.get('name', 'Community Link')}**")
                    if item.get('url'):
                        st.link_button("View Circle", item.get('url'))
        else:
            st.info("No circle data available.")

    with tab_raw:
        st.write("#### 🛠️ Internal State Debugger")
        # If 'job_matches' or 'curated_circles' is empty here, 
        # the node return statements need to be checked.
        st.json(vals)