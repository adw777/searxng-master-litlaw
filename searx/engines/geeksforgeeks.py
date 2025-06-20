from json import loads
from urllib.parse import urlencode, quote_plus

# about
about = {
    "website": "https://www.geeksforgeeks.org",
    "wikidata_id": None,
    "official_api_documentation": None,
    "use_official_api": True,
    "require_api_key": False,
    "results": "JSON",
}

# engine dependent config
categories = ['technical']
paging = False
language_support = False
timeout = 10.0

# search-url
base_url = 'https://recommendations.geeksforgeeks.org/api/v1/global-search'

def request(query, params):
    # Properly encode the query
    encoded_query = quote_plus(query)
    
    search_params = {
        'products': 'articles',
        'articles_count': '50',
        'query': encoded_query
    }
    
    params['url'] = f"{base_url}?{urlencode(search_params)}"
    
    # Add required headers
    params['headers'] = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://www.geeksforgeeks.org',
        'Referer': 'https://www.geeksforgeeks.org/'
    }
    
    # Method should be GET
    params['method'] = 'GET'
    
    return params

def response(resp):
    results = []
    
    try:
        json_data = loads(resp.text)
        
        if not json_data.get('detail', {}).get('articles', {}).get('data'):
            return results
            
        articles = json_data['detail']['articles']['data']
        
        for article in articles:
            result = {
                'title': article.get('post_title', ''),
                'url': article.get('post_url', ''),
                'content': article.get('post_excerpt', ''),
                'img_src': article.get('img', ''),
                'publishedDate': article.get('post_modified', ''),
                'score': article.get('score', 0),
                'engine': 'geeksforgeeks'
            }
            results.append(result)
            
    except Exception as e:
        print(f"Error parsing GeeksForGeeks response: {e}")
        
    return results