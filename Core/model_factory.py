import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from services.parser.yaml_parser import yaml_extraction

#the center of all llm models used in the system
def get_groq_model():
    """
    Centralized function to initialize the LLM based on YAML config.
    """
    
    config = yaml_extraction('config.yaml')
    if config is None:
        print("Critical Error: Configuration could not be loaded. Exiting.")
        exit(1) 
    
    model_settings = config.get('model_settings', {})
    model_name = model_settings.get('name', 'llama3')
    temperature = model_settings.get('temperature', 0)
    
    # Optional: If you ever use a remote Ollama host (like in AWS)
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    return ChatOllama(
        model=model_name,
        temperature=temperature,
        base_url=base_url  
    )

def get_model():
    """
    Centralized function to initialize the LLM based on YAML config.
    """
    config = yaml_extraction('config.yaml')
    if config is None:
        print("Critical Error: Configuration could not be loaded. Exiting.")
        exit(1) 
    # Extract settings with safe fallbacks
    model_settings = config.get('model_groq_settings', {})
    model_name = model_settings.get('name', 'meta-llama/llama-prompt-guard-2-22m')
    temperature = model_settings.get('temperature', 0)
    
    return ChatGroq(
        temperature=temperature,
        model_name=model_name,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )