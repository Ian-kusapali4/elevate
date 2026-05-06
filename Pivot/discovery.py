from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Pivot.schemas import DiscoveryState
from Pivot.tools import career_discovery_search

# Using temperature 0 for discovery to keep search queries focused and relevant
llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)

def discovery_search_node(state: DiscoveryState):
    """
    Analyzes the user profile and triggers search tool calls to find 
    emerging 2026 career trends.
    """
    profile = state.profile
    skills_list = ", ".join(profile.skills[:5])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Career Strategist in 2026. Your job is to identify hybrid roles."),
        ("human", (
            "Current Role: {jobTitle} ({jobLevel})\n"
            "Industries: {industries}\n"
            "Top Skills: {skills}\n"
            "Location: {geo}\n\n"
            "Generate 2 highly specific search queries to find emerging 2026 roles for this person."
        ))
    ])

    # .bind_tools tells the LLM it has permission to use the search function
    chain = prompt | llm.bind_tools([career_discovery_search])
    
    response = chain.invoke({
        "jobTitle": profile.jobTitle,
        "jobLevel": profile.jobLevel,
        "industries": ", ".join(profile.jobIndustry),
        "skills": skills_list,
        "geo": profile.geo
    })

    # Returns the tool_calls which LangGraph will use to trigger the Search tool
    return {"discovery_output": response.tool_calls}