import os
import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Core.Unifiedstate import ElevateMasterState, BrainstormOutput, CareerPath

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0.7, format="json")

def path_brainstormer_node(state: ElevateMasterState):
    profile = state.get("CandidateProfile", {})
    search_intel = str(state.get("discovery_output", "No search data found."))

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a 2026 Career Architect specializing in Agentic Operations. "
            "Return ONLY raw JSON with a single root key called 'suggested_paths'. "
            "Do NOT use markdown formatting like ```json."
        )),
        ("human", "USER PROFILE: {profile}\n\nMARKET INTEL: {search_results}")
    ])

    chain = prompt | llm 

    try:
        response = chain.invoke({"profile": str(profile), "search_results": search_intel})
        
        # 1. Clean and parse
        cleaned_content = response.content.replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(cleaned_content)
        
        # 2. Flexible extraction
        paths_data = parsed_json.get("suggested_paths") or parsed_json.get("pivotPaths") or []
        
        # 3. Validate with Pydantic for safety
        validated_output = BrainstormOutput.model_validate({"suggested_paths": paths_data})
        
        # 4. Return as a list of dicts for the TypedDict state
        serializable_paths = [path.model_dump() for path in validated_output.suggested_paths]
        
        print(f"✅ SUCCESS: Found {len(serializable_paths)} paths")
        return {"suggested_paths": serializable_paths}

    except Exception as e:
        print(f"❌ NODE FAILURE: {str(e)}")
        # Return an empty list so the UI knows the node finished but failed
        return {"suggested_paths": []}