# 高级测试套件设计文档

**版本**: 1.0
**日期**: 2026-03-01
**作者**: Claude Sonnet 4.6
**状态**: 设计阶段

---

## 概述

为 EDA_UFMV 项目的新 API（v0.3.1 类型注解API）设计高级测试套件，包括复杂约束测试和性能测试。

### 目标

1. **复杂约束测试** - 验证系统在复杂约束场景下的正确性
2. **性能测试** - 验证系统的性能指标并检测性能退化
3. **摸高测试** - 找出系统的极限能力
4. **回归检测** - 确保代码变更不会导致性能下降

---

## 测试架构

### 文件组织

```
tests/test_api/
├── test_complex_protocols.py        # 硬件协议场景（~300行）
├── test_complex_constraints.py      # 数学/逻辑约束（~350行）
├── test_complex_stress.py            # 摸高测试（~400行）
├── test_performance_benchmarks.py    # 性能基准测试（~400行）
└── test_performance_stress.py        # 性能压力测试（~350行）

tests/test_api/helpers/
├── __init__.py
├── performance_utils.py             # 性能测量工具
├── scenario_generators.py           # 场景生成器
└── baseline_data.json               # 自动生成的基线
```

### 运行时间估算

| 文件 | 预计运行时间 |
|------|-------------|
| `test_complex_protocols.py` | ~10秒 |
| `test_complex_constraints.py` | ~15秒 |
| `test_complex_stress.py` | ~20秒 |
| `test_performance_benchmarks.py` | ~15秒 |
| `test_performance_stress.py` | ~25秒 |
| **总计** | **~85秒** |

---

## 第一部分：复杂约束测试

### 1.1 硬件协议场景

**测试文件**: `test_complex_protocols.py`

#### AXI总线事务

```python
class AXITransaction(Randomizable):
    addr: rand(int)(bits=32)
    data: rand(int)(bits=32)
    id: randc(int)(bits=4)
    len: rand(int)(bits=8, min=1, max=16)

    @constraint
    def addr_aligned(self):
        return self.addr % 4 == 0

    @constraint
    def burst_boundary(self):
        return (self.addr & ~0x3FF) == ((self.addr + self.len*4) & ~0x3FF)
```

#### UART配置

```python
class UARTConfig(Randomizable):
    baud_rate: rand(int)(enum_values=[9600, 19200, 38400, 57600, 115200])
    parity: rand(str)(enum_values=['NONE', 'EVEN', 'ODD'])
    stop_bits: rand(int)(bits=2, min=1, max=2)

    @constraint
    def high_rate_no_odd_parity(self):
        return not (self.baud_rate >= 115200 and self.parity == 'ODD')
```

#### DMA传输

```python
class DMATransfer(Randomizable):
    src_addr: rand(int)(bits=32)
    dst_addr: rand(int)(bits=32)
    size: rand(int)(bits=16, min=64, max=4096)

    @constraint
    def no_overlap(self):
        return (self.src_addr + self.size <= self.dst_addr) or \
               (self.dst_addr + self.size <= self.src_addr)

    @constraint
    def alignment(self):
        return self.src_addr % 64 == 0 and self.dst_addr % 64 == 0
```

#### SPI协议

```python
class SPITransaction(Randomizable):
    cs_pin: rand(int)(bits=2, min=0, max=3)
    data_len: rand(int)(bits=4, min=1, max=8)
    clk_polarity: rand(int)(bits=1, min=0, max=1)
    clk_phase: rand(int)(bits=1, min=0, max=1)

    @constraint
    def valid_cs_pin(self):
        return self.cs_pin >= 0 and self.cs_pin <= 2
```

### 1.2 高维数学/逻辑约束

**测试文件**: `test_complex_constraints.py`

#### 6元一次方程组

```python
class LinearSystem6Vars(Randomizable):
    x1: rand(int)(bits=8, min=0, max=100)
    x2: rand(int)(bits=8, min=0, max=100)
    x3: rand(int)(bits=8, min=0, max=100)
    x4: rand(int)(bits=8, min=0, max=100)
    x5: rand(int)(bits=8, min=0, max=100)
    x6: rand(int)(bits=8, min=0, max=100)

    @constraint
    def equation1(self):
        return 2*self.x1 + 3*self.x2 - self.x3 + 4*self.x4 - 2*self.x5 + self.x6 == 50

    @constraint
    def equation2(self):
        return self.x1 - 2*self.x2 + 3*self.x3 + self.x4 - 3*self.x5 + 2*self.x6 == 30

    @constraint
    def equation3(self):
        return 3*self.x1 + self.x2 - 2*self.x3 + 5*self.x4 + self.x5 - self.x6 == 80

    @constraint
    def bounds(self):
        return (self.x1 >= 20 and self.x2 >= 10 and self.x3 <= 80)
```

#### 8变量资源分配

```python
class ResourceAllocation8Vars(Randomizable):
    r1: rand(int)(bits=7, min=0, max=100)
    r2: rand(int)(bits=7, min=0, max=100)
    r3: rand(int)(bits=7, min=0, max=100)
    r4: rand(int)(bits=7, min=0, max=100)
    r5: rand(int)(bits=7, min=0, max=100)
    r6: rand(int)(bits=7, min=0, max=100)
    r7: rand(int)(bits=7, min=0, max=100)
    r8: rand(int)(bits=7, min=0, max=100)

    @constraint
    def total_100_percent(self):
        return (self.r1 + self.r2 + self.r3 + self.r4 +
                self.r5 + self.r6 + self.r7 + self.r8) == 100

    @constraint
    def min_each_pool(self):
        return (self.r1 >= 5 and self.r2 >= 5 and self.r3 >= 5 and self.r4 >= 5 and
                self.r5 >= 5 and self.r6 >= 5 and self.r7 >= 5 and self.r8 >= 5)

    @constraint
    def no_single_dominant(self):
        return max(self.r1, self.r2, self.r3, self.r4,
                   self.r5, self.r6, self.r7, self.r8) <= 50
```

#### 10变量优先级调度

```python
class PriorityScheduling10Vars(Randomizable):
    priorities = [rand(int)(bits=4, min=1, max=10) for _ in range(10)]

    @constraint
    def unique_priorities(self):
        return len(set(self.priorities)) == 10

    @constraint
    def sum_constraint(self):
        return sum(self.priorities) == 55
```

### 1.3 摸高测试（极限压力测试）

**测试文件**: `test_complex_stress.py`

#### 渐进式摸高测试

```python
def test_gradual_stress_test():
    """逐步增加难度直到系统极限"""
    levels = [
        (StressLevel1, "15变量/10约束", 5.0),  # 期望5秒内完成
        (StressLevel2, "30变量/20约束", 15.0), # 期望15秒内完成
        (StressLevel3, "50变量/30约束", 30.0), # 期望30秒内完成
    ]

    for cls, desc, timeout in levels:
        obj = cls()
        start = time.time()
        success = obj.randomize()
        elapsed = time.time() - start

        print(f"\n{desc}:")
        print(f"  结果: {'✓ 通过' if success else '✗ 失败'}")
        print(f"  耗时: {elapsed:.3f}秒")

        if success:
            assert elapsed < timeout, f"超时: {elapsed:.3f}秒 > {timeout}秒"
        else:
            print(f"  系统极限: {desc}")
            break
```

#### 寻找系统极限

```python
def test_find_system_limit():
    """自动寻找系统的极限能力"""
    # 从小规模开始，逐步增加
    for n_vars in range(10, 100, 10):
        for n_constraints in range(5, 50, 5):
            obj = create_stress_object(n_vars, n_constraints)
            success = obj.randomize()

            if not success:
                print(f"\n系统极限发现:")
                print(f"  变量数: {n_vars}")
                print(f"  约束数: {n_constraints}")
                return

    print("\n未发现极限（测试范围已达上限）")
```

---

## 第二部分：性能测试

### 2.1 性能基准测试

**测试文件**: `test_performance_benchmarks.py`

#### 参数化性能测试

```python
@pytest.mark.parametrize("num_vars,num_constraints,expected_min_rate", [
    (5, 2, 10000),    # 小规模
    (10, 5, 5000),    # 中规模
    (15, 8, 2000),    # 大规模
    (20, 10, 1000),   # 超大规模
])
def test_randomization_speed(num_vars, num_constraints, expected_min_rate):
    """测试不同规模下的随机化速度"""
    obj = create_object_with_n_vars_and_constraints(num_vars, num_constraints)

    iterations = 1000
    rate = measure_randomization_rate(obj, iterations)

    print(f"  {num_vars}变量/{num_constraints}约束: {rate:.0f} 次/秒")
    assert rate >= expected_min_rate, f"性能不达标: {rate:.0f} < {expected_min_rate}"
```

#### 约束求解性能

```python
@pytest.mark.parametrize("complexity,iterations,expected_max_time", [
    ("simple", 1000, 0.1),      # 简单约束
    ("medium", 500, 0.2),       # 中等约束
    ("complex", 100, 0.5),      # 复杂约束
])
def test_constraint_solving_time(complexity, iterations, expected_max_time):
    """测试约束求解性能"""
    obj = create_complexity_object(complexity)

    start = time.time()
    for _ in range(iterations):
        obj.randomize()
    elapsed = time.time() - start

    avg_time = elapsed / iterations
    print(f"  {complexity}: {avg_time*1000:.3f}ms/次")
    assert elapsed <= expected_max_time, f"超时: {elapsed:.3f}秒 > {expected_max_time}秒"
```

### 2.2 性能压力测试

**测试文件**: `test_performance_stress.py`

#### 内存使用测试

```python
@pytest.mark.parametrize("num_vars,iterations,expected_max_mb", [
    (10, 100, 1),     # 10变量，1MB内
    (30, 100, 3),     # 30变量，3MB内
    (50, 100, 5),     # 50变量，5MB内
])
def test_memory_usage(num_vars, iterations, expected_max_mb):
    """测试内存占用"""
    import tracemalloc
    tracemalloc.start()

    obj = create_n_vars_object(num_vars)
    for _ in range(iterations):
        obj.randomize()

    current, peak = tracemalloc.get_traced_memory()
    peak_mb = peak / 1024 / 1024

    print(f"  {num_vars}变量: {peak_mb:.2f}MB")
    assert peak_mb < expected_max_mb, f"内存超限: {peak_mb:.2f}MB > {expected_max_mb}MB"
```

#### 长时间运行稳定性

```python
def test_long_run_stability():
    """测试长时间运行的稳定性"""
    obj = create_complex_object()

    iterations = 10000
    success_count = 0

    for i in range(iterations):
        if obj.randomize():
            success_count += 1
        else:
            print(f"  第{i+1}次随机化失败")

    success_rate = success_count / iterations
    print(f"  成功率: {success_rate*100:.2f}%")
    assert success_rate >= 0.95, f"成功率过低: {success_rate*100:.2f}%"
```

### 2.3 性能报告输出

```python
def test_generate_performance_report():
    """生成详细性能报告"""
    results = run_all_benchmarks()

    print("\n" + "="*60)
    print("性能测试报告")
    print("="*60)
    print("\n随机化速度:")
    for scale, data in results['randomization'].items():
        print(f"  {scale:15s}: {data['rate']:>6.0f} 次/秒")

    print("\n约束求解时间:")
    for complexity, data in results['solving'].items():
        print(f"  {complexity:15s}: {data['time']*1000:>6.3f} ms/次")

    print("\n内存使用:")
    for scale, data in results['memory'].items():
        print(f"  {scale:15s}: {data['mb']:>6.2f} MB")

    print("="*60)
```

### 2.4 性能回归检测

```python
def test_performance_regression(performance_baseline):
    """与基线对比，检测性能退化"""
    current_data = {
        "small_5_vars_rate": measure_rate_small(),
        "medium_15_vars_rate": measure_rate_medium(),
        "large_30_vars_rate": measure_rate_large(),
    }

    performance_baseline.check_regression(current_data, threshold=0.1)

    # 更新基线
    performance_baseline.update("small_5_vars_rate", current_data["small_5_vars_rate"])
    performance_baseline.update("medium_15_vars_rate", current_data["medium_15_vars_rate"])
    performance_baseline.update("large_30_vars_rate", current_data["large_30_vars_rate"])
```

---

## 第三部分：辅助工具模块

### 3.1 performance_utils.py

```python
"""性能测试工具函数"""

import time
import json
import os
import pytest

def measure_randomization_rate(obj, iterations=1000, warmup=100):
    """测量随机化速率"""
    # 预热
    for _ in range(warmup):
        obj.randomize()

    # 测量
    start = time.time()
    for _ in range(iterations):
        obj.randomize()
    elapsed = time.time() - start

    return iterations / elapsed

def measure_memory_usage(obj, iterations=100):
    """测量内存使用"""
    import tracemalloc
    tracemalloc.start()

    for _ in range(iterations):
        obj.randomize()

    return tracemalloc.get_traced_memory()

class PerformanceBaseline:
    """性能基线管理"""

    def __init__(self, baseline_file="baseline_data.json"):
        self.file = baseline_file
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                return json.load(f)
        return {}

    def save(self, data):
        with open(self.file, 'w') as f:
            json.dump(data, f, indent=2)

    def update(self, metric, value):
        self.data[metric] = value
        self.save(self.data)

    def check_regression(self, current_data, threshold=0.1):
        for metric, baseline_val in self.data.items():
            current_val = current_data.get(metric)
            if current_val is None:
                continue

            # 对于速率，越高越好
            # 对于时间，越低越好
            if "rate" in metric:
                ratio = current_val / baseline_val
            else:
                ratio = baseline_val / current_val

            if ratio < (1 - threshold):
                pytest.fail(
                    f"性能退化: {metric}\n"
                    f"  基线: {baseline_val:.2f}\n"
                    f"  当前: {current_val:.2f}\n"
                    f"  下降: {(1-ratio)*100:.1f}%"
                )
```

### 3.2 scenario_generators.py

```python
"""测试场景生成器"""

from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint

def create_n_vars_object(n, bits=8, min_val=0, max_val=255):
    """创建包含n个变量的Randomizable类"""
    annotations = [rand(int)(bits=bits, min=min_val, max=max_val)
                    for _ in range(n)]

    class DynamicVars(Randomizable):
        pass

    for i, ann in enumerate(annotations):
        setattr(DynamicVars, f'var{i}', ann)

    return DynamicVars

def create_object_with_constraints(num_vars, num_constraints):
    """创建指定变量和约束数量的对象"""
    # 实现细节...
    pass

def create_complexity_object(complexity):
    """根据复杂度级别创建测试对象"""
    # 实现细节...
    pass
```

### 3.3 Pytest Fixtures

```python
# conftest.py
import pytest
from .helpers.scenario_generators import create_n_vars_object

@pytest.fixture(scope="session")
def performance_baseline():
    """性能基线对象"""
    from .helpers.performance_utils import PerformanceBaseline
    return PerformanceBaseline()

@pytest.fixture
def small_object():
    """小规模测试对象（5变量）"""
    return create_n_vars_object(5)

@pytest.fixture
def medium_object():
    """中规模测试对象（15变量）"""
    return create_n_vars_object(15)

@pytest.fixture
def large_object():
    """大规模测试对象（30变量）"""
    return create_n_vars_object(30)

@pytest.fixture
def stress_object():
    """压力测试对象（50变量）"""
    return create_n_vars_object(50)
```

---

## 测试覆盖率目标

| 测试类别 | 目标测试数 | 覆盖场景 |
|---------|-----------|---------|
| 硬件协议 | 4-5个 | AXI, UART, DMA, SPI |
| 数学约束 | 4-5个 | 6元方程组, 8变量资源分配, 10变量优先级 |
| 摸高测试 | 3-4个 | 15/30/50变量极限测试 |
| 性能基准 | 8-10个 | 多规模参数化测试 |
| 性能压力 | 4-5个 | 内存、稳定性、回归检测 |
| **总计** | **25-30个** | **全面覆盖** |

---

## 实施计划

### 阶段1：基础设施（1天）
1. 创建辅助模块目录结构
2. 实现 `performance_utils.py`
3. 实现 `scenario_generators.py`
4. 设置 `conftest.py` fixtures

### 阶段2：复杂约束测试（2天）
1. 实现 `test_complex_protocols.py`
2. 实现 `test_complex_constraints.py`
3. 实现 `test_complex_stress.py`

### 阶段3：性能测试（2天）
1. 实现 `test_performance_benchmarks.py`
2. 实现 `test_performance_stress.py`
3. 集成性能报告和回归检测

### 阶段4：验证和调优（1天）
1. 运行所有测试
2. 调整性能基线值
3. 优化慢速测试
4. 编写使用文档

**总计：6天**

---

## 成功标准

1. ✅ 所有25-30个测试通过
2. ✅ 测试运行时间 < 90秒
3. ✅ 性能测试有明确的通过/失败标准
4. ✅ 支持性能回归自动检测
5. ✅ 摸高测试能找出系统极限
6. ✅ 代码覆盖率 > 90%

---

## 风险和缓解

| 风险 | 缓解措施 |
|------|---------|
| 摸高测试可能超时 | 设置合理的超时时间，使用二分查找快速定位极限 |
| 性能基线不稳定 | 使用多次运行取中位数，设置合理的容差范围 |
| CI环境性能波动 | 使用相对性能指标，而非绝对值 |
| 测试运行时间过长 | 拆分成独立文件，支持选择性运行 |

---

## 附录：性能基线参考值

基于v0.3.1 API的初步性能估计（需实际测试验证）：

| 规模 | 随机化速率 | 单次求解时间 |
|------|-----------|-------------|
| 5变量 | >10,000次/秒 | <0.1ms |
| 15变量 | >5,000次/秒 | <0.2ms |
| 30变量 | >2,000次/秒 | <0.5ms |
| 50变量 | >1,000次/秒 | <1.0ms |

**注**：基线值将在首次测试运行后自动生成并保存。

---

**文档结束**
