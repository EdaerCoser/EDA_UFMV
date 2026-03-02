# RGM 寄存器模型用户指南

**版本**: v0.3.0
**最后更新**: 2026年3月1日

---

## 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [核心概念](#核心概念)
4. [字段访问类型](#字段访问类型)
5. [UVM风格接口](#uvm风格接口)
6. [硬件适配器](#硬件适配器)
7. [代码生成](#代码生成)
8. [高级特性](#高级特性)
9. [最佳实践](#最佳实践)
10. [API参考](#api参考)

---

## 概述

EDA_UFVM RGM (Register Model) 是一个类似UVM寄存器模型的Python实现，用于FPGA原型验证和硬件仿真。它提供了：

- **层次化寄存器建模** - Field → Register → RegisterBlock
- **多种访问类型** - 支持15种AccessType（RW, RO, WO, W1C, W1S等）
- **UVM兼容接口** - set/get/update/mirror/poke/peek
- **硬件适配** - AXI、APB、UART、SSH等硬件接口
- **代码生成** - 自动生成Verilog RTL、C头文件、Python模型

### 设计原则

1. **UVM兼容** - 接口设计与UVM RGM保持一致
2. **灵活性** - 支持多种硬件接口和访问方式
3. **易用性** - 清洁的API，丰富的文档
4. **可扩展** - 工厂模式支持自定义适配器和生成器

---

## 快速开始

### 安装

```bash
pip install eda-ufmv
```

### 基本用法

```python
from rgm import Field, Register, RegisterBlock, AccessType

# 1. 创建寄存器块
block = RegisterBlock("UART", base_address=0x40000000)

# 2. 创建寄存器
ctrl = Register("CTRL", offset=0x00, width=32, reset_value=0x00000000)

# 3. 添加字段
ctrl.add_field(Field("enable", 0, 1, AccessType.RW, 0))
ctrl.add_field(Field("mode", 1, 3, AccessType.RW, 0))
ctrl.add_field(Field("reserved", 4, 28, AccessType.RO, 0))

# 4. 将寄存器添加到块
block.add_register(ctrl)

# 5. 读写操作
block.write_field("CTRL", "enable", 1)
enable = block.read_field("CTRL", "enable")
```

### 生成代码

```python
from rgm.generators import GeneratorFactory

# 生成Verilog RTL
verilog_code = GeneratorFactory.generate("verilog", block)
with open("uart_regs.v", "w") as f:
    f.write(verilog_code)

# 生成C头文件
c_header = GeneratorFactory.generate("c", block)
with open("uart_regs.h", "w") as f:
    f.write(c_header)
```

---

## 核心概念

### Field（字段）

字段是寄存器的最小组成单位，表示寄存器中的连续位。

```python
field = Field(
    name="data",           # 字段名称
    bit_offset=8,          # 起始位位置
    bit_width=8,           # 位宽
    access=AccessType.RW,  # 访问类型
    reset_value=0x00,      # 复位值
    volatile=False,        # 是否易失
    description="Data register field"
)
```

### Register（寄存器）

寄存器包含多个字段，具有统一的地址和宽度。

```python
reg = Register(
    name="STATUS",
    offset=0x04,           # 寄存器偏移地址
    width=32,              # 寄存器位宽
    reset_value=0x00000001 # 复位值
)

# 添加字段
reg.add_field(Field("tx_empty", 0, 1, AccessType.RO, 1))
reg.add_field(Field("rx_full", 1, 1, AccessType.RO, 0))

# 读写寄存器
reg.write(0xFFFFFFFF)
value = reg.read()

# 读写字段
reg.write_field("tx_empty", 1)
tx_empty = reg.read_field("tx_empty")
```

### RegisterBlock（寄存器块）

寄存器块包含多个寄存器，支持层次化组织。

```python
block = RegisterBlock("UART", base_address=0x40000000)

# 添加寄存器
block.add_register(ctrl)
block.add_register(status)

# 通过名称访问寄存器
ctrl_reg = block.get_register("CTRL")

# 读写寄存器
block.write("CTRL", 0x12345678)
value = block.read("CTRL")

# 读写字段
block.write_field("CTRL", "enable", 1)
enable = block.read_field("CTRL", "enable")
```

### 层次化组织

寄存器块可以嵌套，形成层次化结构。

```python
# 顶层块
system = RegisterBlock("SYSTEM", 0x40000000)

# 子块
uart0 = RegisterBlock("UART0", 0x40001000)
uart1 = RegisterBlock("UART1", 0x40002000)

# 添加子块
system.add_block(uart0)
system.add_block(uart1)

# 通过层次化路径访问
uart0_ctrl = system.get_register("UART0.CTRL")
```

---

## 字段访问类型

RGM支持15种字段访问类型：

### 基本类型

| 类型 | 名称 | 读行为 | 写行为 |
|:---|:---|:---|:---|
| **RW** | Read-Write | 返回当前值 | 更新字段 |
| **RO** | Read-Only | 返回当前值 | 忽略写入 |
| **WO** | Write-Only | 返回0 | 更新字段 |

### 写操作类型

| 类型 | 名称 | 行为 |
|:---|:---|:---|
| **W1C** | Write-1-to-Clear | 写1清除对应位，写0保持 |
| **W1S** | Write-1-to-Set | 写1设置对应位，写0保持 |
| **W0C** | Write-0-to-Clear | 写0清除对应位，写1保持 |
| **W0S** | Write-0-to-Set | 写0设置对应位，写1保持 |
| **WC** | Write-Clear | 任何写入都清零 |
| **WS** | Write-Set | 任何写入都置为全1 |

### 读操作类型

| 类型 | 名称 | 行为 |
|:---|:---|:---|
| **RC** | Read-to-Clear | 读取后清零 |
| **RS** | Read-to-Set | 读取后置为全1 |

### 示例

```python
# W1C: 写1清除（中断标志）
flag = Field("interrupt", 0, 1, AccessType.W1C, 0)
flag.write(1)  # 清除为0
flag.write(0)  # 保持不变

# W1S: 写1设置（状态位）
status = Field("done", 0, 1, AccessType.W1S, 0)
status.write(1)  # 设置为1
status.write(0)  # 保持不变

# RC: 读清除（硬件状态）
hw_flag = Field("hw_flag", 0, 1, AccessType.RC, 1)
value = hw_flag.read()  # 返回1，然后清零
next_value = hw_flag.read()  # 返回0
```

---

## UVM风格接口

RGM提供了与UVM兼容的接口方法。

### 镜像值管理

UVM RGM维护三个值：

- **_mirrored_value** - 镜像值（期望值）
- **_actual_value** - 实际硬件值
- **_desired_value** - 期望写入值

### set() - 设置期望值

```python
reg = Register("CTRL", 0x00, 32)
reg.set(0x12345678)  # 设置期望值
# 注意：set()不立即写入硬件
```

### get() - 获取镜像值

```python
mirror_value = reg.get()  # 获取镜像值
```

### update() - 批量写入

```python
reg.set(0xAAAA)  # 设置期望值
reg.set(0xBBBB)  # 再次设置
reg.update()     # 批量写入硬件（最后一次值）
```

### mirror() - 同步硬件值

```python
# 从硬件读取并同步到镜像
value = reg.mirror(check=True)  # 读取并检查是否匹配
```

### poke() - 后门强制写入

```python
# 强制写入，忽略访问权限
reg.poke(0xFFFFFFFF)
```

### peek() - 后门直接读取

```python
# 直接读取硬件值
value = reg.peek()
```

### 完整示例

```python
from rgm import Register, Field, AccessType

reg = Register("CTRL", 0x00, 32)
reg.add_field(Field("enable", 0, 1, AccessType.RO, 0))

# 设置期望值
reg.set(0x01)
assert reg.get() == 0x01

# 尝试更新（RO字段不会更新）
reg.update()
assert reg.read() == 0x00  # 硬件值未改变

# 强制写入（忽略RO权限）
reg.poke(0xFF)
assert reg.peek() == 0xFF
```

---

## 硬件适配器

RGM提供多种硬件适配器，用于访问真实硬件。

### FrontDoor vs BackDoor

- **FrontDoor** - 通过总线协议访问（AXI、APB等）
- **BackDoor** - 直接内存访问（仿真调试）

### AXI适配器

```python
from rgm.adapters import AXIAdapter
from rgm.access import FrontDoorAccess

# 创建AXI适配器
axi = AXIAdapter(base_address=0x40000000)

# 注入硬件驱动（由测试框架提供）
axi.set_driver(my_axi_driver)

# 创建FrontDoor访问
frontdoor = FrontDoorAccess(axi)

# 设置到寄存器块
block.set_access_interface(frontdoor)

# 现在所有读写都通过AXI总线
block.write("CTRL", 0x12345678)
```

### APB适配器

```python
from rgm.adapters import APBAdapter

apb = APBAdapter(base_address=0x40000000)
apb.set_driver(my_apb_driver)
```

### UART适配器

```python
from rgm.adapters import UARTAdapter

uart = UARTAdapter(port="/dev/ttyUSB0", baudrate=115200)
uart.connect()

# 通过UART访问
value = uart.read(0x40000000)
uart.write(0x40000000, 0x1234)
```

### SSH适配器（远程单板）

```python
from rgm.adapters import SSHAdapter

# 创建SSH连接
ssh = SSHAdapter(
    host="192.168.1.100",
    username="fpga",
    password="boardpass",
    read_command="devmem 0x{address}",
    write_command="devmem 0x{address} 32 0x{value}"
)

# 使用上下文管理器
with ssh:
    # 读取远程单板寄存器
    value = ssh.read(0x40000000)

    # 写入远程单板寄存器
    ssh.write(0x40000000, 0x12345678)

# 查看统计信息
stats = ssh.get_statistics()
print(f"Reads: {stats['read_count']}, Writes: {stats['write_count']}")
```

### 自定义适配器

```python
from rgm.adapters import HardwareAdapter

class MyAdapter(HardwareAdapter):
    def read(self, address: int) -> int:
        # 实现读取逻辑
        return my_hardware_read(address)

    def write(self, address: int, value: int) -> None:
        # 实现写入逻辑
        my_hardware_write(address, value)

    def is_connected(self) -> bool:
        return True
```

---

## 代码生成

RGM可以从寄存器模型自动生成代码。

### Verilog RTL生成

```python
from rgm.generators import VerilogGenerator

gen = VerilogGenerator(
    include_reset=True,      # 包含复位逻辑
    use_always_block=True    # 使用always块
)

verilog_code = gen.generate(block)

# 保存到文件
with open("uart_regs.v", "w") as f:
    f.write(verilog_code)
```

生成的Verilog代码包含：
- 模块声明和参数
- 寄存器声明
- 写和复位逻辑（always @posedge）
- 读逻辑（combinational）
- 地址映射注释

### C头文件生成

```python
from rgm.generators import CHeaderGenerator

gen = CHeaderGenerator(
    include_guard=True,      # 包含头文件保护
    include_typedef=True     # 包含typedef定义
)

c_header = gen.generate(block)

# 保存到文件
with open("uart_regs.h", "w") as f:
    f.write(c_header)
```

生成的C头文件包含：
- 基地址和寄存器偏移宏定义
- 字段位掩码和位置宏定义
- Typedef联合体
- 内联读写函数

### Python模型生成

```python
from rgm.generators import PythonGenerator

gen = PythonGenerator(
    include_docstrings=True,   # 包含文档字符串
    include_type_hints=True    # 包含类型提示
)

python_code = gen.generate(block)

# 保存到文件
with open("uart_model.py", "w") as f:
    f.write(python_code)
```

生成的Python代码包含：
- RegisterBlock子类
- 寄存器和字段创建
- 访问方法（read_CTRL, write_CTRL等）

### 工厂模式

```python
from rgm.generators import GeneratorFactory

# 直接生成代码
verilog = GeneratorFactory.generate("verilog", block)
c_header = GeneratorFactory.generate("c", block)
python = GeneratorFactory.generate("python", block)

# 列出所有可用生成器
generators = GeneratorFactory.list_generators()
print(generators)  # ['verilog', 'v', 'c', 'h', 'python', 'py']

# 获取文件扩展名
ext = GeneratorFactory.get_file_extension("verilog")
print(ext)  # '.v'
```

---

## 高级特性

### 地址映射

```python
from rgm import RegisterMap

# 创建地址映射
map = RegisterMap("UART_map", base_address=0x40000000)

# 添加寄存器到映射
map.add_reg(ctrl, offset=0x00)
map.add_reg(status, offset=0x04)

# 通过偏移获取寄存器
reg = map.get_reg_by_offset(0x00)

# 获取物理地址
phys_addr = map.get_phys_address(0x00)  # 0x40000000
```

### 访问接口切换

```python
# 使用FrontDoor（总线访问）
block.set_access_interface(frontdoor)
block.write("CTRL", 0x1234)  # 通过总线写入

# 切换到BackDoor（直接访问）
block.set_backdoor(backdoor)
block.write("CTRL", 0x5678)  # 直接内存写入
```

### UVM风格复位

```python
# SOFT复位：仅复位镜像值
block.reset(kind="SOFT")

# HARD复位：复位硬件
block.reset(kind="HARD")
```

### 字段重叠检测

```python
reg = Register("TEST", 0x00, 32)

# 添加重叠字段会引发错误
reg.add_field(Field("field1", 0, 8, AccessType.RW, 0))
reg.add_field(Field("field2", 4, 8, AccessType.RW, 0))  # 错误！
```

### 地址冲突检测

```python
block = RegisterBlock("UART", 0x40000000)

# 添加冲突地址会引发错误
block.add_register(Register("R1", 0x00, 32))
block.add_register(Register("R2", 0x00, 32))  # 错误！
```

---

## 最佳实践

### 1. 使用层次化组织

```python
# 推荐：层次化结构
system = RegisterBlock("SYSTEM", 0x40000000)
uart0 = RegisterBlock("UART0", 0x40001000)
uart1 = RegisterBlock("UART1", 0x40002000)

# 避免：平面结构
```

### 2. 选择合适的访问类型

```python
# 控制位：RW
Field("enable", 0, 1, AccessType.RW, 0)

# 状态位：RO
Field("busy", 1, 1, AccessType.RO, 0)

# 中断标志：W1C
Field("int_flag", 2, 1, AccessType.W1C, 0)

# 硬件状态：RC
Field("hw_status", 3, 1, AccessType.RC, 0)
```

### 3. 使用UVM风格接口进行批量操作

```python
# 推荐：批量设置后更新
reg.set(0x1111)
reg.set(0x2222)
reg.set(0x3333)
reg.update()  # 只写入一次

# 避免：多次单独写入
reg.write(0x1111)
reg.write(0x2222)
reg.write(0x3333)  # 写入三次
```

### 4. 为字段添加描述

```python
field = Field(
    name="mode",
    bit_offset=4,
    bit_width=3,
    access=AccessType.RW,
    reset_value=0,
    description="UART operation mode: 0=normal, 1=loopback, 2=echo"
)
```

### 5. 使用上下文管理器管理连接

```python
# 推荐：自动管理连接
with SSHAdapter(host="board", username="user") as ssh:
    ssh.write(0x1000, 0x1234)

# 避免：手动管理连接
ssh = SSHAdapter(host="board", username="user")
ssh.connect()
try:
    ssh.write(0x1000, 0x1234)
finally:
    ssh.disconnect()
```

### 6. 代码生成时使用有意义的名称

```python
# 推荐：清晰的命名
block = RegisterBlock("UART", 0x40000000)
reg = Register("CTRL", 0x00, 32)
field = Field("enable", 0, 1, AccessType.RW, 0)

# 避免：缩写和不清晰命名
```

---

## API参考

### Field类

```python
class Field:
    def __init__(
        self,
        name: str,
        bit_offset: int,
        bit_width: int,
        access: AccessType = AccessType.RW,
        reset_value: int = 0,
        volatile: bool = False,
        description: str = ""
    )

    def read(self) -> int
    def write(self, value: int) -> None
    def reset(self) -> None
    def get_mask(self) -> int

    # UVM风格接口
    def set(self, value: int) -> None
    def get(self) -> int
    def peek(self) -> int
    def poke(self, value: int) -> None
```

### Register类

```python
class Register:
    def __init__(
        self,
        name: str,
        offset: int,
        width: int = 32,
        reset_value: int = 0
    )

    def add_field(self, field: Field) -> None
    def get_field(self, name: str) -> Optional[Field]
    def get_fields(self) -> List[Field]

    def read(self) -> int
    def write(self, value: int) -> None
    def reset(self) -> None

    def read_field(self, field_name: str) -> int
    def write_field(self, field_name: str, value: int) -> None

    # UVM风格接口
    def set(self, value: int) -> None
    def get(self) -> int
    def update(self, field: str = None) -> None
    def mirror(self, check: bool = True) -> int
    def poke(self, value: int) -> None
    def peek(self) -> int

    def get_address(self) -> int
    def set_access_interface(self, interface) -> None
```

### RegisterBlock类

```python
class RegisterBlock:
    def __init__(
        self,
        name: str,
        base_address: int = 0
    )

    def add_register(self, register: Register) -> None
    def add_block(self, block: 'RegisterBlock') -> None

    def get_register(self, path: str) -> Optional[Register]
    def get_registers(self) -> List[Register]
    def get_block(self, name: str) -> Optional['RegisterBlock']
    def get_blocks(self) -> List['RegisterBlock']

    def write(self, reg_name: str, value: int) -> None
    def read(self, reg_name: str) -> int
    def write_field(self, reg_name: str, field_name: str, value: int) -> None
    def read_field(self, reg_name: str, field_name: str) -> int

    def reset(self, kind: str = "SOFT") -> None

    def set_access_interface(self, interface) -> None
    def set_frontdoor(self, frontdoor) -> None
    def set_backdoor(self, backdoor) -> None
```

---

## 示例代码

完整示例请参考：
- `examples/rgm/basic_rgm_example.py` - 基础用法
- `examples/rgm/code_generator_example.py` - 代码生成
- `examples/rgm/ssh_access_example.py` - SSH远程访问

---

## 相关文档

- [ROADMAP.md](../development/ROADMAP.md) - 开发路线图
- [ARCHITECTURE.md](../development/ARCHITECTURE.md) - 架构设计
- [CLAUDE.md](../../CLAUDE.md) - 项目概览

---

**文档维护**: EDA_UFVM开发团队
**最后更新**: 2026年3月1日
