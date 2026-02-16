from typing import List
import warnings

class AIFunction:
    def __init__(self, functions_dict:List[dict], functions:list)->None:
        self.functions = functions_dict
        self.__f = functions
        if len(self.functions) != len(self.__f):
            raise ValueError
        return
    
    def add_function(
        self,
        name:str,
        description:str,
        parameters:dict,
        required:List[str],
        function
    )->None:
        self.functions.append(
            {
                'type':'function',
                'function':{
                    'name': name,
                    'description': description,
                    'parameters': {
                        'type': 'object',
                        'properties': parameters,
                        'required': required
                    },
                    'strict': True
                }
            }
        )
        self.__f.append(function)
        return
    
    def include(self, tool_manager:'AIFunction')->None:
        for i, func in enumerate(tool_manager.functions):
            if func['function']['name'] in [f['function']['name'] for f in self.functions]:
                warnings.warn(f"Function {func['name']} already exists in the current manager. Skipping.")
                continue
            else:
                self.functions.append(func)
                self.__f.append(tool_manager.__f[i])
        return
    
    def __call__(self, __func_name:str, *args, **kwargs)->str:
        __func_name = __func_name.strip()
        try:
            idx = -1
            for i, func in enumerate(self.functions):
                if func['function']['name'] == __func_name:
                    idx = i
                    break
            if idx == -1:
                raise ValueError(f'Function {__func_name} not found.')
            res = self.__f[idx](*args, **kwargs)
            if isinstance(res, str):
                return res
            elif res is None:
                return f"工具{__func_name}调用成功。（此工具无返回结果）"
            else:
                try:
                    return str(res)
                except Exception as rt_e:
                    return f'已调用工具{__func_name}，无法处理返回结果：{str(rt_e)}'
        except Exception as e:
            return f'Error calling function {__func_name}: {str(e)}'

AIFunction.__doc__ = '''AIFunction类用于管理AI函数的定义和调用。它包含以下方法：
- __init__(self, functions_dict:List[dict], functions:list): 初始化函数管理器，接受一个函数定义列表和一个函数实现列表。
- add_function(self, name:str, description:str, parameters:dict, required:List[str], function): 添加一个新的函数定义和实现。
- __call__(self, name:str, *args, **kwargs): 根据函数名称调用对应的函数实现，并传递参数。'''
AIFunction.add_function.__doc__ = '''add_function方法用于向函数管理器中添加一个新的函数定义和实现。它接受以下参数：
- name: 函数的名称，必须是唯一的字符串。
- description: 函数的描述信息，用于说明函数的功能和用途。
- parameters: 一个字典，定义函数的参数结构，包括参数的类型和属性，例如：
{
    'param1': {'type': 'string', 'description': '参数1的描述'},
    'param2': {'type': 'integer', 'description': '参数2的描述'}
}
- required: 一个列表，列出函数调用时必须提供的参数名称。
- function: 函数的实现，即一个可调用对象（如函数或lambda表达式），它将被调用时执行。'''
AIFunction.include.__doc__ = '''include方法用于将另一个AIFunction实例中的函数定义和实现合并到当前实例中。它接受一个参数：
- tool_manager: 另一个AIFunction实例，包含要合并的函数定义和实现。
该方法会遍历另一个实例中的函数定义，如果当前实例中已经存在同名的函数，则会发出警告并跳过该函数的合并；如果不存在同名函数，则会将该函数定义和实现添加到当前实例中。'''
AIFunction.__call__.__doc__ = '''__call__方法用于根据函数名称调用对应的函数实现，并传递参数。它接受以下参数：
- __func_name: 要调用的函数的名称，必须是之前通过add_function方法添加的函数名称。
- *args: 可选的位置参数，将被传递给函数实现。
- **kwargs: 可选的关键字参数，将被传递给函数实现。
该方法会在函数定义列表中查找与给定名称匹配的函数，如果找到，则调用对应的函数实现并传递参数。如果没有找到匹配的函数，则会抛出一个ValueError异常。'''


if __name__ == '__main__':
    def test_func_1(x, y):
        return x + y
    def test_func_2(name):
        return f'Hello, {name}!'
    func_manager = AIFunction(
        [
            {
                'name': 'add',
                'description': 'Add two numbers.',
                'parameters': {
                    'x': {'type': 'number', 'description': 'The first number.'},
                    'y': {'type': 'number', 'description': 'The second number.'}
                },
                'required': ['x', 'y']
            }
        ],
        [test_func_1]
    )
    func_manager.add_function(
        name='greet',
        description='Greet a person by name.',
        parameters={
            'name': {'type': 'string', 'description': 'The name of the person to greet.'}
        },
        required=['name'],
        function=test_func_2
    )
    print(func_manager('add', 3, 5))  # Output: 8
    print(func_manager('greet', name='Alice'))  # Output: Hello, Alice