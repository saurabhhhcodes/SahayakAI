import requests
import os
import json
import time

BASE_URL = "http://localhost:8001"
OUTPUT_DIR = "tests/results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_chat(text, lang="en"):
    print(f"\n[TEST] Chat ({lang}): {text}")
    try:
        start = time.time()
        res = requests.post(f"{BASE_URL}/chat", json={"text": text})
        print(f"Status: {res.status_code} | Time: {time.time() - start:.2f}s")
        if res.status_code == 200:
            data = res.json()
            print(f"Response: Tool={data.get('tool_used')}")
            # Save response
            with open(f"{OUTPUT_DIR}/chat_{lang}_{int(time.time())}.json", "w") as f:
                json.dump(data, f, indent=2)
            return data
        else:
            print("FAILED")
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def test_image(prompt):
    print(f"\n[TEST] Image Gen: {prompt}")
    try:
        start = time.time()
        res = requests.get(f"{BASE_URL}/generate/image", params={"prompt": prompt})
        print(f"Status: {res.status_code} | Time: {time.time() - start:.2f}s")
        if res.status_code == 200:
            path = f"{OUTPUT_DIR}/image_{int(time.time())}.png"
            with open(path, "wb") as f:
                f.write(res.content)
            print(f"Saved to {path}")
        else:
            print("FAILED")
    except Exception as e:
        print(f"ERROR: {e}")

def test_video(prompt):
    print(f"\n[TEST] Video Gen: {prompt}")
    try:
        start = time.time()
        res = requests.get(f"{BASE_URL}/generate/video", params={"prompt": prompt})
        print(f"Status: {res.status_code} | Time: {time.time() - start:.2f}s")
        if res.status_code == 200:
            path = f"{OUTPUT_DIR}/video_{int(time.time())}.mp4"
            with open(path, "wb") as f:
                f.write(res.content)
            print(f"Saved to {path}")
        else:
            print("FAILED")
    except Exception as e:
        print(f"ERROR: {e}")

def test_ppt(title):
    print(f"\n[TEST] Smart PPT: {title}")
    try:
        # Simulate empty slides to trigger auto-gen
        payload = {"title": title, "slides": []} 
        start = time.time()
        res = requests.post(f"{BASE_URL}/download/ppt", json=payload)
        print(f"Status: {res.status_code} | Time: {time.time() - start:.2f}s")
        if res.status_code == 200:
            path = f"{OUTPUT_DIR}/presentation_{int(time.time())}.pptx"
            with open(path, "wb") as f:
                f.write(res.content)
            print(f"Saved to {path}")
        else:
            print("FAILED")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("=== STARTING AUTOMATION TEST SUITE ===")
    
    # 1. Chat & Multilingual
    test_chat("Explain gravity to a 5 year old.")
    test_chat("Ek fox ki kahani sunao.", "hi") # Hindi test
    
    # 2. Image
    test_image("A futuristic classroom with AI robots teaching students")
    
    # 3. Video
    test_video("A fox running in a forest")
    
    # 4. Presentation
    test_ppt("The History of Mughal Empire")
    
    print("\n=== TESTS COMPLETED. CHECK 'tests/results' FOLDER ===")
