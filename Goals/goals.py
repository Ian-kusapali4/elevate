# Pivot/goals.py
from typing import List
from langchain_ollama import ChatOllama
from Pivot.schemas import GoalsState

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0.1)

def goal_reverse_engineer_node(state: GoalsState):
    """
    Stage 1: Input is a Specific Goal. 
    Action: Reverse-engineers the requirements for high-tier roles.
    """
    user_goal = state.get("target_goal_description")
    
    # SYSTEM PROMPT: Acting as a Headhunter for High-Salary Roles
    prompt = f"""
    You are an Executive Recruiter. 
    The user's goal is: {user_goal}
    
    Based on 2026 market data:
    1. What are the 5 non-negotiable hard skills for this salary bracket?
    2. What specific certifications or project types (e.g., 'Large Scale Agent Orchestration') are required?
    3. What is the typical 'Years of Experience' for this role?
    
    Return a structured list of requirements.
    """
    
    # Simulate Search Tool Call (In production, use Tavily/Google Search here)
    market_data = llm.invoke(prompt)
    
    return {
        "market_requirements": market_data.content,
        "entry_type": "goal"
    }