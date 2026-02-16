from .tool_manager import AIFunction
from typing import Union, Tuple
import re
import bisect

class _VideoTime_hms:
    def __init__(self, h:int, m:int, s:float)->None:
        if s<0 or m<0 or h<0:
            raise ValueError(f'Invalid time, hour={h}, minute={m}, second={s}.')
        self.h, self.m, self.s = h, m, s
        self.flatten()
        return

    def flatten(self)->None:
        h, m, s = self.h, self.m, self.s
        if h%1!=0:
            hm = (h%1)*60
            m += hm
            h = int(h)
        if m%1!=0:
            ms = (m%1)*60
            s += ms
            m = int(m)

        if s>=60:
            sm = s//60
            s = s%60
            m += sm
        if m>=60:
            mh = m//60
            m = m%60
            h += mh
        self.h, self.m, self.s = h, m, s
        return

    def __str__(self)->str:
        return f'{self.h}:{self.m}:{self.s}'

    def __eq__(self, other):
        return self.h==other.h and self.m==other.m and abs(self.s-other.s)<=0.01

    def __ne__(self, other):
        return self.h!=other.h or self.m!=other.m or abs(self.s-other.s)>0.01

    def __lt__(self, other):
        if self.h>other.h:
            return False
        elif self.h<other.h:
            return True
        
        # self.h == other.h
        elif self.m>other.m:
            return False
        elif self.m<other.m:
            return True
        
        # self.m == other.m
        elif abs(self.s-other.s)>0.01:
            return self.s<other.s
        else:
            return False  # self==other

    def __le__(self, other):
        if self.h>other.h:
            return False
        elif self.h<other.h:
            return True
        
        # self.h == other.h
        elif self.m>other.m:
            return False
        elif self.m<other.m:
            return True
        
        # self.m == other.m
        elif abs(self.s-other.s)>0.01:
            return self.s<other.s
        else:
            return True  # self==other

    def __hash__(self):
        total_cs = int(round((self.h * 3600 + self.m * 60 + self.s) * 100))
        return hash(total_cs)

    def __gt__(self, other):
        if self.h>other.h:
            return True
        elif self.h<other.h:
            return False
        
        # self.h == other.h
        elif self.m>other.m:
            return True
        elif self.m<other.m:
            return False
        
        # self.m == other.m
        elif abs(self.s-other.s)>0.01:
            return self.s>other.s
        else:
            return False  # self==other

    def __ge__(self, other):
        if self.h>other.h:
            return True
        elif self.h<other.h:
            return False
        
        # self.h == other.h
        elif self.m>other.m:
            return True
        elif self.m<other.m:
            return False
        
        # self.m == other.m
        elif abs(self.s-other.s)>0.01:
            return self.s>other.s
        else:
            return True  # self==other


class VideoTime(_VideoTime_hms):
    def __init__(self, time:Union[str, _VideoTime_hms, 'VideoTime', Tuple[int, int, float]] = None, *rest)->None:
        # 支持以下调用方式：VideoTime(h, m, s)，VideoTime((h,m,s))，VideoTime('h:m:s')，或传入已有 VideoTime
        if rest:
            if len(rest) != 2:
                raise ValueError('Invalid positional arguments for VideoTime')
            h, m, s = time, rest[0], rest[1]
            # ensure hours and minutes are integers
            try:
                if not float(h).is_integer() or not float(m).is_integer():
                    raise ValueError('Hours and minutes must be integers; seconds may be decimal.')
            except Exception:
                raise ValueError('Hours and minutes must be integers; seconds may be decimal.')
            h, m = int(h), int(m)
            super().__init__(h, m, float(s))
            return
        if isinstance(time, tuple):
            if len(time) != 3:
                raise ValueError(f'Invalid tuple {time}.')
            h, m, s = time
            try:
                if not float(h).is_integer() or not float(m).is_integer():
                    raise ValueError('Hours and minutes must be integers; seconds may be decimal.')
            except Exception:
                raise ValueError('Hours and minutes must be integers; seconds may be decimal.')
            h, m = int(h), int(m)
            super().__init__(h, m, float(s))
            return
        elif isinstance(time, _VideoTime_hms) or isinstance(time, VideoTime):
            self.h, self.m, self.s = time.h, time.m, time.s
            self.flatten()
            return
        elif isinstance(time, str):
            numbers = re.findall('\d+\.?\d*', time)
            if len(numbers) < 3:
                raise ValueError(f"Could not find enough numbers in time string: '{time}'")
            try:
                h = float(numbers[0])
                m = float(numbers[1])
                s = float(numbers[2])
                if not h.is_integer() or not m.is_integer():
                    raise ValueError('Hours and minutes must be integers; seconds may be decimal.')
                if len(numbers) > 3:
                    import warnings
                    warnings.warn(f"Found more than 3 numbers in time string, only first 3 are used: '{time}'")
                super().__init__(int(h), int(m), float(s))
                return
            except:
                raise ValueError
            
class _OutlineBlock:
    def __init__(self, topic:str, begin:VideoTime, end:VideoTime)->None:
        if not isinstance(begin, VideoTime):
            begin = VideoTime(begin)
        if not isinstance(end, VideoTime):
            end = VideoTime(end)
        self.begin, self.end = begin, end
        self.topic = str(topic)
        self.block = {}
        return

    def write(self, time:Union[str, VideoTime], content:str)->None:
        if isinstance(time, str):
            time=VideoTime(time)
        if time < self.begin or time > self.end:
            raise ValueError('The corresponding time is not within the range of this block. ')
        content = str(content)
        if '|' in content:
            content = content.replace('|', '｜')
        self.block[time] = content
        # 排序
        self.block = dict(sorted(self.block.items(), key=lambda x: x[0]))
        return
    
    def encode(self)->str:
        res = f'\n{self.topic}\n'
        for time, content in self.block.items():
            res += f'{time}|{content}\n'
        res += '*****'
        return res
    
    def decode(self, block:str)->None:
        self.block = {}
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines:
            return
        self.topic = lines.pop(0)
        times = []
        for line in lines:
            if '|' in line:
                time, content = line.strip().split('|', 1)
                time = VideoTime(time)
                self.block[time] = content
                times.append(time)
            elif '*****' in line:
                break
        if not times:
            return
        self.begin = times[0]
        self.end = times[-1]
        return
    
    def __str__(self):
        res = f'\n{self.topic}({self.begin}~{self.end})\n'
        res += '|时间点|内容|\n|---|---|\n'
        for time, content in self.block.items():
            res += f'|{time}|{content}|\n'
        return res
    
class OutlineManager:
    def __init__(self, path:str) -> None:
        self.path = path
        self.outline = {}  # topic(str) : block(_OutlineBlock)
        self.load()
        self.build_functions()
        return
    
    def build_functions(self)->None:
        self.functions = AIFunction([], [])
        self.functions.add_function(
            name='add_content',
            description='将内容添加到大纲中指定时间点。',
            parameters={
                'time': '时间点，格式必须是h:m:s，s支持小数，精确到0.01s',
                'content': '要添加的内容，字符串格式'
            },
            required=['time', 'content'],
            function=self.add_content
        )
        self.functions.add_function(
            name='delete_content',
            description='将大纲中指定时间点的内容删除。',
            parameters={
                'time': '时间点，格式必须是h:m:s，s支持小数，精确到0.01s'
            },
            required=['time'],
            function=self.delete_content
        )
        self.functions.add_function(
            name='edit_outline_block',
            description='编辑大纲块的时间范围，如果该块不存在则创建一个新的块。',
            parameters={
                'topic': '大纲块的主题，字符串格式',
                'begin': '大纲块的开始时间，格式必须是h:m:s，s支持小数，精确到0.01s',
                'end': '大纲块的结束时间，格式必须是h:m:s，s支持小数，精确到0.01s'
            },
            required=['topic', 'begin', 'end'],
            function=self.edit_outline_block
        )
        self.functions.add_function(
            name='delete_outline_block',
            description='删除大纲块。',
            parameters={
                'topic': '大纲块的主题，字符串格式'
            },
            required=['topic'],
            function=self.delete_outline_block
        )
        self.functions.add_function(
            name='view',
            description='查看大纲内容。',
            parameters={},
            required=[],
            function=self.view
        )
        return
    
    def load(self)->None:
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
            blocks = content.split('*****')
            for block in blocks:
                if not block.strip():
                    continue
                # skip malformed/empty blocks that don't contain time|content lines
                if '|' not in block:
                    continue
                ob = _OutlineBlock('', VideoTime(0,0,0), VideoTime(0,0,0))
                ob.decode(block)
                self.outline[ob.topic] = ob
            return
        except FileNotFoundError:
            return
    
    def save(self)->None:
        with open(self.path, 'w', encoding='utf-8') as f:
            for block in self.outline.values():
                f.write(block.encode() + '\n')
        return
    
    def view(self)->str:
        res = ''
        for block in self.outline.values():
            res += f'\n'
            res += str(block)
            res += '-----\n'
        return res
    
    def add_content(self, time:str, content:str)->None:
        time = VideoTime(time)
        blocks = list(self.outline.values())
        blocks.sort(key=lambda x: x.begin)
        begins = [b.begin for b in blocks]
        index = bisect.bisect_right(begins, time) - 1
        if index < 0 or index >= len(blocks):
            raise ValueError('The corresponding time is out of range of the outline. ')
        block = blocks[index]
        block.write(time, content)
        return
    
    def delete_content(self, time:str)->None:
        time = VideoTime(time)
        blocks = list(self.outline.values())
        blocks.sort(key=lambda x: x.begin)
        begins = [b.begin for b in blocks]
        index = bisect.bisect_right(begins, time) - 1
        if index < 0 or index >= len(blocks):
            raise ValueError('The corresponding time is out of range of the outline. ')
        block = blocks[index]
        if time in block.block:
            del block.block[time]
        else:
            raise ValueError('The corresponding time point does not exist in the outline. ')
        return
    
    def edit_outline_block(self, topic:str, begin:str, end:str)->None:
        begin = VideoTime(begin)
        end = VideoTime(end)
        if topic in self.outline:
            block = self.outline[topic]
            block.begin = begin
            block.end = end
        else:
            block = _OutlineBlock(topic, begin, end)
            self.outline[topic] = block
        return
    
    def delete_outline_block(self, topic:str)->None:
        if topic in self.outline:
            del self.outline[topic]
        else:
            raise ValueError('The corresponding topic does not exist in the outline. ')
        return
    
    def __call__(self, *args, **kwargs):
        return self.functions(*args, **kwargs)

if __name__ == '__main__':
    om = OutlineManager('outline.txt')
    om.edit_outline_block('第一部分', '0:0:0', '0:10:0')
    om.edit_outline_block('第二部分', '0:10:0', '0:20:0')
    om.add_content('0:1:30', '这是第一部分的内容。')
    om.add_content('0:5:0', '这是第一部分的另一个内容。')
    om.add_content('0:12:0', '这是第二部分的内容。')
    print(om.view())
    om.save()
    new_om = OutlineManager('outline.txt')
    print(new_om.view())