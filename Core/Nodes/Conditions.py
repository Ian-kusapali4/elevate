from Core.Unifiedstate import ElevateMasterState 
from services.parser.yaml_parser import yaml_extraction
from Core.model_factory import get_model

#these are the graph condtions
my_model = get_model()
critic_config = yaml_extraction('critic_resume_rewrite.yaml')

def ingestion_condition(graph_state: ElevateMasterState):
   
    if not graph_state.get("raw_resume"):
        return "failed"
    
    
    entry_mode = graph_state.get("entry_type")
    
    if entry_mode == "pivot":
        return "go_to_pivots"
    
    return "passed" 

def skill_extraction_condition(graph_state: ElevateMasterState):
    profile = graph_state.get("CandidateProfile")
    search_queries = graph_state.get("search_queries")
    
    print(f"DEBUG: Profile exists: {profile is not None}")
    print(f"DEBUG: Search Queries exist: {search_queries is not None}")

    if profile and search_queries:
        print('--- CONDITION: PASSED ---')
        return "passed"

    if profile:
        print("--- CONDITION: RETRYING ---")
        return "retry"
        
    print("--- CONDITION: FAILED ---")
    return "failed"

def route_user_intent(state: ElevateMasterState):
    
    intent = str(state.get("entry_type", "job_search")).lower().strip()
    
    print(f"--- ROUTER DEBUG: State 'entry_type' is currently: {intent} ---")
    
  
    if intent in ["pivot", "goal", "circle", "job_search"]:
        return intent
    return "job_search"

def job_search_condition(graph_state: ElevateMasterState) -> bool:

    print(f"Search Queries: {graph_state.search_queries}")

    if graph_state.query_search_response == True:

        return "passed"
    elif graph_state.query_search_response == False:
        return "retry"
def job_ranking_condition(graph_state: ElevateMasterState) -> bool:
    """Checks if job listings have been retrieved based on the search queries. If not, it can trigger a retry of the job search."""
    if graph_state.job_listings and len(graph_state.job_listings) > 0:
        return "passed"
    else:
        return "retry"
    
def job_selection_condition(graph_state: ElevateMasterState) -> bool:
    """Checks if a job has been selected from the job listings. If not, it can prompt the user to select one."""
    # would like a human in the loop here to select a job
    if graph_state.selected_job_id:
        return "passed"
    else:
        return "retry"

    
def critic_resume_rewrite_condition(graph_state: ElevateMasterState) -> bool:
    # """checkes the resume rewrite results, see if the response matches the job requirements, if not we can retry the resume rewrite with different prompts or parameters."""
    # try:
    #     critic_prompt = critic_config['Resume_critic']['template'].format(
    #         role=critic_config['Resume_critic']['role'],
    #         selected_job=graph_state.selected_job_id,
    #         final_resume=graph_state.final_resume
    #     )
    # except KeyError as e:
    #     print(f"YAML Key Error: {e}")
    #     return "failed"
    # print("\n--- AI IS CRITICIZING THE REWRITTEN RESUME ---")   
    # ai_response = my_model.invoke(critic_prompt)
    
    return "Procced"

def check_jobs_condition(state: ElevateMasterState) -> str:

    if len(state.job_listings) > 0:
        return "Proceed_to_Selection"
    

    if state.search_retries >= 3:
        return "End_with_Error" 
        

    return "Retry_Search"