import requests
import json
def search_searxng( query, num_results=10):
        """
        Search SearXNG and return the top results
        
        Parameters:
        query (str): The search query
        num_results (int): Number of results to return
        engines (list or str): Specific engine(s) to use for the search. If None, uses a mix of general and custom engines.
        
        Returns:
        list: Top search results
        """
      
        engines = 'tpointtec'
        
        searxng_url = "http://localhost:8081/search"
        # Parameters for the search
        params = {
            'q': query,
            'format': 'json', 
            'engines': engines,
            'language': 'en',
            'pageno': 1,
            'results_count': num_results
        }
        
        try:
            response = requests.get(searxng_url, params=params, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            results_json = response.json()
            results = results_json.get('results', [])[:num_results]
            
            return results
        except requests.exceptions.RequestException as e:
            print(f"Error searching SearXNG: {e}")
            return []

# def search_searxng(query, num_results=10):
#     """
#     Perform a general search using SearXNG and return the top results
    
#     Parameters:
#     query (str): The search query
#     num_results (int): Number of results to return
    
#     Returns:
#     list: Top search results
#     """
#     # Your SearXNG instance URL (update with your actual port if different)
#     searxng_url = "http://localhost:8080/search"
    
#     # Parameters for the search - keeping it general by not specifying categories or engines
#     params = {
#         'q': query,
#         'format': 'json',
#         'language': 'all',
#         'pageno': 1,
#         'results_count': num_results
#     }
    
#     try:
#         response = requests.get(searxng_url, params=params)
#         response.raise_for_status()  # Raise exception for HTTP errors
        
#         results = response.json()
        
        
#         # Extract just the results list
#         return results.get('results', [])[:num_results]
    
#     except requests.exceptions.RequestException as e:
#         print(f"Error searching SearXNG: {e}")
#         return []

def display_results(results):
    """
    Display the search results in a readable format
    """
    if not results:
        print("No results found.")
        return
        
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('title')}")
        print(f"   URL: {result.get('url')}")
        print(f"   Source: {result.get('engine')}")
        print(f"   Description: {result.get('content', 'No description available')}")
        print("-" * 80)

# Example usage
if __name__ == "__main__":
    while True:
        query = input("\nEnter your search query (or 'quit' to exit): ")
        if query.lower() in ['quit', 'exit', 'q']:
            break
            
        print(f"Searching for: {query}")
        results = search_searxng(query)
        display_results(results)