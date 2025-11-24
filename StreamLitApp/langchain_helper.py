
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain # helps to put differnt LLM components together


# Load environment variables
load_dotenv() # use api from .env

"""
make the imports

1) LangChainDeprecationWarning: The class `LLMChain` was deprecated in LangChain 0.1.17 and will be 
removed in 1.0. Use :meth:`~RunnableSequence, e.g., `prompt | llm`` instead.

2) LangChainDeprecationWarning: The method `Chain.__call__` was deprecated in langchain 0.1.0 and will be removed 
in 1.0. Use :meth:`~invoke` instead.


>> Streamlit makes the UI for python code


"""


def generate_pet_name(animal_type, pet_color) :
    llm = ChatAnthropic(
        model = "claude-3-haiku-20240307",
        temperature= 0.9)

    """ we can create a prompt template so we don't have keep asking differnt prompt everytime"""
    prompt_template = PromptTemplate(
        input_variables = ['animal_type', 'pet_color'],
        template= f"I have a {animal_type} pet, it's of {pet_color} and I want a cool name for it. Suggest five cool names for it."
    )

    name_chain= LLMChain(llm= llm,
                         prompt= prompt_template,
                         output_key = "pet_name")

    response = name_chain({'animal_type' : animal_type, 'pet_color' : pet_color})
    
    return response 



if __name__ == "__main__":
    print(generate_pet_name('cow', 'reddish brown'))


    