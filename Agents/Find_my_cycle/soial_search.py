import os
from tavily import TavilyClient
from Core.Unifiedstate import ElevateMasterState

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
def real_social_search_node(state: ElevateMasterState):
    """
    Executes live web searches to find real community links.
    """
    queries = state["search_parameters"]
    found_circles = []
    
    for query in queries:
        # We use 'advanced' search depth to find niche invite links
        search_result = tavily.search(
            query=f"{query} (site:discord.com OR site:slack.com OR site:reddit.com)", 
            search_depth="advanced",
            max_results=2
        )
        
        for res in search_result['results']:
            found_circles.append({
                "platform": "Web/Social",
                "name": res['title'],
                "url": res['url'],
                "snippet": res['content'][:150] # Useful for the Analyst node later
            })
            
    return {"curated_circles": found_circles}