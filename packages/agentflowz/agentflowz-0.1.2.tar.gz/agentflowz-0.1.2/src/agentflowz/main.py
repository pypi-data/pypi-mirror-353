"""  """


from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent
from llama_index.core import Settings
from llama_index.core.workflow import Context
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent.workflow import ToolCallResult, AgentStream


from enum import Enum
from typing import List, Any



class Package():
    def __init__(self) -> None:
        pass

    @staticmethod
    def package_tool(func):
        """  """
        return FunctionTool.from_defaults(func,name=func.__name__)

    @staticmethod
    def package_querypip2tool(query_engine,name,description):
        """  """
        qenginetools = QueryEngineTool.from_defaults(
                query_engine=query_engine,
                name=name,
                description=description,
            )
        return qenginetools



class AgentType(Enum):
    ReactAgent = 'ReactAgent'
    FunctionAgent = 'FunctionAgent'
    # 添加更多选项

class AgentFactory:
    def __new__(cls, type: AgentType,tools:list[FunctionTool] = None,
                                     tools_retriver = None,
                                     ) -> Any:
        assert type.value in [i.value for i in AgentType]
        agent = None
        # assert tools | tools_retriver
        assert (tools is not None) or (tools_retriver is not None)
        if type.value == 'ReactAgent':
            agent = ReActAgent(                
                    tools = tools,
                    tools_retriver=tools_retriver,   
                    llm=Settings.llm,
                    verbose=True,)

        elif type.value == 'FunctionAgent':
            agent = FunctionAgent(
                tools = tools,
                tools_retriver=tools_retriver,
                llm=Settings.llm,
                verbose=True,)

        else:
            raise Exception('Unknown type')

        return agent
    

class EasyAgentz():
    def __init__(self, agent):
        self.agent = agent
        self.ctx = Context(agent)

    async def run(self,prompt = "What is 5+3+2"):
        self.resp = await self.agent.run(prompt,ctx=self.ctx)
        return str(self.resp)

    def update_prompts(self,react_system_prompt:str):
        self.agent.update_prompts({"react_header": react_system_prompt})

    def tool_calls(self):
        return self.resp.tool_calls