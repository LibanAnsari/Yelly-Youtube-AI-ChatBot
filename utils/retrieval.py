from langchain_community.vectorstores import FAISS
from langchain.retrievers import MultiQueryRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def load_vector_store():
    vector_store = FAISS.load_local(
        "data/faiss_index", GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"), allow_dangerous_deserialization=True
    )
    
    return vector_store

def get_mutiquery_retriever(vector_store, llm):
    
    mutiquery_retriever = MultiQueryRetriever.from_llm(
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        llm=llm
    )

    return mutiquery_retriever

def get_mmr_retreiver(vector_store):
    
    mmr_retreiver = vector_store.as_retriever(
        search_type = 'mmr',
        search_kwargs={"k": 4, "lambda_mult": 0.8} # "lambda_mult": 1 will behave as similarity search           
    )
    
    return mmr_retreiver