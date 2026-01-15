from duckduckgo_search import DDGS

def search_images(query: str, max_results: int = 1):
    """
    Search for images using DuckDuckGo and return a list of image URLs.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(
                query,
                max_results=max_results,
                safesearch="on"
            ))
            urls = [r['image'] for r in results]
            return urls
    except Exception as e:
        print(f"Error searching images for {query}: {e}")
        # Fallback to Pollinations.ai (Open Source Generative)
        # Use simple URL encoding for the prompt
        import urllib.parse
        safe_query = urllib.parse.quote(query)
        # Use the 'nologo' and 'seed' to make it look stable? No, just simple path.
        fallback_url = f"https://pollinations.ai/p/{safe_query}"
        return [fallback_url]

if __name__ == "__main__":
    # Test
    print(search_images("Bengal Tiger"))
