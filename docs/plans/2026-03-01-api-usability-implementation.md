# API易用性重构实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 重构EDA_UFVM的随机化API，使用类型注解和Python原生表达式，减少50%样板代码，移除旧装饰器API（不兼容更新）。

**架构:** 使用类型注解（PEP 593 Annotated）声明随机变量，通过元类解析注解并创建RandVar/RandCVar对象；使用Python AST访问者模式将原生Python表达式转换为框架的Expression AST。

**技术栈:** Python 3.8+, typing.Annotated, ast模块, 元类, pytest

---

## 前置准备

### 文档阅读

在开始实施前，阅读以下文档了解上下文：

- **设计文档**: `docs/plans/2026-03-01-api-usability-redesign.md` - 完整设计说明
- **当前API**: `sv_randomizer/api/decorators.py` - 待移除的旧装饰器
- **核心类**: `sv_randomizer/core/randomizable.py` - Randomizable基类
- **变量系统**: `sv_randomizer/core/variables.py` - RandVar/RandCVar实现
- **约束系统**: `sv_randomizer/constraints/expressions.py` - Expression AST

### 当前API测试

运行现有测试了解当前功能：

```bash
# 运行旧API测试（运行前记录结果，作为对比基准）
pytest tests/legacy/ -v > test_results_old.txt
pytest tests/test_rgm/ -v >> test_results_old.txt
```

---

## M1: 类型注解系统 + 元类 (1周)

### Task 1.1: 创建类型注解类

**Files:**
- Create: `sv_randomizer/api/annotations.py`

**Step 1: 创建测试文件**

```python
# tests/test_api/test_annotations.py
import pytest
from typing import get_type_hints, Annotated
from sv_randomizer.api.annotations import Rand, RandC, RandEnum, rand, randc

def test_rand_class():
    """测试Rand类"""
    rand_meta = Rand(bits=16, min=0x1000, max=0xFFFF)
    assert rand_meta.bits == 16
    assert rand_meta.min == 0x1000
    assert rand_meta.max == 0xFFFF

def test_randc_class():
    """测试RandC类"""
    randc_meta = RandC(bits=4)
    assert randc_meta.bits == 4

def test_rand_enum_class():
    """测试RandEnum类"""
    enum_meta = RandEnum("READ", "WRITE", "ACK")
    assert enum_meta.values == ["READ", "WRITE", "ACK"]

def test_rand_builder_syntax():
    """测试rand[int](bits=16)语法"""
    # rand[int] 返回一个builder
    builder = rand(int)
    # builder(**kwargs) 返回 Annotated[int, Rand(...)]
    annotation = builder(bits=16)

    # 验证结构
    assert hasattr(annotation, '__metadata__')
    metadata = annotation.__metadata__[0]
    assert isinstance(metadata, Rand)
    assert metadata.bits == 16

def test_randc_builder_syntax():
    """测试randc[int](bits=4)语法"""
    builder = randc(int)
    annotation = builder(bits=4)

    assert hasattr(annotation, '__metadata__')
    metadata = annotation.__metadata__[0]
    assert isinstance(metadata, RandC)
    assert metadata.bits == 4
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_api/test_annotations.py -v
```
Expected: FAIL - ModuleNotFoundError: No module named 'sv_randomizer.api.annotations'

**Step 3: 实现annotations.py**

```python
# sv_randomizer/api/annotations.py
"""
类型注解API - 提供rand/randc/randenum类型注解
"""
from typing import Annotated, TypeVar, Any, List
from typing_extensions import get_args, get_origin

T = TypeVar('T')

class Rand:
    """rand变量元数据"""
    def __init__(self, bits: int = 32, min: int = None, max: int = None):
        self.bits = bits
        self.min = min
        self.max = max

    def __repr__(self):
        return f"Rand(bits={self.bits}, min={self.min}, max={self.max})"

class RandC:
    """randc变量元数据"""
    def __init__(self, bits: int = 8):
        self.bits = bits

    def __repr__(self):
        return f"RandC(bits={self.bits})"

class RandEnum:
    """枚举类型随机变量元数据"""
    def __init__(self, *values: Any):
        self.values = list(values)

    def __repr__(self):
        return f"RandEnum({self.values})"

def rand(typ: type) -> type:
    """
    创建rand类型注解的辅助函数

    使用方式: rand[int](bits=16, min=0, max=100)
    """
    class _RandBuilder:
        def __call__(self, **kwargs) -> Annotated[typ, Rand(**kwargs)]:
            return Annotated[typ, Rand(**kwargs)]
    return _RandBuilder()

def randc(typ: type) -> type:
    """
    创建randc类型注解的辅助函数

    使用方式: randc[int](bits=4)
    """
    class _RandCBuilder:
        def __call__(self, **kwargs) -> Annotated[typ, RandC(**kwargs)]:
            return Annotated[typ, RandC(**kwargs)]
    return _RandCBuilder()

# 辅助函数：检查注解是否包含Rand/RandC
def is_rand_annotation(hint: Any) -> bool:
    """检查是否为rand类型注解"""
    origin = get_origin(hint)
    if origin is Annotated:
        args = get_args(hint)
        if len(args) > 1 and isinstance(args[1], Rand):
            return True
    return False

def is_randc_annotation(hint: Any) -> bool:
    """检查是否为randc类型注解"""
    origin = get_origin(hint)
    if origin is Annotated:
        args = get_args(hint)
        if len(args) > 1 and isinstance(args[1], RandC):
            return True
    return False

def is_rand_enum_annotation(hint: Any) -> bool:
    """检查是否为枚举类型注解"""
    origin = get_origin(hint)
    if origin is Annotated:
        args = get_args(hint)
        if len(args) > 1 and isinstance(args[1], RandEnum):
            return True
    return False

def extract_rand_metadata(hint: Any) -> Rand:
    """从注解中提取Rand元数据"""
    args = get_args(hint)
    return args[1]

def extract_randc_metadata(hint: Any) -> RandC:
    """从注解中提取RandC元数据"""
    args = get_args(hint)
    return args[1]

__all__ = ['Rand', 'RandC', 'RandEnum', 'rand', 'randc',
           'is_rand_annotation', 'is_randc_annotation', 'is_rand_enum_annotation',
           'extract_rand_metadata', 'extract_randc_metadata']
```

**Step 4: 运行测试（预期通过）**

```bash
pytest tests/test_api/test_annotations.py -v
```
Expected: PASS (all 5 tests)

**Step 5: 提交**

```bash
git add sv_randomizer/api/annotations.py tests/test_api/test_annotations.py
git commit -m "feat(api): 添加类型注解系统基础类

- 实现Rand/RandC/RandEnum元数据类
- 实现rand/randc辅助函数支持语法糖
- 添加注解检查和元数据提取函数
- 添加基础单元测试"
```

---

### Task 1.2: 实现Randomizable元类

**Files:**
- Modify: `sv_randomizer/core/randomizable.py:1-50` (添加元类)
- Test: `tests/test_api/test_metaclass.py`

**Step 1: 创建元类测试**

```python
# tests/test_api/test_metaclass.py
import pytest
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc
from sv_randomizer.core.variables import RandVar, RandCVar, VarType

def test_metaclass_creates_rand_vars():
    """测试元类从类型注解创建RandVar"""
    class TestClass(Randomizable):
        value: rand[int](bits=8)

    # 验证_rand_vars被正确创建
    assert 'value' in TestClass._rand_vars
    assert isinstance(TestClass._rand_vars['value'], RandVar)
    assert TestClass._rand_vars['value'].bit_width == 8

def test_metaclass_creates_randc_vars():
    """测试元类从类型注解创建RandCVar"""
    class TestClass(Randomizable):
        value: randc[int](bits=4)

    # 验证_randc_vars被正确创建
    assert 'value' in TestClass._randc_vars
    assert isinstance(TestClass._randc_vars['value'], RandCVar)
    assert TestClass._randc_vars['value'].bit_width == 4

def test_metaclass_with_min_max():
    """测试带min/max的变量"""
    class TestClass(Randomizable):
        value: rand[int](bits=16, min=100, max=200)

    var = TestClass._rand_vars['value']
    assert var.min_val == 100
    assert var.max_val == 200

def test_metaclass_multiple_vars():
    """测试多个变量"""
    class TestClass(Randomizable):
        a: rand[int](bits=8)
        b: randc[int](bits=4)
        c: rand[int](bits=16, min=0, max=100)

    assert len(TestClass._rand_vars) == 2
    assert len(TestClass._randc_vars) == 1
    assert 'a' in TestClass._rand_vars
    assert 'b' in TestClass._randc_vars
    assert 'c' in TestClass._rand_vars
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_api/test_metaclass.py::test_metaclass_creates_rand_vars -v
```
Expected: FAIL - 元类未实现

**Step 3: 实现元类**

在 `sv_randomizer/core/randomizable.py` 顶部添加：

```python
# sv_randomizer/core/randomizable.py
import random
from typing import Dict, Any, Optional, get_type_hints
from .variables import RandVar, RandCVar, VarType
from ..api.annotations import (
    is_rand_annotation, is_randc_annotation,
    extract_rand_metadata, extract_randc_metadata
)

class RandomizableMeta(type):
    """
    Randomizable的元类 - 自动处理类型注解

    功能：
    1. 解析类属性中的rand/randc类型注解
    2. 自动创建对应的RandVar/RandCVar对象
    3. 将变量注册到类的_rand_vars/_randc_vars字典
    """

    def __new__(cls, name: str, bases: tuple, namespace: dict, **kwargs):
        # 创建新类
        new_cls = super().__new__(cls, name, bases, namespace)

        # 确保有存储字典
        if not hasattr(new_cls, '_rand_vars'):
            new_cls._rand_vars = {}
        if not hasattr(new_cls, '_randc_vars'):
            new_cls._randc_vars = {}

        # 解析类型注解（跳过Randomizable基类本身）
        if name != 'Randomizable':
            try:
                hints = get_type_hints(new_cls, include_extras=True)
                _process_annotations(new_cls, hints)
            except (NameError, AttributeError):
                # 类型注解可能引用尚未定义的类型，跳过
                pass

        return new_cls


def _process_annotations(cls: type, hints: dict) -> None:
    """
    处理类型注解，创建随机变量

    Args:
        cls: 类对象
        hints: 类型注解字典 {属性名: 类型注解}
    """
    for attr_name, hint in hints.items():
        # 跳过特殊方法和私有属性
        if attr_name.startswith('_'):
            continue

        try:
            if is_rand_annotation(hint):
                metadata = extract_rand_metadata(hint)
                var = _create_rand_var(attr_name, metadata)
                cls._rand_vars[attr_name] = var

            elif is_randc_annotation(hint):
                metadata = extract_randc_metadata(hint)
                var = _create_randc_var(attr_name, metadata)
                cls._randc_vars[attr_name] = var
        except Exception as e:
            # 记录错误但继续处理其他注解
            import warnings
            warnings.warn(f"Failed to process annotation '{attr_name}': {e}")


def _create_rand_var(name: str, metadata) -> RandVar:
    """从Rand元数据创建RandVar"""
    var_type = VarType.INT

    # 确定范围
    if metadata.min is not None and metadata.max is not None:
        min_val = metadata.min
        max_val = metadata.max
    else:
        min_val = 0
        max_val = (1 << metadata.bits) - 1

    return RandVar(name, var_type, bit_width=metadata.bits,
                   min_val=min_val, max_val=max_val)


def _create_randc_var(name: str, metadata) -> RandCVar:
    """从RandC元数据创建RandCVar"""
    var_type = VarType.BIT
    return RandCVar(name, var_type, bit_width=metadata.bits)


# 修改Randomizable类使用元类
class Randomizable(metaclass=RandomizableMeta):
    # ... 现有Randomizable类的其余部分保持不变
```

**注意**: 需要保留Randomizable类的所有现有代码，只修改类定义行添加`metaclass=RandomizableMeta`。

**Step 4: 运行测试**

```bash
pytest tests/test_api/test_metaclass.py -v
```
Expected: PASS (all 4 tests)

**Step 5: 提交**

```bash
git add sv_randomizer/core/randomizable.py tests/test_api/test_metaclass.py
git commit -m "feat(core): 实现RandomizableMeta元类

- 元类自动解析rand/randc类型注解
- 自动创建RandVar/RandCVar对象并注册
- 支持min/max范围参数
- 添加元类单元测试"
```

---

### Task 1.3: 集成测试 - 随机化功能

**Files:**
- Test: `tests/test_api/test_integration_basic.py`

**Step 1: 创建集成测试**

```python
# tests/test_api/test_integration_basic.py
import pytest
from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc

def test_basic_randomization():
    """测试基础随机化功能"""
    class TestObj(Randomizable):
        value: rand[int](bits=8)

    obj = TestObj()
    for _ in range(10):
        obj.randomize()
        assert 0 <= obj.value <= 255

def test_randc_randomization():
    """测试randc循环随机"""
    class TestObj(Randomizable):
        value: randc[int](bits=4)

    obj = TestObj()
    seen = set()
    for _ in range(16):
        obj.randomize()
        seen.add(obj.value)
        assert 0 <= obj.value <= 15

    # 4位randc应该产生16个唯一值
    assert len(seen) == 16

def test_multiple_variables():
    """测试多变量随机化"""
    class TestObj(Randomizable):
        a: rand[int](bits=8)
        b: rand[int](bits=16, min=1000, max=2000)
        c: randc[int](bits=2)

    obj = TestObj()
    obj.randomize()

    assert 0 <= obj.a <= 255
    assert 1000 <= obj.b <= 2000
    assert 0 <= obj.c <= 3

def test_seed_control():
    """测试seed控制"""
    class TestObj(Randomizable):
        value: rand[int](bits=8)

    seed(12345)
    obj1 = TestObj()
    obj1.randomize()
    val1 = obj1.value

    seed(12345)
    obj2 = TestObj()
    obj2.randomize()
    val2 = obj2.value

    assert val1 == val2

def test_instance_seed():
    """测试实例级seed"""
    class TestObj(Randomizable):
        value: rand[int](bits=8)

    obj = TestObj()
    obj.randomize(seed=42)
    val1 = obj.value

    obj.randomize(seed=42)
    val2 = obj.value

    assert val1 == val2
```

**Step 2: 运行测试**

```bash
pytest tests/test_api/test_integration_basic.py -v
```
Expected: PASS (all 5 tests) - 如果失败，可能需要调整Randomizable的randomize()方法

**Step 3: 调整Randomizable以支持新变量访问**

如果测试失败，需要在Randomizable中添加属性访问支持：

```python
# 在Randomizable类中添加
def __getattr__(self, name: str) -> Any:
    """支持通过self.name访问随机变量值"""
    if name in self._rand_vars:
        var = self._rand_vars[name]
        return getattr(var, 'value', None)
    if name in self._randc_vars:
        var = self._randc_vars[name]
        return getattr(var, 'value', None)
    raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

def __setattr__(self, name: str, value: Any) -> None:
    """支持设置随机变量值"""
    if name in self._rand_vars:
        self._rand_vars[name].value = value
    elif name in self._randc_vars:
        self._randc_vars[name].value = value
    else:
        super().__setattr__(name, value)
```

**Step 4: 重新运行测试**

```bash
pytest tests/test_api/test_integration_basic.py -v
```
Expected: PASS

**Step 5: 提交**

```bash
git add sv_randomizer/core/randomizable.py tests/test_api/test_integration_basic.py
git commit -m "feat(core): 添加变量属性访问支持

- 实现__getattr__支持self.xxx访问随机变量
- 实现__setattr__支持变量值设置
- 添加集成测试验证基础随机化功能
- 验证seed控制正常工作"
```

---

## M2: Python AST转换器 (1周)

### Task 2.1: 实现Python AST访问者

**Files:**
- Create: `sv_randomizer/api/expression.py`
- Test: `tests/test_api/test_ast_converter.py`

**Step 1: 创建AST转换器测试**

```python
# tests/test_api/test_ast_converter.py
import pytest
from sv_randomizer.api.expression import parse_python_expression
from sv_randomizer.constraints.expressions import (
    BinaryExpr, BinaryOp, VariableExpr, ConstantExpr
)

class MockInstance:
    """模拟Randomizable实例"""
    def __init__(self):
        self.x = 10
        self.y = 20

def test_parse_simple_comparison():
    """测试解析简单比较: self.x > 0"""
    instance = MockInstance()
    expr = parse_python_expression("self.x > 0", instance)

    assert isinstance(expr, BinaryExpr)
    assert isinstance(expr.left, VariableExpr)
    assert expr.left.name == "x"
    assert expr.op == BinaryOp.GT
    assert isinstance(expr.right, ConstantExpr)
    assert expr.right.value == 0

def test_parse_logical_and():
    """测试解析逻辑与: self.x > 0 and self.y < 100"""
    instance = MockInstance()
    expr = parse_python_expression("self.x > 0 and self.y < 100", instance)

    assert isinstance(expr, BinaryExpr)
    assert expr.op == BinaryOp.AND
    assert isinstance(expr.left, BinaryExpr)
    assert isinstance(expr.right, BinaryExpr)

def test_parse_arithmetic():
    """测试解析算术运算: self.x + self.y < 100"""
    instance = MockInstance()
    expr = parse_python_expression("self.x + self.y < 100", instance)

    # 应该解析为: (x + y) < 100
    assert isinstance(expr, BinaryExpr)
    assert expr.op == BinaryOp.LT

def test_parse_chained_comparison():
    """测试链式比较: 0 <= self.x <= 100"""
    instance = MockInstance()
    expr = parse_python_expression("0 <= self.x <= 100", instance)

    # 应该解析为: 0 <= x and x <= 100
    assert isinstance(expr, BinaryExpr)
    assert expr.op == BinaryOp.AND
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_api/test_ast_converter.py -v
```
Expected: FAIL - 模块不存在

**Step 3: 实现AST转换器**

```python
# sv_randomizer/api/expression.py
"""
Python表达式AST转换器

将原生Python表达式转换为框架的Expression AST
"""
import ast
from ..constraints.expressions import (
    BinaryExpr, BinaryOp, UnaryExpr, UnaryOp,
    VariableExpr, ConstantExpr, Expression
)


class PythonExpressionConverter(ast.NodeVisitor):
    """
    Python AST → Expression AST 转换器

    支持的Python语法：
    - 比较运算: ==, !=, <, >, <=, >=
    - 逻辑运算: and, or, not
    - 算术运算: +, -, *, /, %, **
    - 位运算: &, |, ^, ~, <<, >>
    - 属性访问: self.xxx
    - 常量: 数字, 字符串, 布尔值
    """

    def __init__(self, instance):
        """
        Args:
            instance: Randomizable实例（用于验证属性名）
        """
        self.instance = instance

    def visit(self, node):
        """入口方法"""
        if node is None:
            return ConstantExpr(None)
        return super().visit(node)

    def visit_Compare(self, node):
        """
        处理比较运算

        支持链式比较: a < x < b → (a < x) and (x < b)
        """
        left = self.visit(node.left)

        # 处理链式比较
        if len(node.comparators) > 1:
            # a op1 b op2 c → (a op1 b) and (b op2 c)
            result = BinaryExpr(
                left,
                self._convert_cmp_op(node.ops[0]),
                self.visit(node.comparators[0])
            )

            for i in range(1, len(node.comparators)):
                next_left = self.visit(node.comparators[i-1])
                next_right = self.visit(node.comparators[i])
                next_op = self._convert_cmp_op(node.ops[i])

                next_expr = BinaryExpr(next_left, next_op, next_right)
                result = BinaryExpr(result, BinaryOp.AND, next_expr)

            return result

        # 单个比较
        op = self._convert_cmp_op(node.ops[0])
        right = self.visit(node.comparators[0])
        return BinaryExpr(left, op, right)

    def visit_BoolOp(self, node):
        """处理逻辑运算: and, or"""
        if isinstance(node.op, ast.And):
            op = BinaryOp.AND
        elif isinstance(node.op, ast.Or):
            op = BinaryOp.OR
        else:
            raise ValueError(f"Unsupported boolean operator: {type(node.op)}")

        result = self.visit(node.values[0])
        for value in node.values[1:]:
            result = BinaryExpr(result, op, self.visit(value))
        return result

    def visit_UnaryOp(self, node):
        """处理一元运算: not, -, ~"""
        op = self._convert_unary_op(node.op)
        operand = self.visit(node.operand)
        return UnaryExpr(op, operand)

    def visit_BinOp(self, node):
        """处理二元运算: +, -, *, /, %, etc."""
        left = self.visit(node.left)
        op = self._convert_bin_op(node.op)
        right = self.visit(node.right)
        return BinaryExpr(left, op, right)

    def visit_Attribute(self, node):
        """
        处理属性访问: self.xxx

        只支持self.xxx形式，不支持嵌套属性
        """
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            # 验证属性是否存在
            attr_name = node.attr
            if not hasattr(self.instance, attr_name):
                raise AttributeError(
                    f"'{self.instance.__class__.__name__}' has no attribute '{attr_name}'"
                )
            return VariableExpr(attr_name)

        raise ValueError(
            f"Only 'self.xxx' attributes are supported, got: {ast.dump(node)}"
        )

    def visit_Name(self, node):
        """处理变量名: True, False, None"""
        if node.id == 'True':
            return ConstantExpr(True)
        elif node.id == 'False':
            return ConstantExpr(False)
        elif node.id == 'None':
            return ConstantExpr(None)
        else:
            # 其他名称作为变量处理
            return VariableExpr(node.id)

    def visit_Constant(self, node):
        """处理常量: 数字, 字符串, 布尔值"""
        return ConstantExpr(node.value)

    def visit_Num(self, node):
        """Python 3.7兼容: 处理数字常量"""
        return ConstantExpr(node.n)

    def visit_Str(self, node):
        """Python 3.7兼容: 处理字符串常量"""
        return ConstantExpr(node.s)

    def visit_NameConstant(self, node):
        """Python 3.7兼容: 处理True/False/None"""
        return ConstantExpr(node.value)

    def _convert_cmp_op(self, op) -> BinaryOp:
        """转换Python比较运算符到BinaryOp"""
        mapping = {
            ast.Eq: BinaryOp.EQ,
            ast.NotEq: BinaryOp.NE,
            ast.Lt: BinaryOp.LT,
            ast.LtE: BinaryOp.LE,
            ast.Gt: BinaryOp.GT,
            ast.GtE: BinaryOp.GE,
        }
        op_type = type(op)
        if op_type not in mapping:
            raise ValueError(f"Unsupported comparison operator: {op_type}")
        return mapping[op_type]

    def _convert_bin_op(self, op) -> BinaryOp:
        """转换Python二元运算符到BinaryOp"""
        mapping = {
            ast.Add: BinaryOp.ADD,
            ast.Sub: BinaryOp.SUB,
            ast.Mult: BinaryOp.MUL,
            ast.Div: BinaryOp.DIV,
            ast.Mod: BinaryOp.MOD,
            ast.Pow: BinaryOp.POW,
            ast.FloorDiv: BinaryOp.DIV,
            ast.BitAnd: BinaryOp.BITAND,
            ast.BitOr: BinaryOp.BITOR,
            ast.BitXor: BinaryOp.BITXOR,
            ast.LShift: BinaryOp.LSHIFT,
            ast.RShift: BinaryOp.RSHIFT,
        }
        op_type = type(op)
        if op_type not in mapping:
            raise ValueError(f"Unsupported binary operator: {op_type}")
        return mapping[op_type]

    def _convert_unary_op(self, op) -> UnaryOp:
        """转换Python一元运算符到UnaryOp"""
        from ..constraints.expressions import UnaryOp as UnaryOpEnum
        mapping = {
            ast.Not: UnaryOpEnum.NOT,
            ast.USub: UnaryOpEnum.NEG,
            ast.UAdd: UnaryOpEnum.POS,
            ast.Invert: UnaryOpEnum.BITNOT,
        }
        op_type = type(op)
        if op_type not in mapping:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return mapping[op_type]


def parse_python_expression(source_code: str, instance) -> Expression:
    """
    将Python表达式字符串转换为框架Expression对象

    Args:
        source_code: Python表达式代码（如 "self.x > 0 and self.y < 100"）
        instance: Randomizable实例（用于属性验证）

    Returns:
        Expression对象

    Raises:
        ValueError: 表达式语法不支持
        SyntaxError: 表达式语法错误
    """
    # 解析为AST
    try:
        tree = ast.parse(source_code, mode='eval')
    except SyntaxError as e:
        raise SyntaxError(f"Invalid Python expression: {e}")

    # 转换为Expression
    converter = PythonExpressionConverter(instance)
    try:
        return converter.visit(tree.body)
    except Exception as e:
        raise ValueError(f"Failed to convert expression: {e}")


__all__ = ['PythonExpressionConverter', 'parse_python_expression']
```

**Step 4: 运行测试**

```bash
pytest tests/test_api/test_ast_converter.py -v
```
Expected: PASS (all 4 tests)

**Step 5: 提交**

```bash
git add sv_randomizer/api/expression.py tests/test_api/test_ast_converter.py
git commit -m "feat(api): 实现Python AST到Expression转换器

- 实现PythonExpressionConverter访问者类
- 支持比较、逻辑、算术、位运算
- 支持链式比较（a <= x <= b）
- 支持self.xxx属性访问
- 添加完整单元测试"
```

---

### Task 2.2: 扩展AST转换器支持更多语法

**Files:**
- Modify: `sv_randomizer/api/expression.py`
- Test: `tests/test_api/test_ast_converter_advanced.py`

**Step 1: 创建高级测试**

```python
# tests/test_api/test_ast_converter_advanced.py
import pytest
from sv_randomizer.api.expression import parse_python_expression
from sv_randomizer.constraints.expressions import BinaryExpr, BinaryOp

class MockInstance:
    def __init__(self):
        self.x = 10
        self.y = 20
        self.z = 5

def test_modulo_operator():
    """测试取模运算: self.x % 2 == 0"""
    expr = parse_python_expression("self.x % 2 == 0", MockInstance())
    assert expr.op == BinaryOp.EQ

def test_bitwise_operators():
    """测试位运算"""
    expr = parse_python_expression("self.x & 0xFF", MockInstance())
    assert expr.op == BinaryOp.BITAND

def test_complex_expression():
    """测试复杂表达式: (self.x + self.y) * 2 > self.z"""
    expr = parse_python_expression("(self.x + self.y) * 2 > self.z", MockInstance())
    assert expr.op == BinaryOp.GT

def test_not_operator():
    """测试not运算: not (self.x > 100)"""
    expr = parse_python_expression("not (self.x > 100)", MockInstance())
    # not会被转换为UnaryExpr
    from sv_randomizer.constraints.expressions import UnaryExpr, UnaryOp
    assert isinstance(expr, UnaryExpr)
    assert expr.op == UnaryOp.NOT

def test_or_operator():
    """测试or运算: self.x < 0 or self.x > 100"""
    expr = parse_python_expression("self.x < 0 or self.x > 100", MockInstance())
    assert expr.op == BinaryOp.OR
```

**Step 2: 运行测试**

```bash
pytest tests/test_api/test_ast_converter_advanced.py -v
```
Expected: PASS (或FAIL如果某些运算符未实现)

**Step 3: 根据需要扩展expression.py**

如果测试失败，检查并添加缺失的运算符支持。

**Step 4: 提交**

```bash
git add sv_randomizer/api/expression.py tests/test_api/test_ast_converter_advanced.py
git commit -m "feat(api): 扩展AST转换器支持更多运算符

- 支持取模、位运算等高级运算符
- 支持not一元运算符
- 添加复杂表达式测试
- 完善错误处理"
```

---

## M3: 约束装饰器实现 (1周)

### Task 3.1: 实现constraint装饰器

**Files:**
- Modify: `sv_randomizer/api/__init__.py`
- Modify: `sv_randomizer/api/annotations.py`
- Test: `tests/test_api/test_constraint_decorator.py`

**Step 1: 创建约束装饰器测试**

```python
# tests/test_api/test_constraint_decorator.py
import pytest
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint

def test_simple_constraint():
    """测试简单约束"""
    class TestObj(Randomizable):
        x: rand[int](bits=8)

        @constraint
        def x_positive(self):
            return self.x > 0

    obj = TestObj()
    # 验证约束被注册
    assert 'x_positive' in obj._constraints

    # 验证约束生效
    for _ in range(20):
        obj.randomize()
        assert obj.x > 0

def test_multiple_constraints():
    """测试多个约束"""
    class TestObj(Randomizable):
        x: rand[int](bits=8)
        y: rand[int](bits=8)

        @constraint
        def x_less_than_y(self):
            return self.x < self.y

        @constraint
        def sum_less_than_100(self):
            return self.x + self.y < 100

    obj = TestObj()
    for _ in range(20):
        obj.randomize()
        assert obj.x < obj.y
        assert obj.x + obj.y < 100

def test_and_constraint():
    """测试and逻辑"""
    class TestObj(Randomizable):
        x: rand[int](bits=8)

        @constraint
        def x_in_range(self):
            return self.x >= 10 and self.x <= 50

    obj = TestObj()
    for _ in range(20):
        obj.randomize()
        assert 10 <= obj.x <= 50
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_api/test_constraint_decorator.py -v
```
Expected: FAIL - constraint装饰器未正确实现

**Step 3: 实现constraint装饰器**

在 `sv_randomizer/api/annotations.py` 中添加：

```python
# 在 sv_randomizer/api/annotations.py 末尾添加

def constraint(func):
    """
    约束装饰器 - 标记约束方法

    使用方式:
        @constraint
        def my_constraint(self):
            return self.x > 0

    被装饰的方法将在Randomizable初始化时被解析，
    其返回的Python表达式会被转换为Expression对象
    """
    func._is_constraint = True
    return func
```

在 `sv_randomizer/core/randomizable.py` 的 `__init__` 方法中添加约束解析：

```python
# 在Randomizable.__init__方法末尾添加

def __init__(self, seed: Optional[int] = None):
    # ... 现有初始化代码 ...

    # 解析约束方法
    self._parse_constraints()

def _parse_constraints(self):
    """解析所有约束方法，将Python表达式转换为Expression"""
    # 遍历类的所有属性
    for attr_name in dir(self.__class__):
        if attr_name.startswith('_'):
            continue

        attr = getattr(self.__class__, attr_name, None)
        if attr is None:
            continue

        # 检查是否为约束方法
        if hasattr(attr, '_is_constraint'):
            try:
                # 获取方法的源代码
                import inspect
                source = inspect.getsource(attr)

                # 解析AST，提取return语句后的表达式
                tree = ast.parse(source)
                function_node = tree.body[0]

                # 找到return语句
                return_stmt = None
                for node in ast.walk(function_node):
                    if isinstance(node, ast.Return) and node.value is not None:
                        return_stmt = node
                        break

                if return_stmt is None:
                    continue

                # 将Python表达式转换为Expression
                from ..api.expression import parse_python_expression
                expr_str = ast.unparse(return_stmt.value)
                expr = parse_python_expression(expr_str, self)

                # 创建约束对象
                from ..constraints.base import ExpressionConstraint
                constraint_obj = ExpressionConstraint(attr_name, expr)
                self.add_constraint(constraint_obj)

            except Exception as e:
                import warnings
                warnings.warn(f"Failed to parse constraint '{attr_name}': {e}")
```

**Step 4: 运行测试**

```bash
pytest tests/test_api/test_constraint_decorator.py -v
```
Expected: PASS (all 3 tests)

**Step 5: 提交**

```bash
git add sv_randomizer/api/annotations.py sv_randomizer/core/randomizable.py tests/test_api/test_constraint_decorator.py
git commit -m "feat(api): 实现constraint装饰器

- constraint装饰器标记约束方法
- Randomizable初始化时自动解析约束方法
- 将Python表达式转换为Expression对象
- 添加约束装饰器单元测试"
```

---

### Task 3.2: 更新API导出

**Files:**
- Modify: `sv_randomizer/api/__init__.py`

**Step 1: 更新__init__.py导出新API**

```python
# sv_randomizer/api/__init__.py
"""
新API导出 - 类型注解和约束装饰器
"""

# 类型注解和装饰器
from .annotations import rand, randc, constraint

# Seed控制（从seeding模块导入）
from ..core.seeding import set_global_seed as seed
from ..core.seeding import get_global_seed

# Randomizable基类
from ..core.randomizable import Randomizable

# 便捷函数
from .annotations import (
    is_rand_annotation, is_randc_annotation,
    extract_rand_metadata, extract_randc_metadata
)

__all__ = [
    # 核心类
    'Randomizable',

    # 类型注解
    'rand', 'randc', 'constraint',

    # Seed控制
    'seed',
    'get_global_seed',

    # 内部API（用于高级用法）
    'is_rand_annotation', 'is_randc_annotation',
    'extract_rand_metadata', 'extract_randc_metadata',
]
```

**Step 2: 测试导入**

```python
# 测试导入是否正常
from sv_randomizer.api import rand, randc, constraint, seed, Randomizable
from sv_randomizer import Randomizable as R  # 从顶层导入

print("Import test passed!")
```

```bash
python -c "from sv_randomizer.api import rand, randc, constraint, seed, Randomizable; print('OK')"
```
Expected: OK

**Step 3: 提交**

```bash
git add sv_randomizer/api/__init__.py
git commit -m "feat(api): 更新__init__.py导出新API

- 导出rand, randc, constraint装饰器
- 导出seed函数
- 导出Randomizable基类
- 保持向后兼容的导入路径"
```

---

## M4: 更新示例和测试 (1周)

### Task 4.1: 更新基础示例

**Files:**
- Modify: `examples/rand/packet_generator.py`
- Modify: `examples/rand/simple_test.py`

**Step 1: 更新packet_generator.py**

```python
# examples/rand/packet_generator.py - 使用新API
from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc, constraint

class Packet(Randomizable):
    """网络数据包 - 新API版本"""

    # 变量声明
    src_addr: rand[int](bits=16, min=0x1000, max=0xFFFF)
    dest_addr: rand[int](bits=16)
    length: rand[int](bits=8, min=64, max=1500)
    packet_id: randc[int](bits=4)
    opcode: rand[enum]("READ", "WRITE", "ACK", "NACK")

    # 约束
    @constraint
    def valid_addr_range(self):
        return self.src_addr >= 0x1000 and self.src_addr <= 0xFFFF

    @constraint
    def addr_not_equal(self):
        return self.src_addr != self.dest_addr

    @constraint
    def valid_length(self):
        return self.length in [64, 128, 256] or (512 <= self.length <= 1518)

    def pre_randomize(self):
        """随机化前回调"""
        pass

    def post_randomize(self):
        """随机化后回调"""
        pass

# ... 其余示例代码保持不变 ...
```

**Step 2: 运行示例**

```bash
python examples/rand/packet_generator.py
```
Expected: 正常运行，生成随机数据包

**Step 3: 提交**

```bash
git add examples/rand/packet_generator.py
git commit -m "examples: 更新packet_generator使用新API

- 使用类型注解声明变量
- 使用原生Python表达式编写约束
- 代码量减少约50%"
```

**Step 4: 更新其他示例**

对以下文件重复上述步骤：
- `examples/rand/simple_test.py`
- `examples/rand/solve_inequalities.py`
- `examples/rand/seed_demo.py`

**Step 5: 运行所有示例**

```bash
python examples/rand/simple_test.py
python examples/rand/solve_inequalities.py
python examples/rand/seed_demo.py
```
Expected: 全部通过

**Step 6: 提交所有示例更新**

```bash
git add examples/rand/
git commit -m "examples: 批量更新rand示例使用新API

- 更新simple_test.py
- 更新solve_inequalities.py
- 更新seed_demo.py
- 所有示例现在使用新API"
```

---

### Task 4.2: 删除旧API模块

**Files:**
- Delete: `sv_randomizer/api/decorators.py`
- Delete: `sv_randomizer/api/dsl.py`

**Step 1: 检查旧API的使用情况**

```bash
grep -r "from sv_randomizer.api.decorators import" --include="*.py" .
grep -r "from.*decorators.*import" --include="*.py" sv_randomizer/
```

确认没有其他代码依赖旧API。

**Step 2: 备份旧API**

```bash
mkdir -p .backup/old_api
cp sv_randomizer/api/decorators.py .backup/old_api/
cp sv_randomizer/api/dsl.py .backup/old_api/
```

**Step 3: 删除旧文件**

```bash
rm sv_randomizer/api/decorators.py
rm sv_randomizer/api/dsl.py
```

**Step 4: 更新导入引用**

如果有文件导入了旧API，更新它们：

```python
# 旧导入
from sv_randomizer.api.decorators import rand, randc, constraint

# 新导入
from sv_randomizer.api import rand, randc, constraint
```

**Step 5: 运行测试确保没有破坏**

```bash
pytest tests/test_api/ -v
pytest tests/test_rgm/ -v
```
Expected: 全部通过

**Step 6: 提交**

```bash
git add -A
git commit -m "refactor(api): 删除旧装饰器API

- 删除api/decorators.py
- 删除api/dsl.py
- 完全迁移到新API
- 所有测试通过"
```

---

## M5: 文档和迁移工具 (1周)

### Task 5.1: 编写迁移指南

**Files:**
- Create: `docs/guides/migration-v0.3-to-v0.3.1.md`

**Step 1: 创建迁移指南文档**

```markdown
# API v0.3 → v0.3.1 迁移指南

**重要变更**: v0.3.1是一个不兼容更新，旧API已被移除。

## 快速参考

### 变量声明

| 旧API | 新API |
|-------|-------|
| `@rand(bit_width=16)`<br>`def addr(self): return 0` | `addr: rand[int](bits=16)` |
| `@randc(bit_width=4)`<br>`def id(self): return 0` | `id: randc[int](bits=4)` |
| `@rand(enum_values=["A", "B"])`<br>`def op(self): return "A"` | `op: rand[enum]("A", "B")` |
| `@rand(bit_width=8, min_val=0, max_val=100)` | `rand[int](bits=8, min=0, max=100)` |

### 约束

| 旧API | 新API |
|-------|-------|
| `@constraint("name", "x > 0 && x < 100")`<br>`def c(self): pass` | `@constraint`<br>`def name(self):`<br>`    return self.x > 0 and self.x < 100` |
| `VarProxy("x") > 0` | `self.x > 0` |
| `&&`, `\|\|` | `and`, `or` |

## 完整示例

### 旧API (v0.3.0)

```python
from sv_randomizer import Randomizable
from sv_randomizer.api.decorators import rand, randc, constraint
from sv_randomizer.api.dsl import VarProxy

class Packet(Randomizable):
    @rand(bit_width=16)
    def src_addr(self):
        return 0

    @rand(bit_width=8, min_val=0, max_val=1500)
    def length(self):
        return 64

    @randc(bit_width=4)
    def packet_id(self):
        return 0

    @rand(enum_values=["READ", "WRITE"])
    def opcode(self):
        return "READ"

    @constraint("valid_addr", "src_addr >= 0x1000 && src_addr <= 0xFFFF")
    def valid_addr_c(self):
        pass
```

### 新API (v0.3.1)

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint

class Packet(Randomizable):
    src_addr: rand[int](bits=16, min=0x1000, max=0xFFFF)
    length: rand[int](bits=8, min=64, max=1500)
    packet_id: randc[int](bits=4)
    opcode: rand[enum]("READ", "WRITE")

    @constraint
    def valid_addr(self):
        return self.src_addr >= 0x1000 and self.src_addr <= 0xFFFF
```

**代码减少**: 约50%

## 无需改动

以下API保持不变，无需修改代码：

- `randomize()` 调用
- `seed()` 控制
- `constraint_mode()` / `rand_mode()` 切换
- 求解器后端选择
- 所有RGM和Coverage API

## 迁移步骤

1. 更新导入语句
2. 将装饰器变量改为类型注解
3. 重写约束为Python表达式
4. 运行测试验证

## 自动迁移工具

```bash
python -m sv_randomizer.tools.migrate --path . --api-version v0.3.1
```
```

**Step 2: 提交**

```bash
git add docs/guides/migration-v0.3-to-v0.3.1.md
git commit -m "docs: 添加v0.3到v0.3.1迁移指南

- 详细的API对照表
- 完整的迁移示例
- 逐步迁移说明"
```

---

### Task 5.2: 更新API参考文档

**Files:**
- Create: `docs/api/new-api-reference.md`

**Step 1: 创建新API参考文档**

```markdown
# EDA_UFVM API参考 (v0.3.1+)

## 类型注解API

### rand[int](bits=N, min=X, max=Y)

声明普通随机变量（值可重复）。

**参数**:
- `bits`: 位宽（1-64）
- `min`: 最小值（可选，默认0）
- `max`: 最大值（可选，默认为2^bits-1）

**示例**:
```python
addr: rand[int](bits=16, min=0x1000, max=0xFFFF)
```

### randc[int](bits=N)

声明循环随机变量（遍历所有值后才重复）。

**参数**:
- `bits`: 位宽（1-64）

**示例**:
```python
tid: randc[int](bits=4)  # 0-15循环，不重复
```

### rand[enum]("A", "B", "C")

声明枚举类型随机变量。

**参数**:
- 可变参数：所有可能的枚举值

**示例**:
```python
opcode: rand[enum]("READ", "WRITE", "ACK")
```

### @constraint

约束装饰器，使用原生Python表达式。

**示例**:
```python
@constraint
def x_in_range(self):
    return self.x > 0 and self.x < 100
```

## 支持的Python语法

### 比较运算
- `==`, `!=`, `<`, `>`, `<=`, `>=`
- 链式比较: `0 <= x <= 100`

### 逻辑运算
- `and`, `or`, `not`

### 算术运算
- `+`, `-`, `*`, `/`, `%`, `**`

### 位运算
- `&`, `|`, `^`, `~`, `<<`, `>>`

## Randomizable方法

### randomize(with_constraints=None)

随机化对象。

**参数**:
- `with_constraints`: 内联约束字典（可选）

**返回**: bool - 是否成功

### constraint_mode(name, enabled)

启用/禁用约束。

### rand_mode(name, enabled)

启用/禁用随机变量。

## Seed控制

### seed(value)

设置全局随机种子。

### randomize(seed=value)

设置单次随机化的种子。
```

**Step 2: 提交**

```bash
git add docs/api/new-api-reference.md
git commit -m "docs: 添加新API参考文档

- 类型注解API完整说明
- 支持的Python语法列表
- Randomizable方法参考"
```

---

### Task 5.3: 更新README和CHANGELOG

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`

**Step 1: 更新README中的示例代码**

将README中的所有示例代码从旧API更新为新API。

**Step 2: 在CHANGELOG中添加v0.3.1条目**

```markdown
## [0.3.1] - 2026-03-XX

### Breaking Changes
- **新API**: 使用类型注解声明随机变量
- **新API**: 约束使用原生Python表达式
- **移除**: 旧装饰器API（@rand bit_width=等）

### Added
- 类型注解API: rand[int](bits=16), randc[int](bits=4)
- Python原生表达式约束
- 元类自动解析类型注解
- Python AST到Expression转换器

### Changed
- 代码量减少约50%
- 更符合Python直觉
- 更好的IDE类型提示支持

### Migration
- 详见迁移指南: docs/guides/migration-v0.3-to-v0.3.1.md
```

**Step 3: 提交**

```bash
git add README.md CHANGELOG.md
git commit -m "docs: 更新README和CHANGELOG

- README示例代码使用新API
- 添加v0.3.1 CHANGELOG条目
- 标注Breaking Changes"
```

---

## 验收测试

### Final Test 1: 运行所有测试

```bash
# 新API测试
pytest tests/test_api/ -v

# 集成测试
pytest tests/integration/ -v

# RGM测试（应该仍然工作）
pytest tests/test_rgm/ -v

# Coverage测试（应该仍然工作）
python run_coverage_tests.py
```

Expected: 所有测试通过

### Final Test 2: 性能基准

```python
# tests/performance/bench_new_api.py
import time
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc

class TestPacket(Randomizable):
    addr: rand[int](bits=32)
    data: rand[int](bits=8)
    tid: randc[int](bits=4)

# 基准测试
iterations = 10000
start = time.time()
for _ in range(iterations):
    pkt = TestPacket()
    pkt.randomize()
elapsed = time.time() - start

print(f"Performance: {iterations/elapsed:.0f} randomizations/sec")
print(f"Target: >10,000 randomizations/sec")
```

```bash
python tests/performance/bench_new_api.py
```

Expected: 性能不低于旧API的90%

### Final Test 3: 端到端测试

```python
# tests/integration/test_end_to_end.py
from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc, constraint

class NetworkPacket(Randomizable):
    src: rand[int](bits=16, min=0x1000, max=0xFFFF)
    dest: rand[int](bits=16)
    opcode: rand[enum]("READ", "WRITE")

    @constraint
    def addr_valid(self):
        return self.src >= 0x1000 and self.dest >= 0x1000

    @constraint
    def addr_different(self):
        return self.src != self.dest

# 测试所有功能
seed(12345)
pkt = NetworkPacket()
assert pkt.randomize()

print(f"✓ Randomization works: src=0x{pkt.src:04x}, dest=0x{pkt.dest:04x}")

# 测试约束
for _ in range(100):
    pkt.randomize()
    assert pkt.src != pkt.dest

print("✓ Constraints work")

# 测试seed
seed(12345)
pkt2 = NetworkPacket()
pkt2.randomize()
assert pkt2.src == pkt.src

print("✓ Seed control works")

print("\n✅ All end-to-end tests passed!")
```

```bash
python tests/integration/test_end_to_end.py
```

Expected: 全部通过

---

## 完成检查清单

在实施完成后，验证以下各项：

- [ ] 所有新测试通过（tests/test_api/）
- [ ] 所有RGM测试仍然通过（tests/test_rgm/）
- [ ] 所有Coverage测试仍然通过（run_coverage_tests.py）
- [ ] 所有示例代码更新并运行成功（examples/rand/）
- [ ] 性能基准测试通过（不低于旧API 90%）
- [ ] 迁移指南文档完整
- [ ] API参考文档完整
- [ ] README和CHANGELOG更新
- [ ] 旧API模块已删除
- [ ] 代码已提交到git

---

## 实施注意事项

### TDD原则
每个任务都遵循：写测试 → 运行（失败）→ 实现代码 → 运行（通过）→ 提交

### 频繁提交
每个小任务完成后立即提交，保持提交历史清晰。

### 参考文档
遇到问题时参考：
- 设计文档: `docs/plans/2026-03-01-api-usability-redesign.md`
- 当前实现: `sv_randomizer/core/randomizable.py`
- 约束系统: `sv_randomizer/constraints/expressions.py`

### 调试技巧
```python
# 查看类的变量
print(MyClass._rand_vars)
print(MyClass._randc_vars)

# 查看实例的约束
print(obj._constraints)

# 解析后的表达式
from sv_randomizer.api.expression import parse_python_expression
expr = parse_python_expression("self.x > 0", obj)
print(expr)
```

---

**计划创建日期**: 2026-03-01
**预计完成时间**: 5周
**目标版本**: v0.3.1
