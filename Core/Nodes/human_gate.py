from Core.Unifiedstate import ElevateMasterState

def human_decision_gate(state: ElevateMasterState):
    """
    This node does nothing logic-wise. 
    It serves as a breakpoint for the UI to show the user 
    their extracted resume and ask: 'What next?'
    """
    print("--- WAITING FOR USER SELECTION ---")
    return state