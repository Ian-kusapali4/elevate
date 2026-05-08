import uuid
import os
from dotenv import load_dotenv

# 1. Load Environment & Verify Keys
load_dotenv()
print(f"DEBUG: Groq Key Found? {'Yes' if os.environ.get('GROQ_API_KEY') else 'No'}")

from Core.Global_Workflow import build_unified_graph

def run_test(target_goal="Senior AI Agent Developer"):
    # 2. Initialize the Master Graph
    app = build_unified_graph()
    
    # 3. Session Setup
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_input = {
        "file": r"temp_resume.pdf", 
        "target_goal": target_goal,
        "hours_per_day": 2,
        "retry_count": 0
    }

    print(f"\n--- PHASE 1: STARTING GRAPH (EXTRACTION) ---")
    
    # 4. First Run: Stream until the first interrupt
    for event in app.stream(initial_input, config=config):
        for node, data in event.items():
            print(f"[NODE COMPLETED]: {node}")

    # 5. THE INTERACTIVE LOOP
    state = app.get_state(config)
    
    while state.next:
        current_stop = state.next[0]
        print(f"\n--- PAUSED AT: {current_stop} ---")
        
        # --- HUB CHOICE: Selecting the Intent ---
        if "human_decision_gate" in current_stop:
            profile = state.values.get("CandidateProfile", {})
            job_title = profile.get("jobTitle", "Not Specified")
            
            print(f"\nExtracted Profile: {job_title}")
            print("\n--- CHOOSE YOUR DIRECTION ---")
            print("1. Job Search  (type: 'job_search')")
            print("2. Career Pivot (type: 'pivot')")
            print("3. Target Goals (type: 'goal')")
            print("4. Find My Circle (type: 'circle')")
            
            user_input = input("\nEnter choice (1-4 or name): ").strip().lower()
            
            # Mapping for convenience
            choice_map = {"1": "job_search", "2": "pivot", "3": "goal", "4": "circle"}
            final_choice = choice_map.get(user_input, user_input)
            
            print(f"Action: Updating state 'entry_type' to -> '{final_choice.upper()}'")
            
            # CRITICAL: We update the state before resuming
            app.update_state(config, {"entry_type": final_choice})
            
            # VERIFICATION: Double-check state was actually updated
            fresh_state = app.get_state(config)
            print(f"DEBUG: Verified State Value is now: {fresh_state.values.get('entry_type')}")

        # --- SPOKE CHOICE: Selecting Job Details ---
        elif "select_job_details" in current_stop:
            jobs = state.values.get("found_jobs", [])
            print(f"\n--- FOUND {len(jobs)} JOBS ---")
            for idx, job in enumerate(jobs[:5]):
                print(f"[{idx}] {job.get('title')} at {job.get('company')}")
            
            job_idx = input("\nEnter the index of the job to select: ").strip()
            app.update_state(config, {"selected_job_id": job_idx})

        # --- SPOKE CHOICE: Validating Pivot Path ---
        elif "validator" in current_stop:
            print("\n--- VALIDATE PATH ---")
            confirm = input("Accept this roadmap? (yes/no): ").strip().lower()
            app.update_state(config, {"path_accepted": confirm == 'yes'})

        # 6. RESUME FLOW
        print(f"\n--- RESUMING FLOW FROM: {current_stop} ---")
        # stream(None) tells LangGraph to continue from the last checkpoint
        for event in app.stream(None, config=config):
            for node, data in event.items():
                # We print the router debug here to see if it defaults
                if "DEBUG" in str(data):
                    print(data)
                print(f"[NODE COMPLETED]: {node}")
        
        # Refresh state for the next potential interrupt
        state = app.get_state(config)

    print(f"\n--- WORKFLOW COMPLETE ---")

if __name__ == "__main__":
    run_test(target_goal="Senior AI Agent Developer")