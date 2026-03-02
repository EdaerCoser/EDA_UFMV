# 随机化系统使用指南

**版本**: v0.3.1
**更新日期**: 2026年3月1日

---

## 概述

EDA_UFVM的随机化系统提供SystemVerilog风格的约束随机化功能，支持：
- rand/randc随机变量（使用Python类型注解）
- 原生Python表达式约束
- 双求解器架构（PurePython/Z3）
- 完善的种子管理

---

## 核心概念

### Randomizable类

所有可随机化类的基类，提供：
- 随机变量管理
- 约束求解
- 生命周期回调（pre_randomize/post_randomize）

### 求解器架构

| 求解器 | 特点 | 适用场景 |
|:---|:---|:---|
| **PurePython** | 零依赖，速度快 | 简单约束 (<10变量) |
| **Z3 SMT** | 工业级，可满足性强 | 复杂约束 (>10变量) |

---

## 快速开始

### 基础示例

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand

# 定义类型注解
src_addr_rand = rand(int)(bits=16, min=0, max=65535)
dest_addr_rand = rand(int)(bits=16, min=0, max=65535)

class Packet(Randomizable):
    # 使用类型注解定义变量
    src_addr: src_addr_rand
    dest_addr: dest_addr_rand

pkt = Packet()
for i in range(5):
    pkt.randomize()
    print(f"src=0x{pkt.src_addr:04x}, dst=0x{pkt.dest_addr:04x}")
```

### 使用约束

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint

# 定义类型注解
src_addr_rand = rand(int)(bits=16, min=0, max=65535)
dest_addr_rand = rand(int)(bits=16, min=0, max=65535)

class ConstrainedPacket(Randomizable):
    # 变量定义
    src_addr: src_addr_rand
    dest_addr: dest_addr_rand

    # 使用原生Python表达式定义约束
    @constraint
    def valid_addr(self):
        return self.src_addr >= 0x1000 and self.src_addr != self.dest_addr

pkt = ConstrainedPacket()
pkt.randomize()
```

---

## API参考

### 类型注解

#### rand(typ)

创建标准随机变量类型注解。

**参数**:
- `typ` (type): 变量类型
- `bits` (int): 位宽
- `min` (int): 最小值（可选）
- `max` (int): 最大值（可选）

**示例**:
```python
# 创建类型注解
data_rand = rand(int)(bits=32)

class MyClass(Randomizable):
    data: data_rand
```

**枚举类型**:
```python
opcode_rand = rand(str)(enum_values=['READ', 'WRITE', 'IDLE'])

class MyClass(Randomizable):
    opcode: opcode_rand
```

#### randc(typ)

创建循环随机变量类型注解，遍历所有可能值后才重复。

**参数**:
- `typ` (type): 变量类型
- `bits` (int): 位宽
- `min` (int): 最小值（可选）
- `max` (int): 最大值（可选）

**示例**:
```python
# 创建randc类型注解
packet_id_randc = randc(int)(bits=4)

class MyClass(Randomizable):
    packet_id: packet_id_randc
```

### 约束装饰器

#### @constraint

定义约束，使用原生Python表达式。

**特点**:
- 无需字符串表达式
- 支持Python原生语法
- 自动类型检查和IDE支持

**支持的运算符**:
- 关系: `==`, `!=`, `<`, `>`, `<=`, `>=`
- 逻辑: `and`, `or`, `not`
- 算术: `+`, `-`, `*`, `/`, `%`
- 位运算: `&`, `|`, `^`, `~`, `<<`, `>>`
- 链式比较: `0 <= x <= 100`

**示例**:
```python
@constraint
def addr_aligned(self):
    return self.addr % 4 == 0

@constraint
def range_check(self):
    return (0 <= self.value <= 100) or (200 <= self.value <= 300)
```

### DSL便捷函数

#### inside()

范围约束函数。

```python
from sv_randomizer.api import inside

@constraint
def value_in_ranges(self):
    return inside([(0, 100), (200, 300)]) == self.value
```

#### dist()

权重分布约束函数。

```python
from sv_randomizer.api import dist

@constraint
def weighted_distribution(self):
    return dist([(0, 100, 70), (100, 200, 30)]) == self.value
# 70%概率在0-100，30%概率在100-200
```

### Randomizable类方法

#### __init__(self, solver_backend=None)

初始化随机化对象。

**参数**:
- `solver_backend` (str, optional): 求解器后端 (`"pure_python"` 或 `"z3"`)

#### randomize(self)

执行随机化。

**返回**:
- `bool`: 成功返回True，失败返回False

#### pre_randomize(self)

随机化前回调，可被子类重写。

#### post_randomize(self)

随机化后回调，可被子类重写。

---

## 约束系统详解

### 关系运算

```python
@constraint
def gt_check(self):
    return self.x > 10

@constraint
def ne_check(self):
    return self.addr != 0
```

### 逻辑运算

```python
# 与运算
@constraint
def and_check(self):
    return self.x >= 10 and self.x <= 100

# 或运算
@constraint
def or_check(self):
    return self.value < 0 or self.value > 1000

# 非运算
@constraint
def not_check(self):
    return not (self.addr & 0xF)
```

### 链式比较

```python
@constraint
def range_check(self):
    # Python原生链式比较
    return 0 <= self.value <= 100
```

### 范围约束

```python
# 使用inside函数
from sv_randomizer.api import inside

@constraint
def range_constraint(self):
    return inside([(0, 100), (200, 300)]) == self.value

# 或者使用原生表达式
@constraint
def range_expression(self):
    return (0 <= self.value <= 100) or (200 <= self.value <= 300)
```

### 权重分布

```python
from sv_randomizer.api import dist

@constraint
def weighted_addr(self):
    return dist([(0x1000, 0x8000, 70), (0x8000, 0xFFFF, 30)]) == self.addr
```

### 复杂约束

```python
@constraint
def complex_validation(self):
    return (self.addr >= 0x1000 and
            self.addr <= 0xFFFF and
            (self.opcode == 'READ' or self.opcode == 'WRITE'))
```

---

## 种子管理

### 三级种子控制

```python
from sv_randomizer import seed

# 1. 全局种子（影响所有新对象）
seed(42)

# 2. 对象级种子（影响特定对象）
pkt = Packet()
pkt.set_instance_seed(123)

# 3. 临时种子（不影响对象状态）
pkt.randomize()  # 使用对象种子
```

### 可重现性

```python
# 设置相同种子
seed(12345)

# 生成相同的序列
pkt1 = Packet()
pkt1.randomize()
values1 = (pkt1.src_addr, pkt1.dest_addr)

pkt2 = Packet()
pkt2.randomize()
values2 = (pkt2.src_addr, pkt2.dest_addr)

# values1 == values2
```

---

## 求解器选择

### 切换求解器

```python
# 创建对象时指定求解器
obj = ComplexObject(solver_backend="z3")
obj.randomize()

# 或在创建时指定
obj = ComplexObject(solver_backend="pure_python")
```

### 求解器选择建议

| 场景 | 推荐求解器 | 原因 |
|:---|:---|:---|
| 简单约束 (<10变量) | PurePython | 零依赖，速度快 |
| 复杂约束 (>10变量) | Z3 | 可满足性求解能力强 |
| 大规模随机化 | PurePython | 内存占用小 |

---

## 最佳实践

### 1. 约束设计原则

- **保持约束必要且可满足**: 避免过度约束
- **使用范围约束替代多个OR**: 性能更好
- **分离权重约束**: 使用`dist`处理权重分布

### 2. 性能优化

```python
# 推荐：使用inside函数
from sv_randomizer.api import inside

@constraint
def good(self):
    return inside([(0, 100), (200, 300)]) == self.value

# 可用：链式比较
@constraint
def acceptable(self):
    return (0 <= self.value <= 100) or (200 <= self.value <= 300)
```

### 3. 调试技巧

```python
class DebuggableObj(Randomizable):
    def pre_randomize(self):
        print(f"Before: addr={self.addr}")

    def post_randomize(self):
        print(f"After: addr={self.addr}")
        # 验证约束
        assert self.addr >= 0x1000
```

### 4. 代码风格

```python
# 推荐：提前定义类型注解
value_rand = rand(int)(bits=8, min=0, max=255)

class MyClass(Randomizable):
    value: value_rand

    @constraint
    def positive(self):
        return self.value > 0
```

---

## 故障排除

### Q: randomize()返回False怎么办？

**A**: 检查约束是否冲突：
- 约束范围是否为空
- 约束之间是否有矛盾
- 尝试使用Z3求解器

### Q: 如何提高随机化成功率？

**A**:
- 减少约束数量
- 扩大变量范围
- 使用Z3求解器

### Q: randc变量重复了？

**A**: 检查值池大小是否合理，约束是否影响randc变量的范围。

### Q: 如何从旧API迁移？

**A**: 参考迁移指南 [docs/guides/migration-v0.3.md](migration-v0.3.md)

---

## 完整示例

### 网络数据包示例

```python
from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc, constraint, dist

# 定义类型注解
src_addr_rand = rand(int)(bits=16, min=0x1000, max=0xFFFF)
dest_addr_rand = rand(int)(bits=16, min=0x1000, max=0xFFFF)
length_rand = rand(int)(bits=8, min=64, max=1500)
packet_id_randc = randc(int)(bits=4)

class NetworkPacket(Randomizable):
    """网络数据包类"""

    # 变量定义
    src_addr: src_addr_rand
    dest_addr: dest_addr_rand
    length: length_rand
    packet_id: packet_id_randc

    # 约束定义
    @constraint
    def addr_different(self):
        """源地址和目标地址不能相同"""
        return self.src_addr != self.dest_addr

    @constraint
    def valid_length(self):
        """长度必须是标准值"""
        return (self.length == 64 or
                self.length == 128 or
                self.length == 256 or
                (512 <= self.length <= 1518))

    @constraint
    def src_distribution(self):
        """源地址分布权重"""
        return dist([(0x1000, 0x8000, 70),
                    (0x8000, 0xFFFF, 30)]) == self.src_addr

# 使用
seed(42)

pkt = NetworkPacket()
for i in range(5):
    if pkt.randomize():
        print(f"Packet {i+1}:")
        print(f"  Src:     0x{pkt.src_addr:04x}")
        print(f"  Dest:    0x{pkt.dest_addr:04x}")
        print(f"  Length:  {pkt.length}")
        print(f"  ID:      {pkt.packet_id}")
    else:
        print("Failed to randomize!")
```

---

## 相关文档

- 📖 [产品功能清单](../product/features.md#随机化与约束系统)
- 📖 [API参考文档](../product/API_REFERENCE.md)
- 🔄 [v0.3迁移指南](migration-v0.3.md)
- 💡 [示例代码](../../examples/rand/)
- 🧪 [测试代码](../../tests/test_api/)

---

## 更多信息

- [项目主页](../../README.md)
- [开发路线图](../development/ROADMAP.md)
