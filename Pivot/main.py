from Pivot.graph import app
from Pivot.schemas import CandidateProfile
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
# Mock Profile
# Pivot/main.py

user_profile = CandidateProfile(
    jobTitle="Software Engineer",
    companyName="Independent Developer", # Added
    jobType=["Full-time"],                # Added (expecting a list)
    jobExcerpt="Specializing in Python backend development and AI agent orchestration.", # Added
    jobLevel="Mid",
    jobIndustry=["Fintech"],
    skills=["Python", "FastAPI", "Docker"],
    geo="Blantyre, Malawi",
    years_of_experience=5
)

config = {"configurable": {"thread_id": "user_pivot_123"}}
initial_state = {"profile": user_profile, "hours_per_day": 2}

# --- STEP 1: Run until the Choice point ---
for event in app.stream(initial_state, config):
    print(event)

# The graph is now PAUSED before 'validator'.
state = app.get_state(config)
paths = state.values.get("suggested_paths", [])

# CHECK: If paths is empty, we can't proceed
if not paths:
    print("\n❌ ERROR: No career paths were generated.")
    print("Check if your Tavily API key is valid and if Ollama is producing JSON.")
    exit() # Stop the script before the IndexError happens

print("\n--- ACTION REQUIRED ---")
for i, path in enumerate(paths):
    # Using getattr for extra safety
    title = getattr(path, 'title', 'Unknown Role')
    print(f"[{i}] {title}")

try:
    choice = int(input("\nSelect path index to validate: "))
    selected = paths[choice].title
    
    # --- STEP 2: Update state and resume ---
    app.update_state(config, {"selected_path": selected})
    for event in app.stream(None, config):
        print(event)
        
except (ValueError, IndexError):
    print("Invalid selection. Please run the script again and choose a valid number.")