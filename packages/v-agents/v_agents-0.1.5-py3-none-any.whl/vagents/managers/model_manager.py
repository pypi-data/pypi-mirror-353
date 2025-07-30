import inspect
from copy import deepcopy
from vagents.core import LLM, Message, Tool, parse_function_signature
from typing import Callable, Union, List, Optional, Dict

class LMManager:
    def __init__(self):
        self.models: Dict[str, LLM] = {}
    
    def add_model(self, llm: LLM):
        self.models[llm.model_name] = llm
    
    async def call(self, model_name: str, *args, **kwargs):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found.")
        res = await self.models[model_name](*args, **kwargs)
        return res
    
    async def invoke(self, 
                     func: Callable,
                     model_name: str,
                     query: Union[List[Message], str], 
                     tools: Optional[List[Union[Callable, Tool]]] = None, 
                     **kwargs
                    ):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found.")
        
        docstring = inspect.getdoc(func) or "You are a helpful assistant."
        response_format = func.__annotations__.get('return', None)
        
        messages = deepcopy(query)
        
        if isinstance(query, List):
            if query[0].role != "system":
                messages.insert(
                    0, Message(role="system", content=docstring)
                )
            else:
                messages[0].content = docstring
        elif isinstance(query, str):
            messages = [
                Message(role="system", content=docstring)
            ]
        kwargs['tools'] = tools
        
        messages.append(Message(role="user", content=func(query, **kwargs)))
        tool_info = None
        if tools:
            tool_info = [tool.to_llm_format() if isinstance(tool, Tool) else parse_function_signature(tool) for tool in tools]
        
        # remove kwargs that are not in the llm signature
        for key in list(kwargs.keys()):
            if key not in ['messages', 'tools', 'response_format', 'temperature', 'max_tokens', 'min_tokens', 'model', 'tools', 'stream']:
                kwargs.pop(key, None)
        kwargs.pop("tools", None)
        res = await self.models[model_name](
            messages=messages,
            tools=tool_info,
            response_format=response_format,
            **kwargs
        )
        if response_format and hasattr(response_format, "model_json_schema"):
            res = response_format.parse_raw(res)
        if tools:
            return await res.__anext__()
        else:
            return res