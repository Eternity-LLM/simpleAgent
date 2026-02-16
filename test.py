from openai import OpenAI
import json
import os
import getpass
from tools import AIFunction, FileManager, TODOListManager

# 初始化client
api_key=os.environ.get('DEEPSEEK_API_KEY')
if not api_key:
    api_key = getpass.getpass('请输入您的DeepSeek API KEY（不会显示在屏幕上）\n> ')

client = OpenAI(
    api_key=api_key,
    base_url='https://api.deepseek.com/'
)

# 定义工具
AI_TOOLS = AIFunction([], [])
tm = TODOListManager([])
fm = FileManager(os.path.curdir)
AI_TOOLS.include(tm.function)
AI_TOOLS.include(fm.function)
tools = AI_TOOLS.functions

# 创建会话
messages = [{'role':'system', 'content':'你是AI助手DeepSeek。在回答用户的问题时，你可以调用多个工具。复杂任务请调用工具编写TODO待办清单并严格按照清单推进任务。'}]

while True:
    prompt = input('\n\n\n请输入问题（输入/quit退出）：\n> ')
    if prompt.strip() == '/quit':
        break
    messages.append({'role':'user', 'content':prompt})
    print('\n\nAI: ', end='', flush=True)
    stop = False
    while not stop:
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            tools=tools,
            tool_choice='auto',
            stream=True
        )

        tool_calls = {}
        msg = ''
        for chunk in response:
            if chunk.choices[0].finish_reason == 'stop':
                stop = True
            delta = chunk.choices[0].delta

            if delta.content:
                print(delta.content, end='', flush=True)
                msg += delta.content
            
            if delta.tool_calls:
                for tcd in delta.tool_calls:
                    idx = tcd.index
                    if idx not in tool_calls:
                        tool_calls[idx] = tcd
                    else:
                        if tcd.id:
                            tool_calls[idx].id = tcd.id
                        if tcd.function.name:
                            tool_calls[idx].function.name = tcd.function.name
                        if tcd.function.arguments:
                            tool_calls[idx].function.arguments += tcd.function.arguments
        messages.append({'role':'assistant', 'content':msg})
        if tool_calls:
            for tc in tool_calls.values():
                kwargs = json.loads(tc.function.arguments)
                fname = tc.function.name
                print(f'\n\033[36m调用工具 {fname}\033[0m')
                res = AI_TOOLS(fname, **kwargs)
                messages.append({
                    'role':'assistant',
                    'tool_calls':[{
                        'id':tc.id,
                        'type':'function',
                        'function':{
                            'name':fname,
                            'arguments':tc.function.arguments
                        }
                    }]
                })
                messages.append({
                    'role':'tool',
                    'tool_call_id':tc.id,
                    'content':res
                })
