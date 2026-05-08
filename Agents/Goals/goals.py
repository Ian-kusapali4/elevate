from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from Agents.Pivot.schemas import UniversalGoalsState
import ast
import json

# Initialize LLM and Search Tool
llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)
search_tool = TavilySearchResults(k=3)

def goal_analysis_node(state: UniversalGoalsState):
    """
    Performs live research via Tavily and breaks down a goal into 5 dynamic pillars.
    """
    user_goal = state.get("target_goal", "Target Role")
    profile = state.get("CandidateProfile", {})
    candidate_current = profile.get("jobTitle", "Professional")

    print(f"🕵️ SEARCHING MARKET DATA FOR: {user_goal}")
    
    # 1. LIVE WEB SEARCH
    search_query = f"top 5 technical skills and market requirements to become a {user_goal} in 2026"
    try:
        raw_search_results = search_tool.run(search_query)
    except Exception as e:
        print(f"Search failed: {e}")
        raw_search_results = "Use internal knowledge for 2026 market trends."

    # 2. CONSTRUCT RESEARCH-BASED PROMPT
    prompt = f"""
    You are a Career Architect. Based on this LIVE MARKET RESEARCH:
    {raw_search_results}
    
    TARGET GOAL: "{user_goal}"
    CANDIDATE CURRENT ROLE: "{candidate_current}"
    
    TASK: Identify 5 core pillars required to reach this goal.
    For each pillar, assign a 'complexity' (1-5) and a 1-sentence 'reasoning' based on the search data.
    
    OUTPUT FORMAT (Strict Python List of Dicts):
    [
        {{"skill": "Skill Name", "complexity": 4, "reasoning": "Detailed reason why this matters in 2026."}},
        ...
    ]
    """
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Clean formatting
        if "```" in content:
            content = content.split("```")[1].replace("python", "").replace("json", "").strip()
        
        start = content.find("[")
        end = content.rfind("]") + 1
        clean_str = content[start:end]
        
        requirements = ast.literal_eval(clean_str)
        
        # Validation
        if not isinstance(requirements, list) or len(requirements) == 0:
            raise ValueError("Invalid format")

        return {"market_requirements": requirements}

    except Exception as e:
        print(f"⚠️ PARSING ERROR: {e}")
        # Dynamic fallback that still uses the goal name
        return {
            "market_requirements": [
                {"skill": f"{user_goal} Fundamentals", "complexity": 3, "reasoning": "Core domain knowledge required for this specific transition."},
                {"skill": "AI-Enhanced Workflow", "complexity": 4, "reasoning": "Integrating agentic tools into this role is a 2026 standard."},
                {"skill": "Strategic Communications", "complexity": 2, "reasoning": "Stakeholder management tailored for this seniority level."},
                {"skill": "Data-Driven Decisioning", "complexity": 4, "reasoning": "Required to measure impact in the new role."},
                {"skill": "Domain-Specific Certification", "complexity": 5, "reasoning": "Validates expertise for high-level placement."}
            ]
        }