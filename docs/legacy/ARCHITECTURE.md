# ⚠️ 已归档 - SystemVerilog风格随机约束求解器 - 架构设计文档

> **注意**: 本文档已过时，保留仅用于历史参考。请参阅 [development/ARCHITECTURE.md](../development/ARCHITECTURE.md) 获取最新架构文档。

**归档日期**: 2026-03-01
**替代文档**: [development/ARCHITECTURE.md](../development/ARCHITECTURE.md)

---

## 文档概述

本文档详细描述SystemVerilog风格随机约束求解器的系统架构、核心组件设计、数据流和关键实现策略。

---

## 系统架构概览

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户应用层                                │
│  (PacketGenerator, TestBenchGenerator, ConstraintSolver)         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         用户API层                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  @rand/@randc    │  │  @constraint     │  │  DSL语法糖   │  │
│  │  装饰器          │  │  装饰器          │  │  (inside,dist)│  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Randomizable基类                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  randomize() → pre_randomize() → 求解 → post_randomize() │   │
│  └─────────────────────────────────────────────────────────┘   │
│  变量管理: _rand_vars, _randc_vars                              │
│  约束管理: _constraints, _constraint_modes                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         约束系统层                               │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  表达式AST      │  │  约束构建器     │  │  条件约束       │   │
│  │  (BinaryExpr,  │  │  (Inside,      │  │  (Implication) │   │
│  │   UnaryExpr)   │  │   Dist)        │  │                │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        求解器抽象层                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              SolverBackend (抽象接口)                    │   │
│  │  create_variable(), add_constraint(), solve()            │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↙                          ↘                         │
│  ┌────────────────┐          ┌────────────────┐               │
│  │ PurePython     │          │      Z3        │               │
│  │ Backend        │          │    Backend     │               │
│  │ (随机采样+     │          │  (SMT求解器)   │               │
│  │  约束检查)     │          │                │               │
│  └────────────────┘          └────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         变量系统层                               │
│  ┌────────────────┐  ┌────────────────┐                       │
│  │    RandVar     │  │    RandCVar    │                       │
│  │  (可重复随机)  │  │ (循环无重复)   │                       │
│  └────────────────┘  └────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        输出格式层                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │ Verilog        │  │  VHDL          │  │  JSON          │   │
│  │ Formatter      │  │  Formatter     │  │  Formatter     │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心组件设计

### 1. Randomizable基类

**文件**: [`sv_randomizer/core/randomizable.py`](../sv_randomizer/core/randomizable.py)

#### 职责

- 管理随机变量（rand/randc）
- 管理约束（添加、启用/禁用）
- 协调randomization流程
- 提供回调钩子（pre_randomize, post_randomize）

#### 核心方法

```python
class Randomizable:
    def __init__(self):
        self._rand_vars: Dict[str, RandVar] = {}
        self._randc_vars: Dict[str, RandCVar] = {}
        self._constraints: List[Constraint] = []
        self._constraint_modes: Dict[str, bool] = {}
        self._var_modes: Dict[str, bool] = {}

    def randomize(self, with_constraints: Optional[Dict[str, Any]] = None) -> bool:
        """
        执行随机化流程：
        1. 调用pre_randomize()
        2. 收集活跃的变量和约束
        3. 应用内联约束（如果有）
        4. 处理randc变量（直接从值池取值）
        5. 求解rand变量
        6. 将解应用到变量
        7. 调用post_randomize()
        """
        pass

    def constraint_mode(self, constraint_name: str, mode: Optional[bool] = None) -> bool:
        """启用/禁用约束"""
        pass

    def rand_mode(self, var_name: str, mode: Optional[bool] = None) -> bool:
        """启用/禁用随机变量"""
        pass
```

#### randomize()流程详解

```
┌──────────────┐
│randomize()   │
└──────┬───────┘
       ↓
┌─────────────────────────┐
│ pre_randomize()         │  ← 用户自定义前置处理
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│ 收集活跃变量和约束       │
│ _get_active_vars()      │
│ _get_active_constraints()│
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│ 处理randc变量           │
│ var.get_next()          │  ← 直接从值池取值
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│ 调用求解器              │
│ solver.solve()          │
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│ 应用解到变量             │
│ setattr(self, name, val)│
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│ post_randomize()        │  ← 用户自定义后置处理
└──────────┬──────────────┘
           ↓
     return True/False
```

### 2. 变量系统

**文件**: [`sv_randomizer/core/variables.py`](../sv_randomizer/core/variables.py)

#### RandVar设计

```python
class RandVar:
    """
    可重复随机变量（类似SystemVerilog的rand）
    """
    def __init__(self, name: str, var_type: VarType,
                 bit_width: Optional[int] = None,
                 min_val: Optional[int] = None,
                 max_val: Optional[int] = None,
                 enum_values: Optional[List[Any]] = None):
        self.name = name
        self.var_type = var_type
        self.bit_width = bit_width
        self.min_val = min_val
        self.max_val = max_val
        self.enum_values = enum_values
        self.current_value = None

    def generate_unconstrained(self) -> Any:
        """生成无约束随机值"""
        if self.var_type == VarType.INT:
            return random.randint(self.min_val, self.max_val)
        elif self.var_type == VarType.BIT:
            return random.randint(0, (1 << self.bit_width) - 1)
        elif self.var_type == VarType.ENUM:
            return random.choice(self.enum_values)
        elif self.var_type == VarType.BOOL:
            return random.choice([True, False])
```

#### RandCVar设计

```python
class RandCVar:
    """
    循环无重复随机变量（类似SystemVerilog的randc）
    """
    def __init__(self, name: str, var_type: VarType,
                 bit_width: Optional[int] = None,
                 enum_values: Optional[List[Any]] = None):
        self.name = name
        self.var_type = var_type
        self.bit_width = bit_width
        self.enum_values = enum_values
        self._value_pool: List[Any] = []
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """初始化并打乱值池"""
        if self.var_type == VarType.BIT:
            pool_size = 1 << self.bit_width
            self._value_pool = list(range(pool_size))
        elif self.var_type == VarType.ENUM:
            self._value_pool = self.enum_values.copy()

        random.shuffle(self._value_pool)  # 洗牌算法

    def get_next(self) -> Any:
        """获取下一个值，值池耗尽后重新洗牌"""
        if not self._value_pool:
            self._initialize_pool()  # 重新洗牌
        return self._value_pool.pop()

    def reset(self) -> None:
        """重置值池"""
        self._initialize_pool()
```

**关键特性**:
- **值池机制**: 预先生成所有可能值并打乱
- **无重复保证**: 从值池pop取值，确保周期内不重复
- **自动重洗**: 值池耗尽后自动重新初始化并洗牌

### 3. 约束表达式系统

**文件**: [`sv_randomizer/constraints/expressions.py`](../sv_randomizer/constraints/expressions.py)

#### 表达式AST层次结构

```
        Expression (抽象基类)
              ↑
       ┌──────┴──────┐
       │             │
  VariableExpr   ConstantExpr
  (变量引用)      (常量)

        Expression
              ↑
       ┌──────┴──────┐
       │             │
  UnaryExpr      BinaryExpr
  (一元运算)     (二元运算)
  !, -, ~        ==, !=, <, >, &&, ||, ->, +, -, *, /, %
```

#### BinaryOp枚举

```python
class BinaryOp(Enum):
    # 关系运算符
    EQ = "=="        # 等于
    NE = "!="        # 不等于
    LT = "<"         # 小于
    LE = "<="        # 小于等于
    GT = ">"         # 大于
    GE = ">="        # 大于等于

    # 逻辑运算符
    AND = "&&"       # 逻辑与
    OR = "||"        # 逻辑或
    IMPLIES = "->"   # 蕴含

    # 算术运算符
    ADD = "+"        # 加法
    SUB = "-"        # 减法
    MUL = "*"        # 乘法
    DIV = "/"        # 除法
    MOD = "%"        # 取模

    # 位运算符
    BIT_AND = "&"
    BIT_OR = "|"
    BIT_XOR = "^"
    BIT_NOT = "~"
```

#### 蕴含操作符实现

```python
# P -> Q 等价于 !P || Q
def eval(self, context: Dict[str, Any]) -> Any:
    if self.op == BinaryOp.IMPLIES:
        left_val = self.left.eval(context)
        # 如果前件为假，整个表达式为真
        if not left_val:
            return True
        # 前件为真，检查后件
        right_val = self.right.eval(context)
        return right_val
```

### 4. 约束构建器

**文件**: [`sv_randomizer/constraints/builders.py`](../sv_randomizer/constraints/builders.py)

#### InsideConstraint

```python
class InsideConstraint(ExpressionConstraint):
    """
    inside约束：变量在指定范围或值内

    示例:
        inside([0, (1, 10), (20, 30)])
        表示：值==0 OR (1<=值<=10) OR (20<=值<=30)
    """
    def __init__(self, name: str, var_name: str,
                 ranges: List[Union[int, Tuple[int, int]]]):
        self.var_name = var_name
        self.ranges = ranges

        # 构建OR连接的表达式
        expr = self._build_inside_expression()
        super().__init__(name, expr)

    def _build_inside_expression(self) -> Expression:
        """构建inside约束的表达式"""
        exprs = []
        for r in self.ranges:
            if isinstance(r, int):
                # 单个值
                exprs.append(BinaryExpr(
                    VariableExpr(self.var_name),
                    BinaryOp.EQ,
                    ConstantExpr(r)
                ))
            elif isinstance(r, tuple):
                # 范围
                low, high = r
                ge_expr = BinaryExpr(
                    VariableExpr(self.var_name),
                    BinaryOp.GE,
                    ConstantExpr(low)
                )
                le_expr = BinaryExpr(
                    VariableExpr(self.var_name),
                    BinaryOp.LE,
                    ConstantExpr(high)
                )
                exprs.append(BinaryExpr(ge_expr, BinaryOp.AND, le_expr))

        # 用OR连接所有表达式
        result = exprs[0]
        for expr in exprs[1:]:
            result = BinaryExpr(result, BinaryOp.OR, expr)

        return result
```

#### DistConstraint

```python
class DistConstraint(ExpressionConstraint):
    """
    dist约束：加权分布

    示例:
        dist({"A": 50, "B": 30, "C": 20})
        表示：A占50%, B占30%, C占20%
    """
    def __init__(self, name: str, var_name: str,
                 weights: Dict[Any, int]):
        self.var_name = var_name
        self.weights = weights

    def sample(self) -> Any:
        """根据权重采样"""
        import random
        items = list(self.weights.keys())
        weights = list(self.weights.values())
        total = sum(weights)

        # 归一化权重
        normalized = [w / total for w in weights]

        # 加权随机选择
        return random.choices(items, weights=normalized, k=1)[0]
```

### 5. 求解器架构

**文件**:
- [`sv_randomizer/solvers/backend_interface.py`](../sv_randomizer/solvers/backend_interface.py)
- [`sv_randomizer/solvers/pure_python.py`](../sv_randomizer/solvers/pure_python.py)
- [`sv_randomizer/solvers/z3_backend.py`](../sv_randomizer/solvers/z3_backend.py)

#### 抽象接口

```python
class SolverBackend(ABC):
    """
    求解器后端抽象接口
    """
    @abstractmethod
    def create_variable(self, name: str, var_type: str, **kwargs) -> None:
        """创建求解器变量"""
        pass

    @abstractmethod
    def add_constraint(self, constraint: Constraint) -> None:
        """添加约束"""
        pass

    @abstractmethod
    def solve(self) -> Optional[Dict[str, Any]]:
        """求解并返回结果"""
        pass

    @abstractmethod
    def reset(self) -> None:
        """重置求解器"""
        pass
```

#### PurePythonBackend

```python
class PurePythonBackend(SolverBackend):
    """
    纯Python求解器：随机采样+约束检查

    算法：
        1. 生成随机候选解
        2. 检查是否满足所有约束
        3. 满足则返回，否则重试
        4. 超过最大迭代次数则返回None（无解）
    """
    def __init__(self, max_iterations: int = 10000):
        self.max_iterations = max_iterations
        self._variables: Dict[str, Any] = {}
        self._constraints: List[Constraint] = []

    def solve(self) -> Optional[Dict[str, Any]]:
        for iteration in range(self.max_iterations):
            # 生成随机候选解
            candidate = self._generate_candidate()

            # 检查约束
            if self._check_constraints(candidate):
                return candidate

        return None  # 无解

    def _generate_candidate(self) -> Dict[str, Any]:
        """为每个变量生成随机值"""
        candidate = {}
        for name, var_info in self._variables.items():
            if var_info['type'] == 'int':
                candidate[name] = random.randint(
                    var_info['min_val'],
                    var_info['max_val']
                )
            elif var_info['type'] == 'bool':
                candidate[name] = random.choice([True, False])
        return candidate

    def _check_constraints(self, candidate: Dict[str, Any]) -> bool:
        """检查候选解是否满足所有约束"""
        for constraint in self._constraints:
            if not constraint.is_enabled():
                continue
            result = constraint.eval(candidate)
            if not result:
                return False
        return True
```

**优势**:
- 零依赖
- 简单易懂
- 适合中小规模约束

**劣势**:
- 对复杂约束效率低
- 不能保证找到解（即使存在）

#### Z3Backend

```python
class Z3Backend(SolverBackend):
    """
    Z3 SMT求解器后端

    使用Z3 SMT求解器进行约束求解，支持：
    - 复杂约束的高效求解
    - 完备性（有解必能找到）
    - 不可满足问题的快速检测
    """
    def __init__(self):
        import z3
        self.z3 = z3
        self._solver = z3.Solver()
        self._z3_vars: Dict[str, Any] = {}

    def create_variable(self, name: str, var_type: str, **kwargs) -> None:
        """创建Z3变量"""
        if var_type == 'int':
            self._z3_vars[name] = self.z3.Int(name)
        elif var_type == 'bit':
            bit_width = kwargs.get('bit_width', 32)
            self._z3_vars[name] = self.z3.BitVec(name, bit_width)
        elif var_type == 'bool':
            self._z3_vars[name] = self.z3.Bool(name)

        # 添加范围约束
        if 'min_val' in kwargs:
            self._solver.add(self._z3_vars[name] >= kwargs['min_val'])
        if 'max_val' in kwargs:
            self._solver.add(self._z3_vars[name] <= kwargs['max_val'])

    def add_constraint(self, constraint: Constraint) -> None:
        """添加约束到Z3求解器"""
        z3_expr = self._to_z3_expr(constraint.expression)
        self._solver.add(z3_expr)

    def solve(self) -> Optional[Dict[str, Any]]:
        """调用Z3求解"""
        result = self._solver.check()

        if result == self.z3.sat:
            model = self._solver.model()
            solution = {}
            for name, z3_var in self._z3_vars.items():
                solution[name] = model[z3_var].as_long()
            return solution
        else:
            return None  # unsat或unknown
```

**优势**:
- 工业级求解能力
- 支持复杂约束
- 完备性保证

**劣势**:
- 需要安装z3-solver包
- 对简单问题可能过重

### 6. 输出格式化

**文件**: [`sv_randomizer/formatters/verilog.py`](../sv_randomizer/formatters/verilog.py)

```python
class VerilogFormatter:
    """
    Verilog格式化器：将Randomizable对象格式化为Verilog代码
    """
    def format(self, obj: Randomizable) -> str:
        """生成Verilog赋值语句"""
        lines = []
        for var_name in obj.list_rand_vars():
            value = getattr(obj, var_name)
            lines.append(f"assign {var_name} = {self._format_value(value, obj)};")
        return '\n'.join(lines)

    def format_testbench(self, obj: Randomizable, name: str = "tb") -> str:
        """生成完整testbench"""
        template = f"""
module {name};
    // 变量声明
{self._generate_declarations(obj)}

    initial begin
        // 随机化赋值
{self._generate_assignments(obj)}

        // 显示结果
        $display("Values: {self._generate_display(obj)}");
    end
endmodule
        """
        return template.strip()

    def _format_value(self, value: Any, obj: Randomizable) -> str:
        """格式化单个值"""
        var = obj._rand_vars.get(obj.list_rand_vars()[
            obj.list_rand_vars().index(list(obj.__dict__.keys())[
                list(obj.__dict__.values()).index(value)
            ])
        ]) if value in obj.__dict__.values() else None

        if var and var.var_type == VarType.BIT:
            bit_width = var.bit_width or 32
            return f"{bit_width}'h{value:0{bit_width//4}x}"

        return str(value)
```

---

## 数据流设计

### Randomization完整数据流

```
┌──────────────────┐
│  用户调用         │
│  obj.randomize() │
└────────┬─────────┘
         ↓
┌───────────────────────────────────┐
│ pre_randomize()                   │  ← 用户可扩展
└────────┬──────────────────────────┘
         ↓
┌───────────────────────────────────┐
│ 收集活跃变量                       │
│ - _rand_vars (dict)               │
│ - _randc_vars (dict)              │
│ - 检查rand_mode()状态             │
└────────┬──────────────────────────┘
         ↓
┌───────────────────────────────────┐
│ 收集活跃约束                       │
│ - _constraints (list)             │
│ - 检查constraint_mode()状态       │
└────────┬──────────────────────────┘
         ↓
┌───────────────────────────────────┐
│ 处理randc变量                     │
│ FOR EACH randc_var:               │
│   value = var.get_next()          │  ← 从值池取值
│   setattr(obj, name, value)       │
└────────┬──────────────────────────┘
         ↓
┌───────────────────────────────────┐
│ 创建求解器                        │
│ solver = SolverFactory.get_solver()│
└────────┬──────────────────────────┘
         ↓
┌───────────────────────────────────┐
│ 注册变量到求解器                  │
│ FOR EACH rand_var:                │
│   solver.create_variable(...)     │
└────────┬──────────────────────────┘
         ↓
┌───────────────────────────────────┐
│ 添加约束到求解器                  │
│ FOR EACH constraint:              │
│   solver.add_constraint(...)     │
└────────┬──────────────────────────┘
         ↓
┌───────────────────────────────────┐
│ 求解                              │
│ solution = solver.solve()         │
│                                   │
│ PurePython: 随机采样+检查         │
│ Z3: SMT求解                       │
└────────┬──────────────────────────┘
         ↓
    ┌────┴────┐
    ↓         ↓
┌────┐    ┌────────┐
│None│    │solution│
└────┘    └────┬───┘
            ↓
┌───────────────────────────────────┐
│ 应用解                            │
│ FOR EACH (name, value) in solution│
│   obj._rand_vars[name].value = val│
│   setattr(obj, name, value)       │
└────────┬──────────────────────────┘
         ↓
┌───────────────────────────────────┐
│ post_randomize()                  │  ← 用户可扩展
└────────┬──────────────────────────┘
         ↓
    return True/False
```

---

## 关键设计决策

### 1. 为什么使用分离的rand和randc？

**SystemVerilog语义**:
- `rand`: 每次randomize()都可能生成相同值（可重复）
- `randc`: 周期内不重复，遍历完所有可能值后才循环

**实现策略**:
- `RandVar`: 直接使用random模块，每次独立生成
- `RandCVar`: 维护值池，通过洗牌和pop机制实现无重复

### 2. 为什么使用可插拔求解器架构？

**灵活性**:
- PurePython: 零依赖，适合简单场景
- Z3: 工业级能力，适合复杂约束

**一致性**:
- 统一的SolverBackend接口
- 用户代码无需修改即可切换后端

### 3. 为什么使用表达式AST？

**优势**:
- 灵活表达复杂约束
- 支持多种求解器后端
- 易于扩展新操作符

**权衡**:
- 增加了系统复杂度
- 需要表达式求值逻辑

### 4. 为什么分层架构？

**关注点分离**:
- 用户API层: 语法糖和易用性
- 约束层: 约束表达和管理
- 求解器层: 核心算法
- 变量层: 随机值生成

**可维护性**:
- 每层职责清晰
- 易于测试和调试
- 便于扩展新功能

---

## 扩展点

### 1. 添加新的变量类型

在`VarType`中添加新类型，并更新：
- `RandVar.generate_unconstrained()`
- `RandCVar._initialize_pool()`
- 求解器变量创建逻辑

### 2. 添加新的约束类型

继承`ExpressionConstraint`或`Constraint`，实现：
- `eval()` - 约束求值
- `get_variables()` - 获取涉及的变量

### 3. 添加新的求解器后端

实现`SolverBackend`接口：
- `create_variable()`
- `add_constraint()`
- `solve()`
- `reset()`

然后在`SolverFactory`中注册。

### 4. 添加新的输出格式

继承`Formatter`基类，实现：
- `format()` - 基本格式化
- `format_testbench()` - 生成testbench（可选）

---

## 性能考虑

### PurePython后端优化

- **最大迭代次数**: 默认10000，可配置
- **早期终止**: 找到解立即返回
- **约束顺序**: 将选择性强的约束放前面

### Z3后端优化

- **增量求解**: 可复用求解器状态
- **参数调优**: 可配置Z3求解参数
- **超时控制**: 避免无限运行

### RandCVar优化

- **值池缓存**: 避免重复生成
- **惰性重洗**: 只在值池耗尽时重洗

---

## 相关文档

- [实现计划文档](./IMPLEMENTATION_PLAN.md) - 开发计划和功能验证
- [随机种子控制文档](./SEED_CONTROL.md) - 随机种子功能设计
- [README](../README.md) - 项目概述和快速开始

---

**文档版本**: 1.0
**最后更新**: 2025年2月
**维护者**: SV Randomizer Team
