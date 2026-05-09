import os
from dotenv import load_dotenv

# --- ADDED: THE X-RAY STARTUP ---
load_dotenv() 

# These tell the code to send every detail to LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Hire-ability_Engine_Debug"
# -------------------------------

from core.Nodes.nodes import nodes

# Initialize your graph
app = nodes()

def test_graph_with_data():
    test_input = {"file": "resumes/JORDAN M.pdf"}
    config = {"configurable": {"thread_id": "test_run_1"}}

    # --- PART 1: Run until Interrupt ---
    print("▶️ Running until selection interrupt...")
    for event in app.stream(test_input, config=config, stream_mode="updates"):
        print(f"📍 NODE: {list(event.keys())}")

    # --- PART 2: The "Human" Phase ---
    state = app.get_state(config)
    
    # Check if we have jobs to show
    if "job_listings" in state.values and state.values["job_listings"]:
        jobs = state.values["job_listings"].get("results", [])
        
        print("\n" + "="*20 + " AVAILABLE JOBS " + "="*20)
        for i, job in enumerate(jobs):
            print(f"[{i}] {job['title']} @ {job['company']} ({job['source']})")
        print("=" * 56)

        # Get user input
        selection = input("\n👉 Enter the index [i] of the job you want to tailor for: ")
        
        # --- PART 3: Resume the Graph ---
        print(f"\n🚀 Resuming with Job Index: {selection}...")
        
        # Update the state with the user's choice
        app.update_state(config, {"selected_job_id": selection})
        
# Call stream(None) to resume
        for event in app.stream(None, config=config, stream_mode="updates"):
            print(f"📍 NODE: {list(event.keys())}")

    # --- PART 4: Final Output Retrieval ---
    # Fetch the state one last time after the graph finishes
    final_state = app.get_state(config)
    
    # Check the state values directly for the key your agent returns
    # Based on your logs, the human_rewritter_agent returns 'resume_suggestions'
    result = final_state.values.get("resume_suggestions")

    if result:
        print("\n" + "✨" * 10 + " FINAL HUMAN-CENTRIC RESUME " + "✨" * 10)
        print(result)
        print("✨" * 48)
    else:
        print("\n⚠️  No 'resume_suggestions' found in the final state.")
if __name__ == "__main__":
    test_graph_with_data()


# # --- main_cli.py ---
# from core.Nodes.nodes import app  # Import your compiled Engine

# def run_engine():
#     # 1. Start the race
#     thread = {"configurable": {"thread_id": "1"}}
#     initial_input = {"raw_resume": "Text from PDF...", "user_notes": "I want remote work"}
    
#     # This runs until it hits the 'Rank' node and stops
#     for event in app.stream(initial_input, thread, stream_mode="values"):
#         print(f"--- Node Executed: {list(event.keys())} ---")

#     # 2. Get the results from the 'Whiteboard'
#     state = app.get_state(thread)
#     job_list = state.values.get("job_listings", [])
    
#     # 3. CLI Logic (Human Input)
#     print("\nMATCHED JOBS:")
#     for i, job in enumerate(job_list):
#         print(f"[{i}] {job['title']} at {job['company']} (Score: {job['score']})")
    
#     user_choice = int(input("\nSelect job index to tailor resume: "))
#     selected_id = job_list[user_choice]['job_id']

#     # 4. Give the choice to the Graph and wake it up
#     app.update_state(thread, {"selected_job_id": selected_id})
#     app.invoke(None, thread) # Resume!

#     # 5. Get final result
#     final_state = app.get_state(thread)
#     print("\n--- FINAL TAILORED RESUME ---")
#     print(final_state.values.get("final_resume"))

# if __name__ == "__main__":
#     run_engine()
