# ⚠️ 已归档 - SystemVerilog风格随机约束求解器 - 实现计划

> **注意**: 本文档已过时，保留仅用于历史参考。请参阅 [development/ROADMAP.md](../development/ROADMAP.md) 获取最新开发计划。

**归档日期**: 2026-03-01
**替代文档**: [development/ROADMAP.md](../development/ROADMAP.md)

---

## 项目概述

本项目实现一个Python风格的SystemVerilog随机约束求解器，用于芯片/硬件验证场景中生成随机测试数据。该工具支持类似SystemVerilog的rand/randc变量和约束语法，并输出仿真器可用的格式。

### 核心特性

- **基础随机化**: 支持rand（可重复随机）和randc（循环无重复随机）变量
- **约束求解**: 支持inside、dist、关系运算符、逻辑运算符、蕴含等约束
- **可插拔架构**: 支持PurePython和Z3两种求解器后端
- **输出格式**: 支持Verilog/VHDL测试向量输出

### 应用场景

- 硬件验证测试数据生成
- 随机约束求解问题
- 芯片功能验证
- 测试向量自动生成

---

## 整体架构设计

### 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                   用户API层                              │
│  @rand, @randc, @constraint装饰器 + DSL语法糖            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   约束定义层                             │
│   InsideConstraint, DistConstraint, 表达式AST            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   求解器抽象层                           │
│           SolverBackend (PurePython / Z3)               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   变量管理层                             │
│              RandVar, RandCVar                           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   输出格式层                             │
│         VerilogFormatter, VHDLFormatter                  │
└─────────────────────────────────────────────────────────┘
```

### 目录结构

```
demo_rand/
├── sv_randomizer/
│   ├── core/
│   │   ├── randomizable.py    # Randomizable基类
│   │   ├── variables.py       # RandVar, RandCVar
│   │   └── registry.py        # 变量注册表
│   ├── constraints/
│   │   ├── expressions.py     # 表达式AST
│   │   ├── builders.py        # inside, dist约束构建器
│   │   └── conditional.py     # 条件约束
│   ├── solvers/
│   │   ├── backend_interface.py
│   │   ├── pure_python.py     # 纯Python求解器
│   │   ├── z3_backend.py      # Z3求解器后端
│   │   └── solver_factory.py  # 求解器工厂
│   ├── formatters/
│   │   └── verilog.py         # Verilog输出格式
│   ├── utils/
│   │   └── exceptions.py      # 自定义异常
│   └── api/
│       ├── decorators.py      # @rand, @randc装饰器
│       └── dsl.py             # DSL语法糖
├── examples/
│   └── packet_generator.py    # 数据包生成示例
├── tests/
│   └── test_*.py
├── docs/
│   ├── IMPLEMENTATION_PLAN.md
│   ├── ARCHITECTURE.md
│   └── SEED_CONTROL.md
├── setup.py
└── requirements.txt
```

---

## 核心功能实现方案

### 1. Rand/RandC变量系统

#### RandVar实现

`RandVar`类实现可重复随机变量：

- 支持多种变量类型：int, bit, logic, enum, bool
- 支持位宽和范围约束
- `generate_unconstrained()`方法生成无约束随机值

**关键文件**: [`sv_randomizer/core/variables.py`](../sv_randomizer/core/variables.py)

#### RandCVar实现

`RandCVar`类实现循环无重复随机变量：

- 值池初始化和洗牌算法
- `get_next()`方法循环获取值
- 值池耗尽后自动重新洗牌

**关键实现**:
```python
def _initialize_pool(self) -> None:
    self._value_pool = list(range(pool_size))
    random.shuffle(self._value_pool)  # 洗牌算法

def get_next(self) -> Any:
    if not self._value_pool:
        self._initialize_pool()  # 耗尽后重新洗牌
    return self._value_pool.pop()
```

**关键文件**: [`sv_randomizer/core/variables.py`](../sv_randomizer/core/variables.py)

### 2. 约束表达式系统

#### 表达式AST

实现完整的表达式抽象语法树：

- `VariableExpr` - 变量引用
- `ConstantExpr` - 常量
- `BinaryExpr` - 二元运算（支持==, !=, <, >, <=, >=, &&, ||, ->, +, -, *, /, %等）
- `UnaryExpr` - 一元运算（!, -, ~）

**关键文件**: [`sv_randomizer/constraints/expressions.py`](../sv_randomizer/constraints/expressions.py)

#### 约束构建器

- **InsideConstraint**: 支持范围`[(low, high)]`和单个值，构建OR连接的范围约束表达式
- **DistConstraint**: 权重字典存储，实现加权分布采样
- **ArrayConstraint**: 支持size、foreach、unique约束

**关键文件**: [`sv_randomizer/constraints/builders.py`](../sv_randomizer/constraints/builders.py)

### 3. 求解器后端架构

#### 抽象接口

`SolverBackend`定义统一的求解器接口：

- `create_variable()` - 创建求解器变量
- `add_constraint()` - 添加约束
- `solve()` - 求解并返回结果
- `reset()` - 重置求解器状态

**关键文件**: [`sv_randomizer/solvers/backend_interface.py`](../sv_randomizer/solvers/backend_interface.py)

#### PurePython后端

使用随机采样+约束检查算法：

```python
def solve(self):
    for iteration in range(self.max_iterations):
        candidate = self._generate_candidate()  # 随机生成
        if self._check_constraints(candidate):    # 验证约束
            return candidate
    return None  # 无解
```

**优势**: 零依赖，确保基础可用性

**关键文件**: [`sv_randomizer/solvers/pure_python.py`](../sv_randomizer/solvers/pure_python.py)

#### Z3后端

集成Z3 SMT求解器：

- 创建Int/BitVec/Bool变量
- 表达式到Z3格式的转换
- 支持复杂约束的高效求解

**优势**: 工业级求解能力，支持复杂约束

**关键文件**: [`sv_randomizer/solvers/z3_backend.py`](../sv_randomizer/solvers/z3_backend.py)

### 4. 用户API设计

#### 装饰器API

```python
@rand(bit_width=16, min_val=0, max_val=65535)
def addr(self): return 0

@randc(bit_width=4)
def id(self): return 0

@constraint("addr_range")
def addr_in_range(self):
    return inside([0, (100, 200), (500, 600)]) == VarProxy("addr")
```

**关键文件**: [`sv_randomizer/api/decorators.py`](../sv_randomizer/api/decorators.py)

#### DSL语法糖

```python
# inside约束
inside([0, (1, 10), (20, 30)])

# dist约束
dist({"A": 50, "B": 30, "C": 20})

# VarProxy运算符重载
(VarProxy("x") + VarProxy("y")) < 100
```

**关键文件**: [`sv_randomizer/api/dsl.py`](../sv_randomizer/api/dsl.py)

---

## 关键复杂场景技术验证计划

### 场景1: RandC循环随机完整性验证

**目标**: 确保randc变量遍历完所有可能值后才重复

**验证方法**:
- 生成2^N个值（N=位宽），验证全部不重复
- 第2^N+1个值应开始重复
- 在约束下验证仍保持循环特性

**通过标准**:
- randc变量在无约束时遍历所有可能值
- 有约束时遍历满足约束的所有可能值
- 值池耗尽后正确重新洗牌

### 场景2: 约束冲突检测与诊断

**目标**: 准确识别并报告冲突的约束

**验证方法**:
- 构造互斥约束（x < 50 AND x > 100）
- 验证randomize()返回False
- 逐步禁用约束验证诊断能力

**通过标准**:
- 正确检测数学上无解的约束
- 返回清晰的冲突约束名称列表
- 支持增量式约束禁用调试

### 场景3: 权重分布统计验证

**目标**: 验证dist约束的权重分布符合预期

**验证方法**:
- 生成大样本（>1000）随机值
- 使用卡方检验验证分布符合预期（alpha=0.01）

**通过标准**:
- 大样本统计分布与权重设定一致
- 通过卡方检验（p > 0.01）
- 范围权重正确分配到范围内的值

### 场景4: 数组约束性能验证

**目标**: 验证foreach约束展开的性能和正确性

**验证方法**:
- 测试大数组（100+元素）约束求解
- 验证foreach约束正确应用于每个元素
- 测量求解时间

**通过标准**:
- foreach约束正确应用于每个元素
- 大数组求解在5秒内完成
- 动态数组大小约束正确工作

### 场景5: 蕴含约束验证

**目标**: 验证蕴含操作符的正确实现（P -> Q 等价于 !P || Q）

**验证方法**:
- 测试基础蕴含：(addr > 1000) -> (len < 64)
- 测试蕴含链：A -> B -> C
- 验证前件为真时后件必须为真

**通过标准**:
- 蕴含前件为真时，后件必须为真
- 蕴含前件为假时，后件可任意
- 多层蕴含正确链接

### 场景6: 求解器后端一致性

**目标**: 验证PurePython和Z3后端产生一致的解空间

**验证方法**:
- 使用两个后端生成同一问题的样本
- 验证所有解都满足约束
- 测试不可满足问题的检测一致性

**通过标准**:
- 两个后端对可满足问题都生成有效解
- 两个后端对不可满足问题都返回False
- 所有生成的解都满足约束条件

---

## 随机种子控制功能设计

### 功能目标

1. **可重复性**: 相同种子应产生相同的随机序列
2. **调试支持**: 可以重现问题场景
3. **多层次控制**: 全局、对象级、求解器级三个层次

### 架构设计

采用混合策略：使用独立的Random实例传递，同时提供全局种子便捷API。

**优势**:
- **独立性**: 每个Randomizable对象有独立的Random实例
- **可预测性**: 相同种子序列产生相同结果
- **灵活性**: 支持全局、对象级、求解器级三个层次的种子设置
- **向后兼容**: 不设置种子时行为与现有代码一致

### API设计

#### 全局种子API

```python
from sv_randomizer import set_global_seed, get_global_seed

set_global_seed(42)  # 设置全局种子
seed = get_global_seed()  # 获取当前种子
```

#### 对象级种子

```python
class Packet(Randomizable):
    def __init__(self, seed=None):
        super().__init__(seed=seed)

pkt = Packet(seed=123)  # 特定种子
```

#### 临时种子

```python
pkt.randomize(seed=456)  # 临时覆盖，不影响对象状态
```

**详细文档**: [`docs/SEED_CONTROL.md`](./SEED_CONTROL.md)

---

## 开发实施步骤

### 阶段1: 核心基础设施

**文件**:
- `sv_randomizer/core/randomizable.py`
- `sv_randomizer/core/variables.py`
- `sv_randomizer/utils/exceptions.py`

**任务**:
1. 实现自定义异常类（RandomizerError, ConstraintConflictError, UnsatisfiableError）
2. 实现RandVar类（支持多种变量类型）
3. 实现RandCVar类（值池和洗牌算法）
4. 实现Randomizable基类（randomize()流程和状态管理）

### 阶段2: 约束表达式系统

**文件**:
- `sv_randomizer/constraints/expressions.py`
- `sv_randomizer/constraints/base.py`

**任务**:
1. 实现表达式AST（VariableExpr, ConstantExpr, BinaryExpr, UnaryExpr）
2. 实现约束基类（Constraint）

### 阶段3: 约束构建器

**文件**:
- `sv_randomizer/constraints/builders.py`

**任务**:
1. 实现InsideConstraint
2. 实现DistConstraint
3. 实现ArrayConstraint

### 阶段4: 求解器后端

**文件**:
- `sv_randomizer/solvers/backend_interface.py`
- `sv_randomizer/solvers/pure_python.py`
- `sv_randomizer/solvers/z3_backend.py`
- `sv_randomizer/solvers/solver_factory.py`

**任务**:
1. 实现SolverBackend抽象接口
2. 实现PurePythonBackend（随机采样+约束检查）
3. 实现Z3Backend（Z3 SMT求解器集成）
4. 实现SolverFactory（后端注册和工厂）

### 阶段5: 用户API

**文件**:
- `sv_randomizer/api/decorators.py`
- `sv_randomizer/api/dsl.py`

**任务**:
1. 实现装饰器（@rand, @randc, @constraint）
2. 实现DSL语法糖（inside(), dist(), VarProxy）

### 阶段6: 输出格式化

**文件**:
- `sv_randomizer/formatters/verilog.py`
- `sv_randomizer/formatters/base.py`

**任务**:
1. 实现Formatter基类
2. 实现VerilogFormatter（Verilog测试向量生成）

### 阶段7: 示例和测试

**文件**:
- `examples/packet_generator.py`
- `tests/test_*.py`

**任务**:
1. 创建数据包生成示例
2. 编写单元测试（变量生成、约束表达式、randc循环、求解器集成）
3. 编写集成测试（五元不等式求解）

---

## 依赖包

```
# requirements.txt
z3-solver>=4.12.0  # 可选，用于Z3后端
numpy>=1.21.0      # 可选，用于统计验证
scipy>=1.7.0       # 可选，用于卡方检验
```

---

## 技术风险与应对措施

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| randc在约束下可能无法遍历所有值 | 循环随机特性失效 | 记录约束过滤后的值池，仅遍历满足约束的值 |
| 大数组foreach约束性能问题 | 求解时间过长 | 设置数组大小警告阈值，推荐使用Z3后端 |
| Z3依赖可用性问题 | 用户环境无Z3 | 确保PurePython后端完全可用 |
| 权重分布在小样本不准确 | 测试不稳定 | 使用大样本统计验证(>1000) |
| 蕴含约束实现错误 | 逻辑语义错误 | 严格参考SV LRM规范，充分测试 |

---

## 当前实现状态

### 已完成功能

✅ 核心基础设施（Randomizable, RandVar, RandCVar）
✅ 约束表达式系统（完整AST）
✅ 约束构建器（InsideConstraint, DistConstraint）
✅ PurePython求解器后端
✅ Z3求解器后端（可选）
✅ 用户装饰器API（@rand, @randc, @constraint）
✅ DSL语法糖（inside, dist, VarProxy）
✅ Verilog格式化器
✅ 25个单元测试（全部通过）
✅ 五元不等式求解示例

### 待实现功能

🔄 随机种子控制功能（详见`docs/SEED_CONTROL.md`）

---

## 相关文档

- [架构设计文档](./ARCHITECTURE.md) - 详细的系统架构说明
- [随机种子控制文档](./SEED_CONTROL.md) - 随机种子功能详细设计
- [README](../README.md) - 项目概述和快速开始

---

**文档版本**: 1.0
**最后更新**: 2025年2月
**维护者**: SV Randomizer Team
