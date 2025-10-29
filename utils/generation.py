from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable
from .retrieval import get_mutiquery_retriever, get_mmr_retreiver
from .augmentation import format_docs, prompt

@traceable(name='get_chain')
def get_chain(vector_store):
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7
    )

    # retriever = get_mutiquery_retriever(vector_store=vector_store, llm=llm)
    retriever = get_mmr_retreiver(vector_store=vector_store)
    
    parser = StrOutputParser()

    parallel_chain = RunnableParallel({
        "chat_history": RunnableLambda(lambda x: x["chat_history"]),
        "context": RunnableLambda(lambda x: x["question"]) | retriever | RunnableLambda(format_docs),
        "question": RunnableLambda(lambda x: x["question"])
    })

    final_chain = parallel_chain | prompt | llm | parser
    
    return final_chain