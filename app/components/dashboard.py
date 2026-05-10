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

        # Standard Goal Path Tab
        with tab_goal:
            if vals.get("target_goal"):
                st.write(f"### Target: {vals.get('target_goal')}")
                reqs = vals.get("market_requirements", [])
                if reqs:
                    st.write("#### 🧱 High-Income Pillars")
                    for r in reqs:
                        status_icon = {"Missing": "🔴", "Partial": "🟡", "Acquired": "🟢"}.get(r.get('status', 'Missing'), "⚪")
                        with st.expander(f"{status_icon} {r.get('skill')}", expanded=True):
                            st.write(f"**Market Justification:** {r.get('reasoning')}")
                
                st.divider()
                if vals.get("learning_roadmap"):
                    st.warning(f"🕒 **Timeline Assessment:** {vals.get('learning_roadmap')}")
            else:
                st.info("Initiate a goal analysis by typing in the chat or selecting a pivot.")

        with tab_match:
                    matches = vals.get("job_matches") or vals.get("filtered_jobs") or []
                    selected = vals.get("selected_job")

                    if not matches:
                        st.info("No job matches found yet. Try asking Indigo to 'find me a job'.")
                    
                    elif not selected:
                        st.write(f"### 💼 Market Matches ({len(matches)})")
                        st.caption("Showing top 10 relevant matches")
                        
                        for idx, job in enumerate(matches[:10]):
                            j_val = job.model_dump() if hasattr(job, 'model_dump') else job
                            
                            with st.container(border=True):
                                title = j_val.get('title', 'Unknown Role')
                                company = j_val.get('company', 'Company N/A')
                                location = j_val.get('location', 'Remote')
                                url = j_val.get('url') 
                                
                                st.markdown(f"#### ✨ {title}")
                                st.markdown(f"**{company}** • *{location}*")
                                
                                desc = j_val.get('description', '')
                                if desc:
                                    st.markdown(f"*{desc[:180]}...*")

                                col1, col2 = st.columns(2)
                                with col1:
                                    if url:
                                        st.link_button("🔗 View Original Posting", url, use_container_width=True)
                                    else:
                                        st.button("🔗 No Link Available", disabled=True, use_container_width=True)

                                with col2:
                                    if st.button(f"🎯 Select for Rewrite", key=f"job_sel_{idx}", use_container_width=True, type="primary"):
                                        with st.spinner(f"Creating strategy for {title}..."):
                                            run_indigo_agent({
                                                "selected_job": j_val,
                                                "entry_type": "job_match" 
                                            })
                                            st.rerun()

                    else:
                        # --- RESUME REWRITE VIEW ---
                        st.success(f"🎯 Selected: **{selected.get('title')}** at **{selected.get('company')}**")
                        
                        if st.button("⬅️ Back to All Jobs", use_container_width=True):
                            run_indigo_agent({"selected_job": None, "entry_type": "job_match"})
                            st.rerun()
                        
                        st.divider()
                        st.markdown("### 📝 Tailored Resume Strategy & Rewrite")
                        
                        # --- IMPROVED CONTENT LOOKUP ---
                        # Checks all possible keys the agent might have saved the rewrite to
                        raw_content = (
                            vals.get("tailored_resume") or 
                            vals.get("resume_suggestions") or 
                            vals.get("rewritten_resume")
                        )

                        if raw_content:
                            # Logic to handle if the content is a dictionary/JSON instead of a string
                            if isinstance(raw_content, dict):
                                display_text = raw_content.get("content") or raw_content.get("text") or str(raw_content)
                            else:
                                display_text = raw_content

                            st.markdown(display_text)
                            
                            # Optional: Add a download button for the new resume
                            st.download_button(
                                label="📥 Download Rewritten Resume",
                                data=display_text,
                                file_name=f"Indigo_Rewrite_{selected.get('title')}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                        else:
                            with st.status("🚀 Indigo is generating your tailored rewrite...", expanded=True):
                                st.write("Comparing skills to job description...")
                                st.write("Optimizing bullet points for ATS...")
                                st.spinner("Finalizing content...")                            

        with tab_pivots:
                    st.write("### 🔄 Career Pivot Discovery")
                    
                    # Use a session variable to track if we are looking at a specific pivot detail
                    active_pivot = st.session_state.get("active_pivot_view")

                    if active_pivot:
                        # --- VIEW 1: DEEP DIVE VIEW ---
                        st.success(f"🎯 **Exploring Path:** {active_pivot}")
                        if st.button("⬅️ Back to Suggestions"):
                            st.session_state.active_pivot_view = None
                            st.rerun()

                        st.divider()

                        if vals.get("learning_roadmap"):
                            st.write("#### 🗺️ Transition Roadmap")
                            st.info(vals.get("learning_roadmap"))
                            
                            reqs = vals.get("market_requirements", [])
                            if reqs:
                                st.write("#### 🧱 Skill Gap Analysis")
                                for r in reqs:
                                    with st.expander(f"🔹 {r.get('skill')}"):
                                        st.write(r.get('reasoning'))
                        else:
                            st.info("Generating transition details... please wait.")
                    
                    else:
                        # --- VIEW 2: LIST VIEW ---
                        pivot_vals = st.session_state.last_results
                        
                        if st.button("Generate Suggested Pivots", type="primary", use_container_width=True):
                            file_path = pivot_vals.get("file") 
                            st.session_state.last_results = run_indigo_agent({
                                "entry_type": "pivot",
                                "file": file_path 
                            })
                            st.rerun()

                        pivots = pivot_vals.get("suggested_paths", [])
                        
                        if pivots:
                            st.write(f"Found **{len(pivots)}** potential transition paths:")
                            for idx, p in enumerate(pivots):
                                p_val = p.model_dump() if hasattr(p, 'model_dump') else p
                                
                                with st.container(border=True):
                                    st.write(f"#### ✨ {p_val.get('title')}")
                                    st.write(p_val.get('description', 'No description provided.'))
                                    
                                    if st.button(f"🎯 Select '{p_val.get('title')}'", key=f"pivot_sel_{idx}", use_container_width=True):
                                        st.session_state.active_pivot_view = p_val.get('title')
                                        
                                        with st.spinner(f"Analyzing {p_val.get('title')}..."):
                                            new_state = run_indigo_agent({
                                                "target_goal": p_val.get('title'),
                                                "entry_type": "goal",
                                                "file": pivot_vals.get("file")
                                            })
                                            st.session_state.last_results = new_state
                                            st.rerun()
                        
                        # Fixed the UnboundLocalError by moving this inside the else block
                        elif pivot_vals.get("entry_type") == "pivot":
                            st.warning("No suggested paths returned.")

        with tab_circle:
            circle = vals.get("curated_circles", [])
            if circle:
                st.write("### ⭕ Found Professional Circles")
                for item in circle:
                    with st.container(border=True):
                        st.write(f"🔗 **{item.get('name', 'Community Link')}**")
                        if item.get('url'):
                            st.link_button("View Circle", item.get('url'))

        with tab_raw:
            st.write("#### 🛠️ Internal State Debugger")
            st.json(vals)