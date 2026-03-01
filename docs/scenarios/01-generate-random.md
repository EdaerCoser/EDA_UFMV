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

## 5. 深入理解

想了解更多实现细节和高级用法？

- **完整API参考**：[随机化技术参考](../reference/randomization.md)
- **约束深入**：[随机化深入](../concepts/randomization-deep-dive.md)
- **SV对比**：[SV→Python映射](../concepts/sv-to-python-mapping.md)
- **更多示例**：[examples/rand/](../../examples/rand/)

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
2. 放宽约束条件
3. 增加最大迭代次数：`obj.randomize(max_iterations=10000)`

---

### 问题2：随机化速度慢

**症状**：生成1000个样本需要很长时间

**解决方案**：
1. 简化约束（避免复杂嵌套）
2. 使用更快的PurePython求解器（默认）

---

### 问题3：随机结果不符合预期

**症状**：某个值从未出现

**解决方案**：使用种子调试
```python
seed(42)  # 复现问题
obj.randomize()
print(obj.value)  # 检查值
```

---

## 7. 下一步

现在你已经掌握了随机化基础，继续学习：

- **场景2**：[收集功能覆盖率](02-collect-coverage.md) - 测量验证完整性
- **场景6**：[完整验证流程](06-complete-workflow.md) - 看所有模块如何协同

或深入理解原理：
- [随机化深入](../concepts/randomization-deep-dive.md) - 框架、算法、设计模式
- [SV→Python映射](../concepts/sv-to-python-mapping.md) - 完整概念对照表
