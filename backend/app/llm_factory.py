from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
import os

def get_hub_llm(temperature=0):
    # 1. Try Groq (Open Source Llama 3) - Preferred for Hackathon/Free
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            return ChatGroq(
                model_name="llama-3.1-8b-instant",  # Use 8b-instant for speed & quota
                temperature=temperature,
                api_key=groq_key
            )
        except Exception as e:
            print(f"Groq Init Error: {e}")

    # 2. Try OpenAI - Fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and "your-key-here" not in openai_key:
        try:
            return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
        except Exception as e:
            print(f"OpenAI Init Error: {e}")

    # 3. Fallback
    print("WARNING: No API Keys found. Using Mock LLM.")
    return RunnableLambda(lambda x: AIMessage(content="[SYSTEM ALERT] No valid API Key found (GROQ_API_KEY or OPENAI_API_KEY). Please add GROQ_API_KEY to your environment for the Open Source Llama model."))

# Alias for backward compatibility if imported as get_llm
get_llm = get_hub_llm
