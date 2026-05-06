import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
# Ensure your schemas.py is in the 'Pivot' directory
from Pivot.schemas import DiscoveryState, BrainstormOutput

llm = ChatOllama(
    model="gemma3:12b-cloud", 
    temperature=0.7,
    format="json" # Ensures the model strictly follows JSON formatting
)

def path_brainstormer_node(state: DiscoveryState):
    """
    Synthesizes search results and profile data into 3-5 potential career paths.
    """
    # FIX 1: Bracket access for profile
    profile = state["profile"]
    
    # FIX 2: Safe access for discovery_output
    discovery_data = state.get("discovery_output", [])
    search_intel = str(discovery_data)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a 2026 Career Architect. Combine user background with market intelligence. \n\n"
            "CRITICAL: You must return a JSON object with the key 'suggested_paths'. "
            "Each item in the list must follow this EXACT structure (use double curly braces to escape):\n"
            "{{\n"
            "  \"suggested_paths\": [\n"
            "    {{\n"
            "      \"title\": \"Job Title\",\n"
            "      \"description\": \"A detailed overview of what this role entails in 2026.\",\n"
            "      \"pitch\": \"Why this specific role is a perfect match for the user's current skills.\",\n"
            "      \"market_context\": \"Trend data and growth %\",\n"
            "      \"bridge_skills\": [\"Skill 1\", \"Skill 2\"],\n"
            "      \"gap_skills\": [\"Skill 3\", \"Skill 4\"],\n"
            "      \"salary_range\": \"$XXX,XXX - $YYY,YYY\"\n"
            "    }}\n"
            "  ]\n"
            "}}"
        )),
        ("human", (
            "USER PROFILE:\n"
            "Title: {jobTitle}\n"
            "Experience: {years_exp} years\n"
            "Skills: {skills}\n\n"
            "MARKET INTELLIGENCE (2026):\n"
            "{search_results}\n\n"
            "Generate the suggested career paths."
        ))
    ])

    # Enforce Structured Output via Pydantic
    structured_llm = llm.with_structured_output(BrainstormOutput, method="json_mode")
    chain = prompt | structured_llm
    
    try:
        # Run the synthesis
        result = chain.invoke({
            "jobTitle": profile.jobTitle,
            "years_exp": profile.years_of_experience,
            "skills": ", ".join(profile.skills),
            # FIX 3: Changed 'state.discovery_output' to 'search_intel' 
            # This was the specific line causing your last error!
            "search_results": search_intel 
        })
        
        return {"suggested_paths": result.suggested_paths}
    
    except Exception as e:
        print(f"Error in Brainstormer Node: {e}")
        # Fallback empty list if parsing fails
        return {"suggested_paths": []}


if __name__ == "__main__":
    from Pivot.schemas import CandidateProfile, DiscoveryState, EmergingRole

    # 1. Satisfy all CandidateProfile requirements
    mock_profile = CandidateProfile(
        jobTitle="Software Engineer",
        companyName="Self-Employed",
        jobType=["Full-time"],
        jobExcerpt="Lead developer specializing in agentic workflows and AI architecture.",
        years_of_experience=5,
        skills=["Python", "FastAPI", "Docker", "LangGraph"],
        jobLevel="Senior",
        jobIndustry=["Tech"],
        jobGeo="Blantyre"
    )

    # 2. Satisfy all EmergingRole requirements
    mock_intel = EmergingRole(
        title="Agentic Systems Architect",
        relevance_score=95,
        why_it_fits="Deep expertise in LangGraph and state-machine orchestration.",
        market_link="https://linkedin.com/jobs/agentic-architect-2026"
    )

    mock_state = DiscoveryState(
        profile=mock_profile,
        discovery_output=[mock_intel] 
    )

    print("\n" + "="*50)
    print("🚀 CALLING GEMMA3 BRAINSTORMER")
    print("="*50)

    # 3. Invoke the node
    output = path_brainstormer_node(mock_state)

    # 4. Print the synthesized paths with corrected attribute names
    paths = output.get("suggested_paths", [])
    
    if not paths:
        print("❌ No paths generated. Check your Gemma3 connection.")
    else:
        for i, path in enumerate(paths, 1):
            # Using getattr() as a safety net so the script never crashes
            title = getattr(path, 'title', 'N/A')
            desc = getattr(path, 'description', 'N/A')
            market = getattr(path, 'market_context', 'N/A')
            bridge = getattr(path, 'bridge_skills', [])
            gaps = getattr(path, 'gap_skills', [])
            salary = getattr(path, 'salary_range', 'N/A')

            print(f"\n[PATH #{i}]: {title}")
            print(f"📝 DESCRIPTION: {desc}")
            print(f"📊 MARKET CONTEXT: {market}")
            print(f"🔗 BRIDGE SKILLS: {', '.join(bridge)}")
            print(f"⚡ SKILLS TO LEARN: {', '.join(gaps)}")
            print(f"💰 SALARY RANGE: {salary}")
            print("-" * 30)

    print("\n" + "="*50)
    print("✅ TEST COMPLETE")
    print("="*50)