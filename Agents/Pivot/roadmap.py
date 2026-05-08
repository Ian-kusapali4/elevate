from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Agents.Pivot.schemas import DiscoveryState

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0.3)

def roadmap_generator_node(state: DiscoveryState):
    """
    Transforms gap_skills into a time-blocked learning curriculum.
    """
    # 1. Safe access for configuration data
    hours_per_day = state.get("hours_per_day", 2) 
    target_role = state.get("selected_path", "AI Specialist")
    
    # 2. Handle the Analysis Report (Dictionary vs Object)
    analysis = state.get("analysis_report")
    
    gaps_list = []
    if isinstance(analysis, dict):
        # If it's the fallback dictionary
        gaps_list = analysis.get("gaps", [])
    elif analysis:
        # If it's a Pydantic object
        gaps_list = getattr(analysis, "gaps", [])

    # 3. Format the gaps string
    gaps_str = ", ".join(gaps_list) if gaps_list else "Emerging AI Architectures and Cloud MLOps"

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Technical Curriculum Designer. Create a week-by-week "
            "learning roadmap to bridge technical gaps for the role: {role}. "
            "The user has {hours} hours per day to study. \n\n"
            "Format your response with Clear Week Headers (e.g., Week 1: Foundations) "
            "and bulleted topics."
        )),
        ("human", "GAPS TO BRIDGE: {gaps}")
    ])

    chain = prompt | llm
    
    try:
        roadmap = chain.invoke({
            "role": target_role,
            "hours": hours_per_day,
            "gaps": gaps_str
        })

        # Return both the text and the raw gaps for the final loopback node
        return {
            "learning_roadmap": roadmap.content,
            "target_gap_skills": gaps_list
        }
    except Exception as e:
        print(f"Error in Roadmap Node: {e}")
        return {"learning_roadmap": "Unable to generate roadmap at this time."}