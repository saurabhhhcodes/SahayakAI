from app.utils.video_search import video_searcher
import json

def test_search():
    print("--- TEST 1: Good Query ---")
    results = video_searcher.search("Gravity for kids")
    print(json.dumps(results, indent=2))
    
    print("\n--- TEST 2: URL Query (Simulating Hallucination) ---")
    results_url = video_searcher.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(json.dumps(results_url, indent=2))

if __name__ == "__main__":
    test_search()
