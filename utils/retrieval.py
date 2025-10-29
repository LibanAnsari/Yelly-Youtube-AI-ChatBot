from langchain_community.vectorstores import FAISS
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()

@traceable(name='load_vector_store')
def load_vector_store():
    vector_store = FAISS.load_local(
        "/tmp/data/faiss_index", HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"), allow_dangerous_deserialization=True
    )
    
    return vector_store

@traceable(name='get_mutiquery_retriever')
def get_mutiquery_retriever(vector_store, llm):
    
    mutiquery_retriever = MultiQueryRetriever.from_llm(
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        llm=llm
    )

    return mutiquery_retriever

@traceable(name='get_mmr_retriever')
def get_mmr_retreiver(vector_store):
    
    mmr_retreiver = vector_store.as_retriever(
        search_type = 'mmr',
        search_kwargs={"k": 6, "lambda_mult": 0.8} # "lambda_mult": 1 will behave as similarity search           
    )
    
    return mmr_retreiver