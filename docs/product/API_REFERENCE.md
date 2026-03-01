# API 参考文档

SV Randomizer v0.3+ 完整 API 参考

---

## 目录

- [快速开始](#快速开始)
- [核心类](#核心类)
- [类型注解 API](#类型注解-api)
- [约束装饰器](#约束装饰器)
- [DSL 便捷函数](#dsl-便捷函数)
- [表达式系统](#表达式系统)
- [Seed 控制](#seed-控制)
- [求解器后端](#求解器后端)

---

## 快速开始

### 最小示例

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc

value_rand = rand(int)(bits=8)

class MyClass(Randomizable):
    value: value_rand

obj = MyClass()
obj.randomize()
print(obj.value)  # 随机值 0-255
```

### 带约束的示例

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint

x_rand = rand(int)(min=0, max=100)
y_rand = rand(int)(min=0, max=100)

class Constrained(Randomizable):
    x: x_rand
    y: y_rand

    @constraint
    def sum_limited(self):
        return self.x + self.y < 100

obj = Constrained()
obj.randomize()
print(obj.x, obj.y)  # x + y < 100
```

---

## 核心类

### Randomizable

所有随机化类的基类。

```python
from sv_randomizer import Randomizable

class MyClass(Randomizable):
    pass
```

#### 方法

##### `__init__(self, solver_backend: str = None)`

初始化随机化对象。

**参数:**
- `solver_backend` (str, optional): 求解器后端名称 (`"pure_python"` 或 `"z3"`)

**示例:**
```python
# 使用默认求解器
obj = MyClass()

# 指定求解器
obj = MyClass(solver_backend="z3")
```

---

##### `randomize(self) -> bool`

随机化所有 rand/randc 变量，满足所有约束。

**返回:**
- `bool`: 成功返回 True，失败返回 False

**示例:**
```python
obj = MyClass()
if obj.randomize():
    print(f"Success: x={obj.x}")
else:
    print("Failed to satisfy constraints")
```

---

##### `get_constraint(self, name: str) -> Constraint`

获取指定名称的约束对象。

**参数:**
- `name` (str): 约束方法名称

**返回:**
- `Constraint`: 约束对象，不存在返回 None

**示例:**
```python
constraint = obj.get_constraint("my_constraint")
if constraint:
    print(f"Constraint enabled: {constraint.enabled}")
```

---

##### `set_instance_seed(self, seed: int)`

设置实例级别的随机种子。

**参数:**
- `seed` (int): 随机种子值

**示例:**
```python
obj1 = MyClass()
obj1.set_instance_seed(42)
obj1.randomize()

obj2 = MyClass()
obj2.set_instance_seed(42)
obj2.randomize()

# obj1 和 obj2 会产生相同的随机值
```

---

### 钩子方法

#### `pre_randomize(self)`

在随机化**之前**调用。可被子类重写。

**用途:**
- 设置临时约束
- 记录状态
- 验证前置条件

**示例:**
```python
class MyClass(Randomizable):
    def pre_randomize(self):
        print("About to randomize...")
        self.temp_mode = True
```

---

#### `post_randomize(self)`

在随机化**之后**调用。可被子类重写。

**用途:**
- 验证结果
- 计算派生值
- 记录日志

**示例:**
```python
class MyClass(Randomizable):
    def post_randomize(self):
        print(f"Got value: {self.value}")
        self.derived = self.value * 2
```

---

## 类型注解 API

### rand()

创建 rand (随机) 变量类型注解。

#### 语法

```python
from sv_randomizer.api import rand

# 基本语法
variable_rand = rand(type)(**kwargs)
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `type` | type | ✅ | - | 变量类型 (int, str 等) |
| `bits` | int | ❌ | 32 | 位宽 |
| `min` | int | ❌ | None | 最小值 |
| `max` | int | ❌ | None | 最大值 |

#### 返回值

返回可用于类型注解的 `Annotated` 类型。

#### 示例

```python
# 8位无符号整数
value: rand(int)(bits=8)

# 16位有范围限制
addr: rand(int)(bits=16, min=0, max=65535)

# 先定义注解，再使用
x_rand = rand(int)(bits=8)

class MyClass(Randomizable):
    x: x_rand
```

---

### randc()

创建 randc (随机周期) 变量类型注解。

#### 语法

```python
from sv_randomizer.api import randc

variable_randc = randc(type)(**kwargs)
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `type` | type | ✅ | - | 变量类型 |
| `bits` | int | ❌ | 8 | 位宽 |

#### 返回值

返回可用于类型注解的 `Annotated` 类型。

#### 特性

- **不重复**: 在周期内不重复生成相同值
- **全周期**: 遍历所有可能值后重新开始
- **周期长度**: 2^bits

#### 示例

```python
# 4位 randc (周期 16)
id_randc = randc(int)(bits=4)

class MyClass(Randomizable):
    id: id_randc

# 使用
obj = MyClass()
for i in range(16):
    obj.randomize()
    print(obj.id)  # 0-15 不重复
```

---

### Rand, RandC, RandEnum

元数据类，用于 `Annotated` 类型注解。

#### Rand

```python
from typing import Annotated
from sv_randomizer.api.annotations import Rand

value: Annotated[int, Rand(bits=8, min=0, max=255)]
```

#### RandC

```python
from typing import Annotated
from sv_randomizer.api.annotations import RandC

id: Annotated[int, RandC(bits=4)]
```

#### RandEnum

```python
from typing import Annotated
from sv_randomizer.api.annotations import RandEnum

color: Annotated[str, RandEnum("red", "green", "blue")]
```

---

## 约束装饰器

### @constraint

标记约束方法的装饰器。

#### 语法

```python
from sv_randomizer.api import constraint

class MyClass(Randomizable):
    @constraint
    def constraint_name(self):
        return self.x > 0
```

#### 工作原理

1. 装饰的方法在类定义时被识别
2. 方法体被解析为 Python AST
3. AST 转换为框架的 Expression 对象
4. 在 `randomize()` 时求解

#### 支持的 Python 语法

| 语法 | 示例 | 说明 |
|------|------|------|
| 比较运算 | `self.x > 0` | `>`, `<`, `>=`, `<=`, `==`, `!=` |
| 逻辑运算 | `self.x > 0 and self.y < 100` | `and`, `or`, `not` |
| 算术运算 | `self.x + self.y` | `+`, `-`, `*`, `/`, `%` |
| 位运算 | `self.x & 0xFF` | `&`, `|`, `^`, `~`, `<<`, `>>` |
| 链式比较 | `0 <= self.x <= 100` | Python 原生链式比较 |
| 属性访问 | `self.xxx` | 只支持 `self.` 形式 |
| 常量 | `self.x == 42` | 数字, 字符串, 布尔值 |

#### 示例

```python
class Packet(Randomizable):
    src_addr: addr_rand
    dest_addr: dest_addr_rand

    @constraint
    def addr_different(self):
        return self.src_addr != self.dest_addr

    @constraint
    def valid_range(self):
        return 0x1000 <= self.src_addr <= 0xFFFF

    @constraint
    def complex_logic(self):
        return (self.src_addr > 0x1000 and
                self.dest_addr < 0xFFFF and
                self.src_addr != self.dest_addr)
```

---

## DSL 便捷函数

### inside()

创建范围/值成员约束。

#### 语法

```python
from sv_randomizer.api import inside

inside(*ranges) == variable
```

#### 参数

- `*ranges`: 范围元组 `(low, high)` 或单个值

#### 返回值

Expression 对象，表示成员关系约束。

#### 示例

```python
# 值在指定范围内
inside([(0, 255), (1000, 1200)]) == self.value

# 单个值
inside([10, 20, 30]) == self.value

# 混合
inside([(0, 100), 200, (300, 400)]) == self.value
```

---

### dist()

创建权重分布约束。

#### 语法

```python
from sv_randomizer.api import dist

dist(*weights) == variable
```

#### 参数

- `*weights`: 权重元组 `(min, max, weight)` 或 `(value, weight)`

#### 返回值

`DistConstraint` 对象。

#### 示例

```python
# 范围权重
dist([(0, 100, 70), (100, 200, 30)]) == self.x
# 70% 概率在 0-100, 30% 概率在 100-200

# 单值权重
dist([(10, 50), (20, 30), (30, 20)]) == self.value
# 50% 概率=10, 30% 概率=20, 20% 概率=30
```

---

### VarProxy

变量代理类，用于表达式中的变量引用（向后兼容）。

#### 语法

```python
from sv_randomizer.api import VarProxy

VarProxy("variable_name")
```

#### 操作符支持

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `==` | `VarProxy("x") == 0` | 等于 |
| `!=` | `VarProxy("x") != 0` | 不等于 |
| `<` | `VarProxy("x") < 100` | 小于 |
| `>` | `VarProxy("x") > 0` | 大于 |
| `<=` | `VarProxy("x") <= 100` | 小于等于 |
| `>=` | `VarProxy("x") >= 0` | 大于等于 |
| `+` | `VarProxy("x") + VarProxy("y")` | 加法 |
| `-` | `VarProxy("x") - 10` | 减法 |
| `*` | `VarProxy("x") * 2` | 乘法 |
| `&` | `VarProxy("x") & VarProxy("y")` | 逻辑与 |

#### 注

推荐使用原生 `self.xxx` 语法替代 VarProxy：

```python
# 推荐 (新API)
@constraint
def my_constraint(self):
    return self.x > 0 and self.y < 100

# 可用 (向后兼容)
from sv_randomizer.api import VarProxy
return VarProxy("x") > 0 & VarProxy("y") < 100
```

---

## 表达式系统

### Expression 类层次

```
Expression (抽象基类)
├── VariableExpr      # 变量引用
├── ConstantExpr      # 常量值
├── UnaryExpr         # 一元运算 (not, -, ~)
└── BinaryExpr        # 二元运算
```

### BinaryOp 枚举

支持的所有二元运算符。

```python
from sv_randomizer.constraints.expressions import BinaryOp

# 比较运算
BinaryOp.EQ   # ==
BinaryOp.NE   # !=
BinaryOp.LT   # <
BinaryOp.LE   # <=
BinaryOp.GT   # >
BinaryOp.GE   # >=

# 逻辑运算
BinaryOp.AND  # &&
BinaryOp.OR   # ||

# 算术运算
BinaryOp.ADD  # +
BinaryOp.SUB  # -
BinaryOp.MUL  # *
BinaryOp.DIV  # /
BinaryOp.MOD  # %

# 位运算
BinaryOp.BIT_AND    # &
BinaryOp.BIT_OR     # |
BinaryOp.BIT_XOR    # ^
BinaryOp.SHIFT_LEFT # <<
BinaryOp.SHIFT_RIGHT# >>
```

### 手动构建表达式

```python
from sv_randomizer.constraints.expressions import (
    BinaryExpr, BinaryOp, VariableExpr, ConstantExpr
)

# 手动构建: x > 0 and y < 100
expr = BinaryExpr(
    BinaryExpr(
        VariableExpr("x"),
        BinaryOp.GT,
        ConstantExpr(0)
    ),
    BinaryOp.AND,
    BinaryExpr(
        VariableExpr("y"),
        BinaryOp.LT,
        ConstantExpr(100)
    )
)
```

---

## Seed 控制

### 全局 Seed

```python
from sv_randomizer import seed, get_global_seed

# 设置全局 seed
seed(42)

# 获取当前 seed
current_seed = get_global_seed()
```

### 实例 Seed

```python
obj = MyClass()
obj.set_instance_seed(123)
obj.randomize()
```

### 临时 Seed

```python
from sv_randomizer import seed

seed(42)
obj1 = MyClass()
obj1.randomize()  # 使用 seed=42

# 临时更改
with seed(100):
    obj2 = MyClass()
    obj2.randomize()  # 使用 seed=100

obj3 = MyClass()
obj3.randomize()  # 恢复到 seed=42
```

---

## 求解器后端

### PurePython (默认)

无需外部依赖，纯 Python 实现。

**特点:**
- ✅ 零依赖
- ✅ 快速 (~10K 随机化/秒)
- ❌ 复杂约束性能较低

**使用:**
```python
# 默认使用
obj = MyClass()

# 显式指定
obj = MyClass(solver_backend="pure_python")
```

---

### Z3 SMT Solver

工业级 SMT 求解器。

**特点:**
- ✅ 强大的约束求解
- ✅ 支持复杂约束
- ❌ 需要安装 z3-solver

**安装:**
```bash
pip install z3-solver
```

**使用:**
```python
obj = MyClass(solver_backend="z3")
```

---

## 完整示例

### 综合示例

```python
from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc, constraint, dist

# 定义类型注解
addr_rand = rand(int)(bits=16, min=0x1000, max=0xFFFF)
data_rand = rand(int)(bits=8, min=0, max=255)
id_randc = randc(int)(bits=4)

class NetworkPacket(Randomizable):
    """网络数据包类"""

    # 变量定义
    src_addr: addr_rand
    dest_addr: data_rand
    length: data_rand
    packet_id: id_randc

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
    def addr_distribution(self):
        """源地址分布权重"""
        return dist([(0x1000, 0x8000, 70),
                    (0x8000, 0xFFFF, 30)]) == self.src_addr

    def pre_randomize(self):
        """随机化前回调"""
        print("Randomizing packet...")

    def post_randomize(self):
        """随机化后回调"""
        print(f"Packet: src=0x{self.src_addr:04x}, "
              f"dest=0x{self.dest_addr:04x}, "
              f"len={self.length}, "
              f"id={self.packet_id}")

# 使用
seed(42)

pkt = NetworkPacket()
for i in range(5):
    if pkt.randomize():
        pass  # pkt.post_randomize() 会自动调用
    else:
        print("Failed to randomize!")
```

---

## 导入总结

```python
# 核心类
from sv_randomizer import Randomizable, seed

# 类型注解
from sv_randomizer.api import rand, randc

# 约束装饰器
from sv_randomizer.api import constraint

# DSL便捷函数
from sv_randomizer.api import inside, dist, VarProxy

# 表达式系统（高级用法）
from sv_randomizer.constraints.expressions import (
    Expression, VariableExpr, ConstantExpr,
    BinaryExpr, UnaryExpr, BinaryOp
)
```

---

**版本:** v0.3.0
**更新日期:** 2026-03-01
