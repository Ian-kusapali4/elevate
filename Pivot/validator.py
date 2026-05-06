from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Pivot.schemas import DeepDiveResult, CandidateProfile

# Using a powerful model (GPT-4o) here for high-precision gap analysis
llm = ChatOllama(model="gpt-4o", temperature=0)

def market_validation_node(state: dict):
    """
    Detailed comparison between candidate skills and live market requirements.
    """
    profile: CandidateProfile = state["profile"]
    market_data = state["market_data"]
    target_path = state["selected_path"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a 2026 Career Gap Analyst. Compare the Candidate against the Live Market."),
        ("human", "RESUME: {user_skills}\nMARKET DATA: {market_data}")
    ])

    structured_llm = llm.with_structured_output(DeepDiveResult)
    chain = prompt | structured_llm
    
    analysis = chain.invoke({
        "target_path": target_path,
        "user_skills": ", ".join(profile.skills),
        "market_data": str(market_data)
    })

    return {"analysis_report": analysis}