# API v0.3 迁移指南

本文档帮助您从 SV Randomizer v0.2 (装饰器API) 迁移到 v0.3 (类型注解API)。

---

## 概述

v0.3 引入了全新的类型注解API，使用 Python 类型注解和原生表达式，提供更简洁、更符合 Python 风格的语法。

**主要变化:**
- ✨ 类型注解替代装饰器 (`rand[int]` 替代 `@rand`)
- ✨ 原生 Python 表达式替代 Expression DSL
- ✨ `@constraint` 装饰器替代 `add_constraint()`
- ✨ 更简洁的导入路径

---

## 快速对比

### 旧 API (v0.2)

```python
from sv_randomizer import Randomizable
from sv_randomizer.api.decorators import rand, randc
from sv_randomizer.api.dsl import VarProxy, inside

class Packet(Randomizable):
    def __init__(self):
        super().__init__()

        # 装饰器方式定义变量
        @rand(bits=16)
        def addr(self): pass

        @randc(bits=4)
        def id(self): pass

    def constraints(self):
        # DSL方式定义约束
        return [
            (VarProxy("addr") > 0x1000) & (VarProxy("addr") < 0xFFFF),
            inside([(0, 255), (1000, 1200)]) == VarProxy("id")
        ]
```

### 新 API (v0.3)

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint, inside

# 定义类型注解
addr_rand = rand(int)(bits=16)
id_randc = randc(int)(bits=4)

class Packet(Randomizable):
    # 类型注解方式定义变量
    addr: addr_rand
    id: id_randc

    @constraint
    def valid_range(self):
        # 原生Python表达式
        return self.addr >= 0x1000 and self.addr < 0xFFFF

    @constraint
    def id_in_range(self):
        # 使用inside函数
        return inside([(0, 255), (1000, 1200)]) == self.id
```

---

## 详细迁移步骤

### 1. 导入变化

#### 旧导入
```python
from sv_randomizer import Randomizable
from sv_randomizer.api.decorators import rand, randc, constraint
from sv_randomizer.api.dsl import VarProxy, inside, dist
```

#### 新导入
```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint, inside, dist, VarProxy
```

**变化:** 所有 API 统一从 `sv_randomizer.api` 导入。

---

### 2. 变量定义

#### rand 变量

**旧方式 (装饰器):**
```python
class MyClass(Randomizable):
    def __init__(self):
        super().__init__()

        @rand(bits=8)
        def value(self): pass
```

**新方式 (类型注解):**
```python
value_rand = rand(int)(bits=8)

class MyClass(Randomizable):
    value: value_rand
```

#### randc 变量

**旧方式:**
```python
@randc(bits=4)
def id(self): pass
```

**新方式:**
```python
id_randc = randc(int)(bits=4)

class MyClass(Randomizable):
    id: id_randc
```

#### 带范围的变量

**旧方式:**
```python
@rand(bits=16, min=0, max=65535)
def addr(self): pass
```

**新方式:**
```python
addr_rand = rand(int)(bits=16, min=0, max=65535)

class MyClass(Randomizable):
    addr: addr_rand
```

---

### 3. 约束定义

#### 简单约束

**旧方式:**
```python
class MyClass(Randomizable):
    def constraints(self):
        return [
            VarProxy("x") > 0,
            VarProxy("x") + VarProxy("y") < 100
        ]
```

**新方式:**
```python
class MyClass(Randomizable):
    @constraint
    def x_positive(self):
        return self.x > 0

    @constraint
    def sum_limited(self):
        return self.x + self.y < 100
```

#### inside 约束

**旧方式:**
```python
def constraints(self):
    return [
        inside([(0, 255), (1000, 1200)]) == VarProxy("value")
    ]
```

**新方式:**
```python
@constraint
def value_in_range(self):
    return inside([(0, 255), (1000, 1200)]) == self.value
```

**或者使用方法链:**
```python
class MyClass(Randomizable):
    value: rand(int)(...)

    @constraint
    def valid(self):
        return self.value.in_([(0, 255), (1000, 1200)])
```

#### dist 约束

**旧方式:**
```python
def constraints(self):
    return [
        dist([(0, 10, 20), (10, 100, 80)]) == VarProxy("x")
    ]
```

**新方式:**
```python
@constraint
def weighted_distribution(self):
    return dist([(0, 10, 20), (10, 100, 80)]) == self.x
```

---

### 4. 复杂约束

#### 链式比较

**旧方式:**
```python
# 需要拆分为多个条件
return [
    VarProxy("x") >= 0,
    VarProxy("x") <= 100
]
```

**新方式:**
```python
@constraint
def x_in_range(self):
    return 0 <= self.x <= 100  # 支持链式比较!
```

#### 逻辑运算

**旧方式:**
```python
return [
    (VarProxy("x") > 0) & (VarProxy("y") < 100),  # & 表示 AND
    (VarProxy("a") == 1) | (VarProxy("a") == 2)   # | 表示 OR
]
```

**新方式:**
```python
@constraint
def constraint1(self):
    return self.x > 0 and self.y < 100  # 原生 and

@constraint
def constraint2(self):
    return self.a == 1 or self.a == 2  # 原生 or
```

---

### 5. 类方法变化

#### pre_randomize() / post_randomize()

**无变化** - 这些方法继续工作：

```python
class MyClass(Randomizable):
    def pre_randomize(self):
        print("About to randomize...")

    def post_randomize(self):
        print(f"Got value: {self.value}")
```

#### constraints() 方法

**已移除** - 使用 `@constraint` 装饰器替代：

```python
# 旧方式 - 移除 constraints() 方法
def constraints(self):
    return [...]

# 新方式 - 使用 @constraint
@constraint
def my_constraint(self):
    return ...
```

---

### 6. 完整示例

#### 旧 API (v0.2)

```python
from sv_randomizer import Randomizable
from sv_randomizer.api.decorators import rand, randc
from sv_randomizer.api.dsl import VarProxy, inside, dist

class Packet(Randomizable):
    def __init__(self):
        super().__init__()

        @rand(bits=16, min=0x1000, max=0xFFFF)
        def src_addr(self): pass

        @rand(bits=16)
        def dest_addr(self): pass

        @rand(bits=8, min=64, max=1500)
        def length(self): pass

        @randc(bits=4)
        def packet_id(self): pass

    def constraints(self):
        return [
            VarProxy("src_addr") != VarProxy("dest_addr"),
            (VarProxy("length") == 64) |
            (VarProxy("length") == 128) |
            (VarProxy("length") == 256) |
            ((VarProxy("length") >= 512) & (VarProxy("length") <= 1518)),
            dist([(0, 1000, 70), (1000, 2000, 30)]) == VarProxy("src_addr")
        ]
```

#### 新 API (v0.3)

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint, dist

# 定义类型注解
src_addr_rand = rand(int)(bits=16, min=0x1000, max=0xFFFF)
dest_addr_rand = rand(int)(bits=16)
length_rand = rand(int)(bits=8, min=64, max=1500)
packet_id_randc = randc(int)(bits=4)

class Packet(Randomizable):
    # 类型注解定义变量
    src_addr: src_addr_rand
    dest_addr: dest_addr_rand
    length: length_rand
    packet_id: packet_id_randc

    # 约束装饰器
    @constraint
    def addr_different(self):
        return self.src_addr != self.dest_addr

    @constraint
    def valid_length(self):
        return (self.length == 64 or
                self.length == 128 or
                self.length == 256 or
                (512 <= self.length <= 1518))

    @constraint
    def src_addr_distribution(self):
        return dist([(0, 1000, 70), (1000, 2000, 30)]) == self.src_addr
```

**代码减少约 40%，可读性大幅提升!**

---

## 兼容性说明

### 仍然支持的功能

- ✅ 所有核心随机化功能
- ✅ rand/randc 变量
- ✅ inside/dist 约束
- ✅ pre_randomize()/post_randomize() 钩子
- ✅ Seed 控制
- ✅ 求解器后端 (PurePython/Z3)

### 已移除的功能

- ❌ `@rand` / `@randc` 装饰器 (使用类型注解替代)
- ❌ `constraints()` 方法 (使用 `@constraint` 装饰器替代)
- ❌ `VarProxy` DSL (使用原生 Python `self.xxx` 语法)

### 向后兼容

如果您需要继续使用旧 API，可以:

1. **保持在 v0.2 版本**
2. **使用混合模式** (仅用于迁移过渡期):

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint

# 新API - 类型注解
value: rand(int)(bits=8)

# 旧API - Expression DSL (仍然有效)
from sv_randomizer.constraints.expressions import VariableExpr, BinaryExpr, BinaryOp
from sv_randomizer.api.dsl import inside

# 但推荐迁移到新API
@constraint
def old_style_constraints(self):
    return self.value > 0
```

---

## 迁移检查清单

- [ ] 更新导入语句
- [ ] 将 `@rand/@randc` 装饰器改为类型注解
- [ ] 移除 `__init__` 中的变量定义
- [ ] 将 `constraints()` 方法改为 `@constraint` 装饰器
- [ ] 将 `VarProxy()` 改为 `self.xxx`
- [ ] 将 `&/|` 运算符改为 `and/or`
- [ ] 测试所有随机化逻辑
- [ ] 更新文档和示例

---

## 获取帮助

- 📖 查看 [API 参考文档](../product/API_REFERENCE.md)
- 💡 查看 [示例代码](../../examples/)
- 🐛 报告问题: [GitHub Issues](https://github.com/your-org/EDA_UFMV/issues)

---

**版本:** v0.3.0
**更新日期:** 2026-03-01
