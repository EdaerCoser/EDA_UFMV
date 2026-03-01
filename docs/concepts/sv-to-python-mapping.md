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

## 覆盖率详细映射

### 快速参考表

| SystemVerilog | Python (装饰器) | Python (传统API) |
|:---|:---|:---|
| `covergroup name;` | `@covergroup("name")` | `CoverGroup("name")` |
| `coverpoint var;` | `@coverpoint("var")` | `CoverPoint("var", "var")` |
| `bins b = {1,2,3};` | `bins={"values": [1,2,3]}` | 同左 |
| `bins b[] = {[0:255]};` | `bins={"ranges": [[0,255]]}` | 同左 |
| `wildcard bins b[] = {8???};` | `bins={"wildcards": ["8???"]}` | 同左 |
| `auto_bin_max = 16` | `bins={"auto": 16}` | 同左 |
| `ignore_bins b = {0};` | `ignore_bins={"b": [0]}` | 同左 |
| `illegal_bins b = {255};` | `illegal_bins={"b": [255]}` | 同左 |
| `cross cp1, cp2;` | `@cross("name", ["cp1","cp2"])` | `Cross("name", ["cp1","cp2"])` |
| `option.weight = 2.0` | `weight=2.0` | 同左 |
| `cg.sample()` | N/A (自动采样) | `cg.sample(**kwargs)` |

### 核心差异

| 特性 | SystemVerilog | Python (EDA_UFMV) |
|:---|:---|:---|
| **类型系统** | 静态类型，需指定位宽 | 动态类型，自动处理 |
| **采样表达式** | 直接引用变量 | `sample_expr="var"` 或 callable |
| **Bin初始化** | 编译时确定 | AutoBin采用懒加载 |
| **IllegalBin处理** | 记录警告 | 抛出 `IllegalBinHitError` |
| **API风格** | 语法块 | 装饰器（类似语法块）或传统API |

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
- [覆盖率迁移详细参考](../reference/coverage/migration.md)
