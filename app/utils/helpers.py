import streamlit as st
from datetime import datetime

def run_Elevate_agent(inputs):
    """Runs the LangGraph engine and returns the final state."""
    if st.session_state.graph_app is None:
        st.error("Graph engine not initialized. Please check your Global_Workflow.py.")
        return {}

    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    with st.status("🛠️ Elevate Engine: Running Nodes...", expanded=True) as status:
        try:
            # Merge current state with new inputs to keep resume data alive
            current_vals = st.session_state.get("last_results", {})
            full_inputs = {**current_vals, **inputs}
            
            final_output = {}
            # Using stream_mode="values" returns the full state at each step
            for event in st.session_state.graph_app.stream(full_inputs, config, stream_mode="values"):
                final_output = event 
            
            status.update(label="Process Complete!", state="complete")
            return final_output
            
        except Exception as e:
            # Handle the "Target machine actively refused it" error gracefully
            if "10061" in str(e):
                st.error("🔌 **Connection Refused:** Ensure your local LLM (Ollama) is running.")
            else:
                st.error(f"Graph Error: {str(e)}")
            return current_vals 
        

def add_log(msg, level="INFO"):
    """Appends execution logs to the session state."""
    if "logs" not in st.session_state:
        st.session_state.logs = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({"time": timestamp, "level": level, "msg": msg})