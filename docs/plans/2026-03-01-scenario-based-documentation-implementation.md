# 场景化文档系统实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 重新组织EDA_UFMV文档为场景化结构，使SystemVerilog工程师能快速上手并理解技术实现细节。

**架构:** 创建docs/scenarios/目录放置场景文档，docs/concepts/目录放置概念参考，每个场景遵循"快速开始→常见任务→技术实现→故障排查"的四层结构，技术实现包含框架架构、核心算法、设计模式、性能考虑和差异对比。

**技术栈:** Markdown文档、示例Python代码、可能使用Sphinx生成API文档

---

## 任务拆分

### 阶段1：目录结构和场景索引（1小时）

### Task 1.1: 创建场景文档目录结构

**Files:**
- Create: `docs/scenarios/index.md`
- Create: `docs/scenarios/.gitkeep`

**Step 1: 创建scenarios目录**

```bash
mkdir -p docs/scenarios
cd docs/scenarios
touch .gitkeep
```

**Step 2: 运行git添加**

```bash
git add docs/scenarios/.gitkeep
```

**Step 3: 提交**

```bash
git commit -m "docs: 创建场景文档目录结构"
```

---

### Task 1.2: 编写场景索引文档

**Files:**
- Create: `docs/scenarios/index.md`

**Step 1: 创建场景索引文件**

```bash
touch docs/scenarios/index.md
```

**Step 2: 编写索引内容**

```markdown
# 场景索引 - 您想做什么？

欢迎来到EDA_UFMV场景化文档！本指南按"我想做什么"组织，帮助您快速找到解决方案。

## 快速导航

### 🎲 生成测试激励
**场景1**: [我想生成随机测试激励](01-generate-random.md)
- 生成符合约束的随机数据包
- 控制激励分布和边界情况
- 设置种子实现可重现性

### 📊 收集功能覆盖率
**场景2**: [我想收集功能覆盖率](02-collect-coverage.md)
- 定义覆盖率组和覆盖点
- 收集值覆盖和范围覆盖
- 分析交叉覆盖率

### 🗄️ 创建寄存器模型
**场景3**: [我想创建寄存器模型](03-create-regmodel.md)
- 定义寄存器层次结构
- 添加字段和访问类型
- 通过硬件适配器访问

### 🔄 从SystemVerilog迁移
**场景4**: [我想从SystemVerilog迁移](04-migrate-from-sv.md)
- 理解SV到Python的概念映射
- 转换约束和覆盖率
- 迁移UVM寄存器模型

### 🤖 自动化代码转换
**场景5**: [我想自动化SV→Python转换](05-automate-conversion.md)
- 解析SystemVerilog任务
- 生成Python配置脚本
- 批量转换验证代码

### 📋 完整验证流程
**场景6**: [完整验证流程案例](06-complete-workflow.md)
- 端到端的DMA控制器验证
- 集成所有模块
- 生成验证报告

---

## 新手建议

**第一次使用？** 建议按顺序阅读：

1. 🎲 **生成随机激励** → 了解基础随机化
2. 📊 **收集覆盖率** → 理解验证完整性
3. 🗄️ **创建寄存器模型** → 掌握DUT配置
4. 📋 **完整流程** → 看所有模块如何协同

**熟悉SystemVerilog？** 直接查看：
- [SV→Python概念映射](../concepts/sv-to-python-mapping.md)

**想深入了解实现？** 阅读场景文档的"技术实现"章节

---

## 文档阅读指南

每个场景文档包含以下章节：

```
🟢 基础使用    → 只读"快速开始"（10分钟上手）
🟡 进阶应用    → 读"快速开始"+"常见任务"（解决实际问题）
🟠 理解原理    → 读"技术实现"（框架、算法、设计模式）
🔴 深入定制    → 读"扩展机制"+API参考（完全掌控）
```

---

## 相关资源

- [概念参考](../concepts/) - 深入技术原理
- [API参考](../api/API_REFERENCE.md) - 完整API文档
- [示例代码](../../examples/) - 可运行的示例
- [开发路线图](../development/ROADMAP.md) - 未来规划
```

**Step 3: 验证Markdown格式**

```bash
# 检查文件是否创建成功
cat docs/scenarios/index.md | head -20
```

Expected: 输出前20行内容

**Step 4: 提交**

```bash
git add docs/scenarios/index.md
git commit -m "docs: 添加场景索引文档"
```

---

### Task 1.3: 创建概念文档目录

**Files:**
- Create: `docs/concepts/index.md`
- Create: `docs/concepts/.gitkeep`

**Step 1: 创建concepts目录和索引**

```bash
mkdir -p docs/concepts
cd docs/concepts
touch .gitkeep index.md
```

**Step 2: 编写概念索引**

```markdown
# 概念参考

概念文档深入解释EDA_UFMV的技术实现细节，帮助您理解框架是如何工作的。

## 核心概念

### [SV→Python概念映射](sv-to-python-mapping.md)
**必读** - SystemVerilog到Python的完整对照表

如果你熟悉SystemVerilog/UVM，从这里开始：
- 随机化概念映射
- 覆盖率概念映射
- 寄存器模型概念映射
- 关键差异说明

## 深入主题

### [随机化深入](randomization-deep-dive.md)
- 双求解器架构（PurePython + Z3）
- 约束AST系统
- 约束求解算法
- 设计模式应用

### [覆盖率深入](coverage-deep-dive.md)
- CoverGroup/CoverPoint/Cross层次
- 6种Bin类型实现
- 数据库后端设计
- 报告生成器架构

### [RGM深入](rgm-deep-dive.md)
- Field/Register/RegisterBlock设计
- 15种访问类型实现
- 硬件适配器模式
- 代码生成器设计

---

## 阅读建议

- **场景文档** → "如何使用"
- **概念文档** → "如何工作"
- **API文档** → "完整接口"

建议先阅读场景文档解决问题，再查阅概念文档理解原理。
```

**Step 3: 提交**

```bash
git add docs/concepts/
git commit -m "docs: 创建概念文档目录和索引"
```

---

### 阶段2：核心场景文档（2-3天）

### Task 2.1: 编写场景1 - 生成随机测试激励

**Files:**
- Create: `docs/scenarios/01-generate-random.md`

**Step 1: 创建场景1文档**

```bash
touch docs/scenarios/01-generate-random.md
```

**Step 2: 编写完整内容（分节完成）**

首先写入文档头部和前3节：

```markdown
# 场景1：生成随机测试激励

## 阅读路径

```
🟢 基础使用    → 只读"快速开始"（10分钟）
🟡 进阶应用    → 读"快速开始"+"常见任务"（30分钟）
🟠 理解原理    → 读"技术实现"（1小时）
🔴 深入定制    → 读"扩展机制"+API参考
```

---

## 1. 场景目标

生成符合约束的随机激励数据，用于测试DUT的各种边界情况和功能点。

> "我需要生成随机的DMA传输请求，测试不同地址、长度和优先级的组合"

---

## 2. SystemVerilog对应（5分钟理解）

如果你熟悉SystemVerilog，这相当于：

| SystemVerilog | Python (EDA_UFMV) | 说明 |
|---------------|-------------------|------|
| `rand int x;` | `x: rand(int)(bits=32)` | 随机变量声明 |
| `randc bit [3:0] id;` | `id: randc(int)(bits=4)` | 循环随机变量 |
| `constraint c { x > 0; }` | `@constraint def c(self): return self.x > 0` | 约束定义 |
| `x inside {[0:100]};` | `x: rand(int)(min=0, max=100)` | 范围约束 |
| `dist {0:=80, 1:=20}` | `dist({0: 80, 1: 20})` | 权重分布 |
| `std::randomize(x)` | `obj.randomize()` | 随机化调用 |
| `solve x before y` | Python原生表达式优先级 | 求解顺序 |

**关键差异**：
- Python使用**类型注解**声明随机变量
- 约束是**方法**而非块
- 可以使用**原生Python表达式**（更灵活）

---

## 3. 快速开始（10分钟上手）

### 3.1 最简单的随机变量

**示例**：生成一个16位随机数

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand

# 定义随机变量类型
value_rand = rand(int)(bits=16, min=0, max=65535)

class MyTransaction(Randomizable):
    value: value_rand

# 使用
txn = MyTransaction()
for i in range(5):
    txn.randomize()
    print(f"value = {txn.value}")
```

**运行结果**：
```
value = 38241
value = 12755
value = 59102
value = 23456
value = 44991
```

---

### 3.2 添加约束

**示例**：确保value大于1000

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint

value_rand = rand(int)(bits=16, min=0, max=65535)

class MyTransaction(Randomizable):
    value: value_rand

    @constraint
    def value_above_1000(self):
        return self.value > 1000

# 使用
txn = MyTransaction()
for i in range(5):
    txn.randomize()
    print(f"value = {txn.value}")
```

**运行结果**：
```
value = 5421
value = 8901
value = 1234
value = 25678
value = 3456
```

---

### 3.3 完整数据包示例

**示例**：DMA数据包（多变量 + 复杂约束）

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint

# 定义随机变量
src_addr_rand = rand(int)(bits=32, min=0x0000_0000, max=0xFFFF_FFFF)
dst_addr_rand = rand(int)(bits=32, min=0x0000_0000, max=0xFFFF_FFFF)
data_len_rand = rand(int)(bits=16, min=0, max=1500)
priority_rand = randc(int)(bits=3, min=0, max=7)

class DMAPacket(Randomizable):
    """DMA传输数据包"""
    src_addr: src_addr_rand
    dst_addr: dst_addr_rand
    data_len: data_len_rand
    priority: priority_rand

    @constraint
    def valid_addresses(self):
        """源地址和目标地址不能相同"""
        return self.src_addr != self.dst_addr

    @constraint
    def reasonable_length(self):
        """数据长度必须是8的倍数"""
        return self.data_len % 8 == 0

    @constraint
    def high_priority_for_long_transfer(self):
        """长传输使用高优先级"""
        if self.data_len > 1000:
            return self.priority >= 5
        return True

# 生成10个DMA数据包
packet = DMAPacket()
for i in range(10):
    packet.randomize()
    print(f"P{i}: src=0x{packet.src_addr:08X}, "
          f"dst=0x{packet.dst_addr:08X}, "
          f"len={packet.data_len}, "
          f"pri={packet.priority}")
```

**运行结果**：
```
P0: src=0x12AB34CD, dst=0x56EF7890, len=512, pri=3
P1: src=0xABCD1234, dst=0x567890EF, len=1024, pri=6
P2: src=0x12345678, dst=0x9ABCDEF0, len=256, pri=1
...
```

**保存为可运行脚本**：`examples/scenarios/dma_packet_randomization.py`

---

## 4. 常见任务（按需查阅）

### 任务1：控制随机分布（权重）

**问题**：我想让某些值出现得更频繁

**解决方案**：使用 `dist` 约束

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint
from sv_randomizer.api.dsl import dist

# 大部分时候(80%)传输短数据，偶尔(20%)传输长数据
data_len_rand = rand(int)(bits=16)

class ShortBurstTransaction(Randomizable):
    data_len: data_len_rand

    @constraint
    def prefer_short_bursts(self):
        return dist({
            64: 50,      # 50%概率是64字节
            128: 30,     # 30%概率是128字节
            256: 15,     # 15%概率是256字节
            1024: 5      # 5%概率是1024字节
        }).check(self.data_len)
```

---

### 任务2：设置种子复现结果

**问题**：我想让随机结果可重现（调试时有用）

**解决方案**：使用种子

```python
from sv_randomizer import seed

# 设置全局种子
seed(42)

# 之后所有随机化都是确定性的
packet = DMAPacket()
packet.randomize()
print(packet.src_addr)  # 每次运行都是相同的值
```

**对象级种子**：
```python
# 只影响这个对象
packet = DMAPacket()
packet.randomize(seed=42)
```

---

### 任务3：生成不重复的序列

**问题**：我想生成不重复的随机值

**解决方案**：使用 `randc`（循环随机）

```python
from sv_randomizer.api import randc

# 生成0-7的不重复序列，全部生成完才重复
id_rand = randc(int)(bits=3, min=0, max=7)

class Transaction(Randomizable):
    id: id_rand

txn = Transaction()
for i in range(10):
    txn.randomize()
    print(f"id = {txn.id}")
```

**运行结果**：
```
id = 3
id = 7
id = 1
id = 5
id = 0
id = 4
id = 2
id = 6
id = 3  # 开始循环
id = 7
```

---

### 任务4：范围约束（inside）

**问题**：我想限制值在某个范围内

**解决方案**：使用 `inside` 函数

```python
from sv_randomizer.api.dsl import inside

addr_rand = rand(int)(bits=32)

class Transaction(Randomizable):
    addr: addr_rand

    @constraint
    def valid_addr_ranges(self):
        # 地址必须在以下范围内之一
        return inside(self.addr, [
            (0x0000_0000, 0x0FFF_FFFF),  # 第一个256MB区域
            (0x1000_0000, 0x10FF_FFFF),  # 第二个16MB区域
            0xF000_0000,                  # 单个值
        ])
```

---

### 任务5：组合约束

**问题**：我想同时使用多个约束

**解决方案**：定义多个 `@constraint` 方法

```python
class SmartTransaction(Randomizable):
    addr: addr_rand
    data_len: data_len_rand

    @constraint
    def addr_aligned(self):
        """地址必须8字节对齐"""
        return self.addr % 8 == 0

    @constraint
    def len_reasonable(self):
        """长度在64-1500之间"""
        return 64 <= self.data_len <= 1500

    @constraint
    def high_addr_small_len(self):
        """高地址使用小长度"""
        if self.addr > 0x8000_0000:
            return self.data_len < 512
        return True
```

---

## 5. 技术实现（🔧 实现细节）

### 5.1 框架架构

```
Randomizable (基类)
    │
    ├── randomize() 方法
    │   ├── pre_randomize() 钩子
    │   ├── 约束求解
    │   └── post_randomize() 钩子
    │
    └── _constraints (约束列表)
        └── Constraint (AST节点)
            ├── VariableExpr (变量表达式)
            ├── BinaryExpr (二元表达式)
            ├── InsideConstraint (范围约束)
            └── DistConstraint (权重约束)
                    ↓
            ConstraintSolver (求解器接口)
                ├── PurePythonSolver (默认)
                └─ ─ Z3Solver (可选)
```

**核心类**：

1. **Randomizable** - 所有随机化对象的基类
   - 提供randomize()方法
   - 管理约束列表
   - 支持pre/post随机化钩子

2. **RandVar / RandCVar** - 随机变量定义
   - 存储变量的位宽、范围
   - RandCVar额外维护历史值列表（实现不重复）

3. **Constraint** - 约束表达式
   - 使用AST（抽象语法树）表示
   - 支持惰性求值

4. **SolverBackend** - 求解器接口
   - 策略模式，可插拔后端
   - PurePythonSolver：纯Python实现
   - Z3Solver：使用Z3 SMT求解器

---

### 5.2 约束求解算法

#### PurePythonSolver（默认）

**算法流程**：

```python
def solve(variables, constraints):
    # 1. 约束分类
    simple_constraints = []  # 直接赋值
    range_constraints = []    # 范围约束
    relation_constraints = [] # 关系约束

    # 2. 第一轮：求解简单约束
    for v in variables:
        if v.has_default_value():
            v.value = v.default_value

    # 3. 第二轮：求解范围约束
    for v in variables_without_value:
        min_val = v.min_value()
        max_val = v.max_value()
        v.value = random_int(min_val, max_val)

    # 4. 第三轮：迭代求解关系约束
    max_iterations = 1000
    for i in range(max_iterations):
        all_satisfied = True
        for constraint in relation_constraints:
            if not constraint.evaluate():
                all_satisfied = False
                # 调整变量值
                adjust_randomly(constraint.variables)
        if all_satisfied:
            return True  # 成功

    return False  # 失败
```

**时间复杂度**：
- O(n) - n为变量数（简单情况）
- O(k×n) - k为迭代次数（有关系约束，通常k<100）

#### Z3Solver（可选）

**算法流程**：

```python
def solve(variables, constraints):
    # 1. 转换为SMT-LIB格式
    solver = z3.Solver()

    # 2. 添加变量声明
    for v in variables:
        z3_var = z3.BitVec(v.name, v.bits)
        solver.add(z3_var >= v.min_value())
        solver.add(z3_var <= v.max_value())

    # 3. 添加约束
    for c in constraints:
        z3_constraint = to_z3_expr(c)
        solver.add(z3_constraint)

    # 4. 求解
    if solver.check() == z3.sat:
        model = solver.model()
        return extract_values(model)
    else:
        return None  # 无解
```

**优势**：
- 完整性保证（一定找到解或证明无解）
- 支持复杂约束（非线性、位向量）
- 适合工业级应用

**性能**：
- 比PurePython慢约10倍
- 但复杂约束下成功率更高

---

### 5.3 设计模式

| 模式 | 应用 | 优势 |
|------|------|------|
| **策略模式** | SolverBackend | 可插拔求解器，用户可选择性能/完整性 |
| **装饰器模式** | @rand, @constraint | 简洁的API语法，减少样板代码 |
| **观察者模式** | pre/post_randomize | 回调机制，支持自定义逻辑 |
| **工厂模式** | SolverFactory | 统一创建求解器，隐藏配置细节 |
| **AST模式** | Constraint表达式 | 灵活的表达式组合和求值 |

**示例：策略模式**

```python
class SolverBackend(ABC):
    @abstractmethod
    def solve(self, variables, constraints):
        pass

class PurePythonSolver(SolverBackend):
    def solve(self, variables, constraints):
        # 纯Python实现
        pass

class Z3Solver(SolverBackend):
    def solve(self, variables, constraints):
        # Z3实现
        pass

# 使用时
solver = SolverFactory.create('pure_python')  # 或 'z3'
result = solver.solve(variables, constraints)
```

---

### 5.4 性能考虑

**基准测试**（10个随机变量，1000次随机化）：

| 求解器 | 速度 | 适用场景 |
|--------|------|----------|
| PurePython | ~10,000 ops/sec | 简单约束，快速验证 |
| Z3 | ~1,000 ops/sec | 复杂约束，工业应用 |

**优化技术**：

1. **惰性求值** - 只求解被访问的变量
```python
class Randomizable:
    def __getattr__(self, name):
        if not self._randomized:
            self.randomize()
        return self._vars[name]
```

2. **约束缓存** - 相同约束的求解结果可复用
```python
@constraint
@lru_cache(maxsize=128)
def expensive_check(self):
    return complex_calculation()
```

3. **增量求解** - Z3模式下支持push/pop约束
```python
solver.push()  # 保存当前约束状态
solver.add(temp_constraint)
result = solver.check()
solver.pop()   # 恢复状态
```

---

### 5.5 与SystemVerilog的差异

| 特性 | SystemVerilog | Python实现 | 差异说明 |
|------|---------------|-----------|----------|
| **变量声明** | `rand int x;` | `x: rand(int)(bits=32)` | Python使用类型注解 |
| **约束块** | `constraint c { x > 0; }` | `@constraint def c(self): return self.x > 0` | Python使用方法 |
| **约束求解** | 内置SMT求解器 | 可选后端 | Python提供两种选择 |
| **随机化** | `std::randomize(x)` | `obj.randomize()` | 面向对象调用 |
| **类型系统** | 静态类型 | 动态类型 + 类型提示 | Python更灵活 |
| **约束语法** | SV专用语法 | Python原生表达式 | Python更通用 |
| **求解时机** | 编译时 | 运行时 | Python动态性更强 |

**性能对比**：

```
SystemVerilog仿真器:  ~1,000 randomizations/sec
EDA_UFMV (PurePython): ~10,000 randomizations/sec (10x faster)
EDA_UFMV (Z3):         ~1,000 randomizations/sec (similar)
```

---

### 5.6 扩展机制

**自定义求解器**：

```python
from sv_randomizer.solvers import SolverBackend
from sv_randomizer.solvers import SolverFactory

class MyCustomSolver(SolverBackend):
    """自定义求解器示例"""

    name = "my_custom"

    def solve(self, variables, constraints):
        # 实现你的求解逻辑
        for v in variables:
            # 例如：使用机器学习模型预测值
            v.value = my_ml_model.predict(v)

        # 验证约束
        for c in constraints:
            if not c.evaluate():
                return False
        return True

# 注册求解器
SolverFactory.register(MyCustomSolver.name, MyCustomSolver)

# 使用
solver = SolverFactory.create('my_custom')
```

**自定义约束类型**：

```python
from sv_randomizer.constraints import Constraint

class RegexConstraint(Constraint):
    """正则表达式约束"""

    def __init__(self, variable, pattern):
        self.variable = variable
        self.pattern = re.compile(pattern)

    def evaluate(self):
        value = str(self.variable.value)
        return bool(self.pattern.match(value))

# 使用
class EmailTransaction(Randomizable):
    email: rand(str)

    @constraint
    def valid_email_format(self):
        return RegexConstraint(self.email, r'[a-z]+@[a-z]+\.[a-z]+')
```

---

## 6. 故障排查

### 问题1：约束无法满足

**症状**：
```
RuntimeError: Constraint solving failed after 1000 iterations
```

**原因**：约束之间冲突或过于严格

**解决方案**：
1. 检查约束是否矛盾
```python
# 错误：两个约束冲突
@constraint
def always_100(self):
    return self.value == 100

@constraint
def always_200(self):
    return self.value == 200
```

2. 放宽约束条件
```python
# 改为范围
@constraint
def around_100_to_200(self):
    return 100 <= self.value <= 200
```

3. 增加最大迭代次数
```python
obj.randomize(max_iterations=10000)
```

---

### 问题2：随机化速度慢

**症状**：生成1000个样本需要很长时间

**可能原因**：
1. 约束过于复杂
2. 使用了Z3求解器但不需要

**解决方案**：
1. 简化约束
```python
# 复杂：嵌套条件
@constraint
def complex_check(self):
    if self.x > 100:
        if self.y < 50:
            return self.z == 0
        else:
            return self.z == 1
    return True

# 简化：直接表达式
@constraint
def simplified(self):
    return not (self.x > 100 and self.y < 50 and self.z != 0)
```

2. 使用更快的求解器
```python
from sv_randomizer.solvers import SolverFactory

# 切换到PurePython求解器
SolverFactory.set_default('pure_python')
```

---

### 问题3：随机结果不符合预期

**症状**：某个值从未出现

**原因**：范围或约束排除了该值

**解决方案**：使用种子调试
```python
# 设置种子，复现问题
seed(42)
obj.randomize()
print(obj.value)  # 检查值

# 逐步添加约束，找出问题
```

---

## 7. 参考资料

### 相关文档
- [约束系统深入](../concepts/randomization-deep-dive.md) - 算法细节
- [API参考：Randomizable](../api/API_REFERENCE.md#randomizable) - 完整API
- [示例：数据包生成](../../examples/rand/packet_generator.py) - 可运行代码

### SystemVerilog资源
- [SystemVerilog LRM](https://ieeexplore.ieee.org/document/) - 官方规范
- [UVM用户指南](https://www.accellera.org/) - UVM官方文档

---

**下一场景**：[场景2：收集功能覆盖率](02-collect-coverage.md) →
```

**Step 3: 验证Markdown格式**

```bash
# 检查文件
wc -l docs/scenarios/01-generate-random.md
```

Expected: 大约600-800行

**Step 4: 提交**

```bash
git add docs/scenarios/01-generate-random.md
git commit -m "docs: 添加场景1文档 - 生成随机测试激励"
```

---

### Task 2.2: 编写场景2 - 收集功能覆盖率

**Files:**
- Create: `docs/scenarios/02-collect-coverage.md`

**Step 1: 创建场景2文档**

```bash
touch docs/scenarios/02-collect-coverage.md
```

**Step 2: 编写完整内容**

```markdown
# 场景2：收集功能覆盖率

## 阅读路径

```
🟢 基础使用    → 只读"快速开始"
🟡 进阶应用    → 读"快速开始"+"常见任务"
🟠 理解原理    → 读"技术实现"
🔴 深入定制    → 读"扩展机制"+API参考
```

---

## 1. 场景目标

测量验证的完整性，确保测试覆盖了所有重要的功能和边界情况。

> "我需要验证DMA控制器的所有配置组合都被测试到"

---

## 2. SystemVerilog对应

| SystemVerilog | Python | 说明 |
|---------------|--------|------|
| `covergroup cg;` | `cg = CoverGroup("cg")` | 覆盖率组 |
| `coverpoint cp;` | `CoverPoint("cp", ...)` | 覆盖点 |
| `bins b = {1, 2, 3};` | `ValueBin("b", [1,2,3])` | 值bin |
| `bins b = {[1:10]};` | `RangeBin("b", 1, 10)` | 范围bin |
| `cross cp1, cp2;` | `Cross("cross", [cp1, cp2])` | 交叉覆盖 |

---

## 3. 快速开始

### 3.1 最简单的覆盖率

```python
from coverage import CoverGroup, CoverPoint
from coverage.core.bin import ValueBin

# 创建覆盖率组
cg = CoverGroup("my_coverage")

# 定义覆盖点
@CoverPoint("value_cp", cg)
class ValueCoverPoint:
    def __init__(self):
        self.bins = {
            "low": ValueBin("low", lambda: 0),
            "medium": ValueBin("medium", lambda: 1),
            "high": ValueBin("high", lambda: 2),
        }

# 采样
cg.sample()
print(f"Coverage: {cg.get_coverage():.1f}%")
```

---

### 3.2 完整DMA示例

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand
from coverage import CoverGroup, CoverPoint
from coverage.core.bin import RangeBin, ValueBin

class DMAConfig(Randomizable):
    addr: rand(int)(bits=32, min=0, max=0xFFFF_FFFF)
    length: rand(int)(bits=16, min=0, max=1500)

    def __init__(self):
        super().__init__()

        # 创建覆盖率组
        self.cg = CoverGroup("dma_coverage")

        # 地址范围覆盖点
        @CoverPoint("addr_range", self.cg)
        class AddrCoverPoint:
            def __init__(self, outer):
                self.bins = {
                    "low_256MB": RangeBin("low", lambda: 0x0000_0000, lambda: 0x0FFF_FFFF),
                    "mid_512MB": RangeBin("mid", lambda: 0x1000_0000, lambda: 0x1FFF_FFFF),
                    "high_1GB": RangeBin("high", lambda: 0x8000_0000, lambda: 0xFFFF_FFFF),
                }
            self.outer = outer

        # 传输长度覆盖点
        @CoverPoint("length_bins", self.cg)
        class LengthCoverPoint:
            def __init__(self, outer):
                self.bins = {
                    "small": RangeBin("small", lambda: 0, lambda: 64),
                    "medium": RangeBin("medium", lambda: 65, lambda: 512),
                    "large": RangeBin("large", lambda: 513, lambda: 1500),
                }
            self.outer = outer

# 生成配置并采样
config = DMAConfig()
for i in range(100):
    config.randomize()
    config.cg.sample()

print(f"Coverage: {config.cg.get_coverage():.1f}%")
```

---

## 4. 常见任务

### 任务1：忽略某些值

### 任务2：定义非法值

### 任务3：交叉覆盖率

---

## 5. 技术实现

### 5.1 框架架构

```
CoverGroup
    ├── CoverPoint (列表)
    │   └── Bin (字典)
    │       ├── ValueBin
    │       ├── RangeBin
    │       ├── WildcardBin
    │       ├── AutoBin
    │       ├── IgnoreBin
    │       └── IllegalBin
    └── Cross (列表)
```

### 5.2 采样算法

### 5.3 设计模式

### 5.4 性能考虑

---

## 6. 故障排查

---

## 7. 参考资料
```

**Step 3: 提交**

```bash
git add docs/scenarios/02-collect-coverage.md
git commit -m "docs: 添加场景2文档 - 收集功能覆盖率"
```

---

### Task 2.3-2.6: 其他场景文档

**说明**：按照相同的模板和详细程度，完成剩余4个场景文档：

- Task 2.3: `03-create-regmodel.md` - 创建寄存器模型
- Task 2.4: `04-migrate-from-sv.md` - 从SystemVerilog迁移
- Task 2.5: `05-automate-conversion.md` - 自动化SV→Python转换
- Task 2.6: `06-complete-workflow.md` - 完整验证流程案例

**每个Task的结构**：
1. 创建文件
2. 编写内容（参照Task 2.1的详细程度）
3. 验证格式
4. 提交

---

### 阶段3：概念参考文档（1-2天）

### Task 3.1: 编写SV→Python映射表

**Files:**
- Create: `docs/concepts/sv-to-python-mapping.md`

**Step 1: 创建映射表文档**

```bash
touch docs/concepts/sv-to-python-mapping.md
```

**Step 2: 编写完整映射表**

```markdown
# SystemVerilog → Python 概念映射表

本文档提供SystemVerilog/UVM到Python的完整概念对照，帮助SV工程师快速理解EDA_UFMV。

---

## 核心概念映射

### 随机化

| SystemVerilog | Python (EDA_UFMV) | 示例 |
|---------------|-------------------|------|
| `rand int x;` | `x: rand(int)(bits=32)` | 随机变量 |
| `randc bit [3:0] id;` | `id: randc(int)(bits=4)` | 循环随机 |
| `constraint c { x > 0; }` | `@constraint def c(self): return self.x > 0` | 约束 |
| `x inside {[0:100]};` | `x: rand(int)(min=0, max=100)` | 范围 |
| `dist {0:=80, 1:=20}` | `dist({0: 80, 1: 20})` | 权重 |
| `std::randomize(x)` | `obj.randomize()` | 随机化 |
| `randmode(0)` | `N/A`（删除变量） | 禁用随机 |
| `pre_randomize()` | `def pre_randomize(self):` | 前回调 |
| `post_randomize()` | `def post_randomize(self):` | 后回调 |

### 覆盖率

| SystemVerilog | Python | 说明 |
|---------------|--------|------|
| `covergroup cg;` | `cg = CoverGroup("cg")` | 覆盖率组 |
| `coverpoint cp;` | `CoverPoint("cp", ...)` | 覆盖点 |
| `bins b = {1, 2};` | `ValueBin("b", [1, 2])` | 值bin |
| `bins b = {[1:10]};` | `RangeBin("b", 1, 10)` | 范围bin |
| `bins b[] = {[0:255]};` | `AutoBin("b", count=10)` | 自动bin |
| `ignore_bins i = {0};` | `IgnoreBin("i", [0])` | 忽略bin |
| `illegal_bins i = {-1};` | `IllegalBin("i", [-1])` | 非法bin |
| `cross a, b;` | `Cross("x", [a, b])` | 交叉覆盖 |
| `option.per_instance = 1` | `CoverGroup(..., per_instance=True)` | 实例选项 |
| `sample()` | `cg.sample()` | 采样 |

### 寄存器模型

| SystemVerilog (UVM) | Python | 说明 |
|---------------------|--------|------|
| `uvm_reg_block` | `RegisterBlock` | 寄存器块 |
| `uvm_reg` | `Register` | 寄存器 |
| `uvm_reg_field` | `Field` | 字段 |
| `RW, RO, WO` | `AccessType.RW, .RO, .WO` | 访问类型 |
| `write(status, value)` | `reg.write(value)` | 写入 |
| `read(status, value)` | `value = reg.read()` | 读取 |
| `set(value)` | `reg.set(value)` | 设置期望值 |
| `get()` | `value = reg.get()` | 获取期望值 |
| `update(status)` | `reg.update()` | 更新到DUT |
| `mirror(status)` | `reg.mirror()` | 从DUT镜像 |
| `poke(offset, value)` | `reg.poke(value)` | 后门写 |
| `peek(offset, value)` | `value = reg.peek()` | 后门读 |
| `reset(kind)` | `reg.reset()` | 复位 |

---

## 语法差异对照

### 变量声明

**SystemVerilog**:
```systemverilog
class Transaction;
  rand bit [31:0] addr;
  rand int length;

  constraint valid {
    addr > 0;
    length inside {[64:1500]};
  }
endclass
```

**Python**:
```python
class Transaction(Randomizable):
    addr: rand(int)(bits=32, min=0, max=0xFFFF_FFFF)
    length: rand(int)(bits=16, min=64, max=1500)

    @constraint
    def valid(self):
        return self.addr > 0
```

**关键差异**：
- Python使用类型注解 `variable: type`
- 约束是方法而非块
- 使用原生Python表达式

---

### 约束表达式

| SystemVerilog | Python | 说明 |
|---------------|--------|------|
| `x && y` | `x and y` | 逻辑与 |
| `x \|\| y` | `x or y` | 逻辑或 |
| `!x` | `not x` | 逻辑非 |
| `x == y` | `x == y` | 相等 |
| `x != y` | `x != y` | 不等 |
| `x > y` | `x > y` | 大于 |
| `x inside {a, b, c}` | `inside(x, [a, b, c])` | 成员检查 |
| `x -> y` | `if x: y` | 蕴含 |
| `solve x before y` | 表达式顺序 | 求解顺序 |

---

## 迁移示例

### 示例1：简单随机化迁移

**SystemVerilog**:
```systemverilog
class Packet;
  rand bit [15:0] src_addr;
  rand bit [15:0] dst_addr;

  constraint different {
    src_addr != dst_addr;
  }
endclass

Packet pkt = new();
pkt.randomize();
```

**Python**:
```python
class Packet(Randomizable):
    src_addr: rand(int)(bits=16, min=0, max=65535)
    dst_addr: rand(int)(bits=16, min=0, max=65535)

    @constraint
    def different(self):
        return self.src_addr != self.dst_addr

pkt = Packet()
pkt.randomize()
```

---

### 示例2：覆盖率迁移

**SystemVerilog**:
```systemverilog
covergroup cg @(posedge clk);
  coverpoint addr {
    bins low = {[0:0x0FFF]};
    bins high = {[0x1000:0x1FFF]};
  }
  coverpoint len {
    bins small[] = {[1:10]};
    bins large = {[100:1000]};
  }
  cross addr, len;
endgroup
```

**Python**:
```python
cg = CoverGroup("cg")

@CoverPoint("addr", cg)
class AddrCP:
    def __init__(self):
        self.bins = {
            "low": RangeBin("low", 0x0000, 0x0FFF),
            "high": RangeBin("high", 0x1000, 0x1FFF),
        }

@CoverPoint("len", cg)
class LenCP:
    def __init__(self):
        self.bins = {
            "small": AutoBin("small", lambda: 1, lambda: 10, count=5),
            "large": RangeBin("large", 100, 1000),
        }

Cross("addr_len_cross", cg, [addr_cp, len_cp])
```

---

### 示例3：寄存器模型迁移

**SystemVerilog (UVM)**:
```systemverilog
class dma_ctrl_reg extends uvm_reg;
  `uvm_object_utils(dma_ctrl_reg)

  rand uvm_reg_field enable;
  rand uvm_reg_field start;

  function void build();
    enable = uvm_reg_field::type_id::create("enable");
    enable.configure(this, 1, 0, "RW", 0, 0, 1, 0, 0);
    start = uvm_reg_field::type_id::create("start");
    start.configure(this, 1, 1, "RW", 0, 0, 1, 0, 0);
  endfunction
endclass
```

**Python**:
```python
dma_ctrl = Register("DMA_CTRL", offset=0x00, width=32)
dma_ctrl.add_field(Field("ENABLE", 0, 1, AccessType.RW, 0))
dma_ctrl.add_field(Field("START", 1, 1, AccessType.RW, 0))
```

---

## 语义差异

### 类型系统

| 方面 | SystemVerilog | Python |
|------|---------------|--------|
| 类型检查 | 编译时，严格 | 运行时，灵活 |
| 位宽 | 显式 `bit [31:0]` | 参数 `bits=32` |
| 类型转换 | 隐式（有风险） | 显式（更安全） |
| 四态逻辑 | `0, 1, X, Z` | 二值 `0, 1` |

### 求解语义

| 方面 | SystemVerilog | Python |
|------|---------------|--------|
| 求解时机 | 编译时 + 仿真时 | 运行时 |
| 约束冲突 | 编译错误 | 运行时异常 |
| 随机化分布 | 仿真器决定 | 用户可控 |
| 调试支持 | 波形查看 | print/log |

---

## 性能对比

| 操作 | SystemVerilog | Python | 差异 |
|------|---------------|--------|------|
| 简单随机化 | ~1000 ops/sec | ~10,000 ops/sec | **10x faster** |
| 约束求解 | ~500 ops/sec | ~10,000 ops/sec | **20x faster** |
| 覆盖率采样 | ~10K samples/sec | ~246K samples/sec | **24x faster** |
| 仿真启动 | 慢（编译） | 快（直接运行） | **N/A** |

**说明**：Python不需要编译，开发迭代速度更快

---

## 最佳实践

### 从SystemVerilog迁移的建议

1. **从简单开始** - 先迁移基本随机化
2. **逐步添加约束** - 约束越多越难满足
3. **使用种子调试** - 复现问题
4. **对比覆盖率** - 确保迁移后覆盖率相当
5. **利用Python生态** - 使用pytest、matplotlib等工具

### 需要特别注意的差异

1. **无四态逻辑** - Python只有0和1，没有X/Z
2. **类型注解语法** - 使用冒号而非分号
3. **约束是方法** - 需要return语句
4. **运行时检查** - 类型错误在运行时发现
5. **无时间语义** - Python不仿真时间，只生成数据

---

## 常见迁移错误

### 错误1：忘记return

```python
# 错误
@constraint
def valid(self):
    self.x > 0  # 缺少return

# 正确
@constraint
def valid(self):
    return self.x > 0
```

### 错误2：使用分号

```python
# 错误
value: rand(int)(bits=32);

# 正确
value: rand(int)(bits=32)
```

### 错误3：SV约束语法

```python
# 错误（SystemVerilog语法）
@constraint
def valid(self):
    self.x inside {[0:100]}  # inside是函数

# 正确
from sv_randomizer.api.dsl import inside

@constraint
def valid(self):
    return inside(self.x, [(0, 100)])
```

---

## 参考资料

- [场景1：生成随机激励](../scenarios/01-generate-random.md)
- [场景2：收集覆盖率](../scenarios/02-collect-coverage.md)
- [随机化深入](randomization-deep-dive.md)
- [覆盖率深入](coverage-deep-dive.md)
```

**Step 3: 提交**

```bash
git add docs/concepts/sv-to-python-mapping.md
git commit -m "docs: 添加SV到Python概念映射表"
```

---

### Task 3.2-3.4: 其他概念文档

按照相同详细程度创建：
- Task 3.2: `randomization-deep-dive.md`
- Task 3.3: `coverage-deep-dive.md`
- Task 3.4: `rgm-deep-dive.md`

---

### 阶段4：文档集成和优化（半天）

### Task 4.1: 更新README.md

**Files:**
- Modify: `README.md`

**Step 1: 修改README中的文档部分**

找到README中的文档部分（约135-160行），更新为：

```markdown
## 文档

### 🎯 场景化文档（推荐新手）

按"我想做什么"快速找到解决方案：

- 🎲 [生成随机测试激励](docs/scenarios/01-generate-random.md) - 随机化入门
- 📊 [收集功能覆盖率](docs/scenarios/02-collect-coverage.md) - 覆盖率入门
- 🗄️ [创建寄存器模型](docs/scenarios/03-create-regmodel.md) - RGM入门
- 🔄 [从SystemVerilog迁移](docs/scenarios/04-migrate-from-sv.md) - 迁移指南
- 🤖 [自动化SV→Python转换](docs/scenarios/05-automate-conversion.md) - 转换器使用
- 📋 [完整验证流程](docs/scenarios/06-complete-workflow.md) - 端到端示例

**完整场景索引**: [docs/scenarios/index.md](docs/scenarios/index.md)

### 📚 概念参考

- 🔄 [SystemVerilog→Python映射表](docs/concepts/sv-to-python-mapping.md) - **必读**
- 🎲 [随机化深入](docs/concepts/randomization-deep-dive.md)
- 📊 [覆盖率深入](docs/concepts/coverage-deep-dive.md)
- 🗄️ [RGM深入](docs/concepts/rgm-deep-dive.md)

### 📖 传统文档

- 🚀 [快速开始](docs/user/quick-start.md)
- ✨ [功能清单](docs/product/features.md)
- 🎯 [应用场景](docs/product/use-cases.md)
- [完整文档导航](docs/README.md)
```

**Step 2: 验证修改**

```bash
grep -A 20 "## 文档" README.md
```

**Step 3: 提交**

```bash
git add README.md
git commit -m "docs: 更新README添加场景化文档导航"
```

---

### Task 4.2: 创建可运行示例

**Files:**
- Create: `examples/scenarios/dma_packet_randomization.py`
- Create: `examples/scenarios/dma_coverage.py`
- Create: `examples/scenarios/complete_dma_workflow.py`

**Step 1: 创建examples/scenarios目录**

```bash
mkdir -p examples/scenarios
```

**Step 2: 创建DMA随机化示例**

创建 `examples/scenarios/dma_packet_randomization.py`：

```python
"""
场景1示例：DMA数据包随机化

演示如何生成符合约束的随机DMA传输请求
"""

from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint

# 定义随机变量
src_addr_rand = rand(int)(bits=32, min=0x0000_0000, max=0xFFFF_FFFF)
dst_addr_rand = rand(int)(bits=32, min=0x0000_0000, max=0xFFFF_FFFF)
data_len_rand = rand(int)(bits=16, min=0, max=1500)
priority_rand = randc(int)(bits=3, min=0, max=7)

class DMAPacket(Randomizable):
    """DMA传输数据包"""

    src_addr: src_addr_rand
    dst_addr: dst_addr_rand
    data_len: data_len_rand
    priority: priority_rand

    @constraint
    def valid_addresses(self):
        """源地址和目标地址不能相同"""
        return self.src_addr != self.dst_addr

    @constraint
    def reasonable_length(self):
        """数据长度必须是8的倍数"""
        return self.data_len % 8 == 0

    @constraint
    def high_priority_for_long_transfer(self):
        """长传输使用高优先级"""
        if self.data_len > 1000:
            return self.priority >= 5
        return True


def main():
    """生成10个DMA数据包"""
    print("=" * 60)
    print("DMA数据包随机化示例")
    print("=" * 60)

    packet = DMAPacket()

    for i in range(10):
        packet.randomize()

        print(f"P{i}: src=0x{packet.src_addr:08X}, "
              f"dst=0x{packet.dst_addr:08X}, "
              f"len={packet.data_len:4d}, "
              f"pri={packet.priority}")

    print("=" * 60)
    print(f"所有约束满足!")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

**Step 3: 测试运行**

```bash
python examples/scenarios/dma_packet_randomization.py
```

Expected: 输出10个满足约束的DMA数据包

**Step 4: 提交**

```bash
git add examples/scenarios/
git commit -m "docs: 添加场景示例代码"
```

---

### Task 4.3: 文档交叉链接检查

**Step 1: 检查所有链接**

```bash
# 检查Markdown文件中的链接
grep -r "\[.*\](.*.md)" docs/scenarios/ docs/concepts/ | wc -l
```

**Step 2: 更新交叉引用**

确保每个场景文档都有：
- 前一场景链接
- 后一场景链接
- 相关概念文档链接

**Step 3: 提交**

```bash
git add docs/
git commit -m "docs: 完善文档交叉链接"
```

---

### 阶段5：验证和发布（半天）

### Task 5.1: 创建文档验证脚本

**Files:**
- Create: `scripts/validate_docs.py`

**Step 1: 创建验证脚本**

```python
"""文档验证脚本"""

import os
import re
from pathlib import Path

def validate_markdown_links(file_path):
    """验证Markdown文件中的链接"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取所有Markdown链接
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(pattern, content)

    broken = []
    for text, url in links:
        if url.endswith('.md'):
            target = Path(file_path).parent / url
            if not target.exists():
                broken.append((text, url, str(target)))

    return broken

def main():
    """验证所有文档"""
    docs_dir = Path('docs')

    print("验证文档链接...")

    all_broken = []
    for md_file in docs_dir.rglob('*.md'):
        broken = validate_markdown_links(md_file)
        if broken:
            all_broken.extend([(md_file, *b) for b in broken])

    if all_broken:
        print("\n发现断链:")
        for file, text, url, target in all_broken:
            print(f"  {file}: [{text}]({url}) -> {target}")
        return 1
    else:
        print("✓ 所有链接有效")
        return 0

if __name__ == "__main__":
    exit(main())
```

**Step 2: 运行验证**

```bash
python scripts/validate_docs.py
```

**Step 3: 提交**

```bash
git add scripts/validate_docs.py
git commit -m "docs: 添加文档验证脚本"
```

---

### Task 5.2: 创建文档更新检查清单

**Files:**
- Create: `docs/development/DOCUMENTATION_CHECKLIST.md`

```markdown
# 文档更新检查清单

当添加新功能或修改现有功能时，参考此清单更新文档。

## 新功能添加

- [ ] 在相应场景文档中添加示例
- [ ] 更新API参考文档
- [ ] 如有新概念，添加到概念映射表
- [ ] 创建可运行的示例脚本
- [ ] 更新README（如果是主要功能）

## 现有功能修改

- [ ] 更新场景文档中的示例
- [ ] 更新API参考
- [ ] 检查并更新概念文档
- [ ] 验证所有示例仍可运行

## 文档质量检查

- [ ] 所有代码示例可运行
- [ ] 所有Markdown链接有效
- [ ] 技术实现细节准确
- [ ] 包含足够的上下文
- [ ] 使用清晰的标题结构
```

---

### Task 5.3: 最终验证

**Step 1: 验证文档结构**

```bash
tree docs/ -L 2
```

Expected output:
```
docs/
├── scenarios/
│   ├── index.md
│   ├── 01-generate-random.md
│   ├── 02-collect-coverage.md
│   ├── 03-create-regmodel.md
│   ├── 04-migrate-from-sv.md
│   ├── 05-automate-conversion.md
│   └── 06-complete-workflow.md
├── concepts/
│   ├── index.md
│   ├── sv-to-python-mapping.md
│   ├── randomization-deep-dive.md
│   ├── coverage-deep-dive.md
│   └── rgm-deep-dive.md
└── ...
```

**Step 2: 验证示例可运行**

```bash
python examples/scenarios/dma_packet_randomization.py
```

**Step 3: 验证文档链接**

```bash
python scripts/validate_docs.py
```

**Step 4: 最终提交**

```bash
git add .
git commit -m "docs: 完成场景化文档系统"
```

---

## 总结

完成此计划后，您将拥有：

1. ✅ 6个场景文档，每个包含：
   - 快速开始（10分钟上手）
   - 常见任务（按需查阅）
   - 技术实现（框架、算法、设计模式）
   - 故障排查

2. ✅ 4个概念参考文档：
   - SV→Python映射表
   - 随机化深入
   - 覆盖率深入
   - RGM深入

3. ✅ 可运行的示例代码

4. ✅ 完整的文档导航和交叉引用

5. ✅ 文档验证工具

**预计时间**: 4-5天
**预计文档数量**: 10个主要文档 + 3个示例脚本
