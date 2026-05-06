# Pivot/estimator.py

def reality_check_node(state: GoalsState):
    """
    Stage 3: The Baseline Truth.
    Calculates learning time based on user's current 5-year Dev background.
    """
    gaps = state.get("gap_report", {}).get("gaps", [])
    
    # 2026 Learning Benchmarks (Average hours for an experienced Dev)
    benchmarks = {
        "Reinforcement Learning": 80,
        "MLOps (Kubernetes/BentoML)": 50,
        "System Design (Distributed Agents)": 40,
        "AI Ethics & Governance": 15
    }
    
    detailed_effort = {}
    total_hours = 0
    
    for skill in gaps:
        # If skill not in benchmarks, default to 30 hours of deep study
        hours = benchmarks.get(skill, 30)
        detailed_effort[skill] = hours
        total_hours += hours
        
    baseline_truth = (
        f"To reach your goal of {state['target_goal_description']}, "
        f"you need approximately {total_hours} hours of targeted upskilling. "
        f"At 2 hours/day, this is a {round(total_hours/14, 1)} week commitment."
    )
    
    return {
        "effort_estimate": detailed_effort,
        "baseline_truth": baseline_truth
    }