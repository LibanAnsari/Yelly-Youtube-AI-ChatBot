import os
import sys
import streamlit as st
import google.generativeai as genai
from langchain_core.messages import HumanMessage, AIMessage

# Ensure project root is on sys.path so we can import the sibling 'utils' package
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.yt_utils import get_video_info, generate_transcript, save_video_data
from utils.indexing import create_vector_store
from utils.retrieval import load_vector_store
from utils.generation import get_chain

st.set_page_config(
    page_title="Yelly - YouTube ChatBot",
    page_icon="▶️",
    layout="wide"
)

# Apply Poppins font styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
.stApp > div {
    font-family: 'Poppins', sans-serif;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    font-family: 'Consolas', sans-serif !important;
    font-weight: 600;
}
.stTextInput input {
    font-family: 'Poppins', sans-serif !important;
}
.stTextInput label {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 500;
}
.stChatMessage .stMarkdown p {
    font-family: 'Consolas', sans-serif !important;
}
.stChatInput textarea {
    font-family: 'Poppins', sans-serif !important;
}
.stButton button p {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 500;
}
.stMarkdown p {
    font-family: 'Poppins', sans-serif !important;
}
.stAlert .stMarkdown p {
    font-family: 'Poppins', sans-serif !important;
}
.st-emotion-cache-r44huj {
    font-family: 'Poppins', sans-serif !important;
}
.css-1d391kg .stMarkdown p {
    font-family: 'Poppins', sans-serif !important;
}
.css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

def validate_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        list(genai.list_models())
        return True
    except Exception:
        return False

# ---- Sidebar for API Configuration ----
with st.sidebar:
    st.title("🔑 API Configuration")
    st.markdown("---")

    api_key_input = st.text_input(
        "Enter your Google API Key:",
        type="password",
        help="Get your API key from Google AI Studio"
    )

    if "api_valid" not in st.session_state:
        st.session_state.api_valid = False
        st.session_state.api_key = None

    if api_key_input and not st.session_state.api_valid:
        with st.spinner("Validating API key..."):
            if validate_api_key(api_key_input):
                os.environ['GOOGLE_API_KEY'] = api_key_input
                st.session_state.api_key = api_key_input
                st.session_state.api_valid = True
                st.success("✅ API Key configured!")
            else:
                st.error("❌ INVALID API_KEY - Please check your Google API Key")

    elif not api_key_input and not st.session_state.api_valid:
        st.warning("⚠️ Please enter your Google API Key to use the app")

    st.markdown("---")
    st.markdown("### 📝 How to get Google API Key:")
    st.markdown("""
    1. Go to [Google AI Studio](https://aistudio.google.com/apikey)  
    2. Create a new project or select existing  
    3. Enable YouTube Data API v3 (Enabled by default)  
    4. Go to Credentials → Create API Key  
    5. Copy and paste the key above  
    """)

    st.markdown("---")
    st.markdown("### 🔒 Privacy Note:")
    st.markdown("Your API key is only stored temporarily in this session and is not saved or transmitted anywhere.")
    st.markdown("---")
    st.markdown("*Made with 🎀 | By [Liban Ansari](https://github.com/LibanAnsari)*")

if not st.session_state.api_valid:
    st.error("🔑 Please provide your Google API Key in the sidebar to continue.")
    st.stop()


# ---- Main App ----
st.header("Yelly The YouTube ChatBot ▶️👋")

yt_link = st.text_input("Enter the YouTube video link (currently only works with EN videos)")

if yt_link:
    video_id, video_title = get_video_info(yt_link)

    if not video_title:
        st.error('❌ Cannot fetch data! Please check the URL.')
    else:
        st.success(f"✅ Video Title: {video_title}")

        # ---- Safe Transcript Fetch (only once per video_id) ----
        if "video_id" not in st.session_state or st.session_state.video_id != video_id:
            try:
                print(video_id, video_title)
                st.session_state.chat_history = []
                st.session_state.video_id = video_id
                st.session_state.video_title = video_title

                with st.spinner("Fetching transcript..."):
                    captions = generate_transcript(video_id, lang="en")
                    if captions:
                        save_video_data(video_id, video_title, captions)
                        create_vector_store()
                        
                        st.session_state.vectorstore = load_vector_store()
                        print("Vector Store loaded Successfully!")
                        
                        st.session_state.chain = get_chain(st.session_state.vectorstore)
                        print('Chain created Successfully!\n')
                    else:
                        st.error("⚠️ No transcript available for this video.")
            except Exception as e:
                st.error(f"❌ Transcript fetch failed: {e}")

        if "chain" not in st.session_state:
            st.session_state.chain = None
            st.error(f"❌ Failed to Initialize chain")

        # ---- Chatbot UI ----
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if len(st.session_state.chat_history) > 20:
            st.session_state.chat_history = st.session_state.chat_history[-20:]

        try:
            for msg in st.session_state.chat_history:
                role = "user" if isinstance(msg, HumanMessage) else "ai"
                with st.chat_message(role):
                    st.write(msg.content)
        except Exception as e:
            st.error(f"⚠️ Error displaying chat history: {e}")

        query = st.chat_input("Ask Anything :3", key="chatbox")

        if query:
            try:
                st.session_state.chat_history.append(HumanMessage(content=query))

                with st.chat_message("user"):
                    st.write(query)

                if st.session_state.chain:
                    with st.spinner("Thinking till the brains out..."):
                        response = st.session_state.chain.invoke({
                            "chat_history": st.session_state.chat_history,
                            "question": query
                        })
                        if not response:
                            response = "⚠️ No chain available. Please refresh and try again."
                else:
                    print('No chain detected!')
                    response = "⚠️ No chain available. Please refresh and try again."
                    
                st.session_state.chat_history.append(AIMessage(content=response))

                with st.chat_message("ai"):
                    st.write(response)

            except Exception as e:
                st.error(f"❌ Error while processing query: {e}")

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []  # reset only messages, keep video link

# Custom footer
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: var(--background-color);
    color: var(--text-color);
    text-align: center;
    padding: 10x 0;
    font-size: 14px;
    font-family: 'Poppins', sans-serif;
    border-top: 1px solid var(--secondary-background-color);
    z-index: 999;
}
</style>
<div class="footer">
    <p><em>Built with Streamlit and LangChain | Powered by Google GEMINI</em></p>
</div>
""", unsafe_allow_html=True)
