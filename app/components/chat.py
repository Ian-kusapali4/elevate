import streamlit as st

def render_control_interface(col):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    # Retrieve existing state to maintain context (like the uploaded file/resume)
    last_state = st.session_state.graph_app.get_state(config)
    vals = last_state.values if last_state and last_state.values else {}
    existing_file = vals.get("file")

    with col:
        st.subheader("⚙️ Elevate Command Center")
        
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
                    execute_Elevate_task(
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
                execute_Elevate_task({"entry_type": "job_match", "file": existing_file}, config)
                
        with c2:
            if st.button("⭕ Analyze Circle", use_container_width=True):
                execute_Elevate_task({"entry_type": "circle", "file": existing_file}, config)

        if st.button("🔄 Generate Career Pivots", use_container_width=True):
            execute_Elevate_task({"entry_type": "pivot", "file": existing_file}, config)

def execute_Elevate_task(new_data, config):
    try:

        current_results = st.session_state.get("last_results", {})
        existing_file = current_results.get("file")

      
        if existing_file and "file" not in new_data:
            new_data["file"] = existing_file

        # 3. UPDATE GRAPH STATE
        st.session_state.graph_app.update_state(config, new_data)

        with st.status("Elevate Engine Executing...", expanded=True) as status:
          
            for event in st.session_state.graph_app.stream(None, config, stream_mode="updates"):
                if event:
                    node_name = list(event.keys())[0]
                    st.write(f"✅ {node_name.replace('_', ' ').title()} completed.")
            
            status.update(label="Sync Complete!", state="complete")
            
            
            final_state = st.session_state.graph_app.get_state(config)
            st.session_state.last_results = final_state.values
            st.rerun()

    except Exception as e:
        st.error(f"Execution Error: {str(e)}")