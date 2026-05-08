import os
import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Agents.Pivot.schemas import DiscoveryState, BrainstormOutput

llm = ChatOllama(model="gemma3:12b-cloud", temperature=0.7, format="json")

def path_brainstormer_node(state: DiscoveryState):
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
        print("\n" + "="*60)
        print("🚀 BRAINSTORMER: INVOKING LLM...")
        
        response = chain.invoke({
            "profile": str(profile),
            "search_results": search_intel
        })
        
        raw_content = response.content
        print("🔍 DEBUG: RAW LLM COMPLETION BELOW:")
        print(raw_content)
        print("="*60 + "\n")

        # 1. Clean the Markdown out of the string
        cleaned_content = raw_content.replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(cleaned_content)
        
        # 2. Find the paths array, even if the LLM hallucinated the structure
        paths_data = []
        if "brainstormOutput" in parsed_json and "pivotPaths" in parsed_json["brainstormOutput"]:
            paths_data = parsed_json["brainstormOutput"]["pivotPaths"]
        elif "pivotPaths" in parsed_json:
            paths_data = parsed_json["pivotPaths"]
        elif "suggested_paths" in parsed_json:
            paths_data = parsed_json["suggested_paths"]
        elif isinstance(parsed_json, list):
            paths_data = parsed_json # In case it just returns the array
            
        # 3. Rebuild the correct structure for Pydantic
        corrected_json = {"suggested_paths": paths_data}
        
        # 4. Validate
        validated_output = BrainstormOutput.model_validate(corrected_json)
        
        return {"suggested_paths": validated_output.suggested_paths}
    
    except Exception as e:
        print(f"!!! BRAINSTORMER FAILURE: {str(e)}")
        if 'raw_content' in locals():
            print(f"FAILED CONTENT: {raw_content}")

        return {"suggested_paths": [
            {
                "title": "Parsing Error Recovery", 
                "description": f"The JSON was formatted incorrectly: {str(e)[:50]}", 
                "pitch": "Check terminal for raw output", 
                "market_context": "N/A", 
                "bridge_skills": ["Debug JSON"], 
                "gap_skills": [], 
                "salary_range": "N/A"
            }
        ]}

