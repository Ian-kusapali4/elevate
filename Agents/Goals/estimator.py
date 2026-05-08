from Core.Unifiedstate import IndigoMasterState
from langchain_ollama import ChatOllama

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)

def universal_reality_check_node(state: IndigoMasterState):
    """
    Uses AI to provide a blunt, realistic assessment of the time and effort required.
    """
    requirements = state.get("market_requirements", [])
    target_goal = state.get("target_goal", "Target Role")
    profile = state.get("CandidateProfile", {})
    
    skills_list = ", ".join([r.get('skill') for r in requirements])
    
    # Let the AI perform the "Reality Check" instead of just math
    prompt = f"""
    Analyze the gap for a {profile.get('jobTitle')} trying to become a {target_goal}.
    The required pillars are: {skills_list}.
    
    Provide a BLUNT, 3-sentence 'Reality Check'. 
    Sentence 1: Total estimated study hours and weeks.
    Sentence 2: The hardest hurdle they will face.
    Sentence 3: A piece of 'brutal' advice for 2026.
    """
    
    try:
        response = llm.invoke(prompt)
        baseline_truth = response.content.strip()
    except:
        baseline_truth = "Awaiting deeper analysis. Expected timeline: 6-12 months of dedicated transition."

    return {
        "baseline_truth": baseline_truth
    }