import requests
import uuid
import time

BASE_URL = "http://localhost:8001"
USER_ID = str(uuid.uuid4())

def test_memory():
    print(f"Testing Memory for User: {USER_ID}")
    
    # Turn 1: State Name
    print("\n1. Setting Name...")
    res1 = requests.post(f"{BASE_URL}/chat", json={"text": "My name is Saurabh.", "user_id": USER_ID})
    print(f"AI: {res1.json()['data']}")
    
    # Turn 2: Recall Name
    print("\n2. Asking Name...")
    res2 = requests.post(f"{BASE_URL}/chat", json={"text": "What is my name?", "user_id": USER_ID})
    answer = res2.json()['data']
    print(f"AI: {answer}")
    
    if "Saurabh" in answer:
        print("✅ MEMORY TEST PASSED")
    else:
        print("❌ MEMORY TEST FAILED")

if __name__ == "__main__":
    test_memory()
