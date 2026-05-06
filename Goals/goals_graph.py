from langgraph.graph import StateGraph, END
from Goals.goals import goal_analysis_node
from Goals.estimator import universal_reality_check_node
from Pivot.schemas import UniversalGoalsState

# Setup
workflow = StateGraph(UniversalGoalsState)
workflow.add_node("analyze_goal", goal_analysis_node)
workflow.add_node("reality_check", universal_reality_check_node)

workflow.set_entry_point("analyze_goal")
workflow.add_edge("analyze_goal", "reality_check")
workflow.add_edge("reality_check", END)

app = workflow.compile()

# TEST CASE: Non-Developer
test_input = {
    "target_goal": "Content Marketing Manager at a Fashion Tech startup",
    "current_background": "2 years as a retail sales associate"
}

for output in app.stream(test_input):
    for node, data in output.items():
        print(f"--- Node: {node} ---")
        if "baseline_truth" in data:
            print(data["baseline_truth"])
        elif "market_requirements" in data:
            print(f"Identified Pillars: {data['market_requirements']}")