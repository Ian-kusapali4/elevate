from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Core.Unifiedstate import DeepDiveResult

# Using a powerful model here for high-precision gap analysis
llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)

def market_validation_node(state: dict):
    """
    Detailed comparison between candidate skills and live market requirements.
    """
    # 1. Safely pull the profile dictionary
    profile = state.get("CandidateProfile", {})
    
    # 2. Extract skills and handle potential missing keys
    skills = profile.get("skills", [])
    skills_str = ", ".join(skills) if isinstance(skills, list) else "Not Specified"
    
    # 3. Pull market data and target path
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
        # 4. FIXED: Use skills_str instead of profile.skills
        analysis = chain.invoke({
            "target_path": target_path,
            "user_skills": skills_str,
            "market_data": str(market_data)
        })

        return {"analysis_report": analysis}
        
    except Exception as e:
        print(f"Error in Validator Node: {e}")
        # 5. FIXED: Use skills[:3] instead of profile.skills[:3] in the fallback
        return {
            "analysis_report": {
                "strengths": skills[:3] if skills else ["General Expertise"],
                "gaps": ["Market-specific emerging skills"],
                "market_fit_score": 50
            }
        }