# Goals/social_discovery.py
from langchain_ollama import ChatOllama

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)

def generate_circle_parameters_node(state: dict):
    """
    Analyzes the Resume Skill Map to create hyper-niche search terms.
    """
    resume_map = state.get("CandidateProfile")
    
    prompt = f"""
    Analyze this professional profile: {resume_map}
    
    Task: Generate 3 specific search queries to find "circles" (Slack, Discord, or niche forums).
    Rules:
    1. Focus on the intersection of their top 2 skills and their industry.
    2. One query must target a "Seniority" level (e.g., 'Executive' or 'Architect' circles).
    3. One query must target a "Growth" community (e.g., 'AI-driven Marketing experts').
    
    Return a list of strings only.
    """
    
    queries = llm.invoke(prompt)
    # We clean the output to get a list of search strings
    search_params = [q.strip() for q in queries.content.split("\n") if q]
    
    return {"search_parameters": search_params}