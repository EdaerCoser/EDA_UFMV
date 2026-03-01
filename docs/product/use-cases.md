# 应用场景

**版本**: v0.3.1

---

## 1. FPGA原型验证

### 场景描述

快速验证FPGA原型功能，生成测试向量进行功能验证。

### 优势

- 快速生成测试向量
- Python脚本自动化
- 无需学习SystemVerilog

### 典型工作流

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand

# 1. 定义测试激励
stimulus_rand = rand(int)(bits=32)

class TestVector(Randomizable):
    stimulus: stimulus_rand

# 2. 生成测试向量
vectors = []
for i in range(1000):
    vec = TestVector()
    vec.randomize()
    vectors.append(vec.stimulus)

# 3. 导出到Verilog测试平台
formatter = VerilogFormatter()
formatter.format_testbench(vectors, "testbench.v")
```

---

## 2. IC功能验证

### 场景描述

模块级和芯片级功能验证，使用约束随机化和覆盖率驱动验证。

### 优势

- 约束随机化
- 覆盖率驱动
- 快速回归测试

### 典型工作流

```python
# 定义DUT模型
class DUTModel(Randomizable):
    # ... 定义变量和约束 ...

# 定义覆盖率
@covergroup
class DUTCoverage:
    # ... 定义覆盖点 ...

# 覆盖率驱动验证
dut = DUTModel()
cov = DUTCoverage(dut)
cgr = CoverageGuidedRandomizer(dut, cov)

# 自动达到目标覆盖率
cgr.randomize_until_coverage(target_coverage=95.0)
```

---

## 3. 上板测试

### 场景描述

现场FPGA配置验证和调试。

### 优势

- 快速配置生成
- 交互式测试
- 日志和调试支持

---

## 4. 典型用例

### 4.1 AXI总线验证

**需求**: 生成符合AXI协议的随机事务

**实现**:

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint

# 定义类型注解
addr_rand = rand(int)(bits=32)
data_rand = rand(int)(bits=8)
opcode_rand = rand(str)(enum_values=['READ', 'WRITE'])

class AXITransaction(Randomizable):
    addr: addr_rand
    data: data_rand
    opcode: opcode_rand

    @constraint
    def addr_aligned(self):
        return self.addr % 4 == 0
```

**关键点**:
- 地址对齐约束
- 操作码枚举
- 随机数据生成

### 4.2 DMA控制器测试

**需求**: 生成DMA配置，确保地址不重叠

**实现**:

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint

src_addr_rand = rand(int)(bits=32)
dst_addr_rand = rand(int)(bits=32)
transfer_size_rand = rand(int)(bits=16)

class DMAConfig(Randomizable):
    src_addr: src_addr_rand
    dst_addr: dst_addr_rand
    transfer_size: transfer_size_rand

    @constraint
    def addr_not_overlap(self):
        return self.src_addr + self.transfer_size <= self.dst_addr
```

**关键点**:
- 源地址和目标地址不重叠
- 传输大小约束
- 复杂关系运算

### 4.3 UART配置验证

**需求**: 生成UART配置的所有合法组合

**实现**:

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand

baud_rate_rand = rand(str)(enum_values=[9600, 19200, 38400, 57600, 115200])
parity_rand = rand(str)(enum_values=['NONE', 'EVEN', 'ODD'])
stop_bits_rand = rand(int)(bits=2, min=1, max=2)

class UARTConfig(Randomizable):
    baud_rate: baud_rate_rand
    parity: parity_rand
    stop_bits: stop_bits_rand
```

**关键点**:
- 波特率枚举
- 奇偶校验枚举
- 停止位随机

### 4.4 事务级覆盖率收集

**需求**: 收集事务的覆盖率，确保所有场景都被测试

**实现**:

```python
from coverage.core import CoverGroup, CoverPoint, Cross

# 定义覆盖率组
cg = CoverGroup("transaction_cg")

# 地址覆盖点（自动分箱）
addr_cp = CoverPoint("addr", "addr", bins={"auto": 16})
cg.add_coverpoint(addr_cp)

# 操作码覆盖点（值bins）
opcode_cp = CoverPoint("opcode", "opcode",
                       bins={"values": ["READ", "WRITE", "IDLE"]})
cg.add_coverpoint(opcode_cp)

# 交叉覆盖率
cross = Cross("addr_opcode", ["addr", "opcode"])
cg.add_cross(cross)

# 采样并生成报告
for i in range(1000):
    txn.randomize()
    cg.sample(addr=txn.addr, opcode=txn.opcode)

# 生成HTML报告
from coverage.formatters import generate_report
data = {"title": "Transaction Coverage",
        "covergroups": [cg.get_coverage_details()]}
generate_report(data, format="html", filepath="coverage.html")
```

**关键点**:
- 自动分箱
- 值bins
- Cross覆盖率
- HTML报告生成

---

## 5. 应用场景对比

| 场景 | 主要使用功能 | 典型规模 | 验证目标 |
|:---|:---|:---|:---|
| **FPGA原型** | 随机化 | 中等 | 功能正确性 |
| **IC验证** | 随机化 + 覆盖率 | 大规模 | 覆盖率达标 |
| **上板测试** | 随机化 + 报告 | 小规模 | 现场调试 |
| **回归测试** | 测试Agent | 大规模 | 回归验证 |

---

## 相关文档

- ✨ [功能清单](features.md)
- 📖 [随机化系统指南](../guides/randomization.md)
- 📊 [覆盖率系统指南](../guides/coverage/)
- 🔄 [与UVM对比](comparison.md)
