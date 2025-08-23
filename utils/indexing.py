from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def text_splitter(filename="data/transcripts.json"):
    try:
        loader = JSONLoader(
            file_path=filename,
            jq_schema=".[]",
        )
        text = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.create_documents([text[2].page_content]) # This will create a list of Documents (splitted text)

        print(len(chunks),"Docs created")
        print("Splitted Text Successfully!")
        
        return chunks
    except Exception as e:
        print("Error: ", e)


def create_vector_store(filename="data/transcripts.json"):
    try:
        chunks = text_splitter(filename)
        if chunks:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

            vector_store = FAISS.from_documents(chunks, embeddings)
            print("Vector Store created Successfully!")
            
            # print(vector_store.index_to_docstore_id)
            # print(vector_store.get_by_ids([vector_store.index_to_docstore_id[0]]))
            
            vector_store.save_local("data/faiss_index")
            print("Vector Store saved Successfully!")
        
    except Exception as e:
        print("Error: ", e)