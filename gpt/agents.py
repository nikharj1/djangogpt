from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

def create_text_agent(llm):
    from .tools import text_tool  
    prompt = PromptTemplate(
        input_variables=["prompt"],
        template="Generate a text response based on the following input: {prompt}"
    )
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    tools = [text_tool()]
    
    agent = initialize_agent(
        tools=tools,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        llm=llm,
        prompt=prompt,
        memory=memory 
    )
    
    return agent


def create_image_agent(llm):
    from .tools import image_tool  
    prompt = PromptTemplate(
        input_variables=["prompt"],
        template="Generate an image based on the following input: {prompt}"
    )
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    tools = [image_tool()]
    
    agent = initialize_agent(
        tools=tools,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        llm=llm,
        prompt=prompt,
        memory=memory 
    )
    
    return agent
