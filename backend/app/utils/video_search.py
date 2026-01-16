from duckduckgo_search import DDGS

class VideoSearchService:
    def search(self, query: str, limit: int = 4):
        try:
            # Clean Query: If LLM hallucinated a URL, try to save it or fail.
            if query.startswith("http"):
                print(f"WARNING: LLM provided a URL '{query}' instead of keywords. DDGS might fail.")
                # Strategy: If it's a youtube link, maybe just return it as a result if valid? 
                # But better to search for metadata? Hard.
                # Let's just strip the URL and hope? No.
                # Let's just pass it, but maybe add "video" keyword?
                pass 

            print(f"Executing Real Video Search via DDGS for: {query}")
            results = []
            
            with DDGS() as ddgs:
                # 'v' type searches for videos
                ddgs_gen = ddgs.videos(query, max_results=limit)
                
                for r in ddgs_gen:
                    # DDGS returns: title, content, description, duration, publisher, embed_url, etc.
                    results.append({
                        "title": r.get("title"),
                        "link": r.get("content"), # 'content' usually has the watch URL
                        "thumbnail": r.get("images", {}).get("large") or r.get("images", {}).get("medium") or "",
                        "duration": r.get("duration", "Active"),
                        "channel": r.get("publisher", "YouTube")
                    })
            
            if not results:
                print(f"DDGS returned no results for {query}")
                return []
                
            return results
        except Exception as e:
            print(f"Video Search Error (DDGS): {e}")
            return []

video_searcher = VideoSearchService()
