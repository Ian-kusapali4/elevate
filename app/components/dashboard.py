import streamlit as st
from utils.helpers import run_indigo_agent

def render_dashboard(col):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    with col:
        st.subheader("📊 Execution Dashboard")
        current_state = st.session_state.graph_app.get_state(config)
        vals = current_state.values if current_state and current_state.values else {}
        
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
            
            # Use st.session_state.last_results as the source of truth
            vals = st.session_state.last_results
            
            if st.button("Generate Suggested Pivots", type="primary", use_container_width=True):
                # FIX: Grab the file path from the existing state and pass it to the agent
                file_path = vals.get("file") 
                
                st.session_state.last_results = run_indigo_agent({
                    "entry_type": "pivot",
                    "file": file_path  # <-- Passes the PDF path so the loader doesn't crash
                })
                st.rerun()

            pivots = vals.get("suggested_paths", [])
            
            if pivots:
                st.write(f"Found **{len(pivots)}** potential transition paths:")
                for idx, p in enumerate(pivots):
                    # Handle both Pydantic objects and raw dicts
                    p_val = p.model_dump() if hasattr(p, 'model_dump') else p
                    
                    with st.container(border=True):
                        st.write(f"#### ✨ {p_val.get('title')}")
                        st.write(p_val.get('description', 'No description provided.'))
                        
                        skills = p_val.get('bridge_skills', [])
                        if skills:
                            st.caption(f"**Bridge Skills Needed:** {', '.join(skills)}")
                        
                        st.info(f"Potential Salary: {p_val.get('salary_range', 'TBD')}")
                        
                        if st.button(f"🎯 Select '{p_val.get('title')}'", key=f"pivot_sel_{idx}", use_container_width=True):
                            # FIX: Also ensure the file is passed when selecting a new goal
                            new_state = run_indigo_agent({
                                "target_goal": p_val.get('title'),
                                "entry_type": "goal",
                                "file": vals.get("file") # <-- Added here as well for safety
                            })
                            st.session_state.last_results = new_state
                            st.success(f"Goal updated! Switch to the Goal Path tab.")
                            st.rerun()
            
            # Check if we specifically asked for pivots but got none
            elif vals.get("entry_type") == "pivot":
                st.warning("The Pivot node ran, but no 'suggested_paths' were returned. Check LangSmith for extraction errors.")

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
            st.json(vals)