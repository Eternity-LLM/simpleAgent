from ..tool_manager import AIFunction
from volcenginesdkarkruntime import Ark

# 使用前请配置火山引擎API KEY，配置方法见：https://www.volcengine.com/docs/82379/1399008

class SearchTool:
    def __init__(self, ark_api_key:str, ark_ep_id:str):
        self.ark_api_key = ark_api_key
        self.ark_ep_id = ark_ep_id
        self.client = Ark(
            base_url='https://ark.cn-beijing.volces.com/api/v3',
            api_key=self.ark_api_key,
        )
    
    def build_function(self)->None:
        self.function = AIFunction([], [])
        self.function.add_function(
            name='search',
            description='根据用户的查询内容进行网络搜索，并整理搜索结果，输出详细的说明性文本回答。确保总结客观准确，保留关键数据和时间。注意：回答内容将作为网页文本交给其他AI，应当尽可能详细地描述该主题的内容，不得包含无关内容和提问。',
            parameters={
                'query': '要搜索的查询内容，必须是字符串。'
            },
            required=['query'],
            function=self.search
        )

    def search(self, query:str) -> str:
        tools = [{
            "type": "web_search",
            "max_keyword": 5
        }]
        response = self.client.responses.create(
            model=self.ark_ep_id,
            input=[
                {
                    "role": "system",
                    "content": "你是一个AI联网搜索工具。你只需要根据用户的查询内容进行网络搜索，并整理搜索结果，输出详细的说明性文本回答即可，不需要进一步询问用户需求。"
                },
                {"role": "user",
                "content": '现在我需要你对一个内容进行联网搜索，然后整理搜索结果，输出详细的说明性文本回答。'+\
                            '我要求你确保总结客观准确，保留关键数据和时间。注意：你的回答内容将作为**网页文本**交给其他AI，'+\
                            f'应当尽可能详细地描述该主题的内容，不得包含无关内容和提问。你需要搜索的内容是：{query}'
                }
            ],
            tools=tools
        )
        return response.choices[0].message.content
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
SearchTool.search.__doc__ = '''search方法用于根据用户的查询内容进行网络搜索，并整理搜索结果，输出详细的说明性文本回答。它接受一个参数：
- query: 要搜索的查询内容，必须是字符串。
该方法会使用火山引擎的Ark模型来执行网络搜索，并根据用户的查询内容生成一个系统提示和一个用户提示。系统提示告诉模型它是一个AI联网搜索工具，用户提示则包含了具体的搜索需求和要求。方法会调用Ark模型的responses.create接口来获取搜索结果，并从响应中提取生成的文本回答返回。该回答应当尽可能详细地描述搜索主题的内容，确保总结客观准确，保留关键数据和时间，并且不得包含无关内容和提问。'''
SearchTool.__call__.__doc__ = '''__call__方法用于调用当前对象的函数定义列表中的函数。它接受以下参数：
- *args: 可选的位置参数，将被传递给函数实现。
- **kwargs: 可选的关键字参数，将被传递给函数实现。
该方法会在函数定义列表中查找与给定名称匹配的函数，如果找到，则调用对应的函数实现并传递参数。如果没有找到匹配的函数，则会抛出一个ValueError异常。'''
SearchTool.build_function.__doc__ = '''build_function方法用于构建当前对象的函数定义列表。该方法不需要参数。
该方法会创建一个新的AIFunction对象，并使用add_function方法添加一个名为'search'的函数定义。这个函数定义包含了函数的名称、描述、参数信息、必需参数列表以及对应的函数实现。函数实现是当前对象的search方法。该方法不返回任何值，但会将构建好的函数定义列表保存在当前对象的function属性中，以供后续调用使用。'''
SearchTool.__doc__ = SearchTool.__init__.__doc__ = '''SearchTool类用于提供一个基于火山引擎Ark模型的网络搜索工具。它可以根据用户的查询内容进行网络搜索，并整理搜索结果，输出详细的说明性文本回答。使用前需要配置火山引擎API KEY，配置方法见：https://www.volcengine.com/docs/82379/1399008。
构造函数接受两个参数：
- ark_api_key: 火山引擎API KEY，必须是字符串。
- ark_ep_id: 火山引擎模型ID，必须是字符串。
构造函数会使用提供的API KEY创建一个Ark客户端实例，并将其保存在当前对象的client属性中。该类还包含了一个build_function方法用于构建函数定义列表，一个search方法用于执行网络搜索，以及一个__call__方法用于调用函数定义列表中的函数。'''