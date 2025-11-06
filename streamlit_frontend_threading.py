import streamlit as st
from langgraph_database_backend import chatbot,retrieve_all_threads,get_chat_title
from langchain_core.messages import HumanMessage,AIMessage
import uuid

# ****************** utility functions ****************

def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id
    
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].insert(0,thread_id)
    
def load_conversation(thread_id):
    state =chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])
    
    
    
    # ******************** Session steup ***************
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['thread_id'])


    
# ************************* sidebar UI **********
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()



# for thread_id in st.session_state['chat_threads'][::]:
#     if st.sidebar.button(str(thread_id)):

# for i, thread_id in enumerate(st.session_state['chat_threads'], start=1):
#     if st.sidebar.button(f"Chat {i}"):

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads']:
    title = get_chat_title(thread_id) or "New Conversation"
    button_label = f"🗨️ {title}"

    if st.sidebar.button(button_label, key=thread_id):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        # Move opened chat to top (like ChatGPT)
        st.session_state['chat_threads'].remove(thread_id)
        st.session_state['chat_threads'].insert(0, thread_id)

        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages


        st.session_state['thread_id']=thread_id
        messages = load_conversation(thread_id)
        
        temp_messages = []
        
        for msg in messages:
            if isinstance(msg,HumanMessage):
               role='user'
            else:
                role= 'assistant'
            temp_messages.append({'role':role,'content':msg.content})
            
        st.session_state['message_history']=temp_messages
            

# ***************** main UI **********************



# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
    
# {'role': 'user','content':'Hi'}
# {'role':'assistant','content':'Hi=ello'}

user_input=st.chat_input('Type here')

if user_input:
    
    #first add the message to message_history
    st.session_state['message_history'].append({'role': 'user','content': user_input})
    with st.chat_message('user'):
        st.text(user_input)
        
        
    # st.session_state -> dict ->
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
        
    
       # first add the message to message_history
       
if not user_input or user_input.strip() == "":
    # st.warning("Please enter a message before sending.")
    st.stop()
    


with st.chat_message("assistant"):
        
        # Show a spinner while the graph runs (especially important when using tools)
        with st.spinner("Thinking..."):
            
            final_state = chatbot.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG
            )
            
            final_messages = final_state.get('messages', [])
            ai_message = ""
            
            if final_messages:
                # Get the last message, which should be the final answer
                last_message = final_messages[-1]
                
                # Extract clean content from the last AIMessage
                if isinstance(last_message, AIMessage):
                    content = last_message.content
                    
                    if isinstance(content, str):
                        # Case 1: Simple string answer. Use a regex or simple split 
                        # to aggressively remove the starting metadata if it's still present 
                        # as part of the string.
                        if content.startswith("[{'type': 'text', 'text':"):
                            # This is the crucial step to clean the output string
                            try:
                                # Simple split based on where the clean text usually starts 
                                # and ends before the signature.
                                start_index = content.find("'text': '") + 9
                                end_index = content.find("', 'extras':")
                                ai_message = content[start_index:end_index]
                            except:
                                ai_message = content # Fallback if parsing fails
                        else:
                            ai_message = content
                        
                    elif isinstance(content, list):
                        # Case 2: Complex list (tool use) - Join only the string parts
                        cleaned_parts = [item for item in content if isinstance(item, str)]
                        ai_message = "".join(cleaned_parts)
                        
            # if not ai_message:
            #     ai_message = "I couldn't generate a clear response. Please try again."

            # 4. Display the clean, final answer
            st.text(ai_message)

    # 5. Save the clean answer to session history
st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})



