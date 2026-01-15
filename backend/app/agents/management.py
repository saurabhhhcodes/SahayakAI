from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.llm_factory import get_llm

llm = get_llm(temperature=0.3)

MGMT_SYSTEM_PROMPT = """
You are the 'Classroom Management Agent' for Sahayak.AI.
You help teachers manage large, multi-grade, or disruptive classes in government schools.
Focus on:
1. Positive reinforcement.
2. Quick engagement hooks (Claps, Chants, Stories).
3. Grouping strategies for multi-level classes.
4. De-escalation without corporal punishment.

USE VISUALS: If a strategy involves steps or a flow, output a Mermaid diagram code block (```mermaid ... ```).
  Example:
  ```mermaid
  graph TD
    A[Conflict] --> B{{Calm Down?}}
    B -- Yes --> C[Discuss]
    B -- No --> D[Take Break]
  ```

Keep answers short (under 100 words per tip) and immediately actionable.
Use conversation history to maintain context if the user follows up.
"""

def management_agent(query: str, context: str = "", history: list = []):
    prompt = ChatPromptTemplate.from_messages([
        ("system", MGMT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "Context: {context}\n\nQuery: {query}")
    ])
    
    chain = prompt | llm
    return chain.invoke({"query": query, "context": context, "history": history})
