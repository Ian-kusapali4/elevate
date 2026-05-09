import streamlit as st
import os
from utils.helpers import add_log

def render_sidebar(current_dir):
    with st.sidebar:
        st.title("🚀 Indigo v2.0") 
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
        
        t_id = st.session_state.get("thread_id", "default-session")
        config = {"configurable": {"thread_id": t_id}}
        
        # FIX: Check if the file is present AND if we haven't successfully 
        # populated the profile yet. Using .get() is safer.
        if uploaded_file and not st.session_state.get("CandidateProfile"):
            
            # Save file to a permanent-ish path on disk
            temp_path = os.path.join(current_dir, "temp_resume.pdf")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.session_state.get("graph_app") is not None:
                with st.spinner("Analyzing Professional Background..."):
                    try:
                        # This should now show up in your terminal
                        print("DEBUG: Starting Extraction...") 
                        add_log("Extracting Profile...", "PROCESS")
                        
                        # Pass the path to LangGraph
                        st.session_state.graph_app.invoke({"file": temp_path}, config)
                        
                        # Sync state back to Streamlit
                        state = st.session_state.graph_app.get_state(config)
                        
                        if state.values.get("CandidateProfile"):
                            st.session_state.CandidateProfile = state.values.get("CandidateProfile")
                            st.session_state.last_results = state.values
                            st.success("Profile Analyzed!")
                            st.rerun()
                        else:
                            st.error("Graph ran but CandidateProfile is missing. Check your Extraction Node.")

                    except Exception as e:
                        if "10061" in str(e):
                            st.error("🔌 **Connection Error:** Ensure your LLM server is running.")
                        else:
                            st.error(f"Analysis failed: {e}")
            else:
                st.warning("Indigo Engine is not initialized.")

        # Display Profile Section
        if st.session_state.get("CandidateProfile"):
            st.divider()
            profile = st.session_state.CandidateProfile
            st.subheader("👤 Current Profile")
            
            # Use .get() with defaults to prevent UI crashes if keys are missing
            job_title = profile.get('jobTitle', profile.get('title', 'Unknown'))
            st.write(f"**Role:** {job_title}")
            st.write(f"**Level:** {profile.get('jobLevel', 'N/A')}")
            
            with st.expander("Detected Skills"):
                skills = profile.get("skills", [])
                if skills:
                    st.write(", ".join(skills))
                else:
                    st.write("No skills identified.")