# import helper libraries
import langchain_helper as lch
import streamlit as st


st.title("Pets name generator")

animal_type = st.sidebar.selectbox("what is your pet?", ("Cat", "Dog", "Cow", "Hamster"))


# text_area = as llm has token based API charge

if animal_type  == "Cat":
    pet_color = st.sidebar.text_area(label = "What color is your cat?", max_chars = 15)

if animal_type == "Dog":
    pet_color = st.sidebar.text_area(label = "what color is your dog?", max_chars = 15)

if animal_type == "Cow":
    pet_color = st.sidebar.text_area(label = "what color is your Cow?", max_chars =15 )

if animal_type == "Hamster" :
    pet_color = st.sidebar.text_area(label = "What color is your Hamster", max_chars = 15)



#once the color is provided then llm can generate the answer 


if pet_color :
    response = lch.generate_pet_name(animal_type, pet_color)
    st.text(response['pet_name'])

    # Output key variable inside nameChain alligns the text
    

 
