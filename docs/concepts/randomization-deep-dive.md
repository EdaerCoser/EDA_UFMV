# 随机化深入

本文档深入解释EDA_UFVM随机化系统的技术实现细节。

---

## 目录

- [种子复现机制](#种子复现机制)
- [约束求解算法](#约束求解算法)
- [双求解器架构](#双求解器架构)
- [设计模式](#设计模式)

---

## 种子复现机制

### 核心原理

EDA_UFVM使用Python的`random.Random(seed)`实现确定性随机数生成。相同种子必然产生相同的随机序列，从而实现测试的可复现性。

**关键代码路径**：
```
Randomizable.__init__(seed) → create_random_instance() → random.Random(seed)
    ↓
Randomizable.get_random() → 返回缓存的Random实例
    ↓
randomize() → SolverFactory.get_solver(random_instance=rand)
    ↓
SolverBackend.__init__(random_instance) → self._random = random_instance
    ↓
PurePythonBackend._generate_candidate() → self._random.randint()
```

### 三层种子管理

| 种子类型 | 代码位置 | 优先级 | 作用范围 |
|:---|:---|:---|:---|
| **临时种子** | `randomize(seed=...)` | 最高 | 单次randomize()调用 |
| **对象种子** | `Randomizable(seed)` | 中 | 单个对象的所有randomize() |
| **全局种子** | `set_global_seed()` | 低 | 所有新创建的对象 |

**实现文件**: [`sv_randomizer/core/seeding.py`](../../sv_randomizer/core/seeding.py:65-87)

```python
def create_random_instance(seed: Optional[int] = None) -> random.Random:
    """优先级: 传入seed > 全局种子 > 系统熵"""
    if seed is not None:
        return random.Random(seed)
    elif _global_seed is not None:
        return random.Random(_global_seed)
    else:
        return random.Random()
```

### Random实例传递机制

**对象级缓存** ([`randomizable.py:346-361`](../../sv_randomizer/core/randomizable.py:346-361)):

```python
def get_random(self) -> random.Random:
    """延迟创建并缓存Random实例"""
    if self._random is None:
        self._random = create_random_instance(self._seed)
    return self._random
```

**求解器接收** ([`backend_interface.py:21-34`](../../sv_randomizer/solvers/backend_interface.py:21-34)):

```python
class SolverBackend(ABC):
    def __init__(self, seed: Optional[int] = None,
                 random_instance: Optional[random.Random] = None):
        if random_instance is not None:
            self._random = random_instance  # 使用传入的实例
        elif seed is not None:
            self._random = random.Random(seed)
        else:
            self._random = random.Random()
```

### 候选解生成

**PurePython求解器** ([`pure_python.py:120-135`](../../sv_randomizer/solvers/pure_python.py:120-135)):

```python
def _generate_candidate(self) -> Dict[str, Any]:
    """使用self._random生成候选解"""
    candidate = {}
    for name, info in self.var_info.items():
        if info["enum_values"]:
            candidate[name] = self._random.choice(info["enum_values"])
        else:
            candidate[name] = self._random.randint(info["min"], info["max"])
    return candidate
```

**关键点**: 所有随机数生成都通过`self._random`，确保相同种子产生相同候选解序列。

### RandCVar的洗牌机制

**值池初始化** ([`variables.py:155-171`](../../sv_randomizer/core/variables.py:155-171)):

```python
class RandCVar:
    def _initialize_pool(self) -> None:
        """初始化值池并使用Random.shuffle()打乱"""
        # 创建值池: [0, 1, 2, ..., 2^bit_width - 1]
        self._value_pool = list(range(pool_size))

        # 使用Random实例打乱顺序（关键！）
        rand_instance = self._random if self._random is not None else random
        rand_instance.shuffle(self._value_pool)
```

**状态重置** ([`variables.py:188-200`](../../sv_randomizer/core/variables.py:188-200)):

```python
def set_random(self, rand: random.Random) -> None:
    """只有Random实例真正改变时才重置值池"""
    if self._random is not rand:
        self._random = rand
        self._initialize_pool()  # 重新洗牌
```

**复现保证**: 相同种子 → 相同的`shuffle()`结果 → 相同的值池排列顺序。

### 求解算法的确定性

**随机采样+验证** ([`pure_python.py:96-118`](../../sv_randomizer/solvers/pure_python.py:96-118)):

```python
def solve(self) -> Optional[Dict[str, Any]]:
    """按顺序生成候选解，返回第一个满足约束的"""
    for iteration in range(self.max_iterations):
        candidate = self._generate_candidate()  # 确定性序列

        if self._check_constraints(candidate):  # 确定性检查
            return candidate  # 第一个满足的解

    return None
```

**复现条件**:
- 相同种子 → 相同的`_generate_candidate()`序列
- 相同约束 → 相同的`_check_constraints()`结果
- 因此：**第一个满足约束的解必然相同**

### 种子序列消耗特性

每次`randomize()`调用都会消耗随机序列的不同位置：

```python
pkt = Packet(seed=42)
pkt.randomize()  # 消耗序列位置 [0, 1, 2, ...]
pkt.randomize()  # 消耗序列位置 [11, 12, 13, ...]

# 新对象重新开始
pkt2 = Packet(seed=42)
pkt2.randomize()  # 消耗序列位置 [0, 1, 2, ...]（与pkt第一次相同）
```

**原因**: `get_random()`返回缓存的Random实例，其内部状态在每次调用后递增。

---

## 约束求解算法

### PurePython求解器

**算法**: 随机采样 + 约束验证

**特点**:
- 零外部依赖
- 适用于中小规模约束问题（<10变量，<20约束）
- 性能: ~10,000次随机化/秒

**限制**:
- 不保证找到最优解
- 复杂约束可能需要大量迭代
- 约束冲突时无智能回溯

**适用场景**:
- 快速原型验证
- 简单约束问题
- 无外部依赖环境

### Z3求解器

**算法**: SMT (Satisfiability Modulo Theories)

**特点**:
- 工业级求解器
- 支持复杂约束和逻辑推理
- 保证找到满足约束的解（如果存在）

**启用方法**:
```python
pip install z3-solver
obj._solver_backend = "z3"
obj.randomize()
```

**适用场景**:
- 复杂约束（>10变量，>20约束）
- 需要保证解的存在性
- 性能敏感场景

---

## 双求解器架构

### 设计模式: 策略模式 (Strategy Pattern)

**抽象接口** ([`backend_interface.py`](../../sv_randomizer/solvers/backend_interface.py:14-179)):

```python
class SolverBackend(ABC):
    @abstractmethod
    def create_variable(self, name, var_type, **kwargs): pass

    @abstractmethod
    def add_constraint(self, constraint_expr): pass

    @abstractmethod
    def solve(self): pass
```

**具体实现**:
- `PurePythonBackend` ([`pure_python.py`](../../sv_randomizer/solvers/pure_python.py:16-215))
- `Z3Backend` ([`z3_backend.py`](../../sv_randomizer/solvers/z3_backend.py))

**工厂创建** ([`solver_factory.py`](../../sv_randomizer/solvers/solver_factory.py)):

```python
class SolverFactory:
    @staticmethod
    def get_solver(backend_name: Optional[str] = None,
                   random_instance: Optional[random.Random] = None):
        if backend_name == "z3":
            return Z3Backend(random_instance=random_instance)
        else:
            return PurePythonBackend(random_instance=random_instance)
```

**切换求解器**:
```python
# 对象级设置
obj._solver_backend = "z3"

# 全局设置
from sv_randomizer.core.seeding import set_global_seed
set_global_seed(42)  # 同时影响求解器随机数生成
```

---

## 设计模式

### 1. 装饰器模式 (Decorator Pattern)

**用户API**:
- `@rand` - 定义随机变量
- `@randc` - 定义循环随机变量
- `@constraint` - 定义约束表达式

**实现** ([`decorators.py`](../../sv_randomizer/api/decorators.py))

### 2. 工厂模式 (Factory Pattern)

**求解器工厂**: `SolverFactory.get_solver()`
**数据库工厂**: `DatabaseFactory.create()` (覆盖率系统)

### 3. 观察者模式 (Observer Pattern)

**回调机制**:
- `pre_randomize()` - 随机化前回调
- `post_randomize()` - 随机化后回调

### 4. 组合模式 (Composite Pattern)

**约束表达式** ([`expressions.py`](../../sv_randomizer/constraints/expressions.py)):
- `VariableExpr` - 变量引用
- `ConstantExpr` - 常量
- `UnaryExpr` - 一元运算
- `BinaryExpr` - 二元运算
- `InsideConstraint` - 范围约束
- `DistConstraint` - 权重分布

---

## 性能优化

### 延迟创建 (Lazy Initialization)

**Random实例缓存** ([`randomizable.py:346-361`](../../sv_randomizer/core/randomizable.py:346-361)):

```python
def get_random(self) -> random.Random:
    if self._random is None:  # 首次调用时创建
        self._random = create_random_instance(self._seed)
    return self._random
```

### 类型注解解析优化

**元类处理** ([`randomizable.py:27-57`](../../sv_randomizer/core/randomizable.py:27-57)):

```python
class RandomizableMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        # 类创建时一次性解析所有类型注解
        if name != 'Randomizable':
            hints = get_type_hints(new_cls, include_extras=True)
            _process_annotations(new_cls, hints)
        return new_cls
```

**优势**: 避免每次实例化时重新解析注解。

### 深拷贝优化

**实例变量独立化** ([`randomizable.py:144-153`](../../sv_randomizer/core/randomizable.py:144-153)):

```python
def __init__(self, seed: Optional[int] = None):
    cls = self.__class__
    if hasattr(cls, '_rand_vars') and cls._rand_vars:
        # 深拷贝类变量到实例，避免共享状态
        self._rand_vars = {k: copy.deepcopy(v) for k, v in cls._rand_vars.items()}
```

---

## 相关文档

- [场景1：生成随机激励](../scenarios/01-generate-random.md) - 快速上手
- [SV→Python映射](sv-to-python-mapping.md) - 概念对照
- [随机化完整参考](../reference/randomization.md) - API文档
