# sv_to_python/extractor.py
"""
UVM操作提取器 - 使用正则表达式从SV源码中提取UVM寄存器模型操作
"""
from typing import List, Optional, Tuple
import re

from sv_to_python.ir import (
    Operation, RegWrite, RegRead, RegSet, RegGet,
    RegReset, RegRandomize, Comment, Todo, TaskInfo
)
from sv_to_python.errors import ExtractionError


class UVMOperationExtractor:
    """从SV源码中提取UVM寄存器模型操作"""

    # UVM方法正则表达式模式
    # 匹配: model.REG.write(status, value, path)
    #       reg_model.REG_NAME.write(status, value, UVM_FRONTDOOR)
    #       model.BLOCK[idx].reg.write(status, value)

    # write操作: reg_model.REG.write(status, value[, path])
    WRITE_PATTERN = re.compile(
        r'(\w+(?:\s*\[\s*\w+\s*\])?(?:\s*\.\s*\w+(?:\s*\[\s*\w+\s*\])?)*)\s*\.\s*write\s*\(',
        re.MULTILINE
    )

    # read操作: reg_model.REG.read(status, value[, path])
    READ_PATTERN = re.compile(
        r'(\w+(?:\s*\[\s*\w+\s*\])?(?:\s*\.\s*\w+(?:\s*\[\s*\w+\s*\])?)*)\s*\.\s*read\s*\(',
        re.MULTILINE
    )

    # set操作: reg_model.REG.set(value)
    SET_PATTERN = re.compile(
        r'(\w+(?:\s*\[\s*\w+\s*\])?(?:\s*\.\s*\w+(?:\s*\[\s*\w+\s*\])?)*)\s*\.\s*set\s*\(',
        re.MULTILINE
    )

    # get操作: reg_model.REG.get()
    GET_PATTERN = re.compile(
        r'(\w+(?:\s*\[\s*\w+\s*\])?(?:\s*\.\s*\w+(?:\s*\[\s*\w+\s*\])?)*)\s*\.\s*get\s*\(',
        re.MULTILINE
    )

    # reset操作: reg_model.REG.reset([status[, kind]])
    RESET_PATTERN = re.compile(
        r'(\w+(?:\s*\[\s*\w+\s*\])?(?:\s*\.\s*\w+(?:\s*\[\s*\w+\s*\])?)*)\s*\.\s*reset\s*\(',
        re.MULTILINE
    )

    # poke操作（backdoor write）: reg_model.REG.poke(status, value)
    POKE_PATTERN = re.compile(
        r'(\w+(?:\s*\[\s*\w+\s*\])?(?:\s*\.\s*\w+(?:\s*\[\s*\w+\s*\])?)*)\s*\.\s*poke\s*\(',
        re.MULTILINE
    )

    # peek操作（backdoor read）: reg_model.REG.peek(status, value)
    PEEK_PATTERN = re.compile(
        r'(\w+(?:\s*\[\s*\w+\s*\])?(?:\s*\.\s*\w+(?:\s*\[\s*\w+\s*\])?)*)\s*\.\s*peek\s*\(',
        re.MULTILINE
    )

    def extract(self, task: TaskInfo, source_text: str) -> List[Operation]:
        """从task中提取所有操作

        Args:
            task: TaskInfo对象
            source_text: 完整源代码文本

        Returns:
            操作列表
        """
        operations = []

        # 获取task的代码体
        task_body = self._extract_task_body(task.name, source_text)
        if not task_body:
            return operations

        # 按行处理，保留行号信息
        lines = task_body.split('\n')
        for line_no, line in enumerate(lines, start=task.line_no):
            # 提取各种操作
            op = self._extract_write_from_line(line, line_no)
            if op:
                operations.append(op)
                continue

            op = self._extract_read_from_line(line, line_no)
            if op:
                operations.append(op)
                continue

            op = self._extract_poke_from_line(line, line_no)
            if op:
                operations.append(op)
                continue

            op = self._extract_peek_from_line(line, line_no)
            if op:
                operations.append(op)
                continue

            op = self._extract_set_from_line(line, line_no)
            if op:
                operations.append(op)
                continue

            op = self._extract_get_from_line(line, line_no)
            if op:
                operations.append(op)
                continue

            op = self._extract_reset_from_line(line, line_no)
            if op:
                operations.append(op)
                continue

        return operations

    def _extract_task_body(self, task_name: str, source_text: str) -> str:
        """提取task的代码体

        Args:
            task_name: task名称
            source_text: 源代码

        Returns:
            task代码体
        """
        # 查找task定义
        task_pattern = re.compile(
            r'task\s+(?:automatic\s+)?' + re.escape(task_name) + r'\s*(?:\([^)]*\))?;',
            re.MULTILINE
        )

        match = task_pattern.search(source_text)
        if not match:
            return ""

        start_pos = match.end()

        # 查找对应的endtask
        endtask_pattern = re.compile(r'\bendtask\b', re.MULTILINE)
        endtask_match = endtask_pattern.search(source_text[start_pos:])
        if not endtask_match:
            return ""

        end_pos = start_pos + endtask_match.start()
        return source_text[start_pos:end_pos]

    def _extract_write_from_line(self, line: str, line_no: int) -> Optional[RegWrite]:
        """从一行中提取write操作"""
        match = self.WRITE_PATTERN.search(line)
        if not match:
            return None

        reg_path_str = match.group(1)
        reg_path = self._parse_reg_path(reg_path_str)

        # 提取值和backdoor标志
        value = self._extract_write_value(line)
        is_backdoor = self._is_backdoor(line)

        return RegWrite(
            line_no=line_no,
            original_source=line.strip(),
            reg_path=reg_path,
            value=value,
            backdoor=is_backdoor
        )

    def _extract_read_from_line(self, line: str, line_no: int) -> Optional[RegRead]:
        """从一行中提取read操作"""
        match = self.READ_PATTERN.search(line)
        if not match:
            return None

        reg_path_str = match.group(1)
        reg_path = self._parse_reg_path(reg_path_str)
        is_backdoor = self._is_backdoor(line)

        return RegRead(
            line_no=line_no,
            original_source=line.strip(),
            reg_path=reg_path,
            backdoor=is_backdoor
        )

    def _extract_poke_from_line(self, line: str, line_no: int) -> Optional[RegWrite]:
        """从一行中提取poke操作（backdoor write）"""
        match = self.POKE_PATTERN.search(line)
        if not match:
            return None

        reg_path_str = match.group(1)
        reg_path = self._parse_reg_path(reg_path_str)

        value = self._extract_write_value(line)

        return RegWrite(
            line_no=line_no,
            original_source=line.strip(),
            reg_path=reg_path,
            value=value,
            backdoor=True  # poke总是backdoor
        )

    def _extract_peek_from_line(self, line: str, line_no: int) -> Optional[RegRead]:
        """从一行中提取peek操作（backdoor read）"""
        match = self.PEEK_PATTERN.search(line)
        if not match:
            return None

        reg_path_str = match.group(1)
        reg_path = self._parse_reg_path(reg_path_str)

        return RegRead(
            line_no=line_no,
            original_source=line.strip(),
            reg_path=reg_path,
            backdoor=True  # peek总是backdoor
        )

    def _extract_set_from_line(self, line: str, line_no: int) -> Optional[RegSet]:
        """从一行中提取set操作"""
        match = self.SET_PATTERN.search(line)
        if not match:
            return None

        reg_path_str = match.group(1)
        reg_path = self._parse_reg_path(reg_path_str)

        value = self._extract_set_value(line)

        return RegSet(
            line_no=line_no,
            original_source=line.strip(),
            reg_path=reg_path,
            value=value
        )

    def _extract_get_from_line(self, line: str, line_no: int) -> Optional[RegGet]:
        """从一行中提取get操作"""
        match = self.GET_PATTERN.search(line)
        if not match:
            return None

        reg_path_str = match.group(1)
        reg_path = self._parse_reg_path(reg_path_str)

        return RegGet(
            line_no=line_no,
            original_source=line.strip(),
            reg_path=reg_path
        )

    def _extract_reset_from_line(self, line: str, line_no: int) -> Optional[RegReset]:
        """从一行中提取reset操作"""
        match = self.RESET_PATTERN.search(line)
        if not match:
            return None

        reg_path_str = match.group(1)
        reg_path = self._parse_reg_path(reg_path_str)

        return RegReset(
            line_no=line_no,
            original_source=line.strip(),
            reg_path=reg_path,
            kind="HARD"
        )

    def _parse_reg_path(self, path_str: str) -> List[str]:
        """解析寄存器路径字符串

        Args:
            path_str: 例如 "reg_model.REG_NAME" 或 "model.BANK[idx].reg"

        Returns:
            寄存器路径列表，例如 ['REG_NAME'] 或 ['BANK', '[idx]', 'reg']
        """
        # 移除空白字符
        path_str = path_str.strip()

        # 按点分割
        parts = path_str.split('.')

        # 过滤掉模型名称（通常包含model、reg_model等）
        filtered = []
        for part in parts:
            part = part.strip()
            # 跳过常见的模型名称前缀
            if part in ['reg_model', 'model', 'blk_model', 'dma_reg_model']:
                continue
            if part:
                # 处理数组索引: REG_CH[channel] -> REG_CH, channel
                part = self._split_array_part(part)
                filtered.extend(part)

        return filtered

    def _split_array_part(self, part: str) -> List[str]:
        """分割数组索引部分

        Args:
            part: 例如 "REG_CH[channel]" 或 "REG_NAME"

        Returns:
            ['REG_CH', 'channel'] 或 ['REG_NAME']
        """
        # 匹配数组访问: NAME[idx] 或 NAME[idx1][idx2]
        array_pattern = re.compile(r'(\w+)(\[[^\]]+\](?:\[[^\]]+\])*)')

        match = array_pattern.match(part)
        if match:
            name = match.group(1)
            indices = match.group(2)

            result = [name]
            # 提取所有索引
            idx_pattern = re.compile(r'\[(\w+)\]')
            for idx_match in idx_pattern.finditer(indices):
                result.append(idx_match.group(1))

            return result

        return [part]

    def _extract_write_value(self, line: str):
        """从write语句中提取写入的值

        Args:
            line: 代码行

        Returns:
            值（整数或字符串）
        """
        # 匹配: write(status, 32'h0000_0001 或 write(status, value
        # 查找第二个参数
        value_pattern = re.compile(
            r'write\s*\([^,]+,\s*([^,)]+)',
            re.MULTILINE
        )

        match = value_pattern.search(line)
        if match:
            value_str = match.group(1).strip()
            return self._parse_value(value_str)

        return None

    def _extract_set_value(self, line: str):
        """从set语句中提取值"""
        # 匹配: set(32'h0001) 或 set(value)
        value_pattern = re.compile(
            r'set\s*\(\s*([^)]+)\)',
            re.MULTILINE
        )

        match = value_pattern.search(line)
        if match:
            value_str = match.group(1).strip()
            return self._parse_value(value_str)

        return None

    def _parse_value(self, value_str: str):
        """解析值字符串

        Args:
            value_str: 例如 "32'h0000_0001", "0x100", "channel", "123"

        Returns:
            解析后的值
        """
        value_str = value_str.strip()

        # 字面量: 32'h0000_0001
        literal_pattern = re.compile(r"(\d+)['hH]([0-9a-fA-F_]+)")
        match = literal_pattern.match(value_str)
        if match:
            hex_str = match.group(2).replace('_', '')
            return int(hex_str, 16)

        # 十六进制: 0x...
        if value_str.startswith('0x') or value_str.startswith('0X'):
            return int(value_str, 16)

        # 二进制: 0b... 或 'b...
        if value_str.startswith('0b') or value_str.startswith('0B'):
            return int(value_str, 16)

        # 十进制数字
        if value_str.isdigit():
            return int(value_str)

        # 变量名，直接返回
        return value_str

    def _is_backdoor(self, line: str) -> bool:
        """检查是否指定了backdoor访问"""
        # 检查UVM_BACKDOOR标志
        return 'UVM_BACKDOOR' in line or 'BACKDOOR' in line.upper()
