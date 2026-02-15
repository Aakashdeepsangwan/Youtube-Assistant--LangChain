from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain


# For embeddings - using Hugging Face (free)
from langchain_huggingface import HuggingFaceEmbeddings

# For vector database we will use FAISS 
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
from sympy.utilities.iterables import kbins

# load dotenv - to use the API storeed in .env
load_dotenv()


# can use different models like:
# - "sentence-transformers/all-MiniLM-L6-v2" (default, fast and lightweight)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

video_url = "https://www.youtube.com/watch?v=qAF1NjEVHhY&list=WL"

def vector_db_youtube(video_url : str, language: list = ["en-US", "en"])->FAISS:
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
        model = "claude-3-haiku-20240307",
        api_key = os.getenv("claudeAPI") 
    )

    # 2) Prompt Template
    prompt = PromptTemplate(
        input_variables = ["question", "docs"],
        template = 
        """You are a helpful Youtube Assistant that can answer questions about videos based on the video transcript.

Question: {question}

Video Transcript:
{docs}

Instructions:
1. Answer the question using ONLY factual information from the transcript provided above.
2. Keep your answer CONCISE and well-structured:
   - Start with a brief introduction (1-2 sentences maximum)
   - Use bullet points (•) for main points, with each bullet on a NEW LINE
   - Add a blank line after each bullet point for readability
   - Add a blank line between different paragraphs or sections
   - Keep bullet point content brief (1-2 sentences per bullet)
3. Formatting requirements:
   - Each bullet point must be on its own line
   - Add a blank line after each bullet point
   - Add a blank line between paragraphs
   - Use proper spacing throughout
4. If the transcript doesn't contain enough information to answer the question, say "I don't have enough information from the video transcript to answer this question."
5. Be concise - avoid long paragraphs. Use bullet points whenever possible.

IMPORTANT: Format your response with proper line breaks. Each bullet point should be on a new line, followed by a blank line. Separate paragraphs with blank lines.
        """
    )
    

    chain = LLMChain(llm= llm, prompt = prompt)
    response = chain.run(question= query, docs = docs_page_content)
    # Preserve formatting: keep line breaks and spacing
    # Only clean up excessive whitespace while preserving intentional line breaks
    lines = response.split("\n")
    cleaned_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Keep the line if it has content, or if it's an intentional blank line (between paragraphs)
        if stripped or (i > 0 and i < len(lines) - 1 and lines[i-1].strip() and lines[i+1].strip()):
            cleaned_lines.append(stripped if stripped else "")
    response = "\n".join(cleaned_lines)
    return response, docs



if __name__  == "__main__":
    print(vector_db_youtube("https://www.youtube.com/watch?v=qAF1NjEVHhY&list=WL", language=["en-US", "en"]))