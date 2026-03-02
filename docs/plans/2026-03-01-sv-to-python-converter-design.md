# SystemVerilog到Python配置脚本转换器设计文档

**版本**: v0.5.0
**日期**: 2026-03-01
**状态**: 设计阶段

---

## 概述

构建一个工具，将SystemVerilog中的UVM寄存器模型操作序列转换为Python配置脚本。Python脚本使用EDA_UFVM的RGM（Register Model）系统，通过硬件适配器（SSH/AXI/APB）直接控制硬件。

**核心价值**：
- 自动化从SV验证环境到Python生产环境的迁移
- 保留硬件配置的业务逻辑
- 无需手动重写配置序列

---

## 第一部分：系统架构

### 1.1 整体架构

```
输入                    处理流程                      输出
─────────────────────────────────────────────────────────────
SV Task文件  ──►  解析器  ──►  AST  ──►  提取器  ──►  Python脚本
                       (PyVerilog)     (UVM操作)    (Jinja2)
                                         │
                                         ▼
                                   操作序列(IR)
                                   - write/read
                                   - set/get
                                   - reset
                                   - 随机化
```

### 1.2 核心组件

1. **SVParser** - SystemVerilog解析器
   - 使用PyVerilog解析SV文件
   - 生成抽象语法树(AST)

2. **UVMOperationExtractor** - UVM操作提取器
   - 支持15种UVM寄存器模型模式
   - 提取寄存器路径、值、操作类型

3. **PythonGenerator** - Python代码生成器
   - 使用Jinja2模板
   - 支持降级策略

4. **CLI** - 命令行工具
   - convert、list、validate命令

---

## 第二部分：中间表示(IR)

### 2.1 操作类型

```python
@dataclass
class Operation:
    """操作基类"""
    line_no: int
    original_source: str  # 原始SV代码

@dataclass
class RegWrite(Operation):
    """寄存器写入"""
    reg_path: List[str]   # ['DMA_BLOCK', 'channel', 'ch', 'ctrl']
    value: Any
    backdoor: bool = False

@dataclass
class RegRead(Operation):
    """寄存器读取"""
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
    constraints: List[str] = None

@dataclass
class Comment(Operation):
    """注释"""
    text: str

@dataclass
class Todo(Operation):
    """需要手动实现"""
    reason: str
    original_source: str
```

---

## 第三部分：支持的UVM模式

### 3.1 完整支持矩阵

| UVM方法 | 支持状态 | 转换方式 |
|---------|----------|----------|
| `write(status, val)` | ✅ | `reg.write(val)` |
| `write(status, val, BACKDOOR)` | ✅ | `reg.write(val, backdoor=True)` |
| `poke(status, val)` | ✅ | `reg.write(val, backdoor=True)` |
| `read(status, val)` | ✅ | `val = reg.read()` |
| `peek(status, val)` | ✅ | `val = reg.read(backdoor=True)` |
| `set(val)` | ✅ | `reg.value = val` |
| `get()` | ✅ | `val = reg.value` |
| `update()` | ⚠️ | `reg.write()` (需跟踪set值) |
| `reset()` | ✅ | `reg.reset()` |
| `randomize()` | ⚠️ | 使用Randomizable |
| 字段操作 | ✅ | `reg.field.write(val)` |
| 多维数组 | ✅ | `reg[a][b].write(val)` |
| 自定义扩展 | ❌ | 生成TODO注释 |

### 3.2 模式示例

#### 模式1: 基本FrontDoor写入
```systemverilog
reg_model.REG_NAME.write(status, value, UVM_FRONTDOOR);
```
```python
reg_model.reg_name.write(value)
```

#### 模式2: BackDoor写入
```systemverilog
reg_model.REG_NAME.write(status, value, UVM_BACKDOOR);
reg_model.REG_NAME.poke(status, value, "BITS");
```
```python
reg_model.reg_name.write(value, backdoor=True)
```

#### 模式3: 单索引数组
```systemverilog
reg_model.REG_CH[channel].write(status, value, path);
```
```python
reg_model.reg_ch[channel].write(value)
```

#### 模式4: 多维数组
```systemverilog
reg_model.BANK[ch][bank_id].write(status, value);
reg_model.dma_block.channel[ch].ctrl.write(status, val);
```
```python
reg_model.bank[ch][bank_id].write(value)
reg_model.dma_block.channel[ch].ctrl.write(val)
```

#### 模式5: 读取操作
```systemverilog
reg_model.REG_NAME.read(status, value, UVM_FRONTDOOR);
reg_model.REG_NAME.mirror(status, UVM_CHECK, UVM_FRONTDOOR);
```
```python
value = reg_model.reg_name.read()
reg_model.reg_name.mirror(check=True)
```

#### 模式6: Set/Get
```systemverilog
reg_model.REG_NAME.set(value);
value = reg_model.REG_NAME.get();
```
```python
reg_model.reg_name.value = value
value = reg_model.reg_name.value
```

#### 模式7: Update
```systemverilog
reg_model.REG_NAME.FIELD.set(field_value);
reg_model.REG_NAME.update(status);
```
```python
# 需要跟踪set值
reg_model.reg_name.write()  # 使用配置的值
```

#### 模式8: Reset
```systemverilog
reg_model.REG_NAME.reset(status);
```
```python
reg_model.reg_name.reset()
```

#### 模式9: 随机化
```systemverilog
reg_model.REG_NAME.randomize();
```
```python
from sv_randomizer import Randomizable, rand

class RandomizedReg(Randomizable):
    value: rand[int](bits=32)

rand_obj = RandomizedReg()
rand_obj.randomize()
reg_model.reg_name.write(rand_obj.value)
```

#### 模式10: 字段操作
```systemverilog
reg_model.REG_NAME.FIELD.write(status, field_value);
```
```python
# 使用RGM Field API
reg_model.reg_name.field.write(field_value)
```

---

## 第四部分：核心组件设计

### 4.1 UVM操作提取器

```python
class UVMOperationExtractor(ASTVisitor):
    """UVM寄存器模型操作提取器"""

    UVM_METHODS = {
        'write': {'type': 'write', 'args': ['status', 'value', 'path']},
        'read': {'type': 'read', 'args': ['status', 'value', 'path']},
        'poke': {'type': 'write', 'backdoor': True},
        'peek': {'type': 'read', 'backdoor': True},
        'set': {'type': 'set_model', 'args': ['value']},
        'get': {'type': 'get_model', 'args': []},
        'update': {'type': 'update', 'args': ['status', 'path']},
        'reset': {'type': 'reset', 'args': ['status', 'kind']},
        'randomize': {'type': 'randomize', 'args': ['status']},
    }

    def visit_FunctionCall(self, node):
        """处理UVM方法调用"""
        method_name = node.name

        if method_name in self.UVM_METHODS:
            self._dispatch_method(node, method_name)

    def _extract_reg_path(self, call_chain: List[str]) -> List[str]:
        """提取寄存器路径"""
        # ['dma_reg_model', 'DMA_BLOCK', 'channel', 'ch', 'ctrl', 'write']
        # -> ['DMA_BLOCK', 'channel', 'ch', 'ctrl']
        return call_chain[1:-1]
```

### 4.2 Python代码生成器

```python
class PythonGenerator:
    """Python代码生成器"""

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader('templates')
        )

    def generate_task(self, task_info: TaskInfo) -> str:
        """生成Python函数"""
        template = self.env.get_template('task.py.j2')
        return template.render(task=task_info)

    def generate_operation(self, op: Operation) -> str:
        """生成单行操作代码"""
        if isinstance(op, RegWrite):
            return self._gen_write(op)
        elif isinstance(op, RegRead):
            return self._gen_read(op)
        # ... 其他操作类型
```

### 4.3 Jinja2模板

```python
# templates/task.py.j2
def {{ task.name }}({{ task.params | join(', ') }}):
    """
    {{ task.name }} - Generated from SystemVerilog task

    Auto-generated by SV to Python converter
    """
{% for op in task.operations %}
{{ op | generate_operation }}
{% endfor %}
```

---

## 第五部分：CLI工具

### 5.1 命令结构

```bash
sv2python <command> [options] <input>

命令:
  convert    转换SV文件到Python
  list       列出文件中的tasks
  validate   验证转换结果
  config     管理配置文件
```

### 5.2 使用示例

```bash
# 基础转换
sv2python convert dma_tasks.sv -o dma_tasks.py

# 指定RGM模型名称
sv2python convert dma_tasks.sv -o dma_tasks.py --reg-model dma_block

# 只转换特定task
sv2python convert dma_tasks.sv -o init_dma.py --task init_dma

# 列出tasks
sv2python list dma_tasks.sv

# 详细模式
sv2python convert dma_tasks.sv -o dma_tasks.py --verbose --report report.txt
```

---

## 第六部分：错误处理

### 6.1 错误类型

```python
class ConversionError(Exception):
    """转换错误基类"""

class ParseError(ConversionError):
    """SV解析错误"""

class UnsupportedConstruct(ConversionError):
    """不支持的SV构造"""

class AmbiguousValue(ConversionError):
    """值无法确定"""
```

### 6.2 降级策略

遇到无法转换的代码时：

```python
# 生成TODO注释
# TODO: Manual implementation required
# Reason: {reason}
# Original SV at line {line_no}
# {original_source}
raise NotImplementedError("Manual conversion needed")
```

### 6.3 转换报告

```python
@dataclass
class ConversionReport:
    total_tasks: int
    successful: int
    with_warnings: int
    failed: List[str]
    unsupported: List[Tuple[str, str]]

    def print_summary(self):
        """打印摘要"""
        print(f"\n=== Conversion Summary ===")
        print(f"Total: {self.total_tasks}")
        print(f"✓ Successful: {self.successful}")
        print(f"⚠ Warnings: {self.with_warnings}")
        print(f"✗ Failed: {len(self.failed)}")
```

---

## 第七部分：实施里程碑

| 里程碑 | 内容 | 时间 |
|--------|------|------|
| M1 | SV解析器 + 基础操作提取 | 1周 |
| M2 | 15种UVM模式识别 | 1周 |
| M3 | Python生成器 + 模板 | 1周 |
| M4 | CLI工具 + 配置 | 1周 |
| M5 | 测试 + 文档 | 1周 |

**总计**: 5周

---

## 第八部分：验收标准

- [ ] 支持15种UVM寄存器模型模式
- [ ] 转换准确率 > 95%
- [ ] 生成的Python代码可执行
- [ ] CLI工具完整可用
- [ ] 测试覆盖率 > 80%
- [ ] 完整文档和示例

---

## 附录

### A. 完整示例

**输入SV**:
```systemverilog
task automatic init_dma(
  input int channel,
  input logic [31:0] base_addr,
  input int length
);
  // Enable DMA channel
  dma_reg_model.DMA_CTRL[channel].write(
    status, 32'h0000_0001, UVM_FRONTDOOR
  );

  // Set address and length
  dma_reg_model.DMA_ADDR[channel].write(status, base_addr);
  dma_reg_model.DMA_LEN[channel].write(status, length);

  // Start transfer
  dma_reg_model.DMA_CMD[channel].write(status, 32'h0000_0001);
endtask
```

**输出Python**:
```python
def init_dma(channel, base_addr, length):
    """
    init_dma - Generated from SystemVerilog task

    Auto-generated by SV to Python converter
    """
    # Enable DMA channel
    reg_model.dma_ctrl[channel].write(0x00000001)

    # Set address and length
    reg_model.dma_addr[channel].write(base_addr)
    reg_model.dma_len[channel].write(length)

    # Start transfer
    reg_model.dma_cmd[channel].write(0x00000001)
```

### B. 依赖

- PyVerilog: SV解析
- Jinja2: 代码生成
- Click: CLI框架

### C. 参考资料

- UVM用户指南
- SystemVerilog LRM
- EDA_UFVM RGM文档
