# 随机种子控制功能 - 设计文档

## 功能概述

随机种子控制功能允许用户控制随机数生成器的种子，以确保测试的可重复性和便于调试。支持三个层次的种子控制：全局级、对象级和临时级。

---

## 功能需求

### 1. 可重复性

**需求**: 相同的随机种子应产生相同的随机序列

**场景**:
- 回归测试：确保每次运行结果一致
- CI/CD流水线：可预测的测试输出
- 问题复现：重现特定的随机场景

### 2. 调试支持

**需求**: 可以通过种子重现问题场景

**场景**:
- 测试失败时，记录种子值
- 使用相同种子在本地重现问题
- 逐步调试特定随机场景

### 3. 多层次控制

**需求**: 支持全局、对象级、求解器级三个层次的种子设置

**场景**:
- 全局种子：影响所有新创建的对象
- 对象级种子：单个对象独立控制
- 临时种子：单次randomize()使用不同种子

---

## 架构设计

### 设计策略

采用**混合策略**：使用独立的Random实例传递，同时提供全局种子便捷API。

### 优势

- **独立性**: 每个Randomizable对象有独立的Random实例，避免互相干扰
- **可预测性**: 相同种子序列产生相同结果
- **灵活性**: 支持全局、对象级、求解器级三个层次的种子设置
- **向后兼容**: 不设置种子时行为与现有代码一致

### 层次结构

```
┌─────────────────────────────────────────────┐
│         全局种子 (Global Seed)               │
│  set_global_seed(42)                         │
│  影响所有后续创建的Randomizable对象          │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│       对象级种子 (Object-level Seed)         │
│  obj = Packet(seed=123)                      │
│  覆盖全局种子，仅影响此对象                  │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│       临时种子 (Temporary Seed)              │
│  obj.randomize(seed=456)                     │
│  仅影响本次randomize()，不改变对象状态       │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│       求解器级种子 (Solver-level Seed)       │
│  自动继承对象级种子                          │
└─────────────────────────────────────────────┘
```

---

## API设计

### 1. 全局种子API

**文件**: `sv_randomizer/core/seeding.py` (新建)

```python
from typing import Optional
import random

_global_seed: Optional[int] = None

def set_global_seed(seed: Optional[int]) -> None:
    """
    设置全局随机种子

    影响所有后续创建的Randomizable对象（除非指定对象级种子）

    Args:
        seed: 随机种子，None表示使用系统熵

    Example:
        >>> set_global_seed(42)
        >>> obj1 = MyPacket()  # 使用种子42
        >>> obj2 = MyPacket()  # 使用种子42，从同一序列继续
    """
    global _global_seed
    _global_seed = seed

def get_global_seed() -> Optional[int]:
    """
    获取当前全局种子设置

    Returns:
        当前全局种子，None表示未设置

    Example:
        >>> seed = get_global_seed()
        >>> print(f"Global seed: {seed}")
    """
    return _global_seed

def reset_global_seed() -> None:
    """
    重置全局种子为None

    重置后创建的对象将使用系统熵

    Example:
        >>> reset_global_seed()
        >>> obj = MyPacket()  # 使用系统熵
    """
    global _global_seed
    _global_seed = None

def create_random_instance(seed: Optional[int] = None) -> random.Random:
    """
    创建Random实例

    优先级: 传入seed > 全局种子 > 系统熵

    Args:
        seed: 随机种子，None则使用全局种子或系统熵

    Returns:
        Random实例

    Example:
        >>> rand = create_random_instance(42)
        >>> value = rand.randint(0, 100)
    """
    if seed is not None:
        return random.Random(seed)
    elif _global_seed is not None:
        return random.Random(_global_seed)
    else:
        return random.Random()
```

### 2. Randomizable类扩展

**文件**: `sv_randomizer/core/randomizable.py`

```python
from typing import Optional
import random

class Randomizable:
    def __init__(self, seed: Optional[int] = None):
        """
        初始化Randomizable对象

        Args:
            seed: 随机种子，None则使用全局种子
        """
        self._rand_vars: Dict[str, RandVar] = {}
        self._randc_vars: Dict[str, RandCVar] = {}
        self._constraints: List[Constraint] = []
        self._constraint_modes: Dict[str, bool] = {}
        self._var_modes: Dict[str, bool] = {}

        # 新增：种子管理
        self._seed: Optional[int] = seed
        self._random: Optional[random.Random] = None

    def set_seed(self, seed: Optional[int]) -> None:
        """
        设置或重置此对象的随机种子

        Args:
            seed: 随机种子，None则使用全局种子

        Example:
            >>> obj = MyPacket()
            >>> obj.set_seed(42)
            >>> obj.randomize()  # 使用种子42
        """
        self._seed = seed
        self._random = None  # 重置Random实例（延迟创建）

    def get_seed(self) -> Optional[int]:
        """
        获取当前种子设置

        Returns:
            当前种子，None表示未设置（使用全局种子）

        Example:
            >>> seed = obj.get_seed()
            >>> print(f"Object seed: {seed}")
        """
        return self._seed

    def get_random(self) -> random.Random:
        """
        获取此对象的Random实例（延迟创建）

        优先级: 对象级种子 > 全局种子 > 系统熵

        Returns:
            Random实例

        Example:
            >>> rand = obj.get_random()
            >>> value = rand.randint(0, 100)
        """
        if self._random is None:
            if self._seed is not None:
                self._random = random.Random(self._seed)
            else:
                # 使用全局种子管理器
                from .seeding import create_random_instance
                self._random = create_random_instance()
        return self._random

    def randomize(self, seed: Optional[int] = None) -> bool:
        """
        执行随机化

        Args:
            seed: 可选的临时种子，覆盖对象种子

        Returns:
            True表示成功，False表示约束冲突无解

        Example:
            >>> obj = MyPacket()
            >>> # 使用对象级种子
            >>> obj.randomize()
            >>> # 使用临时种子（不影响对象状态）
            >>> obj.randomize(seed=456)
        """
        # 1. 调用pre_randomize
        self.pre_randomize()

        # 2. 确定使用的Random实例
        if seed is not None:
            # 临时种子：创建临时Random实例
            rand = random.Random(seed)
        else:
            # 使用对象级Random实例
            rand = self.get_random()

        # 3. 收集活跃的变量和约束
        active_vars = self._get_active_vars()
        active_constraints = self._get_active_constraints()

        if not active_vars and not active_constraints:
            self.post_randomize()
            return True

        # 4. 应用内联约束（如果有）
        if with_constraints:
            inline_constraints = self._build_inline_constraints(with_constraints)
            active_constraints.extend(inline_constraints)

        # 5. 调用求解器
        try:
            solver = SolverFactory.get_solver(
                self._solver_backend,
                random_instance=rand  # 传递Random实例
            )

            # 处理randc变量
            randc_values = {}
            for var_name, var in self._randc_vars.items():
                if var_name in active_vars:
                    # 设置Random实例
                    var.set_random(rand)
                    value = var.get_next()
                    randc_values[var_name] = value
                    setattr(self, var_name, value)

            # 创建求解器变量
            rand_vars = {k: v for k, v in active_vars.items()
                        if k not in self._randc_vars}

            for var_name, var in rand_vars.items():
                # ... 变量创建逻辑 ...

            # 添加约束
            for constraint in active_constraints:
                # ... 约束添加逻辑 ...

            # 求解
            solution = solver.solve()

            if solution is None:
                return False

            # 应用解
            for var_name, value in solution.items():
                if var_name in self._rand_vars:
                    self._rand_vars[var_name].current_value = value
                setattr(self, var_name, value)

            # 6. 调用post_randomize
            self.post_randomize()
            return True

        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
```

### 3. 变量系统修改

**文件**: `sv_randomizer/core/variables.py`

#### RandVar修改

```python
class RandVar:
    # ... 现有代码 ...

    def generate_unconstrained(self, rand: Optional[random.Random] = None) -> Any:
        """
        生成无约束随机值

        Args:
            rand: Random实例，None则使用全局random模块

        Returns:
            随机值
        """
        if rand is None:
            # 向后兼容：使用全局random模块
            rand_instance = random
        else:
            rand_instance = rand

        if self.var_type == VarType.INT:
            return rand_instance.randint(self.min_val, self.max_val)
        elif self.var_type == VarType.BIT:
            max_val = (1 << self.bit_width) - 1
            return rand_instance.randint(0, max_val)
        elif self.var_type == VarType.ENUM:
            return rand_instance.choice(self.enum_values)
        elif self.var_type == VarType.BOOL:
            return rand_instance.choice([True, False])
        else:
            raise ValueError(f"Unsupported var_type: {self.var_type}")
```

#### RandCVar修改

```python
class RandCVar:
    def __init__(self, name: str, var_type: VarType,
                 bit_width: Optional[int] = None,
                 enum_values: Optional[List[Any]] = None):
        # ... 现有代码 ...
        self._random: Optional[random.Random] = None
        self._initialize_pool()

    def set_random(self, rand: random.Random) -> None:
        """
        设置Random实例

        Args:
            rand: Random实例
        """
        self._random = rand
        # 重置值池以使用新的Random实例
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """初始化并打乱值池"""
        if self.var_type == VarType.BIT:
            pool_size = 1 << self.bit_width
            self._value_pool = list(range(pool_size))
        elif self.var_type == VarType.ENUM:
            self._value_pool = self.enum_values.copy()
        else:
            raise ValueError(f"Unsupported var_type for randc: {self.var_type}")

        # 使用指定的Random实例或全局random
        rand_instance = self._random if self._random is not None else random
        rand_instance.shuffle(self._value_pool)
```

### 4. 求解器扩展

**文件**: `sv_randomizer/solvers/backend_interface.py`

```python
class SolverBackend(ABC):
    def __init__(self, seed: Optional[int] = None,
                 random_instance: Optional[random.Random] = None):
        """
        初始化求解器后端

        Args:
            seed: 随机种子
            random_instance: Random实例（优先级高于seed）
        """
        if random_instance is not None:
            self._random = random_instance
        elif seed is not None:
            self._random = random.Random(seed)
        else:
            self._random = random.Random()
```

**文件**: `sv_randomizer/solvers/pure_python.py`

```python
class PurePythonBackend(SolverBackend):
    def __init__(self, max_iterations: int = 10000,
                 seed: Optional[int] = None,
                 random_instance: Optional[random.Random] = None):
        """
        初始化PurePython后端

        Args:
            max_iterations: 最大迭代次数
            seed: 随机种子
            random_instance: Random实例（优先级高于seed）
        """
        super().__init__(seed, random_instance)
        self.max_iterations = max_iterations
        self._variables: Dict[str, Any] = {}
        self._constraints: List[Constraint] = []

    def _generate_candidate(self) -> Dict[str, Any]:
        """生成随机候选解"""
        candidate = {}
        for name, var_info in self._variables.items():
            if var_info['type'] == 'int':
                candidate[name] = self._random.randint(
                    var_info['min_val'],
                    var_info['max_val']
                )
            elif var_info['type'] == 'bool':
                candidate[name] = self._random.choice([True, False])
        return candidate
```

**文件**: `sv_randomizer/solvers/solver_factory.py`

```python
class SolverFactory:
    @staticmethod
    def get_solver(backend: Optional[str] = None,
                   random_instance: Optional[random.Random] = None) -> SolverBackend:
        """
        获取求解器实例

        Args:
            backend: 后端名称，None则使用默认后端
            random_instance: Random实例

        Returns:
            求解器实例
        """
        backend = backend or SolverFactory._default_backend

        if backend == "pure_python":
            return PurePythonBackend(random_instance=random_instance)
        elif backend == "z3":
            return Z3Backend(random_instance=random_instance)
        else:
            raise ValueError(f"Unknown backend: {backend}")
```

### 5. 约束系统修改

**文件**: `sv_randomizer/constraints/builders.py`

```python
class DistConstraint(ExpressionConstraint):
    def sample(self, rand: Optional[random.Random] = None) -> Any:
        """
        根据权重采样

        Args:
            rand: Random实例，None则使用全局random模块

        Returns:
            采样值
        """
        if rand is None:
            # 向后兼容
            rand_instance = random
        else:
            rand_instance = rand

        items = list(self.weights.keys())
        weights = list(self.weights.values())
        total = sum(weights)

        # 归一化权重
        normalized = [w / total for w in weights]

        # 加权随机选择
        return rand_instance.choices(items, weights=normalized, k=1)[0]
```

### 6. 导出更新

**文件**: `sv_randomizer/__init__.py`

```python
from .core.seeding import set_global_seed, get_global_seed, reset_global_seed

__all__ = [
    # ... 现有导出 ...
    'set_global_seed',
    'get_global_seed',
    'reset_global_seed',
]
```

---

## 使用示例

### 示例1: 全局种子

```python
from sv_randomizer import set_global_seed, Randomizable, RandVar, VarType

# 设置全局种子
set_global_seed(42)

class Packet(Randomizable):
    def __init__(self):
        super().__init__()  # 自动使用全局种子
        self._rand_vars['addr'] = RandVar('addr', VarType.INT, min_val=0, max_val=1000)

# 创建两个对象，使用相同的全局种子
pkt1 = Packet()
pkt1.randomize()
print(f"Packet 1 addr: {pkt1.addr}")  # 例如: 123

pkt2 = Packet()
pkt2.randomize()
print(f"Packet 2 addr: {pkt2.addr}")  # 例如: 456
# pkt2从pkt1的序列继续，不会重新开始
```

### 示例2: 对象级种子

```python
from sv_randomizer import Randomizable, RandVar, VarType

class Packet(Randomizable):
    def __init__(self, seed=None):
        super().__init__(seed=seed)
        self._rand_vars['data'] = RandVar('data', VarType.INT, min_val=0, max_val=100)

# 使用特定种子
pkt1 = Packet(seed=42)
pkt1.randomize()
print(f"Packet 1 data: {pkt1.data}")  # 固定值，例如: 81

# 使用相同种子创建新对象
pkt2 = Packet(seed=42)
pkt2.randomize()
print(f"Packet 2 data: {pkt2.data}")  # 与pkt1相同: 81

# 使用不同种子
pkt3 = Packet(seed=123)
pkt3.randomize()
print(f"Packet 3 data: {pkt3.data}")  # 不同值，例如: 24
```

### 示例3: 临时种子

```python
from sv_randomizer import Randomizable, RandVar, VarType

class Packet(Randomizable):
    def __init__(self):
        super().__init__()
        self._rand_vars['value'] = RandVar('value', VarType.INT, min_val=0, max_val=100)

pkt = Packet()

# 正常randomize（无种子或使用对象级种子）
pkt.randomize()
print(f"Normal: {pkt.value}")  # 例如: 67

# 使用临时种子（不影响对象状态）
pkt.randomize(seed=42)
print(f"Temp seed 42: {pkt.value}")  # 固定值，例如: 81

# 下次randomize()恢复对象级行为
pkt.randomize()
print(f"Normal again: {pkt.value}")  # 继续序列，例如: 34

# 再次使用相同临时种子，结果相同
pkt.randomize(seed=42)
print(f"Temp seed 42 again: {pkt.value}")  # 仍然是81
```

### 示例4: 可重现性验证

```python
from sv_randomizer import Randomizable, RandVar, RandCVar, VarType

class TestPacket(Randomizable):
    def __init__(self, seed=None):
        super().__init__(seed=seed)
        self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)
        self._randc_vars['id'] = RandCVar('id', VarType.BIT, bit_width=3)

# 生成序列1
pkt1 = TestPacket(seed=42)
values1 = []
for _ in range(10):
    pkt1.randomize()
    values1.append((pkt1.x, pkt1.id))
print(f"Sequence 1: {values1}")

# 生成序列2（应完全相同）
pkt2 = TestPacket(seed=42)
values2 = []
for _ in range(10):
    pkt2.randomize()
    values2.append((pkt2.x, pkt2.id))
print(f"Sequence 2: {values2}")

# 验证
assert values1 == values2, "相同种子应产生相同序列"
print("Reproducibility verified!")
```

### 示例5: 调试场景

```python
from sv_randomizer import Randomizable, RandVar, VarType

class ComplexPacket(Randomizable):
    def __init__(self, seed=None):
        super().__init__(seed=seed)
        self._rand_vars['addr'] = RandVar('addr', VarType.INT, min_val=0, max_val=65535)
        self._rand_vars['len'] = RandVar('len', VarType.INT, min_val=0, max_val=1024)
        # ... 添加约束 ...

def test_packet():
    # 测试失败，记录种子
    import time
    seed = int(time.time()) % 10000
    pkt = ComplexPacket(seed=seed)
    pkt.randomize()

    # 模拟测试失败
    if pkt.addr > 50000 and pkt.len < 100:
        print(f"Test failed with seed: {seed}")
        print(f"  addr={pkt.addr}, len={pkt.len}")
        return seed

    return None

failed_seed = test_packet()

# 使用失败的种子重现问题
if failed_seed:
    print(f"\nReproducing with seed {failed_seed}...")
    pkt = ComplexPacket(seed=failed_seed)
    pkt.randomize()
    print(f"Reproduced: addr={pkt.addr}, len={pkt.len}")
    # 现在可以设置断点调试
```

---

## 实现步骤

### 阶段1: 核心种子基础设施

**文件**: `sv_randomizer/core/seeding.py` (新建)

创建全局种子管理模块，实现：
- `set_global_seed()`
- `get_global_seed()`
- `reset_global_seed()`
- `create_random_instance()`

### 阶段2: Randomizable类修改

**文件**: `sv_randomizer/core/randomizable.py`

1. **修改 `__init__` 方法**:
   - 添加 `seed` 参数
   - 初始化 `_seed` 和 `_random` 属性

2. **添加种子管理方法**:
   - `set_seed(seed: Optional[int])`
   - `get_seed() -> Optional[int]`
   - `get_random() -> random.Random`

3. **修改 `randomize` 方法**:
   - 添加 `seed` 参数（临时种子）
   - 传递Random实例给求解器

### 阶段3: 变量系统修改

**文件**: `sv_randomizer/core/variables.py`

1. **修改 `RandVar.generate_unconstrained()`**:
   - 添加 `rand: Optional[random.Random]` 参数
   - 使用传入的rand实例而非全局random模块

2. **修改 `RandCVar`**:
   - 添加 `_random` 属性
   - 修改 `_initialize_pool()` 支持传入Random实例
   - 添加 `set_random()` 方法

### 阶段4: 求解器修改

**文件**:
- `sv_randomizer/solvers/backend_interface.py`
- `sv_randomizer/solvers/pure_python.py`
- `sv_randomizer/solvers/solver_factory.py`

1. **更新 `SolverBackend` 基类**:
   - `__init__` 添加 `random_instance` 参数

2. **修改 `PurePythonBackend`**:
   - 支持传入 `random_instance`
   - 修改 `_generate_candidate()` 使用实例的Random

3. **更新 `SolverFactory`**:
   - 支持传递 `random_instance` 给求解器

### 阶段5: 约束系统修改

**文件**: `sv_randomizer/constraints/builders.py`

1. **修改 `DistConstraint.sample()`**:
   - 添加 `rand: Optional[random.Random]` 参数
   - 向后兼容：None时使用全局random模块

### 阶段6: 导出和文档

**文件**: `sv_randomizer/__init__.py`, `README.md`

1. **更新 `__init__.py`**:
   - 导出种子相关函数：`set_global_seed`, `get_global_seed`, `reset_global_seed`

2. **更新 `README.md`**:
   - 添加随机种子控制章节
   - 提供使用示例

---

## 验证方式

### 单元测试

**新建文件**: `tests/test_seeding.py`

```python
import pytest
from sv_randomizer import (
    Randomizable, RandVar, RandCVar, VarType,
    set_global_seed, get_global_seed, reset_global_seed
)
from sv_randomizer.constraints.base import ExpressionConstraint
from sv_randomizer.constraints.expressions import (
    VariableExpr, ConstantExpr, BinaryExpr, BinaryOp
)
from sv_randomizer.constraints.builders import DistConstraint

def test_same_seed_same_sequence():
    """测试相同种子产生相同序列"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj1 = TestObj(seed=42)
    values1 = [obj1.randomize() or obj1.x for _ in range(10)]

    obj2 = TestObj(seed=42)
    values2 = [obj2.randomize() or obj2.x for _ in range(10)]

    assert values1 == values2

def test_different_seed_different_sequence():
    """测试不同种子产生不同序列"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj1 = TestObj(seed=42)
    values1 = [obj1.randomize() or obj1.x for _ in range(10)]

    obj2 = TestObj(seed=123)
    values2 = [obj2.randomize() or obj2.x for _ in range(10)]

    assert values1 != values2

def test_global_seed():
    """测试全局种子功能"""
    reset_global_seed()
    set_global_seed(42)

    class TestObj(Randomizable):
        def __init__(self):
            super().__init__()  # 使用全局种子
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj1 = TestObj()
    value1 = obj1.randomize() or obj1.x

    # 重置并创建新对象
    reset_global_seed()
    set_global_seed(42)
    obj2 = TestObj()
    value2 = obj2.randomize() or obj2.x

    assert value1 == value2

def test_temporary_seed_no_side_effect():
    """测试临时种子不影响对象状态"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj = TestObj(seed=42)

    # 正常randomize
    obj.randomize()
    value1 = obj.x

    # 使用临时种子
    obj.randomize(seed=123)
    value2 = obj.x

    # 恢复正常
    obj.randomize()
    value3 = obj.x

    # 再次使用相同临时种子
    obj.randomize(seed=123)
    value4 = obj.x

    assert value2 == value4  # 临时种子产生相同值
    # value1和value3应该属于同一序列的不同位置

def test_randc_with_seed():
    """测试RandCVar的种子支持"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._randc_vars['id'] = RandCVar('id', VarType.BIT, bit_width=3)

    obj1 = TestObj(seed=42)
    values1 = []
    for _ in range(8):
        obj1.randomize()
        values1.append(obj1.id)

    obj2 = TestObj(seed=42)
    values2 = []
    for _ in range(8):
        obj2.randomize()
        values2.append(obj2.id)

    assert values1 == values2
    assert len(set(values1)) == 8  # 无重复

def test_dist_constraint_with_seed():
    """测试DistConstraint的可重现性"""
    # 需要先实现DistConstraint的seed支持
    pass

def test_solver_backend_with_seed():
    """测试PurePythonBackend的种子功能"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)
            self._rand_vars['y'] = RandVar('y', VarType.INT, min_val=0, max_val=100)

            # 添加约束: x + y < 100
            expr = BinaryExpr(
                BinaryExpr(VariableExpr('x'), BinaryOp.ADD, VariableExpr('y')),
                BinaryOp.LT,
                ConstantExpr(100)
            )
            self.add_constraint(ExpressionConstraint("sum_constraint", expr))

    obj1 = TestObj(seed=42)
    values1 = []
    for _ in range(10):
        obj1.randomize()
        values1.append((obj1.x, obj1.y))

    obj2 = TestObj(seed=42)
    values2 = []
    for _ in range(10):
        obj2.randomize()
        values2.append((obj2.x, obj2.y))

    assert values1 == values2
```

### 集成测试示例

```python
# 验证可重现性
from sv_randomizer import set_global_seed, Randomizable, RandVar, VarType

# 设置全局种子
set_global_seed(42)

# 生成第一组数据
class Packet(Randomizable):
    def __init__(self):
        super().__init__()
        self._rand_vars['addr'] = RandVar('addr', VarType.INT, min_val=0, max_val=65535)

data1 = []
for _ in range(100):
    pkt = Packet()
    pkt.randomize()
    data1.append(pkt.addr)

# 重置并生成第二组数据
set_global_seed(42)
data2 = []
for _ in range(100):
    pkt = Packet()
    pkt.randomize()
    data2.append(pkt.addr)

# 验证完全相同
assert data1 == data2
print("Reproducibility test passed!")
```

---

## 向后兼容性

### 设计原则

- **所有新参数都是可选的**，默认值为None
- **None行为与现有代码一致**（使用全局random模块）
- **旧代码无需修改**即可继续工作

### 兼容性测试

```python
# 旧代码（无种子）
class OldStylePacket(Randomizable):
    def __init__(self):
        super().__init__()
        self._rand_vars['addr'] = RandVar('addr', VarType.INT, min_val=0, max_val=100)

# 应该仍然工作
pkt = OldStylePacket()
success = pkt.randomize()
assert success
assert 0 <= pkt.addr <= 100
```

---

## 关键文件（按优先级）

1. `sv_randomizer/core/seeding.py` - 新建，全局种子管理基础设施
2. `sv_randomizer/core/randomizable.py` - 核心修改点，主入口
3. `sv_randomizer/core/variables.py` - RandVar和RandCVar支持Random实例
4. `sv_randomizer/solvers/pure_python.py` - 求解器Random实例支持
5. `sv_randomizer/constraints/builders.py` - DistConstraint种子支持

---

## 技术风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Random实例传递链断裂 | 种子失效 | 确保每个层级正确传递Random实例 |
| 向后兼容性破坏 | 旧代码失败 | 所有新参数默认None，保持原有行为 |
| RandCVar值池不一致 | 可重现性失效 | 设置Random实例时重新初始化值池 |
| 全局状态污染 | 对象间干扰 | 每个对象独立Random实例 |

---

## 相关文档

- [实现计划文档](./IMPLEMENTATION_PLAN.md) - 包含随机种子功能的开发计划
- [架构设计文档](./ARCHITECTURE.md) - 系统整体架构说明
- [README](../README.md) - 项目概述和快速开始

---

**文档版本**: 1.0
**最后更新**: 2025年2月
**维护者**: SV Randomizer Team
