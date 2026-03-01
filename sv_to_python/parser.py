# sv_to_python/parser.py
"""
SystemVerilog解析器 - 使用正则表达式进行模式匹配
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

from sv_to_python.ir import TaskInfo
from sv_to_python.errors import ParseError


class SVParser:
    """SystemVerilog文件解析器 - 基于正则表达式的轻量级解析"""

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.source_text: str = ""

    def parse(self) -> str:
        """读取SV文件

        Returns:
            源代码文本
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.source_text = f.read()
            return self.source_text

        except Exception as e:
            raise ParseError(f"Failed to read {self.file_path}: {e}")

    def get_tasks(self) -> Dict[str, TaskInfo]:
        """提取所有task定义

        Returns:
            字典 {task_name: TaskInfo}
        """
        if not self.source_text:
            self.parse()

        tasks = {}

        # 正则表达式匹配task定义
        # 支持多种语法风格:
        # - task name;
        # - task automatic name;
        # - task name(input type port, ...);
        task_pattern = re.compile(
            r'task\s+(?P<automatic>automatic\s+)?(?P<name>\w+)\s*\((?P<ports>[^)]*)\);?',
            re.MULTILINE
        )

        # 备用模式：task name; (无参数列表)
        task_simple_pattern = re.compile(
            r'task\s+(?P<automatic>automatic\s+)?(?P<name>\w+)\s*;',
            re.MULTILINE
        )

        # 搜索带参数的task
        for match in task_pattern.finditer(self.source_text):
            task_name = match.group('name')
            start_pos = match.start()

            # 找到对应的endtask
            end_pos = self._find_endtask(start_pos)
            if end_pos == -1:
                continue

            # 提取参数
            ports_str = match.group('ports')
            parameters = self._parse_ports(ports_str)

            # 提取行号
            line_no = self.source_text[:start_pos].count('\n') + 1

            tasks[task_name] = TaskInfo(
                name=task_name,
                parameters=parameters,
                operations=[],  # 稍后由extractor填充
                line_no=line_no
            )

        # 搜索无参数的task
        for match in task_simple_pattern.finditer(self.source_text):
            task_name = match.group('name')
            if task_name in tasks:
                continue  # 已被前面的模式匹配

            start_pos = match.start()

            # 找到对应的endtask
            end_pos = self._find_endtask(start_pos)
            if end_pos == -1:
                continue

            # 提取行号
            line_no = self.source_text[:start_pos].count('\n') + 1

            tasks[task_name] = TaskInfo(
                name=task_name,
                parameters=[],
                operations=[],
                line_no=line_no
            )

        return tasks

    def _find_endtask(self, start_pos: int) -> int:
        """从start_pos开始查找对应的endtask

        Args:
            start_pos: 搜索起始位置

        Returns:
            endtask的位置，-1表示未找到
        """
        # 从start_pos后搜索endtask
        search_text = self.source_text[start_pos:]

        # 查找endtask
        endtask_match = re.search(r'endtask', search_text, re.IGNORECASE)
        if endtask_match:
            return start_pos + endtask_match.end()

        return -1

    def _parse_ports(self, ports_str: str) -> List[Tuple[str, str]]:
        """解析task参数列表

        Args:
            ports_str: 端口字符串，例如 "input int channel, input logic [31:0] addr"

        Returns:
            [(param_name, param_type), ...]
        """
        parameters = []

        if not ports_str or not ports_str.strip():
            return parameters

        # 按逗号分割参数（考虑嵌套的括号）
        ports = self._split_ports(ports_str)

        for port in ports:
            port = port.strip()
            if not port:
                continue

            # 解析单个端口
            # 格式可能: input type name, output type [msb:lsb] name, etc.
            param = self._parse_single_port(port)
            if param:
                parameters.append(param)

        return parameters

    def _split_ports(self, ports_str: str) -> List[str]:
        """分割端口列表，考虑嵌套括号

        Args:
            ports_str: 端口字符串

        Returns:
            端口列表
        """
        ports = []
        current = []
        depth = 0

        for char in ports_str:
            if char == ',' and depth == 0:
                ports.append(''.join(current).strip())
                current = []
            else:
                if char in '([{':
                    depth += 1
                elif char in ')]}':
                    depth = max(0, depth - 1)
                current.append(char)

        if current:
            ports.append(''.join(current).strip())

        return ports

    def _parse_single_port(self, port: str) -> Optional[Tuple[str, str]]:
        """解析单个端口定义

        Args:
            port: 端口定义字符串

        Returns:
            (name, type) 或 None
        """
        # 移除input/output/inout等方向关键字
        port = re.sub(r'\b(input|output|inout|ref)\b', '', port).strip()

        # 尝试匹配: type name 或 type [bits] name
        # 例如: "int channel" 或 "logic [31:0] addr"
        match = re.match(r'(\w+(?:\s*\[[^\]]+\])?)\s+(\w+)', port)
        if match:
            param_type = match.group(1).strip()
            param_name = match.group(2).strip()
            return (param_name, param_type)

        # 如果无法解析，返回None
        return None

    def get_task_body(self, task_name: str) -> str:
        """获取task的完整代码体

        Args:
            task_name: task名称

        Returns:
            task代码体字符串
        """
        if not self.source_text:
            self.parse()

        # 查找task定义
        task_pattern = re.compile(
            r'task\s+(?:automatic\s+)?' + re.escape(task_name) + r'\s*(?:\([^)]*\))?;',
            re.MULTILINE
        )

        match = task_pattern.search(self.source_text)
        if not match:
            return ""

        start_pos = match.start()

        # 找到对应的endtask
        end_pos = self._find_endtask(start_pos)
        if end_pos == -1:
            return ""

        return self.source_text[start_pos:end_pos]
