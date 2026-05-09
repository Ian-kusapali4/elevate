from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Core.Unifiedstate import  CandidateProfile
from Agents.Pivot.tools import career_discovery_search

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)

def discovery_search_node(state: CandidateProfile):
    """
    Analyzes the user profile and triggers search tool calls to find 
    emerging 2026 career trends.
    """
    # 1. Safely extract data from state
    profile = state.get("CandidateProfile", {})
    skills = profile.get("skills", [])
    
    # 2. Prepare clean variables for the prompt
    # Use snake_case consistently for prompt variables
    current_job = profile.get("jobTitle", "Professional")
    current_level = profile.get("jobLevel", "Experienced")
    current_geo = profile.get("jobGeo", "Remote")
    
    # Format skills and industries for better context
    core_skills_str = ", ".join(skills[:5]) if skills else "General professional skills"
    
    industries = profile.get("jobIndustry", [])
    industry_str = ", ".join(industries) if isinstance(industries, list) else str(industries)

    # 3. The Prompt - Match these {} names exactly to the invoke dictionary below
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Forensic Market Researcher in 2026. Your goal is to find 'High-Adjacency' pivots.\n\n"
            "Instead of generic AI roles, search for:\n"
            "1. Emerging job titles that specifically require {core_skills}.\n"
            "2. How {job_title} roles are being re-classified in the {industry_name} sector.\n"
            "3. Specific 'Bridge Roles' for {job_level} {job_title} professionals in {geo}."
        )),
        ("human", (
            "Current Role: {job_title} ({job_level})\n"
            "Industry: {industry_name}\n"
            "Top Skills: {core_skills}\n"
            "Location: {geo}\n\n"
            "Generate 2 high-intent search queries to identify REAL market shifts."
        ))
    ])

    chain = prompt | llm.bind_tools([career_discovery_search])
    
    # 4. CRITICAL: The keys here MUST match the {} variables in the prompt above
    response = chain.invoke({
        "job_title": current_job,
        "job_level": current_level,
        "industry_name": industry_str,
        "core_skills": core_skills_str,
        "geo": current_geo
    })

    if not response.tool_calls:
        return {"discovery_output": [{"url": "internal", "content": "Market trend: Shift toward Agentic Operations."}]}

    return {"discovery_output": response.tool_calls}