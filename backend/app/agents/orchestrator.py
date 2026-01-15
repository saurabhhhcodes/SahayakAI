from typing import TypedDict, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
from app.llm_factory import get_llm

load_dotenv()

# Define the state
class AgentState(TypedDict):
    messages: list
    next_step: str

# Initialize LLM
llm = get_llm(temperature=0)

ROUTER_PROMPT = """
You are the Orchestrator for Sahayak.AI.
Your job is to route the user's query to the correct expert agent.

Available Agents:
1. 'pedagogy': For queries about HOW to teach, basic explanations, content generation (Lesson Plans, Quizzes, PRESENTATIONS, SLIDES), or IMAGES of educational concepts.
2. 'management': For queries about classroom behavior, discipline, noise, or engagement strategies.
3. 'general': For greetings, general chat, or specific web search requests for non-educational things.

RULES:
- If the user asks for "Presentation", "Slides", "PPT" on a topic -> 'pedagogy'.
- If the user asks for an IMAGE of a concept -> 'pedagogy'.
- If the user asks for an IMAGE of a generic object -> 'general'.
- Analyze the user's input and return ONLY the agent name: 'pedagogy', 'management', or 'general'.
"""

def router_node(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTER_PROMPT),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"input": last_message.content})
    decision = response.content.strip().lower()
    
    if decision not in ['pedagogy', 'management', 'general']:
        decision = 'general'
        
    return {"next_step": decision}

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ... (Previous code)

GENERAL_SYSTEM_PROMPT = """
You are Sahayak.AI, a helpful teaching assistant. 
You are currently in 'General Chat' mode.
Answer the user's questions politely.

**YOUR CAPABILITIES:**
1.- **MULTILINGUAL EXPERT**: You are fluent in all Indian languages (Hindi, Bengali, Tamil, Telugu, Marathi, etc.) and Global languages (Spanish, French, Amharic, Tigrinya). Always answer in the user's requested language.
- **VISUALS**: You can search for images using `[IMAGE_SEARCH: query]`.
- **TEACHING**: You can explain concepts efficiently.

**INSTRUCTIONS:**
- If asked "What can you do?", list your capabilities (Multilingual Expert, Visuals, Teaching).
- If asked for an image, the system will try to find it. Do NOT say "I cannot".
- If they ask about teaching math/science or classroom discipline, suggest they ask specifically so you can transfer them to the expert agents.
- Always use the conversation history to maintain context.
"""

def general_node(state: AgentState):
    messages = state['messages']
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", GENERAL_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    
    # Extract history (all except last message) and input (last message)
    # Note: In main.py we pass the full list. Here we just take it.
    # Actually, state['messages'] is the full list including the latest user message.
    # LangChain's MessagesPlaceholder can take the list directly if we format it right.
    # But for simplicity, let's just pass the whole list as 'history' except the last one for input.
    
    history = messages[:-1]
    last_msg = messages[-1].content
    
    # Quick Check for Image Intent (Simple Heuristic)
    # If explicit request for external image
    image_url = ""
    lower_msg = last_msg.lower()
    if "show me image" in lower_msg or "search image" in lower_msg or "picture of" in lower_msg:
        from app.tools.search import search_images
        # Extract query roughly (remove keywords)
        query = lower_msg.replace("show me image", "").replace("search image", "").replace("picture of", "").replace("show me the image of", "").strip()
        if len(query) > 2:
            urls = search_images(query)
            if urls:
                image_url = f"\n\n![{query}]({urls[0]})"
            else:
                image_url = "\n\n(No images found on the web for this.)"

    response = chain.invoke({"history": history, "input": last_msg})
    
    # Append image if found
    final_content = response.content + image_url
    response.content = final_content
    
    return {"messages": [response]}

# Placeholder for now, will connect to actual agents
def pedagogy_node(state: AgentState):
    # This will be replaced by the actual pedagogy agent call
    return {"messages": [AIMessage(content="[Pedagogy Agent] I see you need help with a concept. Let me check the NCERT guidelines...")]}

def management_node(state: AgentState):
    # This will be replaced by the actual management agent call
    return {"messages": [AIMessage(content="[Management Agent] Handling classroom disruption is tough. Here is a strategy...")]}

# We will build the graph in a separate file or main.py to avoid circular imports during setup.
