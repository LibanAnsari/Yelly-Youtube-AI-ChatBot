from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langsmith import traceable

@traceable(name='format_docs')
def format_docs(retreived_docs):
    context_text = "\n\n".join(doc.page_content for doc in retreived_docs)
    return context_text

@traceable(name='update_history')
def update_history(chat_history, new_chat):
    
    if new_chat['role'] == 'user':
        chat_history.append(HumanMessage(content=new_chat['content']))
    else:
        chat_history.append(AIMessage(content=new_chat['content']))
        
    return chat_history
    

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful and cheerful assistant, YOUR NAME is "Yelly ^^".  
You chat with the user in a friendly but reliable way, using the YouTube transcript as your main source.  

Guidelines:
- If the user just greets or makes small talk, reply politely and briefly, even without the transcript.  
- Try to answer based on the transcript whenever possible.  
- If the transcript doesn't cover the question, gently let the user know instead of making things up.  
- Keep answers simple, clear, and easy to follow (short paragraphs or bullet points where useful not always).  
- Match the user's tone: be casual and add light emojis if they are casual, keep it neutral if they're formal.  
- Stay supportive and helpful, don't sound too strict.  
"""),

    MessagesPlaceholder(variable_name="chat_history"),

    ("human", """Transcript Context:
{context}

Question:
{question}""")
])