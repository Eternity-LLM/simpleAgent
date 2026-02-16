from .tool_manager import AIFunction
import os

class TextFileContent:
    def __init__(self, file_name: str, file_content: str) -> None:
        self.fname, self.fcont = file_name, file_content
        self.template = f'[file name]: {file_name}\n[file content begin]{file_content}[file content end]\n'

    def __str__(self) -> str:
        return self.template

class FileManager:
    def __init__(self, dir_path:str, level:int=3) -> None:
        self.level = level
        self.dir_path = dir_path
        self.files = os.listdir(dir_path)
        if level >= 1:
            for idx, file in enumerate(self.files):
                if os.path.isdir(os.path.join(dir_path, file)):
                    self.files[idx] = FileManager(os.path.join(dir_path, file), level-1)
        self.build_function()
        return
    
    def build_function(self):
        self.function = AIFunction([], [])
        self.function.add_function(
            name='read_file',
            description='读取指定文件的内容，并以特定格式返回文件名和内容。',
            parameters={
                'file_name': {'type': 'string', 'description': '要读取的文件名，必须存在于当前目录中。'}
            },
            required=['file_name'],
            function=self.read_file
        )
        self.function.add_function(
            name='write_file',
            description='将指定内容写入指定文件，如果文件不存在则创建新文件。',
            parameters={
                'file_name': {'type': 'string', 'description': '要写入的文件名，可以是新文件或现有文件。'},
                'content': {'type': 'string', 'description': '要写入文件的内容。'}
            },
            required=['file_name', 'content'],
            function=self.write_file
        )
        self.function.add_function(
            name='add_dir',
            description='在当前目录下创建一个新的子目录。',
            parameters={
                'dir_name': {'type': 'string', 'description': '要创建的子目录名称，必须在当前目录中唯一。'}
            },
            required=['dir_name'],
            function=self.add_dir
        )
        self.function.add_function(
            name='delete_file',
            description='删除当前目录下的指定文件。',
            parameters={
                'file_name': {'type': 'string', 'description': '要删除的文件名，必须存在于当前目录中。'}
            },
            required=['file_name'],
            function=self.delete_file
        )
        self.function.add_function(
            name='delete_dir',
            description='删除当前目录下的指定子目录。',
            parameters={
                'dir_name': {'type': 'string', 'description': '要删除的子目录名称，必须存在于当前目录中，并且是一个目录。'}
            },
            required=['dir_name'],
            function=self.delete_dir
        )
        self.function.add_function(
            name='list_files',
            description='以树状图的形式列出当前目录下的所有文件和子目录，支持显示3层结构。',
            parameters={},
            required=[],
            function=self.list_files
        )
        self.function.add_function(
            name='refresh',
            description='刷新当前目录的文件列表（重新读取磁盘）。',
            parameters={},
            required=[],
            function=self.refresh
        )
        self.function.add_function(
            name='view_dir',
            description='查看当前目录下指定子目录的树状结构，返回字符串。',
            parameters={
                'dir_name': {'type': 'string', 'description': '要查看的子目录名称，必须在当前目录中存在。'}
            },
            required=['dir_name'],
            function=self.view_dir
        )
        return
    
    def refresh(self)->None:
        self.files = os.listdir(self.dir_path)
        if self.level >= 1:
            for idx, file in enumerate(self.files):
                if os.path.isdir(os.path.join(self.dir_path, file)):
                    self.files[idx] = FileManager(os.path.join(self.dir_path, file), self.level-1)

    def read_file(self, file_name:str) -> TextFileContent:
        if file_name not in self.files:
            raise ValueError(f'File {file_name} not found in directory {self.dir_path}.')
        try:
            with open(os.path.join(self.dir_path, file_name), 'r', encoding='utf-8') as f:
                content = f.read()
            return str(TextFileContent(file_name, content))
        except:
            return '无法打开文件。请检查文件是否存在，并且文件名是否正确。不支持查看非文本文件。'
    
    def write_file(self, file_name:str, content:str) -> None:
        with open(os.path.join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
            f.write(content)
        if file_name not in self.files:
            self.files.append(file_name)
    
    def view_dir(self, dir_name:str) -> str:
        dir_path = os.path.join(self.dir_path, dir_name)
        if not os.path.exists(dir_path):
            raise ValueError(f'Directory {dir_name} not found in {self.dir_path}.')
        if not os.path.isdir(dir_path):
            raise ValueError(f'{dir_name} is not a directory in {self.dir_path}.')
        sub_manager = FileManager(dir_path, 3)
        return sub_manager.list_files()

    def add_dir(self, dir_name:str) -> None:
        new_dir_path = os.path.join(self.dir_path, dir_name)
        if not os.path.exists(new_dir_path):
            os.makedirs(new_dir_path)
            self.files.append(FileManager(new_dir_path, self.level-1))
        else:
            raise ValueError(f'Directory {dir_name} already exists in {self.dir_path}.')
    
    def delete_file(self, file_name:str) -> None:
        if file_name not in self.files:
            raise ValueError(f'File {file_name} not found in directory {self.dir_path}.')
        os.remove(os.path.join(self.dir_path, file_name))
        self.files.remove(file_name)
    
    def delete_dir(self, dir_name:str) -> None:
        dir_path = os.path.join(self.dir_path, dir_name)
        if not os.path.exists(dir_path):
            raise ValueError(f'Directory {dir_name} not found in {self.dir_path}.')
        if not os.path.isdir(dir_path):
            raise ValueError(f'{dir_name} is not a directory in {self.dir_path}.')
        os.rmdir(dir_path)
        self.files = [f for f in self.files if not (isinstance(f, FileManager) and f.dir_path == dir_path)]
    
    def list_files(self) -> str:
        # 输出当前目录下的所有文件和文件夹的树状图（3层）
        res = f'{self.dir_path}/\n'
        for file in self.files:
            if isinstance(file, FileManager):
                res += '  ' + file.list_files().replace('\n', '\n  ') + '\n'
            else:
                res += f'  {file}\n'
        return res
    
    def __str__(self) -> str:
        return self.list_files()
    
    def __call__(self, __func_name:str, *args, **kwargs):
        return self.function(__func_name, *args, **kwargs)

FileManager.__doc__ = '''FileManager类用于管理文件系统中的文件和目录。它包含以下方法：
- __init__(self, dir_path:str, level:int=3): 初始化文件管理器，接受一个目录路径和一个层级参数，层级参数用于控制递归读取子目录的深度。
- build_function(self): 构建文件管理器的函数接口，定义了读取文件内容、写入文件、创建目录、删除文件、删除目录和列出文件等功能。
- read_file(self, file_name:str) -> TextFileContent: 读取指定文件的内容，并以特定格式返回文件名和内容。
- write_file(self, file_name:str, content:str) -> None: 将指定内容写入指定文件，如果文件不存在则创建新文件。
- add_dir(self, dir_name:str) -> None: 在当前目录下创建一个新的子目录。
- delete_file(self, file_name:str) -> None: 删除当前目录下的指定文件。
- delete_dir(self, dir_name:str) -> None: 删除当前目录下的指定子目录。
- list_files(self) -> str: 以树状图的形式列出当前目录下的所有文件和子目录，支持显示3层结构。
- __str__(self) -> str: 返回当前目录下的所有文件和子目录的树状图表示。
- __call__(self, __func_name:str, *args, **kwargs): 根据函数名称调用对应的函数实现，并传递参数。'''
FileManager.build_function.__doc__ = '''build_function方法用于构建文件管理器的函数接口，定义了以下功能：
- read_file: 读取指定文件的内容，并以特定格式返回文件名和内容。参数包括file_name，表示要读取的文件名，必须存在于当前目录中。
- write_file: 将指定内容写入指定文件，如果文件不存在则创建新文件。参数包括file_name，表示要写入的文件名，可以是新文件或现有文件；content，表示要写入文件的内容。
- add_dir: 在当前目录下创建一个新的子目录。参数包括dir_name，表示要创建的子目录名称，必须在当前目录中唯一。
- delete_file: 删除当前目录下的指定文件。参数包括file_name，表示要删除的文件名，必须存在于当前目录中。
- delete_dir: 删除当前目录下的指定子目录。参数包括dir_name，表示要删除的子目录名称，必须存在于当前目录中，并且是一个目录。
- list_files: 以树状图的形式列出当前目录下的所有文件和子目录，支持显示3层结构。该功能不需要参数。
注意：此函数会在__init__方法中被自动调用，请不要手动调用该函数。'''
FileManager.read_file.__doc__ = '''read_file方法用于读取指定文件的内容，并以特定格式返回文件名和内容。它接受以下参数：
- file_name: 要读取的文件名，必须存在于当前目录中。
该方法会检查指定的文件是否存在于当前目录中，如果存在，则打开文件并读取其内容，然后返回一个TextFileContent对象的字符串表示形式，其中包含文件名和文件内容。'''
FileManager.write_file.__doc__ = '''write_file方法用于将指定内容写入指定文件，如果文件不存在则创建新文件。它接受以下参数：
- file_name: 要写入的文件名，可以是新文件或现有文件。
- content: 要写入文件的内容。
该方法会打开指定的文件进行写入，如果文件不存在则创建新文件，然后将内容写入文件中。如果写入成功且文件之前不存在，则会将新文件名添加到当前目录的文件列表中。'''
FileManager.add_dir.__doc__ = '''add_dir方法用于在当前目录下创建一个新的子目录。它接受以下参数：
- dir_name: 要创建的子目录名称，必须在当前目录中唯一。
该方法会检查指定的子目录名称是否在当前目录中已经存在，如果不存在，则创建新的子目录，并将一个新的FileManager对象添加到当前目录的文件列表中，以便管理新创建的子目录。如果指定的子目录名称已经存在，则会抛出一个ValueError异常。'''
FileManager.delete_file.__doc__ = '''delete_file方法用于删除当前目录下的指定文件。它接受以下参数：
- file_name: 要删除的文件名，必须存在于当前目录中。
该方法会检查指定的文件是否存在于当前目录中，如果存在，则删除该文件，并将文件名从当前目录的文件列表中移除。如果指定的文件不存在，则会抛出一个ValueError异常。'''
FileManager.delete_dir.__doc__ = '''delete_dir方法用于删除当前目录下的指定子目录。它接受以下参数：
- dir_name: 要删除的子目录名称，必须存在于当前目录中，并且是一个目录。
该方法会检查指定的子目录名称是否存在于当前目录中，并且确认它是一个目录。如果满足条件，则删除该子目录，并将对应的FileManager对象从当前目录的文件列表中移除。如果指定的子目录不存在，或者不是一个目录，则会抛出一个ValueError异常。'''
FileManager.list_files.__doc__ = '''list_files方法用于以树状图的形式列出当前目录下的所有文件和子目录，支持显示3层结构。该方法不需要参数。
该方法会遍历当前目录的文件列表，对于每个文件，如果是一个FileManager对象，则递归调用其list_files方法来获取子目录的树状图表示；如果是一个普通文件，则直接添加到树状图中。最终返回一个字符串，表示当前目录下的所有文件和子目录的树状图结构。'''
FileManager.__str__.__doc__ = '''__str__方法用于返回当前目录下的所有文件和子目录的树状图表示。该方法不需要参数。
该方法会调用list_files方法来获取当前目录下的所有文件和子目录的树状图表示，并返回该字符串。'''
FileManager.__call__.__doc__ = '''__call__方法用于根据函数名称调用对应的函数实现，并传递参数。它接受以下参数：
- __func_name: 要调用的函数的名称，必须是之前通过build_function方法添加的函数名称。
- *args: 可选的位置参数，将被传递给函数实现。
- **kwargs: 可选的关键字参数，将被传递给函数实现。
该方法会在函数定义列表中查找与给定名称匹配的函数，如果找到，则调用对应的函数实现并传递参数。如果没有找到匹配的函数，则会抛出一个ValueError异常。'''
FileManager.refresh.__doc__ = '''refresh方法用于刷新当前目录的文件列表（重新读取磁盘）。该方法不需要参数。
该方法会重新读取当前目录的文件列表，并根据层级参数重新构建子目录的FileManager对象，以确保文件管理器的状态与磁盘上的实际文件系统保持一致。'''
FileManager.view_dir.__doc__ = '''view_dir方法用于查看当前目录下指定子目录的树状结构，返回字符串。它接受以下参数：
- dir_name: 要查看的子目录名称，必须在当前目录中存在。
该方法会检查指定的子目录名称是否存在于当前目录中，并且确认它是一个目录。如果满足条件，则创建一个新的FileManager对象来管理该子目录，并调用其list_files方法来获取子目录的树状图表示，最终返回该字符串。如果指定的子目录不存在，或者不是一个目录，则会抛出一个ValueError异常。'''