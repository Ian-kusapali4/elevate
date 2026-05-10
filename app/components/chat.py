import streamlit as st

def render_control_interface(col):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    # Retrieve existing state to maintain context (like the uploaded file/resume)
    last_state = st.session_state.graph_app.get_state(config)
    vals = last_state.values if last_state and last_state.values else {}
    existing_file = vals.get("file")

    with col:
        st.subheader("⚙️ Indigo Command Center")
        
        # --- SECTION: GOAL SETTING ---
        with st.container(border=True):
            st.markdown("### 🎯 Career Objective")
            goal_input = st.text_input(
                "Define your target role", 
                value=vals.get("target_goal", ""), 
                placeholder="e.g., Senior AI Engineer"
            )
            
            if st.button("🚀 Map Goal Path", use_container_width=True, type="primary"):
                if goal_input:
                    execute_indigo_task(
                        {"target_goal": goal_input, "entry_type": "goal", "file": existing_file},
                        config
                    )
                else:
                    st.warning("Please enter a goal first.")

        st.divider()

        # --- SECTION: ACTION TRIGGERS ---
        st.markdown("### 🛠️ Quick Actions")
        
        c1, c2 = st.columns(2)
        
        with c1:
            if st.button("🔍 Find Job Matches", use_container_width=True):
                execute_indigo_task({"entry_type": "job_match", "file": existing_file}, config)
                
        with c2:
            if st.button("⭕ Analyze Circle", use_container_width=True):
                execute_indigo_task({"entry_type": "circle", "file": existing_file}, config)

        if st.button("🔄 Generate Career Pivots", use_container_width=True):
            execute_indigo_task({"entry_type": "pivot", "file": existing_file}, config)

def execute_indigo_task(new_data, config):
    """Encapsulated execution logic for the Indigo Engine"""
    try:
        # Update state with the new intent and context
        st.session_state.graph_app.update_state(config, new_data)

        with st.status("Indigo Engine Executing...", expanded=True) as status:
            # Run the graph stream
            for event in st.session_state.graph_app.stream(None, config, stream_mode="updates"):
                if event:
                    node_name = list(event.keys())[0]
                    st.write(f"✅ {node_name.replace('_', ' ').title()} completed.")
            
            status.update(label="Sync Complete!", state="complete")
            
            # Refresh session results and trigger UI update
            final_state = st.session_state.graph_app.get_state(config)
            st.session_state.last_results = final_state.values
            st.rerun()

    except Exception as e:
        st.error(f"Execution Error: {str(e)}")