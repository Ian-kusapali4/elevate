# Pivot/goals.py
from langchain_ollama import ChatOllama
from Pivot.schemas import UniversalGoalsState # Using the new general schema

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)

def goal_analysis_node(state: UniversalGoalsState):
    """
    Reverse-engineers the pillars of success for ANY professional goal.
    """
    goal = state["target_goal"]
    
    prompt = f"""
    Role: Market Research Analyst (Year: 2026)
    Target Goal: "{goal}"
    
    Task: Identify the 5 core pillars (skills or competencies) required to achieve this goal.
    Assign a 'Complexity Score' from 1-5 for each.
    - 1: Basic (can be learned in a weekend)
    - 3: Intermediate (requires a few weeks of study)
    - 5: Advanced (requires months of deep work or certification)
    
    Format your response as a valid Python list of dicts: 
    [ {{"skill": "Skill Name", "complexity": 3}}, {{"skill": "Skill Name", "complexity": 5}} ]
    """
    
    response = llm.invoke(prompt)
    # Extract the list from the LLM response
    raw_content = response.content.strip().replace("```python", "").replace("```", "")
    import ast
    try:
        requirements = ast.literal_eval(raw_content)
        return {"market_requirements": requirements}
    except Exception as e:
        print(f"Parsing Error: {e} | Raw Content: {raw_content}")
        # Fallback to prevent crash
        return {"market_requirements": [{"skill": "General Mastery", "complexity": 3}]}