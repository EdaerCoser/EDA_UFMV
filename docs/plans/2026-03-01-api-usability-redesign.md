# API易用性重构设计文档

**版本**: v0.3.1
**日期**: 2026-03-01
**状态**: 设计阶段
**破坏性变更**: 是

---

## 概述

重构EDA_UFVM的随机化API，大幅简化使用方式，消除样板代码，提供更符合Python直觉的编程体验。

**核心改进**:
- 代码量减少约50%
- 使用纯Python表达式编写约束
- 类型注解声明随机变量
- 移除旧装饰器API（不兼容更新）

---

## 第一部分：新API设计

### 1.1 变量声明语法

使用类型注解声明随机变量：

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint

class Packet(Randomizable):
    # 基础随机变量
    addr: rand[int](bits=16, min=0x1000, max=0xFFFF)
    data: rand[int](bits=8)

    # 循环随机变量
    transaction_id: randc[int](bits=4)

    # 枚举类型
    opcode: rand[enum]("READ", "WRITE", "ACK", "NACK")
```

### 1.2 约束表达式语法

使用纯Python表达式：

```python
class Packet(Randomizable):
    addr: rand[int](bits=16)
    dest_addr: rand[int](bits=16)

    @constraint
    def addr_valid(self):
        return self.addr >= 0x1000 and self.addr <= 0xFFFF

    @constraint
    def addr_not_equal(self):
        return self.addr != self.dest_addr
```

### 1.3 保留的核心功能

所有现有功能保持不变：

```python
# 随机化
pkt = Packet()
pkt.randomize()

# 内联约束
pkt.randomize(with_constraints={"addr": 0x2000})

# 回调函数
def pre_randomize(self):
    print("Before randomize")

def post_randomize(self):
    print(f"After: addr={self.addr}")

# 约束和随机模式控制
pkt.constraint_mode("addr_valid", False)
pkt.rand_mode("addr", False)

# Seed控制（保持不变）
seed(12345)
pkt.randomize()
pkt.randomize(seed=123)  # 临时seed

# 求解器切换
pkt.set_solver_backend("z3")
```

---

## 第二部分：实现架构

### 2.1 模块结构

```
sv_randomizer/
├── api/
│   ├── __init__.py            # 导出 rand, randc, constraint, seed
│   ├── annotations.py         # 类型注解实现
│   └── expression.py          # Python AST转换器
├── core/
│   ├── randomizable.py        # Randomizable类（更新元类）
│   ├── variables.py           # RandVar, RandCVar（保持）
│   └── seeding.py             # Seed控制（保持）
├── constraints/
│   ├── base.py                # 约束基类（保持）
│   ├── expressions.py         # Expression AST（保持）
│   ├── inside.py              # Inside约束（保持）
│   └── dist.py                # Dist约束（保持）
├── solvers/
│   └── ...                    # 求解器（保持不变）
└── utils/
    └── exceptions.py          # 异常（保持）
```

**删除的模块**:
- `api/decorators.py`（旧装饰器）
- `api/dsl.py`（VarProxy等DSL）

### 2.2 核心实现

#### 类型注解API

```python
# api/annotations.py
from typing import Annotated, TypeVar

class Rand:
    def __init__(self, bits: int = 32, min: int = None, max: int = None):
        self.bits = bits
        self.min = min
        self.max = max

class RandC:
    def __init__(self, bits: int = 8):
        self.bits = bits

class RandEnum:
    def __init__(self, *values):
        self.values = list(values)

def rand(typ: type) -> type:
    class _RandBuilder:
        def __call__(self, **kwargs):
            return Annotated[typ, Rand(**kwargs)]
    return _RandBuilder()

def randc(typ: type) -> type:
    class _RandCBuilder:
        def __call__(self, **kwargs):
            return Annotated[typ, RandC(**kwargs)]
    return _RandCBuilder()

def constraint(func):
    func._is_constraint = True
    return func
```

#### 元类实现

```python
# core/randomizable.py
from typing import get_type_hints

class RandomizableMeta(type):
    def __new__(cls, name, bases, namespace):
        new_cls = super().__new__(cls, name, bases, namespace)

        # 初始化
        if not hasattr(new_cls, '_rand_vars'):
            new_cls._rand_vars = {}
        if not hasattr(new_cls, '_randc_vars'):
            new_cls._randc_vars = {}

        # 解析类型注解
        hints = get_type_hints(new_cls, include_extras=True)
        for attr_name, hint in hints.items():
            if _is_rand_annotation(hint):
                var = _create_rand_var_from_annotation(attr_name, hint)
                new_cls._rand_vars[attr_name] = var
            elif _is_randc_annotation(hint):
                var = _create_randc_var_from_annotation(attr_name, hint)
                new_cls._randc_vars[attr_name] = var

        return new_cls
```

#### Python AST转换器

```python
# api/expression.py
import ast
from ..constraints.expressions import *

class PythonExpressionConverter(ast.NodeVisitor):
    """Python AST → Expression AST"""

    def visit_Compare(self, node):
        left = self.visit(node.left)
        op = self._convert_cmp_op(node.ops[0])
        right = self.visit(node.comparators[0])
        return BinaryExpr(left, op, right)

    def visit_BoolOp(self, node):
        if isinstance(node.op, ast.And):
            op = BinaryOp.AND
        else:
            op = BinaryOp.OR
        result = self.visit(node.values[0])
        for value in node.values[1:]:
            result = BinaryExpr(result, op, self.visit(value))
        return result

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        op = self._convert_bin_op(node.op)
        right = self.visit(node.right)
        return BinaryExpr(left, op, right)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            return VariableExpr(node.attr)
        raise ValueError("Only self.xxx attributes are supported")

    def visit_Constant(self, node):
        return ConstantExpr(node.value)
```

---

## 第三部分：代码对比

### 3.1 旧API（将被移除）

```python
from sv_randomizer import Randomizable, rand, randc, constraint, VarProxy, inside

class Packet(Randomizable):
    @rand(bit_width=16)
    def src_addr(self):
        return 0

    @rand(bit_width=16)
    def dest_addr(self):
        return 0

    @rand(bit_width=8, min_val=0, max_val=1500)
    def length(self):
        return 64

    @randc(bit_width=4)
    def packet_id(self):
        return 0

    @rand(enum_values=["READ", "WRITE", "ACK", "NACK"])
    def opcode(self):
        return "READ"

    @constraint("valid_addr_range", "src_addr >= 0x1000 && src_addr <= 0xFFFF")
    def valid_addr_range_c(self):
        pass

    @constraint("addr_not_equal", "src_addr != dest_addr")
    def addr_not_equal_c(self):
        pass
```

**代码量**: ~35行

### 3.2 新API

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint

class Packet(Randomizable):
    src_addr: rand[int](bits=16, min=0x1000, max=0xFFFF)
    dest_addr: rand[int](bits=16)
    length: rand[int](bits=8, min=64, max=1500)
    packet_id: randc[int](bits=4)
    opcode: rand[enum]("READ", "WRITE", "ACK", "NACK")

    @constraint
    def valid_addr_range(self):
        return self.src_addr >= 0x1000 and self.src_addr <= 0xFFFF

    @constraint
    def addr_not_equal(self):
        return self.src_addr != self.dest_addr
```

**代码量**: ~16行（-54%）

---

## 第四部分：测试计划

### 4.1 测试结构

```
tests/
├── test_api/
│   ├── test_annotations.py       # 类型注解功能测试
│   ├── test_constraints.py       # 约束表达式测试
│   ├── test_ast_converter.py     # Python AST转换测试
│   ├── test_seed_control.py      # Seed功能保持测试
│   ├── test_solver_backends.py   # 求解器兼容性测试
│   └── test_examples.py          # 示例代码更新测试
├── integration/
│   └── test_end_to_end.py        # 端到端集成测试
└── performance/
    └── bench_new_api.py          # 新API性能基准
```

### 4.2 关键测试用例

- 基础随机变量（rand/randc）
- 枚举类型
- 简单约束（比较、逻辑）
- 复杂约束（算术、嵌套）
- Seed控制和可复现性
- 求解器后端切换
- 内联约束
- 约束模式切换

**目标**: 保持100%测试通过率

---

## 第五部分：迁移支持

### 5.1 迁移工具

```bash
# 自动转换脚本
python -m sv_randomizer.tools.migrate --path . --api-version v2
```

### 5.2 迁移对照表

| 旧API | 新API |
|-------|-------|
| `@rand(bit_width=16)` | `rand[int](bits=16)` |
| `@randc(bit_width=4)` | `randc[int](bits=4)` |
| `@rand(enum_values=[...])` | `rand[enum](...)` |
| `@constraint("name", "expr")` | `@constraint` + `return expr` |
| `VarProxy("x")` | `self.x` |
| `&&`, `\|\|` | `and`, `or` |

### 5.3 无需改动

- `randomize()` 调用
- `seed()` 控制
- 约束模式切换
- 求解器选择
- 所有RGM和Coverage API

---

## 第六部分：实施里程碑

| 里程碑 | 内容 | 时间 |
|--------|------|------|
| M1 | 类型注解系统 + 元类 | 1周 |
| M2 | Python AST转换器 | 1周 |
| M3 | 约束装饰器实现 | 1周 |
| M4 | 更新所有示例和测试 | 1周 |
| M5 | 文档和迁移工具 | 1周 |

**总计**: 5周

---

## 第七部分：风险和缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Python AST解析限制 | 中 | 提前测试边界情况，限制支持语法 |
| 用户迁移成本 | 高 | 提供自动转换工具 + 详细文档 |
| 性能回归 | 低 | 基准测试，优化热路径 |
| IDE类型提示支持 | 低 | 文档说明，未来可改进 |

---

## 第八部分：验收标准

- [ ] 所有新测试通过（>150个）
- [ ] 所有示例代码更新并通过
- [ ] 性能不低于旧API（±10%）
- [ ] 迁移工具可用
- [ ] 文档完整（API参考 + 迁移指南）
- [ ] Seed功能正常工作
- [ ] 两种求解器后端都可用

---

## 附录

### A. 完整示例

```python
from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc, constraint

class NetworkPacket(Randomizable):
    """网络数据包 - 使用新API"""

    # 变量声明
    src_addr: rand[int](bits=16, min=0x1000, max=0xFFFF)
    dest_addr: rand[int](bits=16)
    length: rand[int](bits=8, min=64, max=1500)
    packet_id: randc[int](bits=4)
    opcode: rand[enum]("READ", "WRITE", "ACK", "NACK")

    # 约束
    @constraint
    def addr_valid(self):
        return self.src_addr >= 0x1000 and self.dest_addr >= 0x1000

    @constraint
    def addr_different(self):
        return self.src_addr != self.dest_addr

    @constraint
    def length_valid(self):
        return self.length in [64] or range(128, 256) or range(512, 1519)

    def pre_randomize(self):
        print(f"Generating packet...")

    def post_randomize(self):
        print(f"Packet: src=0x{self.src_addr:04x}, dest=0x{self.dest_addr:04x}")

# 使用
seed(12345)
pkt = NetworkPacket()
pkt.randomize()

print(f"Opcode: {pkt.opcode}")
print(f"ID: {pkt.packet_id}")
```

### B. 参考资料

- PEP 593: Flexible Function and Variable Annotations
- Python AST Documentation
- SystemVerilog LRM (随机化约束语义)
- Pydantic V2 (类型注解灵感)
