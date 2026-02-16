import requests
import os
from tqdm import tqdm
from ..tool_manager import AIFunction

class DownloadTool:
    def __init__(self, output_dir:str):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.build_function()
    
    def build_function(self):
        self.function = AIFunction([], [])
        self.function.add_function(
            name='download_file',
            description='根据提供的URL下载文件，并显示下载进度。确保下载完成后文件保存到指定目录，并且验证文件完整性。',
            parameters={
                'url': {'type': 'string', 'description': '要下载的文件的URL地址，必须是字符串。'},
                'save_path': {'type': 'string', 'description': '文件保存的相对路径（相对于输出目录），必须是字符串。'},
                'timeout': {'type': 'integer', 'description': '下载超时时间，单位为秒，默认为30秒，必须是整数。'}
            },
            required=['url', 'save_path'],
            function=self.download_file_with_progress
        )
    
    def download_file_with_progress(self, url:str, save_path:str, timeout:int=30) -> None:
        """
        带进度条的文件下载
        """
        try:
            full_save_path = os.path.join(self.output_dir, save_path)
            save_dir = os.path.dirname(full_save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            # 获取文件总大小（单位：字节）
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 1024 * 1024
            
            # 创建进度条
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(full_save_path))
            
            with open(full_save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))  # 更新进度条
            
            progress_bar.close()
            # 验证文件大小是否匹配
            if total_size != 0 and progress_bar.n != total_size:
                print("警告：文件下载不完整！")
            else:
                print(f"\n文件下载完成，保存至：{full_save_path}")
                
        except requests.exceptions.RequestException as e:
            print(f"下载失败：{e}")
        except Exception as e:
            print(f"下载失败：{e}")
        return
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

DownloadTool.download_file_with_progress.__doc__ = '''download_file_with_progress方法用于根据提供的URL下载文件，并显示下载进度。它接受以下参数：
- url: 要下载的文件的URL地址，必须是字符串。
- save_path: 文件保存的相对路径（相对于输出目录），必须是字符串。
- timeout: 下载超时时间，单位为秒，默认为30秒，必须是整数。
该方法会尝试从指定的URL下载文件，并将其保存到输出目录下的指定路径。下载过程中会显示一个进度条，指示下载的进度和速度。下载完成后，方法会验证下载的文件大小是否与服务器提供的内容长度匹配，以确保文件完整性。
如果下载成功，方法会打印文件保存的路径；如果下载失败，则会捕获异常并打印错误信息。'''
DownloadTool.__call__.__doc__ = '''__call__方法用于调用当前对象的函数定义列表中的函数。它接受以下参数：
- *args: 可选的位置参数，将被传递给函数实现。
- **kwargs: 可选的关键字参数，将被传递给函数实现。
该方法会在函数定义列表中查找与给定名称匹配的函数，如果找到，则调用对应的函数实现并传递参数。如果没有找到匹配的函数，则会抛出一个ValueError异常。'''
DownloadTool.build_function.__doc__ = '''build_function方法用于构建当前对象的函数定义列表。该方法不需要参数。
该方法会创建一个新的AIFunction对象，并使用add_function方法添加一个名为'download_file'的函数定义。这个函数定义包含了函数的名称、描述、参数信息、必需参数列表以及对应的函数实现。函数实现是当前对象的download_file_with_progress方法。该方法不返回任何值，但会将构建好的函数定义列表保存在当前对象的function属性中，以供后续调用使用。'''
DownloadTool.__doc__ = DownloadTool.__init__.__doc__ = '''DownloadTool类用于提供一个基于Python requests库的文件下载工具。它可以根据提供的URL下载文件，并显示下载进度。使用时需要指定一个输出目录，下载完成后文件将保存到该目录下。构造函数接受一个参数：
- output_dir: 文件下载后保存的目录路径，必须是字符串。如果目录不存在，则会自动创建。'''