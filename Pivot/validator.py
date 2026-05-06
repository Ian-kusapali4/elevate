from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Pivot.schemas import DeepDiveResult, CandidateProfile

# Using a powerful model here for high-precision gap analysis
llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)

def market_validation_node(state: dict):
    """
    Detailed comparison between candidate skills and live market requirements.
    """
    # 1. Use brackets for the profile (since we know it exists from START)
    profile: CandidateProfile = state["profile"]
    
    # 2. Use .get() for market_data to avoid the KeyError
    # If the deep-dive search hasn't run, we fall back to discovery_output or a placeholder
    market_data = state.get("market_data")
    if not market_data:
        market_data = state.get("discovery_output", "No live market postings found; using trend data.")
        
    target_path = state.get("selected_path", "General AI Role")

    prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a strict JSON-only API. You must compare the candidate against the role of {target_path}.\n"
        "RESPONSE RULES:\n"
        "1. Do NOT write any conversational text or disclaimers.\n"
        "2. Return ONLY a JSON object matching this structure:\n"
        "{{\"strengths\": [], \"gaps\": [], \"market_fit_score\": 0}}"
    )),
    ("human", "RESUME SKILLS: {user_skills}\nMARKET DATA: {market_data}")
])

    # Enforce structured output
    structured_llm = llm.with_structured_output(DeepDiveResult)
    chain = prompt | structured_llm
    
    try:
        analysis = chain.invoke({
            "target_path": target_path,
            "user_skills": ", ".join(profile.skills),
            "market_data": str(market_data)
        })

        return {"analysis_report": analysis}
        
    except Exception as e:
        print(f"Error in Validator Node: {e}")
        # Fallback empty report so the graph can continue to the roadmap
        return {
            "analysis_report": {
                "strengths": profile.skills[:3],
                "gaps": ["Market-specific emerging skills"],
                "market_fit_score": 50
            }
        }