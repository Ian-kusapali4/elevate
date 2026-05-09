from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from Agents.Pivot.schemas import UniversalGoalsState
import ast
import re

# Initialize LLM and Search Tool
llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)
search_tool = TavilySearchResults(k=3)

def goal_analysis_node(state: UniversalGoalsState):
    """
    Analyzes professional goals with a focus on high-income skill gaps and 2026 market reality.
    Redefines 'complexity' as a 'Time-to-Mastery' metric to make UI bars meaningful.
    """
    user_goal = state.get("target_goal")
    if not user_goal or user_goal == "None":
        user_goal = "Target Career Goal"

    profile = state.get("CandidateProfile", {})
    current_role = profile.get("jobTitle", "Professional")
    current_skills = profile.get("skills", [])

    print(f"🎯 AGGRESSIVE ANALYSIS FOR GOAL: {user_goal}")
    
    # 1. SEARCH FOR SALARY DRIVERS & MARKET GAPS
    search_query = f"requirements and high-income skills to earn $200k+ as a {user_goal} in 2026"
    try:
        market_intel = search_tool.run(search_query)
    except Exception as e:
        print(f"Search failed: {e}")
        market_intel = "Focus on Agentic AI, high-level strategy, and technical leadership."

    # 2. CONSTRUCT STRONGER PROMPT WITH MEANINGFUL SCALING
    prompt = f"""
    You are a Brutally Honest Career Strategist in 2026. 
    The user wants to earn $200k+ as a "{user_goal}". 
    Current Role: "{current_role}".
    Current Skills: {current_skills}

    MARKET CONTEXT (2026): {market_intel}

    TASK:
    Identify 5 "Gap Skills" required to reach the $200k level.
    
    CRITICAL: THE 'COMPLEXITY' SCORE (1-5) REPRESENTS THE MASTERY GAP:
    - 1: Minor Adjustment (Weekend of study).
    - 2: Short Course (2-4 weeks).
    - 3: Significant Pivot (2-3 months of deep practice).
    - 4: Professional Mastery (4-6 months + Project work).
    - 5: Strategic Overhaul (6-12 months / Certification / High barrier to entry).

    For each pillar, assign:
    - skill: High-leverage name.
    - complexity: 1-5 (Mastery Gap).
    - reasoning: ROI justification (Why this pays $200k).
    - status: Either 'Missing', 'Partial', or 'Acquired'.

    OUTPUT ONLY A VALID PYTHON LIST:
    [
        {{"skill": "Skill Name", "complexity": 5, "reasoning": "...", "status": "Missing"}},
    ]
    """
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        # Clean the response string
        content = re.sub(r"```(python|json)?\n?", "", content)
        content = content.replace("```", "").strip()
        
        start_index = content.find("[")
        end_index = content.rfind("]") + 1
        
        if start_index == -1 or end_index == 0:
            raise ValueError("No list found in LLM output.")
            
        clean_list_str = content[start_index:end_index]
        requirements = ast.literal_eval(clean_list_str)
        
        if not isinstance(requirements, list):
            raise ValueError("Output is not a list.")

        return {"market_requirements": requirements, "target_goal": user_goal}

    except Exception as e:
        print(f"⚠️ PARSING ERROR: {e}")
        return {
            "market_requirements": [
                {"skill": f"{user_goal} Architecture", "complexity": 5, "reasoning": "The core design logic needed for $200k+ roles.", "status": "Missing"},
                {"skill": "Agentic System Design", "complexity": 4, "reasoning": "Standard 2026 automation proficiency.", "status": "Missing"},
                {"skill": "Operational ROI", "complexity": 3, "reasoning": "Connecting technical work to revenue.", "status": "Missing"},
                {"skill": "Stakeholder Influence", "complexity": 2, "reasoning": "High-level political/strategic alignment.", "status": "Partial"},
                {"skill": "AI Tooling", "complexity": 1, "reasoning": "Daily productivity via latest AI models.", "status": "Acquired"}
            ],
            "target_goal": user_goal
        }