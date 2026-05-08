from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0)

def resume_loopback_node(state: dict):
    """
    Generates optimized resume bullet points based on the newly acquired skills
    and the specific 2026 market demand for the target role.
    """
    target_role = state.get("selected_path")
    roadmap = state.get("learning_roadmap")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Resume Optimizer. Write 3 high-impact bullet points "
                   "that reflect completion of the following curriculum for the role of {role}."),
        ("human", "COMPLETED CURRICULUM: {roadmap}")
    ])

    chain = prompt | llm
    bullets = chain.invoke({"role": target_role, "roadmap": roadmap})

    return {"resume_suggestions": bullets.content}