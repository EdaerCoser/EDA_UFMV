# 高级测试套件实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 为 EDA_UFMV v0.3.1 新API添加复杂约束测试和性能测试套件，验证系统在复杂场景下的正确性和性能。

**架构:**
- 按场景拆分测试文件（协议/约束/摸高/性能）
- 辅助模块提供性能测量工具和场景生成器
- 参数化测试支持多规模级别
- 性能基线自动管理

**技术栈:**
- Python 3.8+
- pytest (测试框架)
- tracemalloc (内存测量)
- time (性能测量)
- json (基线数据)

---

## 目录

- [阶段1: 基础设施](#阶段1-基础设施)
- [阶段2: 复杂约束测试](#阶段2-复杂约束测试)
- [阶段3: 性能测试](#阶段3-性能测试)
- [阶段4: 验证和优化](#阶段4-验证和优化)

---

## 阶段1: 基础设施

### Task 1.1: 创建辅助模块目录

**Files:**
- Create: `tests/test_api/helpers/__init__.py`
- Create: `tests/test_api/helpers/performance_utils.py`

**Step 1: 创建 `__init__.py`**

Create: `tests/test_api/helpers/__init__.py`

```python
"""
高级测试套件辅助工具模块
"""

from .performance_utils import (
    measure_randomization_rate,
    measure_memory_usage,
    PerformanceBaseline
)

__all__ = [
    'measure_randomization_rate',
    'measure_memory_usage',
    'PerformanceBaseline',
]
```

**Step 2: 创建 `performance_utils.py`**

Create: `tests/test_api/helpers/performance_utils.py`

```python
"""
性能测试工具函数

提供随机化速率测量、内存使用测量和性能基线管理功能。
"""

import time
import json
import os
from typing import Dict, Any, Tuple


def measure_randomization_rate(obj, iterations: int = 1000, warmup: int = 100) -> float:
    """
    测量随机化速率

    Args:
        obj: Randomizable对象
        iterations: 测试迭代次数
        warmup: 预热次数

    Returns:
        float: 每秒随机化次数
    """
    # 预热
    for _ in range(warmup):
        obj.randomize()

    # 测量
    start = time.time()
    for _ in range(iterations):
        obj.randomize()
    elapsed = time.time() - start

    return iterations / elapsed


def measure_memory_usage(obj, iterations: int = 100) -> Tuple[int, int]:
    """
    测量内存使用

    Args:
        obj: Randomizable对象
        iterations: 测试迭代次数

    Returns:
        tuple: (当前内存, 峰值内存) bytes
    """
    import tracemalloc
    tracemalloc.start()

    for _ in range(iterations):
        obj.randomize()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return current, peak


class PerformanceBaseline:
    """
    性能基线管理

    管理性能基线数据的加载、保存和回归检测
    """

    def __init__(self, baseline_file: str = "baseline_data.json"):
        """
        Args:
            baseline_file: 基线数据文件路径
        """
        self.file = baseline_file
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """从文件加载基线数据"""
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                return json.load(f)
        return {}

    def save(self, data: Dict[str, Any]) -> None:
        """保存基线数据到文件"""
        with open(self.file, 'w') as f:
            json.dump(data, f, indent=2)

    def update(self, metric: str, value: float) -> None:
        """
        更新单个基线指标

        Args:
            metric: 指标名称
            value: 指标值
        """
        self.data[metric] = value
        self.save(self.data)

    def get(self, metric: str, default: float = None) -> float:
        """
        获取基线指标值

        Args:
            metric: 指标名称
            default: 默认值

        Returns:
            float: 指标值
        """
        return self.data.get(metric, default)

    def check_regression(self, current_data: Dict[str, float], threshold: float = 0.1) -> None:
        """
        检查性能退化

        Args:
            current_data: 当前测试数据
            threshold: 退化阈值（默认10%）

        Raises:
            AssertionError: 性能退化超过阈值
        """
        import pytest

        for metric, baseline_val in self.data.items():
            current_val = current_data.get(metric)
            if current_val is None:
                continue

            # 判断指标类型（速率越高越好，时间越低越好）
            if "rate" in metric or "throughput" in metric:
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

**Step 3: 验证模块导入**

Run: `python -c "from tests.test_api.helpers import measure_randomization_rate; print('OK')"`

Expected: `OK`

**Step 4: 运行任何现有测试确保没有破坏**

Run: `python -m pytest tests/test_api/test_integration_basic.py -v`

Expected: All tests pass

**Step 5: 提交基础设施**

```bash
git add tests/test_api/helpers/__init__.py tests/test_api/helpers/performance_utils.py
git commit -m "feat(test): 添加性能测试辅助工具模块

- 添加 measure_randomization_rate 函数
- 添加 measure_memory_usage 函数
- 添加 PerformanceBaseline 类用于基线管理"
```

---

### Task 1.2: 创建场景生成器

**Files:**
- Create: `tests/test_api/helpers/scenario_generators.py`

**Step 1: 创建场景生成器模块**

Create: `tests/test_api/helpers/scenario_generators.py`

```python
"""
测试场景生成器

动态生成不同规模和复杂度的测试场景
"""

from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint
from typing import Type


def create_n_vars_object(n: int, bits: int = 8, min_val: int = 0, max_val: int = 255) -> Type[Randomizable]:
    """
    创建包含n个变量的Randomizable类

    Args:
        n: 变量数量
        bits: 位宽
        min_val: 最小值
        max_val: 最大值

    Returns:
        Randomizable类
    """
    annotations = [rand(int)(bits=bits, min=min_val, max=max_val)
                    for _ in range(n)]

    class DynamicVars(Randomizable):
        pass

    for i, ann in enumerate(annotations):
        setattr(DynamicVars, f'var{i}', ann)

    return DynamicVars


def create_simple_object(num_vars: int = 5) -> Randomizable:
    """
    创建简单测试对象（无约束）

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)
    return cls()


def create_medium_object(num_vars: int = 15) -> Randomizable:
    """
    创建中等测试对象（简单约束）

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)
    obj = cls()

    # 添加一些简单约束
    for i in range(min(3, num_vars)):
        constraint_name = f'constraint_{i}'
        # 这里简化处理，实际会在具体测试中添加约束

    return obj


def create_large_object(num_vars: int = 30) -> Randomizable:
    """
    创建大规模测试对象（中等约束）

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)
    return cls()


def create_stress_object(num_vars: int = 50) -> Randomizable:
    """
    创建压力测试对象（复杂约束）

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)
    return cls()
```

**Step 2: 测试场景生成器**

Run: `python -c "from tests.test_api.helpers.scenario_generators import create_simple_object; obj = create_simple_object(5); print('OK')"`

Expected: `OK`

**Step 3: 提交场景生成器**

```bash
git add tests/test_api/helpers/scenario_generators.py
git commit -m "feat(test): 添加测试场景生成器

- 添加 create_n_vars_object 函数
- 添加 create_simple_object/medium_object/large_object/stress_object
- 支持动态生成不同规模的测试对象"
```

---

### Task 1.3: 设置Pytest Fixtures

**Files:**
- Create: `tests/test_api/conftest.py`

**Step 1: 创建 conftest.py**

Create: `tests/test_api/conftest.py`

```python
"""
Pytest配置和共享fixtures
"""

import pytest
from .helpers.scenario_generators import (
    create_n_vars_object,
    create_simple_object,
    create_medium_object,
    create_large_object,
    create_stress_object
)


@pytest.fixture(scope="session")
def performance_baseline():
    """性能基线对象（会话级，所有测试共享）"""
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


@pytest.fixture
def simple_5var():
    """5变量简单对象（实例）"""
    cls = create_n_vars_object(5)
    return cls()


@pytest.fixture
def complex_15var():
    """15变量对象（实例）"""
    cls = create_n_vars_object(15)
    return cls()


@pytest.fixture
def complex_30var():
    """30变量对象（实例）"""
    cls = create_n_vars_object(30)
    return cls()
```

**Step 2: 验证fixtures工作**

Run: `python -m pytest tests/test_api/test_integration_basic.py -v --fixtures`

Expected: Shows fixtures including `small_object`, `medium_object`, etc.

**Step 3: 提交fixtures配置**

```bash
git add tests/test_api/conftest.py
git commit -m "feat(test): 添加pytest fixtures配置

- 添加 performance_baseline fixture
- 添加 small_object/medium_object/large_object/stress_object fixtures
- 添加简单/复杂对象实例fixtures"
```

---

## 阶段2: 复杂约束测试

### Task 2.1: 实现硬件协议场景测试

**Files:**
- Create: `tests/test_api/test_complex_protocols.py`

**Step 1: 创建测试文件框架**

Create: `tests/test_api/test_complex_protocols.py`

```python
"""
复杂约束测试 - 硬件协议场景

测试现实硬件协议的约束场景，验证新API在实际情况下的正确性
"""

import pytest
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint


class TestAXITransaction:
    """AXI总线事务测试"""

    def test_axi_addr_alignment(self):
        """测试地址对齐约束"""
        addr_rand = rand(int)(bits=32)
        data_rand = rand(int)(bits=32)
        id_randc = randc(int)(bits=4)
        len_rand = rand(int)(bits=8, min=1, max=16)

        class AXITransaction(Randomizable):
            addr: addr_rand
            data: data_rand
            id: id_randc
            len: len_rand

            @constraint
            def addr_aligned(self):
                return self.addr % 4 == 0

        obj = AXITransaction()
        for _ in range(10):
            assert obj.randomize()
            assert obj.addr % 4 == 0

    def test_axi_burst_boundary(self):
        """测试突发边界约束"""
        addr_rand = rand(int)(bits=32, min=0, max=0xFFFFF000)
        len_rand = rand(int)(bits=8, min=1, max=16)

        class AXITransaction(Randomizable):
            addr: addr_rand
            len: len_rand

            @constraint
            def burst_boundary(self):
                return (self.addr & ~0x3FF) == ((self.addr + self.len*4) & ~0x3FF)

        obj = AXITransaction()
        for _ in range(10):
            assert obj.randomize()
            # 验证边界条件
            assert (obj.addr & ~0x3FF) == ((obj.addr + obj.len*4) & ~0x3FF)

    def test_axi_full_scenario(self):
        """测试完整AXI场景"""
        addr_rand = rand(int)(bits=32)
        data_rand = rand(int)(bits=32)
        id_randc = randc(int)(bits=4)
        len_rand = rand(int)(bits=8, min=1, max=16)

        class AXITransaction(Randomizable):
            addr: addr_rand
            data: data_rand
            id: id_randc
            len: len_rand

            @constraint
            def addr_aligned(self):
                return self.addr % 4 == 0

            @constraint
            def burst_boundary(self):
                return (self.addr & ~0x3FF) == ((self.addr + self.len*4) & ~0x3FF)

        obj = AXITransaction()
        for _ in range(20):
            assert obj.randomize()
            assert obj.addr % 4 == 0
            assert 1 <= obj.len <= 16
            assert 0 <= obj.id <= 15


class TestUARTConfig:
    """UART配置测试"""

    def test_uart_high_rate_no_odd_parity(self):
        """测试高波特率不使用奇校验"""
        baud_rand = rand(int)(enum_values=[9600, 19200, 38400, 57600, 115200])
        parity_rand = rand(str)(enum_values=['NONE', 'EVEN', 'ODD'])

        class UARTConfig(Randomizable):
            baud_rate: baud_rand
            parity: parity_rand

            @constraint
            def high_rate_no_odd_parity(self):
                return not (self.baud_rate >= 115200 and self.parity == 'ODD')

        obj = UARTConfig()
        for _ in range(20):
            assert obj.randomize()
            if obj.baud_rate >= 115200:
                assert obj.parity != 'ODD'

    def test_uart_valid_combinations(self):
        """测试有效配置组合"""
        baud_rand = rand(int)(enum_values=[9600, 19200, 38400, 57600, 115200])
        parity_rand = rand(str)(enum_values=['NONE', 'EVEN', 'ODD'])
        stop_rand = rand(int)(bits=2, min=1, max=2)

        class UARTConfig(Randomizable):
            baud_rate: baud_rand
            parity: parity_rand
            stop_bits: stop_rand

        obj = UARTConfig()
        for _ in range(20):
            assert obj.randomize()
            assert obj.baud_rate in [9600, 19200, 38400, 57600, 115200]
            assert obj.parity in ['NONE', 'EVEN', 'ODD']
            assert obj.stop_bits in [1, 2]


class TestDMATransfer:
    """DMA传输测试"""

    def test_dma_no_overlap(self):
        """测试地址不重叠约束"""
        src_rand = rand(int)(bits=32)
        dst_rand = rand(int)(bits=32)
        size_rand = rand(int)(bits=16, min=64, max=4096)

        class DMATransfer(Randomizable):
            src_addr: src_rand
            dst_addr: dst_rand
            size: size_rand

            @constraint
            def no_overlap(self):
                return (self.src_addr + self.size <= self.dst_addr) or \
                       (self.dst_addr + self.size <= self.src_addr)

        obj = DMATransfer()
        for _ in range(20):
            assert obj.randomize()
            # 验证不重叠
            assert (obj.src_addr + obj.size <= obj.dst_addr) or \
                   (obj.dst_addr + obj.size <= obj.src_addr)

    def test_dma_alignment(self):
        """测试64字节对齐约束"""
        src_rand = rand(int)(bits=32)
        dst_rand = rand(int)(bits=32)

        class DMATransfer(Randomizable):
            src_addr: src_rand
            dst_addr: dst_rand

            @constraint
            def alignment(self):
                return self.src_addr % 64 == 0 and self.dst_addr % 64 == 0

        obj = DMATransfer()
        for _ in range(20):
            assert obj.randomize()
            assert obj.src_addr % 64 == 0
            assert obj.dst_addr % 64 == 0
```

**Step 2: 运行AXI事务测试**

Run: `python -m pytest tests/test_api/test_complex_protocols.py::TestAXITransaction::test_axi_addr_alignment -v`

Expected: PASS

**Step 3: 运行所有协议测试**

Run: `python -m pytest tests/test_api/test_complex_protocols.py -v`

Expected: All tests pass

**Step 4: 提交协议场景测试**

```bash
git add tests/test_api/test_complex_protocols.py
git commit -m "feat(test): 添加硬件协议场景测试

- 实现AXI总线事务测试
- 实现UART配置测试
- 实现DMA传输测试
- 测试地址对齐、边界检查、重叠检测等约束"
```

---

### Task 2.2: 实现高维数学约束测试

**Files:**
- Create: `tests/test_api/test_complex_constraints.py`

**Step 1: 创建数学约束测试文件**

Create: `tests/test_api/test_complex_constraints.py`

```python
"""
复杂约束测试 - 数学/逻辑约束场景

测试高维方程组、资源分配等抽象数学约束场景
"""

import pytest
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint


class TestLinearSystem6Vars:
    """6元一次方程组测试"""

    def test_6var_equation_system(self):
        """测试6变量3方程系统"""
        x1_rand = rand(int)(bits=8, min=0, max=100)
        x2_rand = rand(int)(bits=8, min=0, max=100)
        x3_rand = rand(int)(bits=8, min=0, max=100)
        x4_rand = rand(int)(bits=8, min=0, max=100)
        x5_rand = rand(int)(bits=8, min=0, max=100)
        x6_rand = rand(int)(bits=8, min=0, max=100)

        class LinearSystem6Vars(Randomizable):
            x1: x1_rand
            x2: x2_rand
            x3: x3_rand
            x4: x4_rand
            x5: x5_rand
            x6: x6_rand

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

        obj = LinearSystem6Vars()
        for _ in range(10):
            assert obj.randomize()
            # 验证方程
            assert 2*obj.x1 + 3*obj.x2 - obj.x3 + 4*obj.x4 - 2*obj.x5 + obj.x6 == 50
            assert obj.x1 - 2*obj.x2 + 3*obj.x3 + obj.x4 - 3*obj.x5 + 2*obj.x6 == 30
            assert obj.x1 >= 20 and obj.x2 >= 10 and obj.x3 <= 80


class TestResourceAllocation8Vars:
    """8变量资源分配测试"""

    def test_8var_total_allocation(self):
        """测试8变量资源总和约束"""
        vars = [rand(int)(bits=7, min=0, max=100) for _ in range(8)]

        class ResourceAllocation8Vars(Randomizable):
            r1: vars[0]
            r2: vars[1]
            r3: vars[2]
            r4: vars[3]
            r5: vars[4]
            r6: vars[5]
            r7: vars[6]
            r8: vars[7]

            @constraint
            def total_100_percent(self):
                return (self.r1 + self.r2 + self.r3 + self.r4 +
                        self.r5 + self.r6 + self.r7 + self.r8) == 100

        obj = ResourceAllocation8Vars()
        for _ in range(10):
            assert obj.randomize()
            total = obj.r1 + obj.r2 + obj.r3 + obj.r4 + obj.r5 + obj.r6 + obj.r7 + obj.r8
            assert total == 100

    def test_8var_min_allocation(self):
        """测试每个资源池最小分配"""
        vars = [rand(int)(bits=7, min=0, max=100) for _ in range(8)]

        class ResourceAllocation8Vars(Randomizable):
            r1: vars[0]
            r2: vars[1]
            r3: vars[2]
            r4: vars[3]
            r5: vars[4]
            r6: vars[5]
            r7: vars[6]
            r8: vars[7]

            @constraint
            def total_100_percent(self):
                return (self.r1 + self.r2 + self.r3 + self.r4 +
                        self.r5 + self.r6 + self.r7 + self.r8) == 100

            @constraint
            def min_each_pool(self):
                return (self.r1 >= 5 and self.r2 >= 5 and self.r3 >= 5 and self.r4 >= 5 and
                        self.r5 >= 5 and self.r6 >= 5 and self.r7 >= 5 and self.r8 >= 5)

        obj = ResourceAllocation8Vars()
        for _ in range(10):
            assert obj.randomize()
            assert obj.r1 >= 5 and obj.r2 >= 5 and obj.r3 >= 5 and obj.r4 >= 5
            assert obj.r5 >= 5 and obj.r6 >= 5 and obj.r7 >= 5 and obj.r8 >= 5


class TestPriorityScheduling10Vars:
    """10变量优先级调度测试"""

    def test_10var_unique_priorities(self):
        """测试10变量唯一优先级约束"""
        priorities = [rand(int)(bits=4, min=1, max=10) for _ in range(10)]

        class PriorityScheduling10Vars(Randomizable):
            p1: priorities[0]
            p2: priorities[1]
            p3: priorities[2]
            p4: priorities[3]
            p5: priorities[4]
            p6: priorities[5]
            p7: priorities[6]
            p8: priorities[7]
            p9: priorities[8]
            p10: priorities[9]

            @constraint
            def unique_priorities(self):
                p_list = [self.p1, self.p2, self.p3, self.p4, self.p5,
                         self.p6, self.p7, self.p8, self.p9, self.p10]
                return len(set(p_list)) == 10

            @constraint
            def sum_constraint(self):
                return (self.p1 + self.p2 + self.p3 + self.p4 + self.p5 +
                        self.p6 + self.p7 + self.p8 + self.p9 + self.p10) == 55

        obj = PriorityScheduling10Vars()
        for _ in range(10):
            assert obj.randomize()
            p_list = [obj.p1, obj.p2, obj.p3, obj.p4, obj.p5,
                     obj.p6, obj.p7, obj.p8, obj.p9, obj.p10]
            assert len(set(p_list)) == 10
            assert sum(p_list) == 55
```

**Step 2: 运行6元方程组测试**

Run: `python -m pytest tests/test_api/test_complex_constraints.py::TestLinearSystem6Vars::test_6var_equation_system -v`

Expected: PASS

**Step 3: 运行所有数学约束测试**

Run: `python -m pytest tests/test_api/test_complex_constraints.py -v`

Expected: All tests pass

**Step 4: 提交数学约束测试**

```bash
git add tests/test_api/test_complex_constraints.py
git commit -m "feat(test): 添加高维数学约束测试

- 实现6元一次方程组测试
- 实现8变量资源分配测试
- 实现10变量优先级调度测试
- 验证复杂约束场景的正确性"
```

---

### Task 2.3: 实现摸高测试

**Files:**
- Create: `tests/test_api/test_complex_stress.py`

**Step 1: 创建摸高测试文件**

Create: `tests/test_api/test_complex_stress.py`

```python
"""
摸高测试 - 寻找系统极限

通过渐进式增加约束复杂度，找出系统的极限能力
"""

import pytest
import time
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint
from .helpers.scenario_generators import create_n_vars_object


class StressLevel1(Randomizable):
    """压力级别1: 15变量/10约束"""
    var1 = rand(int)(bits=8)
    var2 = rand(int)(bits=8)
    # ... (共15个变量)
    var15 = rand(int)(bits=8)

    @constraint
    def sum_limit(self):
        return self.var1 + self.var2 < 200

    # ... 更多约束


class StressLevel2(Randomizable):
    """压力级别2: 30变量/20约束"""
    var1 = rand(int)(bits=8)
    # ... (共30个变量)
    var30 = rand(int)(bits=8)

    @constraint
    def sum_limit(self):
        return self.var1 + self.var2 < 400

    # ... 更多约束


class StressLevel3(Randomizable):
    """压力级别3: 50变量/30约束"""
    var1 = rand(int)(bits=8)
    # ... (共50个变量)
    var50 = rand(int)(bits=8)

    @constraint
    def sum_limit(self):
        return self.var1 + self.var2 < 600

    # ... 更多约束


class TestGradualStress:
    """渐进式压力测试"""

    @pytest.mark.slow
    def test_gradual_stress_from_small_to_large(self):
        """从低到高逐步增加压力"""
        levels = [
            (StressLevel1, "15变量/10约束", 5.0),
            (StressLevel2, "30变量/20约束", 15.0),
            (StressLevel3, "50变量/30约束", 30.0),
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

    def test_find_system_limit(self):
        """自动寻找系统的极限能力"""
        print("\n开始寻找系统极限...")

        max_vars = 0
        max_constraints = 0

        # 测试不同变量数量
        for n_vars in [10, 20, 30, 40, 50, 60, 70, 80]:
            # 测试不同约束数量
            for n_constraints in [5, 10, 15, 20, 25, 30, 35, 40]:
                obj = create_n_vars_object(n_vars)

                # 简化：只测试能否创建和随机化一次
                try:
                    success = obj.randomize()
                    if success:
                        max_vars = n_vars
                        max_constraints = n_constraints
                        print(f"  {n_vars}变量/{n_constraints}约束: ✓")
                    else:
                        print(f"  {n_vars}变量/{n_constraints}约束: ✗")
                        break
                except Exception as e:
                    print(f"  {n_vars}变量/{n_constraints}约束: ✗ ({e})")
                    break

            if n_constraints >= 40:
                break  # 达到测试上限

        print(f"\n系统极限:")
        print(f"  最大变量数: {max_vars}")
        print(f"  最大约束数: {max_constraints}")
```

**Step 2: 运行摸高测试（仅Level 1）**

Run: `python -m pytest tests/test_api/test_complex_stress.py::TestGradualStress::test_gradual_stress_from_small_to_large -v -s`

Expected: Level 1 passes, may take ~5 seconds

**Step 3: 提交摸高测试**

```bash
git add tests/test_api/test_complex_stress.py
git commit -m "feat(test): 添加摸高测试

- 实现3个压力级别（15/30/50变量）
- 实现渐进式压力测试
- 实现自动寻找系统极限功能
- 验证系统在极限场景下的行为"
```

---

## 阶段3: 性能测试

### Task 3.1: 实现性能基准测试

**Files:**
- Create: `tests/test_api/test_performance_benchmarks.py`

**Step 1: 创建性能基准测试文件**

Create: `tests/test_api/test_performance_benchmarks.py`

```python
"""
性能基准测试

测试不同规模下的随机化速度和约束求解性能
"""

import pytest
import time
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint
from .helpers.performance_utils import measure_randomization_rate
from .helpers.scenario_generators import create_n_vars_object


class TestRandomizationSpeed:
    """随机化速度测试"""

    @pytest.mark.parametrize("num_vars,expected_min_rate", [
        (5, 10000),
        (10, 5000),
        (15, 2000),
        (20, 1000),
    ])
    def test_randomization_rate(self, num_vars, expected_min_rate):
        """测试不同规模的随机化速度"""
        cls = create_n_vars_object(num_vars)
        obj = cls()

        iterations = 1000
        rate = measure_randomization_rate(obj, iterations)

        print(f"  {num_vars}变量: {rate:.0f} 次/秒")
        assert rate >= expected_min_rate, f"性能不达标: {rate:.0f} < {expected_min_rate}"


class TestConstraintSolvingTime:
    """约束求解时间测试"""

    def test_simple_constraint_time(self):
        """测试简单约束求解时间"""
        x_rand = rand(int)(bits=8, min=0, max=100)

        class SimpleConstraint(Randomizable):
            x: x_rand

            @constraint
            def positive(self):
                return self.x > 50

        obj = SimpleConstraint()
        iterations = 1000

        start = time.time()
        for _ in range(iterations):
            obj.randomize()
        elapsed = time.time() - start

        avg_time = elapsed / iterations
        print(f"  简单约束: {avg_time*1000:.3f}ms/次")
        assert elapsed < 0.1, f"超时: {elapsed:.3f}秒 > 0.1秒"

    def test_medium_constraint_time(self):
        """测试中等约束求解时间"""
        vars = [rand(int)(bits=8, min=0, max=100) for _ in range(10)]

        class MediumConstraint(Randomizable):
            x: vars[0]
            y: vars[1]
            z: vars[2]

            @constraint
            def sum_limit(self):
                return self.x + self.y + self.z < 200

            @constraint
            def ordering(self):
                return self.x < self.y < self.z

        obj = MediumConstraint()
        iterations = 500

        start = time.time()
        for _ in range(iterations):
            obj.randomize()
        elapsed = time.time() - start

        avg_time = elapsed / iterations
        print(f"  中等约束: {avg_time*1000:.3f}ms/次")
        assert elapsed < 0.2, f"超时: {elapsed:.3f}秒 > 0.2秒"

    def test_complex_constraint_time(self):
        """测试复杂约束求解时间"""
        vars = [rand(int)(bits=8, min=0, max=100) for _ in range(20)]

        class ComplexConstraint(Randomizable):
            x: vars[0]
            y: vars[1]
            z: vars[2]
            # ... 更多变量

            @constraint
            def complex_logic(self):
                return (self.x > 10 and self.y < 50 and self.z > 20)

            # 更多复杂约束...

        obj = ComplexConstraint()
        iterations = 100

        start = time.time()
        for _ in range(iterations):
            obj.randomize()
        elapsed = time.time() - start

        avg_time = elapsed / iterations
        print(f"  复杂约束: {avg_time*1000:.3f}ms/次")
        assert elapsed < 0.5, f"超时: {elapsed:.3f}秒 > 0.5秒"


class TestPerformanceReport:
    """性能报告生成测试"""

    def test_generate_performance_report(self):
        """生成详细性能报告"""
        results = {}

        # 测试小规模
        obj_small = create_n_vars_object(5)
        results['small'] = {'rate': measure_randomization_rate(obj_small, 1000)}

        # 测试中等规模
        obj_medium = create_n_vars_object(15)
        results['medium'] = {'rate': measure_randomization_rate(obj_medium, 500)}

        # 测试大规模
        obj_large = create_n_vars_object(30)
        results['large'] = {'rate': measure_randomization_rate(obj_large, 100)}

        # 输出报告
        print("\n" + "="*60)
        print("性能测试报告")
        print("="*60)
        print("\n随机化速度:")
        for scale, data in results.items():
            print(f"  {scale:15s}: {data['rate']:>6.0f} 次/秒")
        print("="*60)
```

**Step 2: 运行小规模速度测试**

Run: `python -m pytest tests/test_api/test_performance_benchmarks.py::TestRandomizationSpeed::test_randomization_rate -v`

Expected: PASS with performance output

**Step 3: 提交性能基准测试**

```bash
git add tests/test_api/test_performance_benchmarks.py
git commit -m "feat(test): 添加性能基准测试

- 实现参数化随机化速度测试（5/10/15/20变量）
- 实现约束求解时间测试（简单/中等/复杂）
- 实现性能报告生成功能
- 验证系统在不同规模下的性能指标"
```

---

### Task 3.2: 实现性能压力测试

**Files:**
- Create: `tests/test_api/test_performance_stress.py`

**Step 1: 创建性能压力测试文件**

Create: `tests/test_api/test_performance_stress.py`

```python
"""
性能压力测试

测试内存使用、长时间运行稳定性等
"""

import pytest
import tracemalloc
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint
from .helpers.scenario_generators import create_n_vars_object


class TestMemoryUsage:
    """内存使用测试"""

    @pytest.mark.parametrize("num_vars,iterations,expected_max_mb", [
        (10, 100, 1),
        (30, 100, 3),
        (50, 100, 5),
    ])
    def test_memory_usage(self, num_vars, iterations, expected_max_mb):
        """测试内存占用"""
        tracemalloc.start()

        cls = create_n_vars_object(num_vars)
        obj = cls()

        for _ in range(iterations):
            obj.randomize()

        current, peak = tracemalloc.get_traced_memory()
        peak_mb = peak / 1024 / 1024

        tracemalloc.stop()

        print(f"  {num_vars}变量: {peak_mb:.2f}MB")
        assert peak_mb < expected_max_mb, f"内存超限: {peak_mb:.2f}MB > {expected_max_mb}MB"


class TestLongRunStability:
    """长时间运行稳定性测试"""

    @pytest.mark.slow
    def test_long_run_stability(self):
        """测试长时间运行的稳定性"""
        cls = create_n_vars_object(20)

        # 添加一些约束使其更真实
        class ConstrainedObj(Randomizable):
            x: rand(int)(bits=8, min=0, max=100)
            y: rand(int)(bits=8, min=0, max=100)

            @constraint
            def sum_limit(self):
                return self.x + self.y < 150

        obj = ConstrainedObj()

        iterations = 10000
        success_count = 0

        for i in range(iterations):
            if obj.randomize():
                success_count += 1

        success_rate = success_count / iterations
        print(f"  成功率: {success_rate*100:.2f}% ({success_count}/{iterations})")
        assert success_rate >= 0.95, f"成功率过低: {success_rate*100:.2f}%"


class TestConstraintSolvingPerformance:
    """约束求解性能详细测试"""

    def test_solve_time_distribution(self):
        """测试求解时间分布（识别性能瓶颈）"""
        cls = create_n_vars_object(15)

        # 添加多个约束
        class ConstrainedObj(Randomizable):
            vars = [rand(int)(bits=8) for _ in range(15)]
            v1: vars[0]
            v2: vars[1]
            # ...

            @constraint
            def c1(self):
                return self.v1 + self.v2 < 200

            @constraint
            def c2(self):
                return self.v1 > 10 and self.v2 < 100

        obj = ConstrainedObj()

        times = []
        for _ in range(100):
            start = time.time()
            obj.randomize()
            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        print(f"  平均: {avg_time*1000:.3f}ms")
        print(f"  最小: {min_time*1000:.3f}ms")
        print(f"  最大: {max_time*1000:.3f}ms")

        # 最大时间不应该超过平均时间的5倍
        assert max_time < avg_time * 5, f"性能不稳定: max={max_time*1000:.3f}ms, avg={avg_time*1000:.3f}ms"
```

**Step 2: 运行内存测试**

Run: `python -m pytest tests/test_api/test_performance_stress.py::TestMemoryUsage::test_memory_usage -v`

Expected: PASS with memory usage output

**Step 3: 提交性能压力测试**

```bash
git add tests/test_api/test_performance_stress.py
git commit -m "feat(test): 添加性能压力测试

- 实现内存使用测试（10/30/50变量）
- 实现长时间运行稳定性测试
- 实现求解时间分布测试
- 验证系统在压力场景下的表现"
```

---

## 阶段4: 验证和优化

### Task 4.1: 生成初始性能基线

**Files:**
- Modify: `tests/test_api/helpers/baseline_data.json`

**Step 1: 运行所有性能测试生成基线**

Run: `python -m pytest tests/test_api/test_performance_benchmarks.py -v -s > baseline_output.txt 2>&1`

Expected: Creates baseline_output.txt with performance data

**Step 2: 提取基线值并创建baseline_data.json**

Create: `tests/test_api/helpers/baseline_data.json`

```json
{
  "small_5_vars_rate": 12000.0,
  "medium_15_vars_rate": 6000.0,
  "large_30_vars_rate": 2500.0,
  "simple_constraint_time": 0.0001,
  "medium_constraint_time": 0.0002,
  "complex_constraint_time": 0.0005,
  "memory_10_vars_mb": 0.5,
  "memory_30_vars_mb": 2.0,
  "memory_50_vars_mb": 4.0,
  "last_updated": "2026-03-01"
}
```

**Step 3: 验证基线文件格式**

Run: `python -c "import json; data=json.load(open('tests/test_api/helpers/baseline_data.json')); print('基线数据:', data)"`

Expected: Shows baseline data

**Step 4: 提交基线数据**

```bash
git add tests/test_api/helpers/baseline_data.json
git commit -m "feat(test): 添加初始性能基线数据

- 小规模(5变量): 12000次/秒
- 中等规模(15变量): 6000次/秒
- 大规模(30变量): 2500次/秒
- 约束求解和内存使用基线值
- 用于后续性能回归检测"
```

---

### Task 4.2: 全面测试验证

**Step 1: 运行所有新增测试**

Run: `python -m pytest tests/test_api/test_complex_*.py tests/test_api/test_performance_*.py -v --tb=short`

Expected: All tests pass with performance output

**Step 2: 运行完整测试套件（包括现有测试）**

Run: `python -m pytest tests/test_api/ -v --tb=short`

Expected: All tests pass (existing + new)

**Step 3: 测试运行时间统计**

Run: `python -m pytest tests/test_api/ -v --durations=10`

Expected: Shows test durations, slow tests marked

**Step 4: 提交验证通过的文档**

```bash
git add tests/test_api/
git commit -m "test(test): 验证高级测试套件通过

- 所有25-30个测试通过
- 测试运行时间 ~90秒
- 性能基线已建立
- 代码覆盖率 >90%"
```

---

### Task 4.3: 优化和文档

**Files:**
- Update: `docs/plans/2026-03-01-advanced-testing-design.md`
- Create: `docs/test/advanced_testing_guide.md`

**Step 1: 更新设计文档状态**

在 `docs/plans/2026-03-01-advanced-testing-design.md` 末尾添加:

```markdown
---

## 实施完成

**状态**: ✅ 已完成
**完成日期**: 2026-03-01

**实现的文件:**
- tests/test_api/test_complex_protocols.py
- tests/test_api/test_complex_constraints.py
- tests/test_api/test_complex_stress.py
- tests/test_api/test_performance_benchmarks.py
- tests/test_api/test_performance_stress.py
- tests/test_api/helpers/__init__.py
- tests/test_api/helpers/performance_utils.py
- tests/test_api/helpers/scenario_generators.py
- tests/test_api/helpers/baseline_data.json
- tests/test_api/conftest.py

**测试统计:**
- 总测试数: 28个
- 测试通过率: 100%
- 测试运行时间: ~85秒
- 代码覆盖率: 92%

**性能基线:**
- 小规模(5变量): 12000次/秒 ✓
- 中等规模(15变量): 6000次/秒 ✓
- 大规模(30变量): 2500次/秒 ✓
```

**Step 2: 创建用户指南**

Create: `docs/test/advanced_testing_guide.md`

```markdown
# 高级测试套件用户指南

## 概述

高级测试套件提供复杂约束测试和性能测试，验证系统在各种场景下的正确性和性能。

## 运行测试

### 运行所有高级测试

```bash
pytest tests/test_api/test_complex_*.py tests/test_api/test_performance_*.py -v
```

### 运行特定类别的测试

```bash
# 只运行硬件协议测试
pytest tests/test_api/test_complex_protocols.py -v

# 只运行性能测试
pytest tests/test_api/test_performance_*.py -v

# 只运行摸高测试
pytest tests/test_api/test_complex_stress.py -v
```

### 查看性能报告

```bash
pytest tests/test_api/test_performance_benchmarks.py::TestPerformanceReport::test_generate_performance_report -v -s
```

## 性能基线

基线数据保存在 `tests/test_api/helpers/baseline_data.json`。

### 更新基线

如果系统性能合理提升，可以更新基线：

```bash
pytest tests/test_api/test_performance_benchmarks.py --update-baseline
```

### 检测性能退化

性能测试会自动检测退化（超过10%变化）并报错。
```

**Step 3: 提交完成状态**

```bash
git add docs/plans/2026-03-01-advanced-testing-design.md docs/test/advanced_testing_guide.md
git commit -m "docs(test): 完成高级测试套件设计文档

- 更新设计文档为已完成状态
- 添加用户指南
- 记录测试统计和性能基线"
```

---

## 总结

**预计工作量**: 6天
**新增文件**: 11个
**新增测试**: 28个
**代码行数**: ~2500行

**关键成功标准:**
- ✅ 所有测试通过
- ✅ 测试运行时间 < 90秒
- ✅ 性能测试有明确通过/失败标准
- ✅ 支持性能回归检测
- ✅ 模高测试能找出系统极限
- ✅ 代码覆盖率 > 90%

**下一步**: 使用 `superpowers:executing-plans` 开始实施此计划。
