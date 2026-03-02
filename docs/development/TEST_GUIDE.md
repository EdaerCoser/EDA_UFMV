# EDA_UFVM 测试指南

**版本**: v1.0
**日期**: 2026-03-01
**目标**: 提供完整的测试体系概览和使用指南

---

## 目录

- [测试概览](#测试概览)
- [测试目录结构](#测试目录结构)
- [测试分类](#测试分类)
- [运行测试](#运行测试)
- [测试标记](#测试标记)
- [覆盖率目标](#覆盖率目标)
- [CI/CD集成](#cicd集成)
- [编写新测试](#编写新测试)
- [性能基准](#性能基准)
- [故障排除](#故障排除)

---

## 测试概览

EDA_UFVM采用分层测试策略，确保代码质量和系统可靠性：

| 测试类型 | 数量 | 目的 | 运行频率 |
|:---|:---|:---|:---|
| **单元测试** | ~250 | 验证单个组件功能 | 每次提交 |
| **集成测试** | ~80 | 验证跨模块协作 | 每次提交 |
| **异常处理测试** | ~200 | 验证错误分支 | 每次提交 |
| **边界情况测试** | ~150 | 验证极值和边界 | 每次提交 |
| **性能测试** | ~25 | 建立性能基线 | 每日/每周 |
| **端到端测试** | ~30 | 验证完整工作流 | 每次发布 |

**总计**: ~735个测试用例

### 测试覆盖率目标

- **代码覆盖率**: ≥85% (目标90%)
- **异常分支覆盖率**: ≥90%
- **边界条件覆盖率**: ≥85%
- **集成测试覆盖**: ≥80%

---

## 测试目录结构

```
tests/
├── conftest.py                          # 全局pytest配置和共享fixtures
├── fixtures/                            # 共享测试数据
│   └── __init__.py
├── utils/                               # 测试工具函数
│   └── __init__.py
│
├── unit/                                # 单元测试
│   ├── test_error_handling/             # 异常处理测试
│   │   ├── __init__.py
│   │   ├── test_coverage_errors.py      # Coverage模块19个异常类
│   │   ├── test_rgm_errors.py           # RGM模块6个异常类
│   │   └── test_randomizer_errors.py    # Randomizer模块6个异常类
│   │
│   └── test_boundary_cases/             # 边界情况测试
│       ├── __init__.py
│       ├── test_limit_values.py         # 极值测试 (MAX, MIN, 溢出)
│       ├── test_collections.py          # 集合边界 (空, 大, 嵌套)
│       └── test_string_types.py         # 字符串边界 (空, 长, Unicode)
│
├── integration/                         # 集成测试
│   ├── test_cross_module/               # 跨模块集成测试
│   │   ├── __init__.py
│   │   ├── test_rgm_coverage_integration.py      # RGM + Coverage
│   │   └── test_randomizer_coverage_integration.py # Randomizer + Coverage
│   │
│   └── test_end_to_end/                 # 端到端工作流测试
│       ├── __init__.py
│       └── test_verification_flow.py    # 完整验证流程
│
├── performance/                         # 性能测试
│   ├── benchmarks/                      # 性能基线数据
│   └── test_benchmarks.py               # 性能基准测试
│
├── test_coverage/                       # Coverage系统测试 (141个)
├── test_rgm/                            # RGM系统测试 (186个)
├── test_parser/                         # 解析器测试 (57个)
├── legacy/                              # 旧版随机化测试 (42个)
│
├── run_all_tests.py                     # 综合测试运行器
└── run_rgm_tests.py                     # RGM测试运行器
```

---

## 测试分类

### 1. 异常处理测试 (Exception Handling Tests)

**目的**: 验证所有异常类在适当条件下被正确抛出

**覆盖的异常类**:

#### Coverage模块 (19个)
```
CoverageError (基类)
├── CoverGroupError
│   ├── InvalidCoverPointError
│   ├── SamplingError
│   └── CoverageMergeError
├── CoverPointError
│   ├── BinDefinitionError
│   ├── BinOverlapError
│   └── InvalidSampleError
├── CrossError
│   ├── InvalidCrossError
│   └── CrossBinOverflowError
├── DatabaseError
│   ├── DatabaseConnectionError
│   ├── DatabaseWriteError
│   └── DatabaseReadError
└── ReportError
    ├── ReportGenerationError
    └── InvalidReportFormatError
```

#### RGM模块 (6个)
- `RGMError` - 基类
- `FieldOverlapError` - 字段重叠
- `AddressConflictError` - 地址冲突
- `InvalidAccessError` - 无效访问
- `RegisterNotFoundError` - 寄存器未找到
- `FieldNotFoundError` - 字段未找到

#### Randomizer模块 (6个)
- `RandomizerError` - 基类
- `ConstraintConflictError` - 约束冲突
- `UnsatisfiableError` - 约束不可满足
- `VariableNotFoundError` - 变量未找到
- `SolverBackendError` - 求解器错误
- `InvalidConstraintError` - 无效约束

**示例**:
```python
def test_field_overlap_raised_on_overlapping_fields(self):
    """Test FieldOverlapError is raised when fields overlap."""
    reg = Register("TEST_REG", 0x00, 32)

    field1 = Field("field1", bit_offset=0, bit_width=8, access=AccessType.RW)
    reg.add_field(field1)

    field2 = Field("field2", bit_offset=4, bit_width=8, access=AccessType.RW)
    with pytest.raises(FieldOverlapError):
        reg.add_field(field2)
```

### 2. 边界情况测试 (Boundary Case Tests)

**目的**: 验证系统在极值和边界条件下的行为

#### 测试类别

##### 数值边界 (test_limit_values.py)
- **最大值测试**: 255 (8-bit), 65535 (16-bit), 4294967295 (32-bit)
- **最小值测试**: 0, -128 (signed 8-bit), -32768 (signed 16-bit)
- **溢出测试**: 值超过范围时的包装/截断行为
- **特殊浮点值**: NaN, Inf, -Inf
- **位宽边界**: 1-bit到64-bit

**示例**:
```python
@pytest.mark.parametrize("bit_width,expected_max", [
    (8, 255),
    (16, 65535),
    (32, 4294967295),
])
def test_randvar_max_uint_values(self, bit_width, expected_max):
    """Test RandVar handles maximum unsigned integer values."""
    var = RandVar("test_var", VarType.BIT, bit_width=bit_width)
    var._value = expected_max
    assert var._value == expected_max
```

##### 集合边界 (test_collections.py)
- **空集合**: 空列表、空字典、空CoverGroup
- **单元素集合**: 单个bin、单个寄存器
- **大集合**: 1000个bin、100个寄存器
- **嵌套集合**: 层次结构、嵌套范围

##### 字符串边界 (test_string_types.py)
- **空字符串**: 长度为0的字符串
- **单字符**: 单个字符变量名
- **长字符串**: 1000+字符名称
- **Unicode**: 中文、日文、阿拉伯文、表情符号
- **特殊字符**: 换行、制表符、null字节

### 3. 集成测试 (Integration Tests)

**目的**: 验证模块间的协作和数据流一致性

#### RGM + Coverage集成

**测试场景**:
- 寄存器访问覆盖率跟踪
- 字段级覆盖率采样
- 随机化寄存器配置与覆盖率联动
- 跨寄存器交叉覆盖率
- 状态机转换覆盖率

**示例**:
```python
def test_register_with_coverage(self):
    """Test that a register can have associated coverage."""
    block = RegisterBlock("TEST", 0x40000000)
    reg = Register("STATUS", 0x00, 32)
    reg.add_field(Field("busy", bit_offset=0, bit_width=1, access=AccessType.RO))

    # Create coverage for register reads
    cg = CoverGroup("status_cg")
    cp = CoverPoint("status_cp", "value", bins={"values": [0, 1, 2, 3]})
    cg.add_coverpoint(cp)

    # Sample coverage
    reg.read()
    cg.sample(value=reg._current_value)
    assert cg.coverage >= 0.0
```

#### Randomizer + Coverage集成

**测试场景**:
- 自动覆盖率采样
- 分布式覆盖率跟踪
- 约束空间覆盖率
- 跨变量覆盖率
- 覆盖率引导的随机化

### 4. 端到端测试 (End-to-End Tests)

**目的**: 验证完整的用户工作流

**测试场景**:
- **UVM-like验证流程**: Build → Connect → Run → Cleanup
- **UART验证场景**: 完整的UART控制器验证
- **SPI验证场景**: 完整的SPI控制器验证
- **覆盖率数据库持久化**: 保存和加载覆盖率数据
- **报告生成流程**: HTML和JSON报告生成

**示例**:
```python
def test_complete_verification_workflow(self):
    """Test complete workflow: RGM -> Randomize -> Coverage -> Report."""
    # 1. Build Phase: Create RGM
    dut = RegisterBlock("DUT", 0x40000000)
    ctrl = Register("CTRL", 0x00, 32)
    ctrl.add_field(Field("config", bit_offset=0, bit_width=8, access=AccessType.RW))
    dut.add_register(ctrl)

    # 2. Create Randomizable Transaction
    class TestTransaction(Randomizable):
        def __init__(self, dut_block):
            super().__init__()
            self.dut = dut_block
            self.config = RandVar("config", VarType.BIT, bit_width=8)
            self.cg = CoverGroup("test_cg")
            cp = CoverPoint("config_cp", "config", bins={"auto": 10})
            self.cg.add_coverpoint(cp)
            self.add_covergroup(self.cg)

    # 3. Run Phase: Execute tests
    test = TestTransaction(dut)
    for _ in range(50):
        test.randomize()
        test.dut.write("CTRL", field="config", value=test.config.value)

    # 4. Report Phase: Generate report
    reporter = HTMLReport("report.html")
    reporter.generate(test.cg)

    assert test.cg.coverage > 0.0
```

### 5. 性能测试 (Performance Tests)

**目的**: 建立性能基线并检测回归

#### 性能基准 (最小操作数/秒)

| 操作类别 | 基准性能 | 回归阈值 |
|:---|:---|:---|
| 简单采样 (<10 bins) | 10,000 ops/s | 9,000 ops/s |
| 复杂采样 (>100 bins) | 1,000 ops/s | 900 ops/s |
| Cross覆盖率采样 | 500 ops/s | 450 ops/s |
| 简单随机化 | 10,000 ops/s | 9,000 ops/s |
| 约束随机化 | 1,000 ops/s | 900 ops/s |
| 寄存器读取 | 50,000 ops/s | 45,000 ops/s |
| 寄存器写入 | 50,000 ops/s | 45,000 ops/s |
| 字段访问 | 100,000 ops/s | 90,000 ops/s |

#### 可扩展性测试

- **Coverage可扩展性**: 验证10到1000个bin的性能下降
- **RGM可扩展性**: 验证1到100个寄存器的性能下降
- **内存效率**: 对象创建开销

---

## 运行测试

### 基本命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块的测试
pytest tests/test_coverage/ -v          # Coverage系统
pytest tests/test_rgm/ -v               # RGM系统
pytest tests/legacy/ -v                 # 旧版随机化

# 运行测试类别
pytest tests/unit/ -v                   # 单元测试
pytest tests/integration/ -v            # 集成测试
pytest tests/performance/ -v            # 性能测试

# 使用专用运行器 (避免pytest-qt问题)
python run_coverage_tests.py            # Coverage测试
python run_rgm_tests.py                 # RGM测试
python run_all_tests.py                 # 所有测试
```

### 按标记运行

```bash
# 运行P0关键测试
pytest tests/ -m P0 -v

# 运行异常处理测试
pytest tests/ -m error_handling -v

# 运行边界情况测试
pytest tests/ -m boundary -v

# 运行集成测试
pytest tests/ -m integration -v

# 运行性能测试
pytest tests/ -m performance -v

# 跳过慢速测试
pytest tests/ -m "not slow" -v

# 组合标记
pytest tests/ -m "P0 and unit" -v       # P0级单元测试
pytest tests/ -m "P1 or integration" -v # P1级或集成测试
```

### 覆盖率报告

```bash
# 生成覆盖率报告
pytest tests/ --cov=sv_randomizer --cov=coverage --cov=rgm --cov-report=html

# 设置最低覆盖率阈值
pytest tests/ --cov=sv_randomizer --cov-fail-under=85

# 生成详细报告 (显示未覆盖行)
pytest tests/ --cov-report=term-missing

# 仅覆盖特定模块
pytest tests/test_coverage/ --cov=coverage --cov-report=html
```

### 并行测试执行

```bash
# 使用pytest-xdist并行执行 (安装后)
pip install pytest-xdist
pytest tests/ -n auto                  # 自动检测CPU核心数
pytest tests/ -n 4                     # 使用4个worker
```

---

## 测试标记

### 标记定义

| 标记 | 用途 | 示例 |
|:---|:---|:---|
| `unit` | 单元测试 - 快速、隔离的组件测试 | `@pytest.mark.unit` |
| `integration` | 集成测试 - 跨组件交互测试 | `@pytest.mark.integration` |
| `performance` | 性能测试 - 吞吐量和时延测试 | `@pytest.mark.performance` |
| `benchmark` | 基准测试 - 建立性能基线 | `@pytest.mark.benchmark` |
| `regression` | 回归测试 - 防止bug重现 | `@pytest.mark.regression` |
| `P0` | P0关键测试 - 必须通过才能发布 | `@pytest.mark.P0` |
| `P1` | P1重要测试 - 应该通过 | `@pytest.mark.P1` |
| `P2` | P2增强测试 - 最好通过 | `@pytest.mark.P2` |
| `slow` | 慢速测试 - 需要较长时间 | `@pytest.mark.slow` |
| `error_handling` | 异常处理测试 | `@pytest.mark.error_handling` |
| `boundary` | 边界情况测试 | `@pytest.mark.boundary` |
| `cross_module` | 跨模块集成测试 | `@pytest.mark.cross_module` |
| `end_to_end` | 端到端工作流测试 | `@pytest.mark.end_to_end` |

### 标记使用示例

```python
import pytest

@pytest.mark.unit
@pytest.mark.P0
def test_critical_function(self):
    """P0级单元测试"""
    assert critical_function() == expected

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P1
def test_rgm_coverage_integration(self):
    """RGM和Coverage的P1级集成测试"""
    # 测试代码

@pytest.mark.performance
@pytest.mark.benchmark
def test_sampling_performance(benchmark):
    """采样性能基准测试"""
    cg = setup_covergroup()
    result = benchmark(cg.sample, value=42)
    assert result > PERFORMANCE_BASELINE

@pytest.mark.slow
@pytest.mark.P2
def test_large_scale_simulation(self):
    """大规模慢速仿真测试"""
    # 需要>10秒的测试
```

---

## 覆盖率目标

### 代码覆盖率

当前目标：**≥85%** (理想90%)

```bash
# 查看当前覆盖率
pytest tests/ --cov=sv_randomizer --cov=coverage --cov=rgm --cov-report=term-missing
```

### 按模块覆盖率

| 模块 | 当前覆盖率 | 目标覆盖率 | 优先级 |
|:---|:---|:---|:---|
| `sv_randomizer/` | ~85% | 90% | P0 |
| `coverage/` | ~90% | 95% | P0 |
| `rgm/` | ~85% | 90% | P0 |

### 异常分支覆盖率

目标：**≥90%**

```bash
# 运行异常处理测试
pytest tests/unit/test_error_handling/ -v

# 验证所有异常被测试
pytest tests/unit/test_error_handling/test_coverage_errors.py -v
pytest tests/unit/test_error_handling/test_rgm_errors.py -v
pytest tests/unit/test_error_handling/test_randomizer_errors.py -v
```

### 边界条件覆盖率

目标：**≥85%**

```bash
# 运行边界情况测试
pytest tests/unit/test_boundary_cases/ -v
```

---

## CI/CD集成

### GitHub Actions工作流

项目使用GitHub Actions进行自动化测试，位于`.github/workflows/test.yml`。

#### 工作流作业

1. **test-unit**: 单元测试
   - 平台: Ubuntu, Windows, macOS
   - Python版本: 3.8, 3.9, 3.10, 3.11
   - 运行: P0测试、异常处理、边界情况

2. **test-integration**: 集成测试
   - 平台: Ubuntu, Windows
   - Python版本: 3.9, 3.10, 3.11
   - 运行: Coverage、RGM、跨模块、端到端

3. **test-performance**: 性能测试
   - 平台: Ubuntu
   - Python版本: 3.10
   - 运行: 性能基准、回归检测

4. **test-coverage**: 覆盖率报告
   - 平台: Ubuntu
   - Python版本: 3.10
   - 运行: 所有测试，生成覆盖率报告
   - 阈值: 85%

5. **test-extended**: 扩展测试
   - 条件: workflow_dispatch或main分支
   - 运行: 包含慢速测试的所有测试

### 触发条件

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:  # 手动触发
```

### 本地运行CI测试

```bash
# 模拟CI环境运行
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/ -m "P0 or integration" -v

# 使用与CI相同的Python版本
python3.10 -m pytest tests/ --cov=sv_randomizer --cov=coverage --cov=rgm --cov-fail-under=85
```

---

## 编写新测试

### 测试文件模板

```python
"""
Tests for [模块/功能名称]

描述: 这个测试文件测试[具体功能]
"""

import pytest
from [module] import [Class, Function]

# =============================================================================
# 测试类/函数
# =============================================================================

@pytest.mark.unit
@pytest.mark.P0
class Test[ClassName]:
    """Tests for [ClassName]"""

    def test_[specific_behavior](self):
        """Test that [specific behavior] works correctly."""
        # Setup
        obj = [Class]()

        # Execute
        result = obj.method()

        # Assert
        assert result == expected

    @pytest.mark.parametrize("input,expected", [
        (1, 2),
        (3, 6),
        (5, 10),
    ])
    def test_[parameterized](self, input, expected):
        """Test with parameterized inputs."""
        obj = [Class]()
        result = obj.method(input)
        assert result == expected


# =============================================================================
# 异常处理测试
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
def test_[exception_raised](self):
    """Test that [Exception] is raised when [condition]."""
    with pytest.raises([Exception]):
        [code_that_raises]

# =============================================================================
# 边界情况测试
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.parametrize("boundary_value", [0, 255, -1, 256])
def test_[boundary_case](self, boundary_value):
    """Test behavior at boundary values."""
    obj = [Class]()
    result = obj.method(boundary_value)
    assert is_valid(result)
```

### 使用共享Fixtures

```python
# 在tests/conftest.py中定义的全局fixtures可以直接使用

def test_with_covergroup(sample_covergroup):
    """Test using shared covergroup fixture."""
    cg = sample_covergroup
    cg.sample(value=42)
    assert cg.coverage > 0.0

def test_with_temp_dir(temp_dir):
    """Test using temporary directory fixture."""
    # temp_dir会自动创建并在测试后清理
    import os
    filepath = os.path.join(temp_dir, "test.txt")
    with open(filepath, 'w') as f:
        f.write("test")

def test_with_helpers(test_helpers):
    """Test using helper functions fixture."""
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("test error")

    test_helpers.assert_exception_contains(exc_info, "test error")
```

### 编写集成测试

```python
@pytest.mark.integration
@pytest.mark.cross_module
def test_[integration_scenario](self, integrated_rgm_coverage):
    """Test [specific integration scenario]."""
    # 使用预配置的集成测试fixture
    txn = integrated_rgm_coverage

    # 执行工作流
    txn.randomize()
    txn.block.write("CTRL", field="mode", value=txn.mode.value)

    # 验证集成
    assert txn.cg.coverage > 0.0
    assert txn.block.read("CTRL", field="mode") == txn.mode.value
```

### 编写性能测试

```python
@pytest.mark.performance
@pytest.mark.benchmark
def test_[operation]_performance(benchmark):
    """Benchmark [operation] performance."""
    # Setup
    obj = [Class]()

    # Benchmark会运行多次并计算统计数据
    def operation():
        return obj.method()

    result = benchmark(operation)

    # 验证性能不低于基线
    assert result.stats['ops'] >= BASELINE_OPS_PER_SEC
```

### 测试命名规范

- **文件名**: `test_<module>.py` 或 `test_<feature>.py`
- **类名**: `Test<ClassName>` (PascalCase)
- **函数名**: `test_<specific_behavior>` (snake_case)
- **异常测试**: `test_<exception>_raised_on_<condition>`
- **边界测试**: `test_<boundary_type>_boundary`

---

## 性能基准

### 当前性能基线

基于v0.3.0版本在标准硬件上的测量：

| 操作 | 基准 (ops/s) | 最小可接受 (ops/s) |
|:---|:---|:---|
| **Coverage采样** | | |
| 简单采样 (10 bins) | 246,000 | 221,400 |
| 复杂采样 (200 bins) | 84,500 | 76,050 |
| Cross采样 (10x10) | 5,000 | 4,500 |
| **随机化** | | |
| 简单随机化 (无约束) | 12,000 | 10,800 |
| 约束随机化 (2约束) | 8,500 | 7,650 |
| RandC循环 (8值) | 15,000 | 13,500 |
| **RGM访问** | | |
| 寄存器读取 | 65,000 | 58,500 |
| 寄存器写入 | 62,000 | 55,800 |
| 字段访问 | 120,000 | 108,000 |

### 性能回归阈值

- **警告**: 性能下降超过10%
- **失败**: 性能下降超过20%

### 运行性能测试

```bash
# 运行所有性能测试
pytest tests/performance/test_benchmarks.py -v -m benchmark

# 运行特定性能测试
pytest tests/performance/test_benchmarks.py::TestCoverageSamplingPerformance -v

# 生成性能报告
pytest tests/performance/test_benchmarks.py -v --benchmark-only
```

---

## 故障排除

### 常见问题

#### 1. pytest-qt DLL加载错误 (Windows)

**错误**:
```
ImportError: DLL load failed while importing QtCore
```

**解决方案**:
```bash
# 方法1: 使用专用运行器
python run_coverage_tests.py
python run_rgm_tests.py

# 方法2: 设置环境变量
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/ -v

# 方法3: 卸载pytest-qt
pip uninstall pytest-qt
```

#### 2. 导入错误

**错误**:
```
ImportError: cannot import name 'CoverGroup' from 'coverage'
```

**解决方案**:
```bash
# 确保以可编辑模式安装
pip install -e .

# 或使用开发模式
pip install -e ".[dev]"
```

#### 3. 测试超时

**错误**:
```
Failed: Timeout >300s
```

**解决方案**:
```bash
# 跳过慢速测试
pytest tests/ -m "not slow" -v

# 或增加超时时间
pytest tests/ --timeout=600
```

#### 4. 覆盖率不达标

**错误**:
``# Failed: Coverage minimum not met: 84% < 85%
```

**解决方案**:
```bash
# 临时降低阈值
pytest tests/ --cov-fail-under=80

# 或查看未覆盖的代码
pytest tests/ --cov-report=term-missing

# 然后添加测试提高覆盖率
```

#### 5. 性能测试失败

**错误**:
```
AssertionError: Performance 8500 ops/sec below baseline 10000
```

**解决方案**:
```bash
# 查看详细性能信息
pytest tests/performance/ -v -s

# 更新基线值（如果性能真的改进了）
# 编辑 tests/performance/test_benchmarks.py
# 更新 PERFORMANCE_BASELINES 字典

# 或跳过性能测试
pytest tests/ -m "not performance" -v
```

### 调试测试

```bash
# 进入调试模式
pytest tests/ --pdb

# 在第一个失败时进入调试
pytest tests/ -x --pdb

# 显示print输出
pytest tests/ -s

# 只运行失败的测试
pytest tests/ --lf

# 详细输出
pytest tests/ -vv
```

### 查看测试详细信息

```bash
# 显示测试的完整输出
pytest tests/ -v -s

# 显示最慢的10个测试
pytest tests/ --durations=10

# 显示测试覆盖率
pytest tests/ --cov=sv_randomizer --cov-report=term-missing
```

---

## 最佳实践

### 1. 测试组织

- **保持测试独立**: 每个测试应该独立运行，不依赖其他测试
- **使用descriptive名称**: 测试名称应清楚描述测试的内容
- **一个测试一个断言**: 除非测试场景，否则保持测试简单
- **使用setUp/tearDown**: 在类中使用`setup_method`和`teardown_method`

### 2. Fixture使用

- **优先使用共享fixtures**: 使用`conftest.py`中定义的fixtures
- **fixtures有明确作用域**: 使用`scope="function"`, `scope="session"`等
- **清理资源**: 使用yield fixtures确保资源被清理

```python
@pytest.fixture(scope="function")
def temp_config_file(temp_dir):
    """Create a temporary config file."""
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'w') as f:
        f.write('{"key": "value"}')

    yield config_path

    # 清理 (temp_dir会自动清理)
```

### 3. 参数化测试

对于多个相似测试用例，使用参数化：

```python
@pytest.mark.parametrize("input,expected", [
    (0, 0),
    (1, 1),
    (2, 4),
    (10, 100),
])
def test_square(input, expected):
    assert square(input) == expected
```

### 4. 跳过和预期失败

```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 9),
                    reason="Requires Python 3.9+")
def test_python39_feature():
    pass

@pytest.mark.xfail(reason="Known bug, tracking in #123")
def test_known_bug():
    assert False  # 预期失败
```

### 5. Mock使用

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using mock object."""
    mock_obj = Mock()
    mock_obj.method.return_value = 42

    result = mock_obj.method()
    assert result == 42

def test_with_patch():
    """Test patching external dependency."""
    with patch('module.external_function') as mock_func:
        mock_func.return_value = "mocked"
        result = module.use_external()
        assert result == "mocked"
```

---

## 贡献指南

### 添加新测试

1. **确定测试类型**: 单元测试、集成测试、性能测试
2. **选择合适的目录**: 遵循目录结构
3. **使用适当的标记**: `@pytest.mark.unit`, `@pytest.mark.P0`等
4. **编写清晰的文档**: 每个测试应有docstring
5. **确保测试独立**: 可以单独运行
6. **更新CI配置**: 如需新的测试类别

### 代码审查清单

在提交PR前，确保：
- [ ] 所有新代码都有对应的测试
- [ ] 测试覆盖率未下降
- [ ] 所有P0测试通过
- [ ] 性能测试无回归
- [ ] 异常处理有对应测试
- [ ] 边界条件已测试
- [ ] 文档已更新

---

## 资源链接

- **pytest文档**: https://docs.pytest.org/
- **pytest-cov文档**: https://pytest-cov.readthedocs.io/
- **GitHub Actions**: https://docs.github.com/en/actions
- **项目文档**: [../README.md](../../README.md)
- **开发指南**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**维护者**: EDA_UFVM Team
**最后更新**: 2026-03-01
