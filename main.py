import streamlit as st
import imports as lch

st.title("Youtube Assistant")

with st.sidebar :
    with st.form(key = "my_form"):
        youtube_url = st.sidebar.text_area(
            label = "What is the Youtube Video Url",
            max_chars = 50
        )

        query = st.sidebar.text_area(
            label = "Ask me about the video ?",
            max_chars= 50,
            key = "query"
        )
        
        submit_button = st.form_submit_button(label="Submit")

if submit_button:
    if query and youtube_url:
        try:
            with st.spinner("Processing video and generating response..."):
                db = lch.vector_db_youtube(youtube_url)
                response, docs = lch.get_response_from_query(db, query)
                st.success("Response generated!")
                st.markdown(response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please provide both a YouTube URL and a question.")


    

