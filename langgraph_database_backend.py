from langgraph.graph import StateGraph,START,END
from typing_extensions import TypedDict,Annotated
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

load_dotenv()

llm = ChatGoogleGenerativeAI(model= 'gemini-2.5-flash',temperature=0.7)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages] 
    
def chat_node(state: ChatState):
    messages = state['messages']
    response= llm.invoke(messages)
    return {"messages": [response]}  

    #checkpointer
    
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

checkpointer = SqliteSaver(conn=conn) 

graph = StateGraph(ChatState)
graph.add_node("chat_node",chat_node)
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)
chatbot = graph.compile(checkpointer = checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    
    return list(all_threads)


def get_chat_title(thread_id):
    """Return a short chat title based on the first user message."""
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    messages = state.values.get("messages", [])
    for msg in messages:
        if msg.type == "human":
            text = msg.content.strip()
            if len(text) > 40:
                text = text[:40] + "..."
            return text
    return "New Conversation"
