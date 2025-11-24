from anthropic import Anthropic
from langchain_anthropic import ChatAnthropic # LLMS
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# usings agents
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType

#load the api
load_dotenv()

def langchain_agent() :
    llm = ChatAnthropic(
        model = "claude-3-haiku-20240307",
        temperature = 0.7
    )

    tools = load_tools(['wikipedia', "llm-math"], llm= llm)

    # initiate the agent
    agent = initialize_agent(
        tools, llm, agent= AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose= True
    )

    result = agent.run(
        "what's the average age of dog? Multiply the age by 3"
    )

    print(result)

# Result= The average age of a dog is 11.5 years. Multiplying this by 3 gives an answer of 34.5 years.

"""
To prevent errors :
    1) Install the wikipedia library

    >> Other problem, Agent couldn't process the though after reading the text from wikipedia
    Reason : Anthropic Model simply redacts the reasoning
    Solution : 1) I can ask for intermediate steps explicitely
               2) Use Custom Prompt : Build one with "Create_react_agent" and a "PromptTemplate" this will instruct
                claude write something uinder Thought
"""

if __name__ == "__main__":
    langchain_agent()