from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Pivot.schemas import DiscoveryState

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0.3)

def roadmap_generator_node(state: DiscoveryState):
    """
    Transforms gap_skills into a time-blocked learning curriculum.
    """
    # Assuming user provides 'hours_per_day' in the state elsewhere
    hours_per_day = state.get("hours_per_day", 2) 
    analysis = state.get("analysis_report")
    target_role = state.get("selected_path")

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Technical Curriculum Designer. Create a week-by-week "
            "learning roadmap to bridge technical gaps for the role: {role}. "
            "The user has {hours} hours per day to study. \n\n"
            "Return a structured plan with specific topics and estimated completion time."
        )),
        ("human", "GAPS TO BRIDGE: {gaps}")
    ])

    chain = prompt | llm
    
    roadmap = chain.invoke({
        "role": target_role,
        "hours": hours_per_day,
        "gaps": ", ".join(analysis.gaps) if analysis else "New AI Frameworks"
    })

    return {"learning_roadmap": roadmap.content}