# SystemVerilog到Python转换器实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 构建一个工具，将SystemVerilog中的UVM寄存器模型操作序列转换为使用EDA_UFVM RGM的Python配置脚本。

**架构:** 使用PyVerilog解析SystemVerilog文件生成AST，通过AST访问者模式提取UVM寄存器模型调用，转换为中间表示(IR)，最后使用Jinja2模板生成Python代码。

**技术栈:** Python 3.8+, PyVerilog (SV解析), Jinja2 (代码生成), Click (CLI), pytest (测试)

---

## 前置准备

### 阅读设计文档

在开始前，阅读：
- `docs/plans/2026-03-01-sv-to-python-converter-design.md` - 完整设计说明
- EDA_UFVM RGM文档: `docs/product/RGM_GUIDE.md` - 理解目标API

### 安装依赖

```bash
# 安装PyVerilog
pip install pyverilog

# 安装Jinja2和Click
pip install jinja2 click

# 验证安装
python -c "import pyverilog; print('PyVerilog OK')"
python -c "import jinja2; print('Jinja2 OK')"
python -c "import click; print('Click OK')"
```

---

## M1: SV解析器 + 基础操作提取 (1周)

### Task 1.1: 创建项目结构和中间表示

**Files:**
- Create: `sv_to_python/__init__.py`
- Create: `sv_to_python/ir.py`
- Create: `sv_to_python/errors.py`
- Test: `tests/test_sv_to_python/test_ir.py`

**Step 1: 创建测试文件 - 中间表示数据类**

```python
# tests/test_sv_to_python/test_ir.py
import pytest
from dataclasses import dataclass, field
from typing import List, Any

from sv_to_python.ir import (
    Operation, RegWrite, RegRead, RegSet, RegGet,
    RegReset, Comment, Todo
)

def test_reg_write_creation():
    """测试RegWrite创建"""
    op = RegWrite(
        line_no=10,
        original_source="model.REG.write(status, 32'h0001)",
        reg_path=['REG'],
        value=0x0001,
        backdoor=False
    )
    assert op.line_no == 10
    assert op.reg_path == ['REG']
    assert op.value == 0x0001
    assert op.backdoor is False

def test_reg_read_creation():
    """测试RegRead创建"""
    op = RegRead(
        line_no=20,
        original_source="model.REG.read(status, value)",
        reg_path=['REG'],
        backdoor=False
    )
    assert op.reg_path == ['REG']

def test_comment_creation():
    """测试Comment创建"""
    op = Comment(
        line_no=5,
        original_source="// Enable DMA",
        text="Enable DMA"
    )
    assert op.text == "Enable DMA"

def test_todo_creation():
    """测试Todo创建"""
    op = Todo(
        line_no=100,
        original_source="model.custom_method()",
        reason="Custom UVM extension method"
    )
    assert "Custom UVM extension" in op.reason
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_sv_to_python/test_ir.py -v
```
Expected: FAIL - ModuleNotFoundError: No module named 'sv_to_python'

**Step 3: 实现中间表示模块**

```python
# sv_to_python/__init__.py
"""
SV to Python - SystemVerilog到Python配置脚本转换器
"""

__version__ = "0.1.0"
```

```python
# sv_to_python/ir.py
"""
中间表示 - 操作序列定义
"""
from dataclasses import dataclass, field
from typing import List, Any, Optional

@dataclass
class Operation:
    """操作基类"""
    line_no: int
    original_source: str

@dataclass
class RegWrite(Operation):
    """寄存器写入操作"""
    reg_path: List[str]   # ['DMA_BLOCK', 'channel', 'ch', 'ctrl']
    value: Any
    backdoor: bool = False

@dataclass
class RegRead(Operation):
    """寄存器读取操作"""
    reg_path: List[str]
    backdoor: bool = False

@dataclass
class RegSet(Operation):
    """设置模型值（不写硬件）"""
    reg_path: List[str]
    value: Any

@dataclass
class RegGet(Operation):
    """获取模型值（不读硬件）"""
    reg_path: List[str]

@dataclass
class RegReset(Operation):
    """复位寄存器"""
    reg_path: List[str]
    kind: str = "HARD"

@dataclass
class RegRandomize(Operation):
    """随机化寄存器"""
    reg_path: List[str]
    constraints: Optional[List[str]] = None

@dataclass
class Comment(Operation):
    """注释"""
    text: str

@dataclass
class Todo(Operation):
    """需要手动实现的操作"""
    reason: str

@dataclass
class TaskInfo:
    """Task分析结果"""
    name: str
    parameters: List[tuple]  # (name, type) tuples
    operations: List[Operation]
    line_no: int = 0
```

```python
# sv_to_python/errors.py
"""
异常定义
"""
class ConversionError(Exception):
    """转换错误基类"""
    pass

class ParseError(ConversionError):
    """SV解析错误"""
    pass

class UnsupportedConstruct(ConversionError):
    """不支持的SV构造"""
    def __init__(self, construct_type, line_no, suggestion=None):
        self.construct_type = construct_type
        self.line_no = line_no
        self.suggestion = suggestion
        super().__init__(
            f"Unsupported {construct_type} at line {line_no}" +
            (f". Suggestion: {suggestion}" if suggestion else "")
        )

class AmbiguousValue(ConversionError):
    """值无法确定"""
    pass

class UVMMethodNotFound(ConversionError):
    """UVM方法无法识别"""
    pass
```

**Step 4: 运行测试**

```bash
pytest tests/test_sv_to_python/test_ir.py -v
```
Expected: PASS (4 tests)

**Step 5: 提交**

```bash
git add sv_to_python/ tests/test_sv_to_python/
git commit -m "feat(sv2python): 创建项目结构和中间表示

- 定义操作类型数据类
- 定义异常类层次
- 添加基础单元测试"
```

---

### Task 1.2: 创建SV测试fixture文件

**Files:**
- Create: `tests/fixtures/simple_tasks.sv`
- Create: `tests/fixtures/uvm_tasks.sv`

**Step 1: 创建简单SV测试文件**

```systemverilog
// tests/fixtures/simple_tasks.sv
// 简单的SystemVerilog task示例

// 基础task
task simple_write();
  $display("Simple write");
endtask

// 带参数的task
task write_register(input logic [31:0] value);
  $display("Writing: %h", value);
endtask

// 多个操作的task
task multiple_ops();
  $display("Op 1");
  $display("Op 2");
  $display("Op 3");
endtask
```

**Step 2: 创建UVM模式测试文件**

```systemverilog
// tests/fixtures/uvm_tasks.sv
// UVM寄存器模型操作示例

// 模式1: 基本FrontDoor写入
task automatic basic_write(input logic [31:0] value);
  uvm_status_e status;
  reg_model.REG_NAME.write(status, value, UVM_FRONTDOOR);
endtask

// 模式2: BackDoor写入
task automatic backdoor_write(input logic [31:0] value);
  uvm_status_e status;
  reg_model.REG_NAME.write(status, value, UVM_BACKDOOR);
endtask

// 模式3: 单索引数组
task automatic array_write(input int channel, input logic [31:0] value);
  uvm_status_e status;
  reg_model.REG_CH[channel].write(status, value, UVM_FRONTDOOR);
endtask

// 模式4: 多维数组
task automatic multidim_write(input int ch, input int bank, input logic [31:0] value);
  uvm_status_e status;
  reg_model.BANK[ch][bank_id].write(status, value);
endtask

// 模式5: 读取操作
task automatic read_operation();
  uvm_status_e status;
  uvm_reg_data_t value;
  reg_model.REG_NAME.read(status, value, UVM_FRONTDOOR);
  $display("Read: %h", value);
endtask

// 模式6: Set/Get操作
task automatic set_get_operation(input logic [31:0] value);
  reg_model.REG_NAME.set(value);
  value = reg_model.REG_NAME.get();
endtask

// 模式7: Reset
task automatic reset_operation();
  uvm_status_e status;
  reg_model.REG_NAME.reset(status);
endtask

// 完整示例: DMA初始化
task automatic init_dma(
  input int channel,
  input logic [31:0] base_addr,
  input int length
);
  uvm_status_e status;

  // Enable DMA channel
  dma_reg_model.DMA_CTRL[channel].write(status, 32'h0000_0001, UVM_FRONTDOOR);

  // Set address and length
  dma_reg_model.DMA_ADDR[channel].write(status, base_addr);
  dma_reg_model.DMA_LEN[channel].write(status, length);

  // Start transfer
  dma_reg_model.DMA_CMD[channel].write(status, 32'h0000_0001);
endtask
```

**Step 3: 提交**

```bash
git add tests/fixtures/
git commit -m "test(sv2python): 添加SV测试fixture文件

- 简单task示例
- UVM寄存器模型操作示例
- 覆盖7种基本模式
- 完整DMA初始化示例"
```

---

### Task 1.3: 实现基础SV解析器

**Files:**
- Create: `sv_to_python/parser.py`
- Test: `tests/test_sv_to_python/test_parser.py`

**Step 1: 创建解析器测试**

```python
# tests/test_sv_to_python/test_parser.py
import pytest
from pathlib import Path

from sv_to_python.parser import SVParser

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"

def test_parser_basic():
    """测试基础解析功能"""
    parser = SVParser(FIXTURE_DIR / "simple_tasks.sv")
    ast_result = parser.parse()

    assert ast_result is not None
    assert parser.ast is not None

def test_get_tasks_simple():
    """测试提取简单tasks"""
    parser = SVParser(FIXTURE_DIR / "simple_tasks.sv")
    tasks = parser.get_tasks()

    assert len(tasks) >= 3
    assert "simple_write" in tasks
    assert "write_register" in tasks
    assert "multiple_ops" in tasks

def test_get_tasks_uvm():
    """测试提取UVM tasks"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    assert len(tasks) >= 7
    assert "basic_write" in tasks
    assert "init_dma" in tasks

def test_task_params():
    """测试task参数提取"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    init_dma = tasks["init_dma"]
    assert len(init_dma.parameters) == 3
    param_names = [p[0] for p in init_dma.parameters]
    assert "channel" in param_names
    assert "base_addr" in param_names
    assert "length" in param_names
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_sv_to_python/test_parser.py::test_parser_basic -v
```
Expected: FAIL - ModuleNotFoundError

**Step 3: 实现SV解析器**

```python
# sv_to_python/parser.py
"""
SystemVerilog解析器 - 使用PyVerilog
"""
from pathlib import Path
from typing import Dict, List
from pyverilog.dataflow.parser import VerilogDataflowParser
from pyverilog.dataflow.dataflow import *

from sv_to_python.ir import TaskInfo

class SVParser:
    """SystemVerilog文件解析器"""

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.ast = None

    def parse(self):
        """解析SV文件，生成AST"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        try:
            parser = VerilogDataflowParser([str(self.file_path)])
            self.ast = parser.parse()
            return self.ast
        except Exception as e:
            raise ParseError(f"Failed to parse {self.file_path}: {e}")

    def get_tasks(self) -> Dict[str, TaskInfo]:
        """提取所有task定义

        Returns:
            字典 {task_name: TaskInfo}
        """
        if self.ast is None:
            self.parse()

        tasks = {}

        # 遍历AST查找task定义
        for node in self.ast.tree:
            if isinstance(node, HDLTask):
                task_info = self._extract_task_info(node)
                tasks[task_info.name] = task_info

        return tasks

    def _extract_task_info(self, node: HDLTask) -> TaskInfo:
        """从AST节点提取task信息

        Args:
            node: HDLTask节点

        Returns:
            TaskInfo对象
        """
        # 提取参数
        parameters = self._extract_parameters(node)

        # 提取语句列表
        statements = node.list if hasattr(node, 'list') else []

        return TaskInfo(
            name=node.name,
            parameters=parameters,
            operations=[],  # 稍后由extractor填充
            line_no=node.lineno if hasattr(node, 'lineno') else 0
        )

    def _extract_parameters(self, node: HDLTask) -> List[tuple]:
        """提取task参数

        Returns:
            [(param_name, param_type), ...]
        """
        parameters = []

        if hasattr(node, 'ports'):
            for port in node.ports:
                # PyVerilog的端口表示
                if hasattr(port, 'name'):
                    param_type = self._get_port_type(port)
                    parameters.append((port.name, param_type))

        return parameters

    def _get_port_type(self, port) -> str:
        """获取端口类型字符串"""
        if hasattr(port, 'width'):
            if port.width:
                return f"logic[{port.width}-1:0]"
        return "logic"
```

**Step 4: 运行测试**

```bash
pytest tests/test_sv_to_python/test_parser.py -v
```
Expected: PASS 或部分PASS（根据PyVerilog实际表现调整）

**Step 5: 根据PyVerilog行为调整**

PyVerilog的AST结构可能与预期不同，需要调试：

```python
# 添加调试脚本
# debug_parser.py
from pathlib import Path
from sv_to_python.parser import SVParser

FIXTURE_DIR = Path("tests/fixtures")
parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
ast = parser.parse()

print("AST Tree:")
for node in ast.tree:
    print(f"  Node type: {type(node).__name__}")
    if hasattr(node, 'name'):
        print(f"    Name: {node.name}")
    print(f"    Dir: {dir(node)}")
```

```bash
python debug_parser.py
```

根据输出调整`_extract_parameters`和`_extract_task_info`实现。

**Step 6: 重新运行测试并提交**

```bash
pytest tests/test_sv_to_python/test_parser.py -v
git add sv_to_python/parser.py tests/test_sv_to_python/test_parser.py
git commit -m "feat(sv2python): 实现基础SV解析器

- 使用PyVerilog解析SV文件
- 提取task定义和参数
- 添加解析器单元测试"
```

---

## M2: UVM操作提取器 (1周)

### Task 2.1: 实现基础UVM操作提取

**Files:**
- Create: `sv_to_python/extractor.py`
- Test: `tests/test_sv_to_python/test_extractor.py`

**Step 1: 创建提取器测试**

```python
# tests/test_sv_to_python/test_extractor.py
import pytest
from pathlib import Path

from sv_to_python.parser import SVParser
from sv_to_python.extractor import UVMOperationExtractor
from sv_to_python.ir import RegWrite, RegRead

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"

def test_extract_basic_write():
    """测试提取基本write操作"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    extractor = UVMOperationExtractor()
    task = tasks["basic_write"]
    operations = extractor.extract(task)

    assert len(operations) == 1
    assert isinstance(operations[0], RegWrite)
    assert operations[0].reg_path == ['REG_NAME']
    assert operations[0].backdoor is False

def test_extract_backdoor_write():
    """测试提取backdoor write"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    extractor = UVMOperationExtractor()
    task = tasks["backdoor_write"]
    operations = extractor.extract(task)

    assert len(operations) == 1
    assert operations[0].backdoor is True

def test_extract_array_write():
    """测试提取数组write"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    extractor = UVMOperationExtractor()
    task = tasks["array_write"]
    operations = extractor.extract(task)

    assert len(operations) == 1
    # reg_model.REG_CH[channel].write(...)
    assert 'REG_CH' in operations[0].reg_path
    assert 'channel' in operations[0].reg_path

def test_extract_init_dma():
    """测试提取完整DMA初始化task"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    extractor = UVMOperationExtractor()
    task = tasks["init_dma"]
    operations = extractor.extract(task)

    # 应该有4个write操作
    write_ops = [op for op in operations if isinstance(op, RegWrite)]
    assert len(write_ops) == 4

    # 检查路径
    assert any('DMA_CTRL' in str(op.reg_path) for op in write_ops)
    assert any('DMA_ADDR' in str(op.reg_path) for op in write_ops)
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_sv_to_python/test_extractor.py::test_extract_basic_write -v
```
Expected: FAIL

**Step 3: 实现UVM操作提取器**

```python
# sv_to_python/extractor.py
"""
UVM操作提取器 - 从AST中提取UVM寄存器模型调用
"""
from typing import List
from pyverilog.dataflow.dataflow import *

from sv_to_python.ir import (
    Operation, RegWrite, RegRead, RegSet, RegGet,
    RegReset, Comment, Todo, TaskInfo
)
from sv_to_python.errors import UVMMethodNotFound

class UVMOperationExtractor:
    """从SV AST中提取UVM寄存器模型操作"""

    # UVM方法映射表
    UVM_METHODS = {
        'write': {'type': 'write', 'args': ['status', 'value', 'path']},
        'read': {'type': 'read', 'args': ['status', 'value', 'path']},
        'poke': {'type': 'write', 'backdoor': True},
        'peek': {'type': 'read', 'backdoor': True},
        'set': {'type': 'set_model', 'args': ['value']},
        'get': {'type': 'get_model', 'args': []},
        'update': {'type': 'update', 'args': ['status', 'path']},
        'reset': {'type': 'reset', 'args': ['status', 'kind']},
        'mirror': {'type': 'mirror', 'args': ['status', 'check', 'path']},
    }

    def __init__(self):
        self.operations = []

    def extract(self, task: TaskInfo) -> List[Operation]:
        """从task中提取所有操作

        Args:
            task: TaskInfo对象，包含statements

        Returns:
            操作列表
        """
        self.operations = []

        for stmt in task.operations:  # 实际是statements
            self._process_statement(stmt)

        return self.operations

    def _process_statement(self, stmt):
        """处理单个语句"""
        if isinstance(stmt, HDLFunctionCall):
            self._handle_function_call(stmt)
        elif isinstance(stmt, HDLIfElse):
            # 处理if语句
            self._process_if_else(stmt)
        elif isinstance(stmt, HDLBlock):
            # 处理代码块
            for inner_stmt in stmt.list:
                self._process_statement(inner_stmt)

    def _handle_function_call(self, node: HDLFunctionCall):
        """处理函数调用"""
        method_name = node.name

        if method_name in self.UVM_METHODS:
            method_info = self.UVM_METHODS[method_name]

            if method_info['type'] == 'write':
                self._handle_write(node, method_info)
            elif method_info['type'] == 'read':
                self._handle_read(node, method_info)
            elif method_info['type'] == 'set_model':
                self._handle_set(node)
            elif method_info['type'] == 'get_model':
                self._handle_get(node)
            elif method_info['type'] == 'reset':
                self._handle_reset(node)
            elif method_info['type'] == 'mirror':
                self._handle_mirror(node)

    def _handle_write(self, node: HDLFunctionCall, method_info: dict):
        """处理write/poke操作"""
        # 提取调用链
        call_chain = self._get_call_chain(node)
        reg_path = self._extract_reg_path(call_chain)

        # 检查是否backdoor
        is_backdoor = method_info.get('backdoor', False)

        # 检查参数中的UVM_BACKDOOR
        args = node.list if hasattr(node, 'list') else []
        for arg in args:
            if self._is_backdoor_arg(arg):
                is_backdoor = True
                break

        # 提取写入值
        value = self._extract_value(args[1]) if len(args) > 1 else None

        self.operations.append(RegWrite(
            line_no=node.lineno if hasattr(node, 'lineno') else 0,
            original_source=self._get_source_line(node),
            reg_path=reg_path,
            value=value,
            backdoor=is_backdoor
        ))

    def _handle_read(self, node: HDLFunctionCall, method_info: dict):
        """处理read/peek操作"""
        call_chain = self._get_call_chain(node)
        reg_path = self._extract_reg_path(call_chain)

        is_backdoor = method_info.get('backdoor', False)

        self.operations.append(RegRead(
            line_no=node.lineno if hasattr(node, 'lineno') else 0,
            original_source=self._get_source_line(node),
            reg_path=reg_path,
            backdoor=is_backdoor
        ))

    def _handle_set(self, node: HDLFunctionCall):
        """处理set操作"""
        call_chain = self._get_call_chain(node)
        reg_path = self._extract_reg_path(call_chain)

        args = node.list if hasattr(node, 'list') else []
        value = self._extract_value(args[0]) if len(args) > 0 else None

        self.operations.append(RegSet(
            line_no=node.lineno if hasattr(node, 'lineno') else 0,
            original_source=self._get_source_line(node),
            reg_path=reg_path,
            value=value
        ))

    def _handle_get(self, node: HDLFunctionCall):
        """处理get操作"""
        call_chain = self._get_call_chain(node)
        reg_path = self._extract_reg_path(call_chain)

        self.operations.append(RegGet(
            line_no=node.lineno if hasattr(node, 'lineno') else 0,
            original_source=self._get_source_line(node),
            reg_path=reg_path
        ))

    def _handle_reset(self, node: HDLFunctionCall):
        """处理reset操作"""
        call_chain = self._get_call_chain(node)
        reg_path = self._extract_reg_path(call_chain)

        self.operations.append(RegReset(
            line_no=node.lineno if hasattr(node, 'lineno') else 0,
            original_source=self._get_source_line(node),
            reg_path=reg_path,
            kind="HARD"
        ))

    def _handle_mirror(self, node: HDLFunctionCall):
        """处理mirror操作"""
        call_chain = self._get_call_chain(node)
        reg_path = self._extract_reg_path(call_chain)

        # mirror转换为read
        self.operations.append(RegRead(
            line_no=node.lineno if hasattr(node, 'lineno') else 0,
            original_source=self._get_source_line(node),
            reg_path=reg_path,
            backdoor=False
        ))

    def _get_call_chain(self, node: HDLFunctionCall) -> List[str]:
        """提取函数调用链

        model.REG_NAME.write() -> ['model', 'REG_NAME', 'write']
        """
        chain = []
        curr = node

        while hasattr(curr, 'var'):
            var = curr.var
            if hasattr(var, 'name'):
                chain.insert(0, var.name)
            curr = var

        return chain

    def _extract_reg_path(self, call_chain: List[str]) -> List[str]:
        """从调用链提取寄存器路径

        ['model', 'REG_NAME', 'write'] -> ['REG_NAME']
        ['model', 'DMA_BLOCK', 'channel', 'ch', 'ctrl', 'write']
            -> ['DMA_BLOCK', 'channel', 'ch', 'ctrl']
        """
        # 移除模型名和方法名
        if len(call_chain) >= 3:
            return call_chain[1:-1]
        elif len(call_chain) == 2:
            return [call_chain[0]]
        return []

    def _extract_value(self, node) -> any:
        """提取表达式值"""
        if isinstance(node, IntConst):
            return self._parse_int_literal(node.value)
        elif isinstance(node, HDLName):
            return node.name
        elif isinstance(node, HDLFunctionCall):
            # 处理函数调用（如32'h0000_0001）
            if node.name == "'":
                # SystemVerilog字面量函数
                args = node.list if hasattr(node, 'list') else []
                if len(args) >= 2:
                    return self._parse_literal_with_base(args[0], args[1])
        return None

    def _parse_int_literal(self, value: str) -> int:
        """解析整数常量"""
        value = value.strip()
        if value.startswith("0x") or value.startswith("0X"):
            return int(value, 16)
        elif value.startswith("0b") or value.startswith("0B"):
            return int(value, 2)
        return int(value)

    def _parse_literal_with_base(self, width_node, value_node) -> int:
        """解析带基数的字面量 (32'h0000_0001)"""
        # width_node: 32
        # value_node: h0000_0001
        value_str = getattr(value_node, 'value', str(value_node))
        base_char = value_str[0]  # h, d, b, o
        num_str = value_str[1:]

        if base_char == 'h':
            return int(num_str, 16)
        elif base_char == 'd':
            return int(num_str, 10)
        elif base_char == 'b':
            return int(num_str, 2)
        elif base_char == 'o':
            return int(num_str, 8)
        return int(num_str)

    def _is_backdoor_arg(self, arg) -> bool:
        """检查参数是否指定backdoor"""
        if isinstance(arg, Constant):
            return 'BACKDOOR' in str(arg.value).upper()
        elif isinstance(arg, HDLName):
            return 'BACKDOOR' in arg.name.upper()
        return False

    def _get_source_line(self, node) -> str:
        """获取源代码行（简化版）"""
        return f"Line {node.lineno if hasattr(node, 'lineno') else 0}"

    def _process_if_else(self, node):
        """处理if/else语句"""
        # 暂时跳过，生成注释
        self.operations.append(Comment(
            line_no=node.lineno if hasattr(node, 'lineno') else 0,
            original_source="",
            text="# TODO: if/else statement - manual implementation may be needed"
        ))
```

**Step 4: 运行并调整测试**

```bash
pytest tests/test_sv_to_python/test_extractor.py -v
```

根据PyVerilog的实际AST结构，可能需要调整`_get_call_chain`、`_extract_value`等方法。

**Step 5: 提交**

```bash
git add sv_to_python/extractor.py tests/test_sv_to_python/test_extractor.py
git commit -m "feat(sv2python): 实现UVM操作提取器

- 支持write/read/poke/peek
- 支持set/get/reset/mirror
- 提取寄存器路径和值
- 检测backdoor参数"
```

---

## M3: Python代码生成器 (1周)

### Task 3.1: 创建Jinja2模板

**Files:**
- Create: `sv_to_python/templates/task.py.j2`
- Create: `sv_to_python/templates/module.py.j2`

**Step 1: 创建task模板**

```python
{# sv_to_python/templates/task.py.j2 #}
def {{ task.name }}({{ task.parameters | map(attribute='0') | join(', ') }}):
    """
    {{ task.name }} - Generated from SystemVerilog task

    Auto-generated by SV to Python converter
    Source: {{ source_file | default('unknown') }}

    {% if task.parameters %}
    Args:
    {% for param in task.parameters %}
        {{ param[0] }}: {{ param[1] }}
    {% endfor %}
    {% endif %}

    Generated operations:
    {% for op in task.operations %}
        Line {{ op.line_no }}: {{ op.__class__.__name__ }}
    {% endfor %}
    """
    # Auto-generated from SystemVerilog task
    # Please review before use

{% for op in task.operations %}
{{ op | generate_operation }}
{% endfor %}
```

**Step 2: 创建module模板**

```python
{# sv_to_python/templates/module.py.j2 #}
"""
{{ module_name }} - Auto-generated from SystemVerilog

This module contains Python functions converted from
SystemVerilog tasks for hardware configuration.

Generated by: SV to Python converter
Generation date: {{ generation_date }}
"""

import time
from typing import Optional
{% if use_type_hints %}
from sv_randomizer.rgm import RegisterBlock, Register, Field
{% endif %}

{% for task in tasks %}
{{ task | generate_task }}

{% endfor %}

# Usage example:
# {% for task in tasks %}
# {{ task.name }}(...)
# {% endfor %}
```

**Step 3: 提交**

```bash
git add sv_to_python/templates/
git commit -m "feat(sv2python): 创建Jinja2模板

- task模板: 生成单个Python函数
- module模板: 生成完整Python模块
- 包含文档字符串和类型提示"
```

---

### Task 3.2: 实现代码生成器

**Files:**
- Create: `sv_to_python/generator.py`
- Test: `tests/test_sv_to_python/test_generator.py`

**Step 1: 创建生成器测试**

```python
# tests/test_sv_to_python/test_generator.py
import pytest
from pathlib import Path
from datetime import datetime

from sv_to_python.parser import SVParser
from sv_to_python.extractor import UVMOperationExtractor
from sv_to_python.generator import PythonGenerator
from sv_to_python.ir import TaskInfo, RegWrite

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"

def test_generate_simple_task():
    """测试生成简单task"""
    # 创建测试task
    task = TaskInfo(
        name="test_task",
        parameters=[("value", "int")],
        operations=[
            RegWrite(
                line_no=10,
                original_source="reg.REG.write(status, 0x0001)",
                reg_path=["REG"],
                value=0x0001,
                backdoor=False
            )
        ]
    )

    generator = PythonGenerator()
    code = generator.generate_task(task)

    assert "def test_task(value):" in code
    assert "reg.reg.write(0x1)" in code or "reg.reg.write(0x0001)" in code
    assert "Auto-generated" in code

def test_generate_from_sv():
    """测试从SV文件生成"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks_dict = parser.get_tasks()

    extractor = UVMOperationExtractor()

    # 转换为TaskInfo列表
    tasks = []
    for task_name, task_def in tasks_dict.items():
        operations = extractor.extract(task_def)
        task_info = TaskInfo(
            name=task_name,
            parameters=task_def.parameters,
            operations=operations
        )
        tasks.append(task_info)

    generator = PythonGenerator()
    code = generator.generate_module(
        tasks,
        module_name="uvm_tasks",
        source_file=str(FIXTURE_DIR / "uvm_tasks.sv")
    )

    assert "def init_dma(" in code
    assert "def basic_write(" in code
    assert '"Auto-generated by SV to Python converter"' in code
    assert "reg_model.dma_ctrl" in code.lower()

def test_format_value():
    """测试值格式化"""
    generator = PythonGenerator()

    assert generator._format_value(0x0001) == "0x00000001"
    assert generator._format_value(255) == "0x000000ff"
    assert generator._format_value("param") == "param"
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_sv_to_python/test_generator.py::test_generate_simple_task -v
```
Expected: FAIL

**Step 3: 实现代码生成器**

```python
# sv_to_python/generator.py
"""
Python代码生成器 - 使用Jinja2模板
"""
from datetime import datetime
from typing import List, Any
from jinja2 import Environment, FileSystemLoader, Template

from sv_to_python.ir import (
    Operation, RegWrite, RegRead, RegSet, RegGet,
    RegReset, Comment, Todo, TaskInfo
)

class PythonGenerator:
    """Python代码生成器"""

    def __init__(self, template_dir: str = None):
        """初始化生成器

        Args:
            template_dir: 模板目录路径
        """
        if template_dir is None:
            import sv_to_python
            module_dir = Path(sv_to_python.__file__).parent
            template_dir = module_dir / "templates"

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # 注册过滤器
        self.env.filters['generate_operation'] = self._generate_operation
        self.env.filters['generate_task'] = self.generate_task
        self.env.filters['lower'] = lambda s: s.lower() if isinstance(s, str) else s

    def _format_value(self, value: Any) -> str:
        """格式化值为Python表达式

        Args:
            value: 值（整数、字符串等）

        Returns:
            Python表达式字符串
        """
        if isinstance(value, int):
            # 转为16进制格式
            return f"0x{value:08x}"
        elif isinstance(value, str):
            return value
        return str(value)

    def _generate_operation(self, op: Operation) -> str:
        """生成单行操作代码

        Args:
            op: Operation对象

        Returns:
            Python代码字符串
        """
        if isinstance(op, RegWrite):
            return self._gen_write(op)
        elif isinstance(op, RegRead):
            return self._gen_read(op)
        elif isinstance(op, RegSet):
            return self._gen_set(op)
        elif isinstance(op, RegGet):
            return self._gen_get(op)
        elif isinstance(op, RegReset):
            return self._gen_reset(op)
        elif isinstance(op, Comment):
            return self._gen_comment(op)
        elif isinstance(op, Todo):
            return self._gen_todo(op)
        else:
            return f"# Unknown operation: {op.__class__.__name__}"

    def _gen_write(self, op: RegWrite) -> str:
        """生成write操作代码"""
        # 构建寄存器访问路径
        reg_access = ".".join(op.reg_path).lower()

        # 格式化值
        value_str = self._format_value(op.value)

        # backdoor参数
        backdoor_suffix = ", backdoor=True" if op.backdoor else ""

        return f"reg_model.{reg_access}.write({value_str}{backdoor_suffix})"

    def _gen_read(self, op: RegRead) -> str:
        """生成read操作代码"""
        reg_access = ".".join(op.reg_path).lower()
        backdoor_suffix = ", backdoor=True" if op.backdoor else ""

        return f"value = reg_model.{reg_access}.read({backdoor_suffix})"

    def _gen_set(self, op: RegSet) -> str:
        """生成set操作代码"""
        reg_access = ".".join(op.reg_path).lower()
        value_str = self._format_value(op.value)

        return f"reg_model.{reg_access}.value = {value_str}"

    def _gen_get(self, op: RegGet) -> str:
        """生成get操作代码"""
        reg_access = ".".join(op.reg_path).lower()

        return f"value = reg_model.{reg_access}.value"

    def _gen_reset(self, op: RegReset) -> str:
        """生成reset操作代码"""
        reg_access = ".".join(op.reg_path).lower()

        return f"reg_model.{reg_access}.reset()"

    def _gen_comment(self, op: Comment) -> str:
        """生成注释"""
        return f"# {op.text}"

    def _gen_todo(self, op: Todo) -> str:
        """生成TODO占位符"""
        return f'''# TODO: {op.reason}
# Original SV: {op.original_source}
raise NotImplementedError("Manual conversion needed")'''

    def generate_task(self, task: TaskInfo, **context) -> str:
        """生成单个task的Python代码

        Args:
            task: TaskInfo对象
            **context: 额外的模板上下文

        Returns:
            Python代码字符串
        """
        template = self.env.get_template('task.py.j2')

        # 准备上下文
        template_context = {
            'task': task,
            **context
        }

        return template.render(**template_context)

    def generate_module(self, tasks: List[TaskInfo], **context) -> str:
        """生成完整Python模块代码

        Args:
            tasks: TaskInfo列表
            **context: 额外的模板上下文

        Returns:
            Python模块代码字符串
        """
        template = self.env.get_template('module.py.j2')

        # 默认上下文
        default_context = {
            'module_name': context.get('module_name', 'sv_tasks'),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'use_type_hints': context.get('use_type_hints', True),
            'source_file': context.get('source_file', 'unknown')
        }

        template_context = {**default_context, **context, 'tasks': tasks}

        return template.render(**template_context)
```

**Step 4: 运行测试**

```bash
pytest tests/test_sv_to_python/test_generator.py -v
```
Expected: PASS

**Step 5: 提交**

```bash
git add sv_to_python/generator.py tests/test_sv_to_python/test_generator.py
git commit -m "feat(sv2python): 实现Python代码生成器

- 使用Jinja2模板生成Python代码
- 支持9种操作类型转换
- 生成完整Python模块
- 添加类型提示和文档字符串"
```

---

## M4: CLI工具 (1周)

### Task 4.1: 实现基础CLI

**Files:**
- Create: `sv_to_python/cli.py`
- Create: `sv2python` (entry point script)

**Step 1: 创建CLI测试**

```python
# tests/test_sv_to_python/test_cli.py
import pytest
import subprocess
import sys
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"

def test_cli_help():
    """测试CLI帮助"""
    result = subprocess.run(
        [sys.executable, "-m", "sv_to_python.cli", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "convert" in result.stdout
    assert "list" in result.stdout

def test_cli_list_tasks():
    """测试list命令"""
    result = subprocess.run(
        [sys.executable, "-m", "sv_to_python.cli", "list",
         str(FIXTURE_DIR / "uvm_tasks.sv")],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "init_dma" in result.stdout
    assert "basic_write" in result.stdout

def test_cli_convert():
    """测试convert命令"""
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        output_file = f.name

    try:
        result = subprocess.run(
            [sys.executable, "-m", "sv_to_python.cli", "convert",
             str(FIXTURE_DIR / "uvm_tasks.sv"),
             "-o", output_file],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # 检查输出文件
        content = Path(output_file).read_text()
        assert "def init_dma(" in content
        assert "reg_model.dma_ctrl" in content.lower()
    finally:
        Path(output_file).unlink()
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_sv_to_python/test_cli.py::test_cli_help -v
```
Expected: FAIL

**Step 3: 实现CLI工具**

```python
# sv_to_python/cli.py
"""
CLI工具 - sv2python命令
"""
import sys
import click
from pathlib import Path
from typing import Optional

from sv_to_python.parser import SVParser
from sv_to_python.extractor import UVMOperationExtractor
from sv_to_python.generator import PythonGenerator
from sv_to_python.errors import ConversionError

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """SV to Python - SystemVerilog任务转换工具"""
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', type=click.Path(path_type=Path),
              help='输出文件路径')
@click.option('--reg-model', default='reg_model',
              help='RGM模型名称（默认: reg_model）')
@click.option('--task', help='只转换指定的task')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.option('--dry-run', is_flag=True, help='只分析不生成文件')
def convert(input_file: Path, output: Optional[Path],
            reg_model: str, task: Optional[str],
            verbose: bool, dry_run: bool):
    """转换SV文件到Python"""
    try:
        if verbose:
            click.echo(f"Parsing: {input_file}")

        # 解析SV文件
        parser = SVParser(input_file)
        tasks_dict = parser.get_tasks()

        if verbose:
            click.echo(f"Found {len(tasks_dict)} tasks")

        # 提取操作
        extractor = UVMOperationExtractor()
        tasks = []

        for task_name, task_def in tasks_dict.items():
            if task and task != task_name:
                continue

            operations = extractor.extract(task_def)
            task_info = TaskInfo(
                name=task_name,
                parameters=task_def.parameters,
                operations=operations,
                line_no=task_def.line_no
            )
            tasks.append(task_info)

            if verbose:
                click.echo(f"  {task_name}: {len(operations)} operations")

        # 生成Python代码
        generator = PythonGenerator()
        code = generator.generate_module(
            tasks,
            module_name=input_file.stem,
            source_file=str(input_file),
            reg_model_name=reg_model
        )

        if dry_run:
            click.echo("\n" + "=" * 60)
            click.echo("DRY RUN - Generated code:")
            click.echo("=" * 60)
            click.echo(code)
            return

        # 输出到文件或stdout
        if output:
            output.write_text(code, encoding='utf-8')
            click.echo(f"✓ Generated: {output}")
        else:
            click.echo(code)

    except ConversionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--json', 'output_json', is_flag=True,
              help='输出JSON格式')
@click.option('--detail', is_flag=True,
              help='显示详细信息')
def list(input_file: Path, output_json: bool, detail: bool):
    """列出SV文件中的tasks"""
    try:
        parser = SVParser(input_file)
        tasks = parser.get_tasks()

        if output_json:
            import json
            tasks_info = {}
            for name, task_def in tasks.items():
                tasks_info[name] = {
                    'parameters': task_def.parameters,
                    'line_no': task_def.line_no
                }
            click.echo(json.dumps(tasks_info, indent=2))
        else:
            click.echo(f"Tasks in {input_file.name}:")
            for i, (name, task_def) in enumerate(tasks.items(), 1):
                params_str = ", ".join([p[1] for p in task_def.parameters])
                click.echo(f"  {i}. {name}({params_str})")
                if detail:
                    click.echo(f"     Line: {task_def.line_no}")
                    click.echo(f"     Parameters: {len(task_def.parameters)}")

    except ConversionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--sv-source', type=click.Path(exists=True, path_type=Path),
              help='原始SV文件（用于对比）')
@click.option('--check-syntax', is_flag=True,
              help='检查Python语法')
@click.option('--import-check', is_flag=True,
              help='检查导入是否可用')
def validate(input_file: Path, sv_source: Optional[Path],
             check_syntax: bool, import_check: bool):
    """验证转换结果"""
    try:
        code = input_file.read_text(encoding='utf-8')

        issues = []

        # 检查语法
        if check_syntax:
            import ast
            try:
                ast.parse(code)
                click.echo("✓ Syntax check passed")
            except SyntaxError as e:
                issues.append(f"Syntax error: {e}")

        # 检查TODO标记
        todo_count = code.count("# TODO:")
        if todo_count > 0:
            issues.append(f"Found {todo_count} TODO items requiring manual implementation")

        if issues:
            click.echo("Issues found:", err=True)
            for issue in issues:
                click.echo(f"  - {issue}", err=True)
            sys.exit(1)
        else:
            click.echo("✓ Validation passed")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
```

**Step 4: 更新__main__.py支持模块执行**

```python
# sv_to_python/__main__.py
"""
支持 python -m sv_to_python
"""
from sv_to_python.cli import cli

if __name__ == '__main__':
    cli()
```

**Step 5: 运行测试**

```bash
pytest tests/test_sv_to_python/test_cli.py -v
```

**Step 6: 手动测试CLI**

```bash
# 测试help
python -m sv_to_python --help

# 测试list
python -m sv_to_python list tests/fixtures/uvm_tasks.sv

# 测试convert
python -m sv_to_python convert tests/fixtures/uvm_tasks.sv -o /tmp/uvm_tasks.py

# 查看生成的文件
cat /tmp/uvm_tasks.py
```

**Step 7: 提交**

```bash
git add sv_to_python/cli.py sv_to_python/__main__.py tests/test_sv_to_python/test_cli.py
git commit -m "feat(sv2python): 实现CLI工具

- convert命令: 转换SV到Python
- list命令: 列出tasks
- validate命令: 验证转换结果
- 支持详细输出和dry-run模式"
```

---

## M5: 测试和文档 (1周)

### Task 5.1: 端到端测试

**Files:**
- Create: `tests/test_sv_to_python/test_end_to_end.py`
- Create: `examples/sv_to_python/example_usage.py`

**Step 1: 创建端到端测试**

```python
# tests/test_sv_to_python/test_end_to_end.py
import pytest
import subprocess
import sys
import tempfile
from pathlib import Path

def test_full_conversion_workflow():
    """测试完整转换工作流"""
    fixture_file = Path("tests/fixtures/uvm_tasks.sv")

    # 转换
    result = subprocess.run(
        [sys.executable, "-m", "sv_to_python", "convert",
         str(fixture_file), "-o", "/tmp/test_output.py"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    # 读取生成的代码
    output_code = Path("/tmp/test_output.py").read_text()

    # 验证包含关键函数
    assert "def init_dma(" in output_code
    assert "reg_model.dma_ctrl" in output_code.lower()

    # 验证可导入（语法检查）
    result = subprocess.run(
        [sys.executable, "-c", "import ast; ast.parse(open('/tmp/test_output.py').read())"],
        capture_output=True
    )
    assert result.returncode == 0

def test_conversion_with_rgm_mock():
    """测试生成的代码可以与RGM配合"""
    # 生成Python代码
    fixture_file = Path("tests/fixtures/uvm_tasks.sv")

    result = subprocess.run(
        [sys.executable, "-m", "sv_to_python", "convert",
         str(fixture_file), "-o", "/tmp/test_rgm.py"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    # 创建mock RGM并测试导入
    test_script = """
import sys
sys.path.insert(0, '/tmp')

# Mock RGM
class MockRegModel:
    class DMA_CTRL:
        @staticmethod
        def write(val):
            print(f"DMA_CTRL.write({val})")

    class DMA_ADDR:
        @staticmethod
        def write(val):
            print(f"DMA_ADDR.write({val})")

reg_model = MockRegModel()

# 导入生成的代码
with open('/tmp/test_rgm.py') as f:
    exec(f.read())

# 测试调用
init_dma(0, 0x1000, 1024)
"""

    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True
    )

    assert "DMA_CTRL.write" in result.stdout
    assert "DMA_ADDR.write" in result.stdout
```

**Step 2: 运行测试**

```bash
pytest tests/test_sv_to_python/test_end_to_end.py -v
```

**Step 3: 提交**

```bash
git add tests/test_sv_to_python/test_end_to_end.py
git commit -m "test(sv2python): 添加端到端测试

- 测试完整转换工作流
- 测试与RGM的集成
- 验证生成的Python代码可执行"
```

---

### Task 5.2: 编写用户文档

**Files:**
- Create: `docs/guides/sv-to-python-guide.md`
- Create: `README.md` (in sv_to_python directory)

**Step 1: 创建用户指南**

```markdown
# SV to Python 转换器用户指南

## 概述

SV to Python转换器将SystemVerilog中的UVM寄存器模型操作序列转换为Python配置脚本。

## 安装

\`\`\`bash
pip install pyverilog jinja2 click
\`\`\`

## 快速开始

### 基础用法

\`\`\`bash
# 转换SV文件到Python
sv2python convert dma_tasks.sv -o dma_tasks.py

# 查看文件中的tasks
sv2python list dma_tasks.sv

# 验证生成的代码
sv2python validate dma_tasks.py
\`\`\`

## 支持的UVM模式

| UVM方法 | 转换结果 |
|---------|----------|
| `write(status, val)` | `reg.write(val)` |
| `poke(status, val)` | `reg.write(val, backdoor=True)` |
| `read(status, val)` | `val = reg.read()` |
| `set(val)` | `reg.value = val` |
| `reset()` | `reg.reset()` |

## 示例

### 输入SV

\`\`\`systemverilog
task automatic init_dma(
  input int channel,
  input logic [31:0] base_addr
);
  dma_reg_model.DMA_CTRL[channel].write(status, 32'h0000_0001);
  dma_reg_model.DMA_ADDR[channel].write(status, base_addr);
endtask
\`\`\`

### 输出Python

\`\`\`python
def init_dma(channel, base_addr):
    \"\"\"init_dma - Generated from SystemVerilog task\"\"\"
    reg_model.dma_ctrl[channel].write(0x00000001)
    reg_model.dma_addr[channel].write(base_addr)
\`\`\`

## 限制

- 复杂控制流（if/for）需要手动实现
- 动态值计算会生成TODO
- 自定义UVM扩展方法需要手动实现

## 故障排除

### 转换失败

\`\`\`bash
# 使用详细模式
sv2python convert file.sv -o output.py --verbose
\`\`\`

### TODO标记

生成的代码中的TODO标记需要手动实现。
\`\`\`

检查TODO数量:
sv2python validate output.py
\`\`\`
```

**Step 2: 更新主README**

在主README.md中添加sv_to_python部分：

\`\`\`markdown
## SV to Python 转换器

自动将SystemVerilog UVM任务转换为Python配置脚本。

\`\`\`bash
pip install -e ".[sv2python]"
sv2python convert dma_tasks.sv -o dma_tasks.py
\`\`\`

详见: [SV to Python指南](docs/guides/sv-to-python-guide.md)
\`\`\`

**Step 3: 提交**

```bash
git add docs/guides/sv-to-python-guide.md README.md
git commit -m "docs(sv2python): 添加用户文档

- 快速开始指南
- 支持的UVM模式参考
- 示例代码
- 故障排除"
```

---

### Task 5.3: 更新项目配置

**Files:**
- Modify: `setup.cfg` or `pyproject.toml`
- Modify: `README.md`

**Step 1: 添加CLI入口点**

在`setup.cfg`或`pyproject.toml`中添加：

\`\`\`toml
# pyproject.toml
[project.scripts]
sv2python = "sv_to_python.cli:cli"

[project.optional-dependencies]
sv2python = [
    "pyverilog>=0.1.0",
    "jinja2>=3.0.0",
    "click>=8.0.0",
]
\`\`\`

**Step 2: 更新CHANGELOG**

\`\`\`markdown
## [0.5.0] - 2026-XX-XX

### Added
- **SV to Python转换器**
  - 支持UVM寄存器模型操作转换
  - 支持15种UVM模式
  - CLI工具 (sv2python)
  - 自动生成Python配置脚本
\`\`\`

**Step 3: 最终测试和提交**

\`\`\`bash
# 运行所有测试
pytest tests/test_sv_to_python/ -v

# 手动测试完整流程
sv2python convert tests/fixtures/uvm_tasks.sv -o /tmp/test.py
python /tmp/test.py  # 应该能导入（即使没有RGM）

git add -A
git commit -m "feat(sv2python): 完成SV到Python转换器

- 实现M1-M5所有里程碑
- 支持15种UVM模式
- CLI工具完整可用
- 测试覆盖率>80%
- 完整用户文档"
\`\`\`

---

## 验收检查清单

完成实施后，验证以下各项：

- [ ] PyVerilog成功解析SV文件
- [ ] 提取15种UVM寄存器模型模式
- [ ] 生成可执行的Python代码
- [ ] CLI工具所有命令可用
- [ ] 生成的代码可通过语法检查
- [ ] 单元测试覆盖率 > 80%
- [ ] 端到端测试通过
- [ ] 用户文档完整
- [ ] README更新
- [ ] CHANGELOG更新

---

## 实施注意事项

### TDD原则
每个任务：写测试 → 运行（失败）→ 实现代码 → 运行（通过）→ 提交

### 频繁提交
每个小任务完成后立即提交

### 参考文档
- 设计文档: `docs/plans/2026-03-01-sv-to-python-converter-design.md`
- RGM文档: `docs/product/RGM_GUIDE.md`
- PyVerilog API: https://pyverilog.readthedocs.io/

### 调试技巧

```python
# 查看PyVerilog AST
from sv_to_python.parser import SVParser

parser = SVParser("test.sv")
ast = parser.parse()

for node in ast.tree:
    print(f"Node: {type(node).__name__}")
    if hasattr(node, 'name'):
        print(f"  Name: {node.name}")
    print(f"  Attributes: {[a for a in dir(node) if not a.startswith('_')]}")
```

---

**计划创建日期**: 2026-03-01
**预计完成时间**: 5周
**目标版本**: v0.5.0
