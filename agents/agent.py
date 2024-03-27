from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.agents import create_openai_tools_agent
from langchain.agents.agent import AgentExecutor
from langchain.chains import LLMChain
from langchain.prompts.chat import MessagesPlaceholder

class ChainOfThoughtAgentExecutor():
    """Agent Executor that aims to retrieve Chain of thought history.
    May include tools that help the AI to better make decisions.
    """
    def __init__(self, llm, prompt, memory, requests=[], verbose=True):
        self.llm = llm
        self.prompt = prompt
        self.memory = memory
        self.verbose = verbose
        self.requests = requests
        self.chain = LLMChain(
                llm=self.llm,
                prompt=self.prompt,
                memory=self.memory,
                verbose=verbose,
        )

    def request(self, data=None):
        for request in self.requests:
            resp = self.chain.invoke({'input': request, 'data': data})
            print(resp['text'])
        return resp['text']

    def invoke(self, _input):
        resp = self.chain.invoke(_input)
        print(resp['text'])
        return resp['text']

class SubmitAgentExecutor():
    """Agent Executor that have the AI call submit tool(s) based on memory.
    Require at least one tool for submission.
    """
    def __init__(self, llm, prompt, tools, memory, verbose=True):
        self.llm = llm
        self.prompt = prompt + MessagesPlaceholder("agent_scratchpad")
        self.tools = tools
        self.memory = memory
        self.verbose = verbose
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.chain = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                prompt=self.prompt,
                memory=self.memory,
                verbose=self.verbose,
        )

    def invoke(self, _input):
        return self.chain.invoke(_input)

class ChatAndThenSubmitAgentExecutor():
    """Agent Executor that have the AI chat and then submit.
    Require at least one tool for submission.
    """
    def __init__(self, llm, chat_prompt, tools_prompt, tools, memory, requests=[], verbose=True):
        self.memory = memory
        self.chatter = ChainOfThoughtAgentExecutor(
                llm=llm,
                prompt=chat_prompt,
                memory=self.memory,
                requests=requests,
                verbose=verbose,
        )
        self.submitter = SubmitAgentExecutor(
                llm=llm,
                prompt=tools_prompt,
                tools=tools,
                memory=self.memory,
                verbose=verbose,
        )

    def invoke(self, _input):
        self.chatter.request(_input.get('data', None))
        return self.submitter.invoke(_input)
