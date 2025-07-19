import os
import streamlit as st
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import re
from typing import List, Dict, Any
import anthropic

# Load environment variables
load_dotenv("core.env")

class YouTubeAssistant:
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Handle the case where the key might have spaces (strip them)
        if self.anthropic_key:
            self.anthropic_key = self.anthropic_key.strip()
        
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        # Initialize Claude client
        self.client = anthropic.Anthropic(api_key=self.anthropic_key)
        
        self.transcript = None
        self.video_info = None
        self.conversation_history = []

    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("Invalid YouTube URL")

    def get_video_info(self, video_id: str) -> Dict[str, str]:
        """Get video title and description"""
        try:
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            return {
                "title": yt.title,
                "description": yt.description,
                "length": str(yt.length),
                "views": str(yt.views)
            }
        except Exception as e:
            st.error(f"Error getting video info: {str(e)}")
            return {"title": "Unknown", "description": "", "length": "0", "views": "0"}

    def get_transcript(self, video_id: str) -> str:
        """Get transcript from YouTube video"""
        try:
            # Try to get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all transcript segments
            full_transcript = ""
            for segment in transcript_list:
                full_transcript += segment['text'] + " "
            
            return full_transcript.strip()
        
        except Exception as e:
            # Try different language codes if English fails
            try:
                available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = available_transcripts.find_generated_transcript(['en'])
                transcript_data = transcript.fetch()
                
                full_transcript = ""
                for segment in transcript_data:
                    full_transcript += segment['text'] + " "
                
                return full_transcript.strip()
            
            except Exception as e2:
                raise Exception(f"Could not retrieve transcript: {str(e2)}")

    def process_video(self, youtube_url: str):
        """Process YouTube video and store transcript"""
        try:
            # Extract video ID
            video_id = self.extract_video_id(youtube_url)
            
            # Get video info
            self.video_info = self.get_video_info(video_id)
            
            # Get transcript
            transcript = self.get_transcript(video_id)
            
            if not transcript:
                raise Exception("No transcript available for this video")
            
            self.transcript = transcript
            self.conversation_history = []  # Reset conversation history
            
            return True, "Video processed successfully!"
        
        except Exception as e:
            return False, f"Error processing video: {str(e)}"

    def ask_question(self, question: str, max_chars: int = 4000) -> str:
        """Ask a question about the video"""
        if not self.transcript:
            return "Please process a video first."
        
        # Truncate transcript if too long for API
        transcript_excerpt = self.transcript[:max_chars]
        if len(self.transcript) > max_chars:
            transcript_excerpt += "... [transcript truncated]"
        
        # Build conversation context
        context = f"Based on the following YouTube video transcript, please answer the user's question.\n\nTranscript:\n{transcript_excerpt}\n\n"
        
        # Add conversation history
        if self.conversation_history:
            context += "Previous conversation:\n"
            for entry in self.conversation_history[-4:]:  # Keep last 4 exchanges
                context += f"Q: {entry['question']}\nA: {entry['answer']}\n\n"
        
        context += f"Current question: {question}\n\nPlease provide a comprehensive answer based on the transcript content."
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": context}
                ]
            )
            
            answer = response.content[0].text
            
            # Add to conversation history
            self.conversation_history.append({
                "question": question,
                "answer": answer
            })
            
            return answer
        except Exception as e:
            return f"Error answering question: {str(e)}"

def main():
    st.set_page_config(
        page_title="YouTube Assistant",
        page_icon="🎥",
        layout="wide"
    )
    
    st.title("🎥 YouTube Assistant with Claude AI")
    st.markdown("Ask questions about any YouTube video using AI!")
    
    # Initialize session state
    if "assistant" not in st.session_state:
        try:
            st.session_state.assistant = YouTubeAssistant()
        except ValueError as e:
            st.error(str(e))
            st.stop()
    
    if "processed" not in st.session_state:
        st.session_state.processed = False
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for video input
    with st.sidebar:
        st.header("📹 Video Input")
        youtube_url = st.text_input(
            "Enter YouTube URL:",
            placeholder="https://www.youtube.com/watch?v=..."
        )
        
        if st.button("Process Video", type="primary"):
            if youtube_url:
                with st.spinner("Processing video..."):
                    success, message = st.session_state.assistant.process_video(youtube_url)
                    
                    if success:
                        st.session_state.processed = True
                        st.session_state.messages = []  # Clear previous messages
                        st.success(message)
                        
                        # Display video info
                        if st.session_state.assistant.video_info:
                            st.subheader("📊 Video Info")
                            st.write(f"**Title:** {st.session_state.assistant.video_info['title']}")
                            st.write(f"**Length:** {int(st.session_state.assistant.video_info['length'])//60} minutes")
                            st.write(f"**Views:** {st.session_state.assistant.video_info['views']}")
                    else:
                        st.error(message)
            else:
                st.error("Please enter a YouTube URL")
        
        # Example questions
        if st.session_state.processed:
            st.subheader("💡 Example Questions")
            example_questions = [
                "What is the main topic of this video?",
                "Can you summarize the key points?",
                "What are the most important takeaways?",
                "Are there any specific examples mentioned?",
                "What conclusions does the speaker draw?"
            ]
            
            for question in example_questions:
                if st.button(question, key=f"example_{question}"):
                    st.session_state.messages.append({"role": "user", "content": question})
                    with st.spinner("Thinking..."):
                        response = st.session_state.assistant.ask_question(question)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
    
    # Main chat interface
    if st.session_state.processed:
        st.header("💬 Chat with the Video")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about the video..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.assistant.ask_question(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
    
    else:
        st.info("👈 Please enter a YouTube URL in the sidebar to get started!")
        
        # Show features
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🎯 Features")
            st.write("• Automatic transcript extraction")
            st.write("• Intelligent chunking")
            st.write("• Context-aware responses")
        
        with col2:
            st.subheader("🤖 AI Powered")
            st.write("• Claude AI integration")
            st.write("• Vector similarity search")
            st.write("• Conversation memory")
        
        with col3:
            st.subheader("🚀 Easy to Use")
            st.write("• Simple URL input")
            st.write("• Interactive chat")
            st.write("• Example questions")

if __name__ == "__main__":
    main() 