import streamlit as st
import re

def render_chat_interface(col):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    with col:
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
            
            # FIX: Get the existing file path from the last known state
            # This prevents the 'NoneType has no attribute seek' error
            existing_file = st.session_state.last_results.get("file")

            with chat_container.chat_message("assistant"):
                response_text = ""
                new_data = {"file": existing_file} # Initialize with existing file

                if any(w in p_lower for w in ["goal", "target", "become"]):
                    clean_goal = re.sub(r'(?i)^(set goal to|set goal|goal is|goal|target is|target|become a|become)\s*:?\s*', '', prompt).strip()
                    response_text = f"Targeting: **{clean_goal}**. Mapping gaps..."
                    new_data.update({"target_goal": clean_goal, "entry_type": "goal"})
                
                elif any(w in p_lower for w in ["match", "job", "career"]):
                    response_text = "Scanning market for job matches..."
                    new_data.update({"entry_type": "job_match"})
                
                elif any(w in p_lower for w in ["circle", "network", "people"]):
                    response_text = "Analyzing your professional circle..."
                    new_data.update({"entry_type": "circle"})
                
                else:
                    response_text = "Processing your request..."
                    new_data.update({"entry_type": "general"})

                st.write(response_text)
                
                # Update state with BOTH the new intent AND the existing file path
                st.session_state.graph_app.update_state(config, new_data)

                with st.status("Indigo Engine Running...", expanded=False) as status:
                    try:
                        # Passing None as input because we updated state above
                        for event in st.session_state.graph_app.stream(None, config, stream_mode="updates"):
                            if event:
                                node_name = list(event.keys())[0]
                                st.write(f"✅ {node_name.replace('_', ' ').title()} synced.")
                        
                        status.update(label="Sync Complete!", state="complete")
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
                        # Refresh results for the dashboard
                        final_state = st.session_state.graph_app.get_state(config)
                        st.session_state.last_results = final_state.values
                        st.rerun()

                    except Exception as e:
                        st.error(f"Execution Error: {str(e)}")