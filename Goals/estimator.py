from Pivot.schemas import UniversalGoalsState

def universal_reality_check_node(state: UniversalGoalsState):
    """
    Calculates effort by converting complexity into hours.
    Universal Logic: 20 hours of study per complexity level.
    """
    requirements = state["market_requirements"]
    
    # Universal Constant for 2026 pedagogical data
    HOURS_PER_LEVEL = 20 
    
    detailed_effort = {}
    total_hours = 0
    
    for item in requirements:
        skill = item["skill"]
        complexity = item["complexity"]
        
        # Base calculation
        base_time = complexity * HOURS_PER_LEVEL
        
        # General Experience Multiplier:
        # We check the background length. If they have >3 years exp in any field,
        # we apply a 'Learning Efficiency' discount of 15%.
        multiplier = 0.85 if "year" in state["current_background"].lower() else 1.0
        
        adjusted_time = int(base_time * multiplier)
        detailed_effort[skill] = adjusted_time
        total_hours += adjusted_time

    baseline_truth = (
        f"ESTIMATED EFFORT: {total_hours} Hours\n"
        f"This covers {len(requirements)} mandatory pillars for the '{state['target_goal']}' path.\n"
        f"At a steady pace of 10 hours/week, you will reach your goal in {round(total_hours/10, 1)} weeks."
    )
    
    return {
        "effort_estimate": detailed_effort,
        "baseline_truth": baseline_truth
    }