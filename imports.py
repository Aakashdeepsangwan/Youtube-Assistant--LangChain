# from langchain.document_loaders import YoutubeLoader - it's depreciated
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Optional imports (not needed for vector_db_youtube function)
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# For embeddings - using Hugging Face (free)
from langchain_huggingface import HuggingFaceEmbeddings

# For vector database we will use FAISS 
# from langchain.vectorstores import FAISS - deprecated
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from sympy.utilities.iterables import kbins

# load dotenv - to use the API storeed in .env
load_dotenv()

# Initialize Hugging Face embeddings (free, runs locally)
# You can use different models like:
# - "sentence-transformers/all-MiniLM-L6-v2" (default, fast and lightweight)
# - "sentence-transformers/all-mpnet-base-v2" (better quality, slower)
# - "sentence-transformers/paraphrase-MiniLM-L6-v2" (good for semantic similarity)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

video_url = "https://www.youtube.com/watch?v=qAF1NjEVHhY&list=WL"

def vector_db_youtube(video_url : str, language: list = ["en-US", "en"])->FAISS:
    # this is basic loading command -> same used for pdf's word docs
    # Specify language codes - try en-US first (common for US videos), then fallback to en
    # YoutubeLoader accepts language as a list or string
    loader = YoutubeLoader.from_youtube_url(video_url, language=language)
    transcript = loader.load()

    # Text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 100
    )

    docs = text_splitter.split_documents(transcript) # documents splitted


    # initialise phase - > chunk converted to embeddings and stored in db 
    db = FAISS.from_documents(docs,embeddings)
    return db


# Perform the similarity Search
def get_response_from_query(db, query,k=4):
    # claude Haiku model can hangle 4097 tokens
    docs = db.similarity_search(query, k= k)
    docs_page_content = " ".join(d.page_content for d in docs)

    # 1) LLM Template
    llm = ChatAnthropic(
        model = "claude-3-haiku-20240307" 
    )

    # 2) Prompt Template
    prompt = PromptTemplate(
        input_variables = ["question", "docs"],
        template = 
        """  
        Your are a helpful Youtube Assistant that can answer questuons about videos
        Based on the video transcript

        Answer the following question : {question}
        By searching the following video transcrit : {docs}

        Only use the fuctual information from the transcript to answer the question

        If you don't have enough information to answer this question,
        say "I don't know"

        Your answer should be detailed.
        """
    )
    

    chain = LLMChain(llm= llm, prompt = prompt)
    response = chain.run(question= query, docs = docs_page_content)
    response = response.replace("\n", "")
    return response, docs



if __name__  == "__main__":
    print(vector_db_youtube("https://www.youtube.com/watch?v=qAF1NjEVHhY&list=WL", language=["en-US", "en"]))