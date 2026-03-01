# 场景2：收集功能覆盖率

## 阅读路径

```
🟢 基础使用    → 只读"快速开始"（10分钟）
🟡 进阶应用    → 读"快速开始"+"常见任务"（30分钟）
🟠 理解原理    → 读"技术实现"（1小时）
🔴 深入定制    → 读"扩展机制"+API参考
```

---

## 1. 场景目标

测量验证的完整性，确保测试覆盖了所有重要的功能和边界情况。

> "我需要验证DMA控制器的所有配置组合都被测试到"

---

## 2. SystemVerilog对应（5分钟理解）

| SystemVerilog | Python | 说明 |
|---------------|--------|------|
| `covergroup cg;` | `cg = CoverGroup("cg")` | 覆盖率组 |
| `coverpoint cp;` | `CoverPoint("cp", ...)` | 覆盖点 |
| `bins b = {1, 2};` | `ValueBin("b", [1, 2])` | 值bin |
| `bins b = {[1:10]};` | `RangeBin("b", 1, 10)` | 范围bin |
| `bins b[] = {[0:255]};` | `AutoBin("b", count=10)` | 自动bin |
| `ignore_bins i = {0};` | `IgnoreBin("i", [0])` | 忽略bin |
| `illegal_bins i = {255};` | `IllegalBin("i", [255])` | 非法bin |
| `cross cp1, cp2;` | `Cross("x", [cp1, cp2])` | 交叉覆盖 |

**关键差异**：
- Python使用类或函数调用，不是语法块
- Bin类型使用专门的类
- 采样可以是自动或手动

---

## 3. 快速开始（10分钟上手）

### 3.1 最简单的覆盖率

**示例**：覆盖一个值的范围

```python
from coverage import CoverGroup, CoverPoint
from coverage.core.bin import RangeBin

# 创建覆盖率组
cg = CoverGroup("my_coverage")

# 定义覆盖点
addr_cp = CoverPoint("addr", "addr", bins={
    "low": RangeBin("low", 0x0000, 0x0FFF),
    "mid": RangeBin("mid", 0x1000, 0x1FFF),
    "high": RangeBin("high", 0x2000, 0xFFFF)
})

cg.add_coverpoint(addr_cp)

# 采样
cg.sample(addr=0x1234)
cg.sample(addr=0x2345)

# 查看覆盖率
print(f"Coverage: {cg.get_coverage():.1f}%")
```

---

### 3.2 与随机化集成

**示例**：自动采样覆盖率

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand
from coverage import CoverGroup, CoverPoint
from coverage.core.bin import RangeBin

class DMAConfig(Randomizable):
    def __init__(self):
        super().__init__()
        self.addr = rand(int)(bits=32, min=0, max=0xFFFF_FFFF)
        self.length = rand(int)(bits=16, min=0, max=1500)

        # 创建覆盖率组
        self.cg = CoverGroup("dma_coverage")

        # 地址覆盖点
        addr_cp = CoverPoint("addr", "addr", bins={
            "low_256MB": RangeBin("low", 0x0000_0000, 0x0FFF_FFFF),
            "mid_512MB": RangeBin("mid", 0x1000_0000, 0x1FFF_FFFF),
            "high_1GB": RangeBin("high", 0x8000_0000, 0xFFFF_FFFF)
        })
        self.cg.add_coverpoint(addr_cp)

        # 添加到Randomizable（自动采样）
        self.add_covergroup(self.cg)

# 生成配置并自动采样
config = DMAConfig()
for i in range(100):
    config.randomize()  # 自动采样覆盖率

print(f"Coverage: {config.cg.get_coverage():.1f}%")
```

---

### 3.3 交叉覆盖率

**示例**：地址和长度的组合

```python
from coverage import CoverGroup, CoverPoint, Cross
from coverage.core.bin import RangeBin, AutoBin

cg = CoverGroup("cross_coverage")

# 地址覆盖点
addr_cp = CoverPoint("addr", "addr", bins={
    "low": RangeBin("low", 0x0000, 0x0FFF),
    "high": RangeBin("high", 0x1000, 0xFFFF)
})

# 长度覆盖点
len_cp = CoverPoint("length", "length", bins={
    "auto": AutoBin("auto", lambda: 64, lambda: 1512, count=5)
})

# 交叉覆盖
cross = Cross("addr_len_cross", [addr_cp, len_cp])

cg.add_coverpoint(addr_cp)
cg.add_coverpoint(len_cp)
cg.add_cross(cross)

# 采样
for addr in [0x1000, 0x2000, 0x8000]:
    for length in [128, 256, 512]:
        cg.sample(addr=addr, length=length)

print(f"Coverage: {cg.get_coverage():.1f}%")
print(f"Cross coverage: {cross.get_coverage():.1f}%")
```

---

## 4. 常见任务（按需查阅）

### 任务1：忽略某些值

**问题**：我想忽略某些无效值

**解决方案**：使用 IgnoreBin

```python
from coverage.core.bin import RangeBin, IgnoreBin

addr_cp = CoverPoint("addr", "addr", bins={
    "valid_range": RangeBin("valid", 0x1000, 0xFFFF),
    "ignore_reserved": IgnoreBin("reserved", [0x0000, 0xFFFF])
})
```

---

### 任务2：定义非法值

**问题**：某些值不应该出现

**解决方案**：使用 IllegalBin（会抛出异常）

```python
from coverage.core.bin import RangeBin, IllegalBin

addr_cp = CoverPoint("addr", "addr", bins={
    "valid_range": RangeBin("valid", 0x1000, 0xFFFF),
    "illegal_addr": IllegalBin("illegal", [0x0000])
})
```

---

### 任务3：使用通配符匹配

**问题**：我想匹配特定模式的值

**解决方案**：使用 WildcardBin

```python
from coverage.core.bin import WildcardBin

# 匹配 8??? 的地址（8位开始，后3位任意）
pattern_cp = CoverPoint("pattern", "addr", bins={
    "pattern_8xxx": WildcardBin("pattern", "8???")
})
```

---

### 任务4：持久化覆盖率数据

**问题**：我想跨多次运行累积覆盖率

**解决方案**：使用文件数据库

```python
from coverage.database import DatabaseFactory
from coverage import CoverGroup

# 创建文件数据库
db = DatabaseFactory.create('file', path='coverage_data.json')

# 创建覆盖率组并指定数据库
cg = CoverGroup("my_coverage", database=db)

# 第一次运行
cg.sample(addr=0x1000)
cg.save()  # 保存到文件

# 第二次运行（累积）
cg.load()  # 从文件加载
cg.sample(addr=0x2000)
print(f"Total coverage: {cg.get_coverage():.1f}%")
```

---

### 任务5：生成HTML报告

**问题**：我想生成可视化覆盖率报告

**解决方案**：使用HTML报告生成器

```python
from coverage.formatters import ReportFactory

# 创建HTML报告
reporter = ReportFactory.create('html', output_dir='coverage_report')
reporter.generate(cg)

# 报告生成在 coverage_report/index.html
```

---

## 5. 深入理解

想了解更多实现细节和高级用法？

- **完整迁移指南**：[覆盖率迁移详细参考](../reference/coverage/migration.md)
- **覆盖率深入**：[覆盖率深入](../concepts/coverage-deep-dive.md)
- **SV对比**：[SV→Python映射](../concepts/sv-to-python-mapping.md)
- **更多示例**：[examples/coverage/](../../examples/coverage/)

---

## 6. 故障排查

### 问题1：IllegalBin被命中

**症状**：
```
IllegalBinHitError: Illegal bin 'illegal_addr' was hit with value 0x0000
```

**解决方案**：
1. 检查DUT配置，确保不生成非法值
2. 或将IllegalBin改为IgnoreBin（仅记录，不抛异常）

---

### 问题2：覆盖率不增长

**症状**：多次采样后覆盖率仍为0%

**原因**：采样值不在任何bin范围内

**解决方案**：
1. 检查bin定义是否正确
2. 打印采样值调试
3. 添加AutoBin自动覆盖所有值

---

### 问题3：交叉覆盖率爆炸

**症状**：交叉组合太多，内存不足

**解决方案**：
1. 减少单个覆盖点的bin数量
2. 使用过滤函数限制组合
3. 分离为多个独立的覆盖点

---

## 7. 下一步

现在你已经掌握了覆盖率基础，继续学习：

- **场景3**：[创建寄存器模型](03-create-regmodel.md) - DUT配置管理
- **场景6**：[完整验证流程](06-complete-workflow.md) - 端到端示例

或深入理解原理：
- [覆盖率深入](../concepts/coverage-deep-dive.md) - 架构、算法、性能
- [SV→Python映射](../concepts/sv-to-python-mapping.md) - 完整对照表
