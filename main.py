import streamlit as st
import imports as lch
import textwrap # we don't need to scroll the page

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
        
        submit_button = st.form_submit_button(label = "submit")

if query and youtube_url :
    db = lch.vector_db_youtube(youtube_url)
    response, docs = lch.get_response_from_query(db,query)
    st.text (textwrap.fill(response, width=80))


    


