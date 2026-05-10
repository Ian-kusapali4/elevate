from Core.Unifiedstate import ElevateMasterState 

#this is the human in the loop node where the user will select the job they want and the node also filters the data to remove unnessary information, there by reducing the token usage and context window

def select_job_details(state: ElevateMasterState):
    """
    Acts as a data filter. It takes the full list and returns 
    ONLY the chosen job, clearing the rest of the listings.
    """
    target_id = state.get("selected_job_id")
    all_listings = state.get("job_listings", {}).get("results", [])

    try:
        
        selected_index = int(target_id)
        chosen_job = all_listings[selected_index]
    except (ValueError, IndexError, TypeError):
   
        return {"error_message": "Invalid job selection. Please try again."}

    print(f"🎯 Job Selected: {chosen_job['title']} at {chosen_job['company']}")

    return {
       
        "job_listings": None,           
        #"raw_resume": None,             
        "target_job_description": chosen_job['description'], 
        "selected_job_id": str(target_id) 
    }