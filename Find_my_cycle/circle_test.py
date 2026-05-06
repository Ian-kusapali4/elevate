import ast
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from Find_my_cycle.soial_search import real_social_search_node

# 1. DEFINE THE STATE
class CircleState(TypedDict):
    resume_map: dict
    target_goal: str
    search_parameters: List[str]
    curated_circles: List[dict]

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)

# 2. DEFINE THE NODES
def generate_circle_parameters_node(state: CircleState):
    resume = state["resume_map"]
    goal = state["target_goal"]
    
    prompt = f"""
    USER PROFILE: {resume}
    TARGET GOAL: {goal}
    
    TASK: Generate 3 hyper-specific search queries to find niche communities 
    (Discord, Slack, Reddit, or Private Forums).
    
    CRITERIA:
    1. Query 1: Intersection of current skills and target industry.
    2. Query 2: Seniority-based peer groups.
    3. Query 3: Future-tech or 'Growth' circles relevant to the goal.
    
    Return ONLY a Python list of strings like: ["query1", "query2", "query3"]
    """
    response = llm.invoke(prompt)
    # Removing markdown backticks if the LLM adds them
    cleaned_content = response.content.replace("```python", "").replace("```", "").strip()
    queries = ast.literal_eval(cleaned_content)
    return {"search_parameters": queries}


# 3. COMPILE THE GRAPH
workflow = StateGraph(CircleState)
workflow.add_node("generate_params", generate_circle_parameters_node)
workflow.add_node("find_links", real_social_search_node)
workflow.set_entry_point("generate_params")
workflow.add_edge("generate_params", "find_links")
workflow.add_edge("find_links", END)
app = workflow.compile()

# 4. PLUG IN THE TEST INPUT HERE
if __name__ == "__main__":
    test_input = {
        "resume_map": {
            "experience": "4 years",
            "current_role": "Content Specialist",
            "skills": ["Copywriting", "SEO", "Adobe Creative Suite"],
            "industry": "Fast Fashion Retail"
        },
        "target_goal": "Head of Growth at a Fashion AI Startup"
    }

    print("--- STARTING FIND MY CIRCLE TEST ---")
    for event in app.stream(test_input):
        for node, data in event.items():
            if node == "generate_params":
                print(f"\n[PHASE 2.1] Generated Niche Search Queries:")
                for i, q in enumerate(data['search_parameters'], 1):
                    print(f"  {i}. {q}")
            elif node == "find_links":
                print(f"\n[PHASE 2.2] Curated Circle Results:")
                for circle in data['curated_circles']:
                    print(f"  - {circle['platform']}: {circle['name']} ({circle['url']})")