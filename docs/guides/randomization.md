# 随机化系统使用指南

**版本**: v0.1.0
**更新日期**: 2026年3月1日

---

## 概述

EDA_UFMV的随机化系统提供SystemVerilog风格的约束随机化功能，支持：
- rand/randc随机变量
- 丰富的约束类型（关系、逻辑、蕴含、范围、权重）
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
from sv_randomizer import Randomizable, rand

class Packet(Randomizable):
    @rand(bit_width=16, min_val=0, max_val=65535)
    def src_addr(self): return 0

    @rand(bit_width=16, min_val=0, max_val=65535)
    def dest_addr(self): return 0

pkt = Packet()
for i in range(5):
    pkt.randomize()
    print(f"src=0x{pkt.src_addr:04x}, dst=0x{pkt.dest_addr:04x}")
```

### 使用约束

```python
from sv_randomizer import Randomizable, rand, constraint

class ConstrainedPacket(Randomizable):
    @rand(bit_width=16, min_val=0, max_val=65535)
    def src_addr(self): return 0

    @rand(bit_width=16, min_val=0, max_val=65535)
    def dest_addr(self): return 0

    @constraint("valid_addr", "src_addr >= 0x1000 && src_addr != dest_addr")
    def valid_addr_c(self): pass

pkt = ConstrainedPacket()
pkt.randomize()
```

---

## API参考

### 装饰器

#### @rand

定义标准随机变量。

**参数**:
- `bit_width` (int): 位宽
- `min_val` (int): 最小值（可选）
- `max_val` (int): 最大值（可选）
- `enum_values` (list): 枚举值列表（可选）

**示例**:
```python
@rand(bit_width=32)
def data(self): return 0

@rand(enum_values=['READ', 'WRITE', 'IDLE'])
def opcode(self): return 'READ'
```

#### @randc

定义循环随机变量，遍历所有可能值后才重复。

**参数**:
- `bit_width` (int): 位宽
- `min_val` (int): 最小值（可选）
- `max_val` (int): 最大值（可选）

**示例**:
```python
@randc(bit_width=4)
def packet_id(self): return 0
```

#### @constraint

定义约束。

**参数**:
- `name` (str): 约束名称
- `expression` (str): 约束表达式（字符串形式）

**支持的运算符**:
- 关系: `==`, `!=`, `<`, `>`, `<=`, `>=`
- 逻辑: `&&`, `||`, `!`
- 算术: `+`, `-`, `*`, `/`, `%`
- 位运算: `&`, `|`, `^`, `~`, `<<`, `>>`
- 范围: `value in [low:high]` 或 `value in [val1, val2, ...]`

**示例**:
```python
@constraint("addr_aligned", "addr % 4 == 0")
def addr_aligned_c(self): pass

@constraint("range_check", "value in [0:100] || value in [200:300]")
def range_c(self): pass
```

### Randomizable类方法

#### __init__(self, seed=None)

初始化随机化对象。

**参数**:
- `seed` (int, optional): 对象级种子

#### randomize(self, seed=None)

执行随机化。

**参数**:
- `seed` (int, optional): 临时种子（不影响对象状态）

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
@constraint("gt_check", "x > 10")
@constraint("ne_check", "addr != 0")
```

### 逻辑运算

```python
# 与运算
@constraint("and_check", "x >= 10 && x <= 100")

# 或运算
@constraint("or_check", "value < 0 || value > 1000")

# 非运算
@constraint("not_check", "!(addr & 0xF)")
```

### 范围约束

```python
# 单个范围
@constraint("range1", "value in [0:100]")

# 多个范围
@constraint("range2", "value in [0:100] || value in [200:300]")

# 值列表
@constraint("values", "opcode in ['READ', 'WRITE']")
```

### 复杂约束

```python
@constraint("complex",
          "addr >= 0x1000 && addr <= 0xFFFF && "
          "(opcode == 'READ' || opcode == 'WRITE')")
def complex_c(self): pass
```

---

## 种子管理

### 三级种子控制

```python
from sv_randomizer import set_global_seed

# 1. 全局种子（影响所有新对象）
set_global_seed(42)

# 2. 对象级种子（影响特定对象）
pkt = Packet(seed=123)

# 3. 临时种子（不影响对象状态）
pkt.randomize(seed=456)
```

### 可重现性

```python
# 设置相同种子
set_global_seed(12345)

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
from sv_randomizer.solvers import SolverFactory

# 使用Z3求解器
SolverFactory.set_default_backend("z3")

# 创建对象并随机化
obj = ComplexObject()
obj.randomize()

# 恢复默认求解器
SolverFactory.set_default_backend("pure_python")
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
# 推荐：使用inside约束
@constraint("good", "value in [0:100] || value in [200:300]")

# 避免：多个OR
@constraint("bad", "value == 0 || value == 1 || ... || value == 100")
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

---

## 相关文档

- 📖 [产品功能清单](../product/features.md#随机化与约束系统)
- 💡 [示例代码](../../examples/rand/)
- 🧪 [测试代码](../../tests/legacy/)
- 🌱 [种子管理详解](seeding.md) (待创建)
- ⚖️ [约束系统详解](constraints.md) (待创建)

---

## 更多信息

- [项目主页](../../README.md)
- [开发路线图](../development/ROADMAP.md)
