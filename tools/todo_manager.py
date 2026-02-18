from .tool_manager import AIFunction

class TODOListManager:
    def __init__(self, todo_list:list=[])->None:
        self.todo = todo_list
        self.nsteps = len(self.todo)
        self.progress = [False for i in range(self.nsteps)]
        self.cur_step = 1
        self.pause = False
        self.build_function()

    def __str__(self)->str:
        res = '\n```TODO\n'
        for idx, step in enumerate(self.todo, start=1):
            if idx < self.cur_step:
                res += '[+] '
            elif idx == self.cur_step:
                res += '[*] '
            else:
                res += '[-] '
            res += f'{step}\n'
        res += f'```\n'
        if self.cur_step > self.nsteps:
            res += '当前所有任务均已完成！'
        else:
            res += f'标注[+][*][-]分别表示已完成、当前步骤、未完成步骤。\n当前正在处理的步骤为第{self.cur_step}步：\n```text\n{self.todo[self.cur_step-1]}\n```'
        return res

    def pause_todo(self)->None:
        self.pause = True

    def clear(self)->None:
        self.cur_step = 1
        self.nsteps = 0
        self.progress = []
        self.todo = []

    def complete_step(self)->None:
        self.progress[self.cur_step-1] = True
        self.cur_step += 1
        return
    
    def redo(self)->None:
        self.cur_step -= 1
        self.progress[self.cur_step-1] = False
        return

    def complete_all(self)->None:
        self.progress = [True for i in range(self.nsteps)]
        self.cur_step = self.nsteps + 1
        return

    def append(self, step:str)->None:
        self.nsteps += 1
        self.progress += [False]
        self.todo.append(step)

    def print(self, color:bool=True)->None:
        if not color:
            print(self)
            return
        res = '\033[33m\nTODO\n\033[0m'
        for idx, step in enumerate(self.todo, start=1):
            if idx < self.cur_step:
                res += '\033[32m√\033[0m '   # Green check mark for completed steps
            elif idx == self.cur_step:
                res += '\033[36m→ '   # Cyan arrow for the current step
            else:
                res += '\033[31m×\033[0m '   # Red cross for incomplete steps
            res += f'{step}\n'
        res += '\n'
        if self.cur_step > self.nsteps:
            res += '\033[32m当前所有任务均已完成！\033[0m'
        else:
            res += f'\033[33m标注[√][→][×]分别表示已完成、当前步骤、未完成步骤。\n当前正在处理的步骤为第{self.cur_step}步：\n\033[36m{self.todo[self.cur_step-1]}\n\033[0m'
        print(res)
        return

    def build_function(self):
        self.function = AIFunction([], [])
        self.function.add_function(
            name='add_todo',
            description='向待办事项列表中添加一个新的步骤。',
            parameters={
                'step': {'type': 'string', 'description': '要添加的步骤内容'}
            },
            required=['step'],
            function=self.append
        )
        self.function.add_function(
            name='complete_step',
            description='标记当前步骤为已完成，并将当前步骤指针移动到下一个步骤。',
            parameters={},
            required=[],
            function=self.complete_step
        )
        self.function.add_function(
            name='complete_all',
            description='标记所有步骤为已完成，并将当前步骤指针移动到最后。',
            parameters={},
            required=[],
            function=self.complete_all
        )
        self.function.add_function(
            name='clear_todo',
            description='清空待办事项列表和相关状态。',
            parameters={},
            required=[],
            function=self.clear
        )
        self.function.add_function(
            name='check_todo',
            description='以Markdown格式查看当前待办事项列表的状态。',
            parameters={},
            required=[],
            function=self.__str__
        )
        self.function.add_function(
            name='pause_todo',
            description='暂停处理当前待办事项，以便进一步确认用户要求。调用前请先输出一段提示信息，说明当前正在处理的步骤，并询问用户是否继续执行和执行的细节。',
            parameters={},
            required=[],
            function=self.pause_todo
        )
        return
    
    @property
    def all_completed(self)->bool:
        # Check if all steps are completed
        return all(self.progress)

    def __call__(self, __func_name:str, *args, **kwargs):
        return self.function(__func_name, *args, **kwargs)



TODOListManager.__doc__ = '''TODOListManager类用于管理待办事项列表。它包含以下方法：
- __init__(self, todo_list:list=[]): 初始化待办事项管理器，接受一个待办事项列表作为参数。
- __str__(self): 返回待办事项列表的字符串表示形式。
- clear(self): 清空待办事项列表和相关状态。
- complete_step(self): 标记当前步骤为已完成，并将当前步骤指针移动
- complete_all(self): 标记所有步骤为已完成，并将当前步骤指针移动到最后。
- append(self, step:str): 向待办事项列表中添加一个新的步骤。
- print(self, color:bool=True): 打印待办事项列表，支持彩色输出以区分已完成、当前步骤和未完成的步骤。'''
TODOListManager.__str__.__doc__ = '''__str__方法返回待办事项列表的Markdown表示形式。它会根据当前步骤的状态为每个步骤添加不同的标记：
- 已完成的步骤前会添加[+]标记。
- 当前步骤前会添加[*]标记。
- 未完成的步骤前会添加[-]标记。
方法还会在列表末尾添加当前正在处理的步骤的详细信息。'''
TODOListManager.clear.__doc__ = '''clear方法用于清空待办事项列表和相关状态。它会重置当前步骤指针、步骤数量、进度列表和待办事项列表，使其回到初始状态。'''
TODOListManager.complete_step.__doc__ = '''complete_step方法用于标记当前步骤为已完成，并将当前步骤指针移动到下一个步骤。它会将当前步骤的进度标记为True，并将当前步骤指针加1。'''
TODOListManager.complete_all.__doc__ = '''complete_all方法用于标记所有步骤为已完成，并将当前步骤指针移动到最后。它会将所有步骤的进度标记为True，并将当前步骤指针设置为步骤数量加1。'''
TODOListManager.append.__doc__ = '''append方法用于向待办事项列表中添加一个新的步骤。它接受一个字符串参数step，表示要添加的步骤内容。方法会将步骤添加到待办事项列表中，并更新步骤数量和进度列表。'''
TODOListManager.print.__doc__ = '''print方法用于打印待办事项列表。它接受一个布尔参数color，表示是否使用彩色输出。方法会根据当前步骤的状态为每个步骤添加不同的标记，并使用不同的颜色区分已完成、当前步骤和未完成的步骤。如果color参数为False，则使用普通文本输出。'''
TODOListManager.build_function.__doc__ = '''build_function方法用于构建并注册待办事项管理器的AI调用接口（使用AIFunction）。
它会将常用操作（添加步骤、标记完成、全部完成、清空、检查）以函数接口的形式注册，方便外部通过函数名调用对应的方法。'''
TODOListManager.__call__.__doc__ = '''__call__方法根据函数名称（由build_function注册的名称）调用对应的函数实现。
参数为函数名及其位置/关键字参数，会委托给内部的AIFunction实例进行调用并返回结果。'''
TODOListManager.pause_todo.__doc__ = '''pause_todo方法用于暂停处理当前待办事项，以便进一步确认用户要求。调用前请先输出一段提示信息，说明当前正在处理的步骤，并询问用户是否继续执行和执行的细节。该方法会将内部的pause状态设置为True，以表示待办事项处理已暂停。'''

if __name__ == '__main__':
    todo_manager = TODOListManager(['Step 1: Do something', 'Step 2: Do something else', 'Step 3: Finish up'])
    todo_manager.append('Step 4: Extra step')
    todo_manager.print()
    todo_manager.complete_step()
    todo_manager.print()
    todo_manager.complete_all()
    todo_manager.print()
    todo_manager.clear()
    todo_manager.print()
    todo_manager.append('New Step 1: Start over')
    todo_manager.append('New Step 2: Continue')
    todo_manager.print()
