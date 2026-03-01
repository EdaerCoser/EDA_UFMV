# SystemVerilog覆盖率语法到Python迁移指南

**版本**: v0.2.0
**更新日期**: 2026年3月1日
**目标读者**: 从SystemVerilog迁移到EDA_UFMV的验证工程师

---

## 1. 概述

### 1.1 文档目的

本文档帮助熟悉SystemVerilog覆盖率的验证工程师快速掌握EDA_UFMV的Python覆盖率系统。通过SystemVerilog与Python语法的对照对比，理解如何在Python中实现相同的功能覆盖率功能。

### 1.2 覆盖率系统架构

EDA_UFMV的覆盖率系统是独立顶层模块（`coverage/`），提供SystemVerilog风格的API：

```
coverage/
├── core/          # 核心类 (CoverGroup, CoverPoint, Cross, Bin)
├── database/      # 数据库后端 (Memory, File)
├── formatters/    # 报告生成器 (HTML, JSON, UCIS)
└── api/           # SystemVerilog风格装饰器
```

### 1.3 SystemVerilog vs Python核心差异

| 特性 | SystemVerilog | Python (EDA_UFMV) |
|:---|:---|:---|
| **类型系统** | 静态类型，需指定位宽 | 动态类型，自动处理 |
| **采样表达式** | 直接引用变量 | `sample_expr="var"` 或 callable |
| **Bin初始化** | 编译时确定 | AutoBin采用懒加载 |
| **IllegalBin处理** | 记录警告 | 抛出 `IllegalBinHitError` |
| **API风格** | 语法块 | 装饰器（类似语法块）或传统API |

### 1.4 快速参考表

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

---

## 2. 基础语法映射

### 2.1 CoverGroup定义

**SystemVerilog代码:**
```systemverilog
covergroup addr_cg @(posedge clk);
    // coverpoints here
endgroup
```

**Python代码（装饰器风格 - 推荐）:**
```python
from coverage.api import covergroup, coverpoint

@covergroup("addr_cg", sample_event="clk")
class AddrCoverage:
    @coverpoint("addr", bins={"ranges": [[0, 0xFF]]})
    def addr(self):
        return self._addr
```

**Python代码（传统API风格）:**
```python
from coverage.core import CoverGroup, CoverPoint

# 创建CoverGroup
addr_cg = CoverGroup("addr_cg")

# 创建并添加CoverPoint
addr_cp = CoverPoint("addr", "addr", bins={"ranges": [[0, 0xFF]]})
addr_cg.add_coverpoint(addr_cp)
```

**关键差异说明:**

1. **采样事件**:
   - SV: `@(posedge clk)` - 语法块的一部分
   - Python: `sample_event="clk"` - 装饰器参数

2. **结构方式**:
   - SV: 使用 `endgroup` 结束定义
   - Python: 使用类定义（装饰器）或函数调用（传统API）

3. **CoverPoint添加**:
   - SV: 在covergroup内部声明
   - Python: 通过 `add_coverpoint()` 方法或装饰器自动添加

### 2.2 CoverPoint定义

**SystemVerilog代码:**
```systemverilog
coverpoint addr;
    bins low[] = {[0:127]};
    bins mid[] = {[128:255]};
    bins high[] = {[256:511]};
    ignore_bins reserved = {0};
```

**Python代码（装饰器风格）:**
```python
@coverpoint("addr",
            bins={
                "low": [[0, 0x7F]],
                "mid": [[0x80, 0xFF]],
                "high": [[0x100, 0x1FF]]
            },
            ignore_bins={
                "reserved": [0]
            })
def addr(self):
    return self._addr
```

**Python代码（传统API风格）:**
```python
addr_cp = CoverPoint(
    name="addr",
    sample_expr="addr",
    bins={
        "low": [[0, 0x7F]],
        "mid": [[0x80, 0xFF]],
        "high": [[0x100, 0x1FF]]
    },
    ignore_bins={
        "reserved": [0]
    }
)
```

### 2.3 采样表达式

**SystemVerilog代码:**
```systemverilog
coverpoint addr;  // 直接引用变量名
```

**Python代码（字符串表达式）:**
```python
CoverPoint("addr", sample_expr="addr", bins={...})
```

**Python代码（callable）:**
```python
CoverPoint("addr",
           sample_expr=lambda: self.addr,
           bins={...})
```

**Python代码（装饰器自动推断）:**
```python
@coverpoint("addr", bins={...})
def addr(self):
    return self._addr  # 自动使用返回值
```

### 2.4 完整示例对比

**SystemVerilog代码:**
```systemverilog
class Transaction;
    rand bit [15:0] addr;
    rand bit [7:0]  opcode;

    covergroup cg @(posedge clk);
        coverpoint addr;
            bins low[] = {[0:0x0FFF]};
            bins mid[] = {[0x1000:0x1FFF]};
            bins high[] = {[0x2000:0xFFFF]};
            ignore_bins reserved = {0};
        coverpoint opcode;
            bins values[] = {READ, WRITE, NOP};
    endgroup

    function new();
        cg = new();
    endfunction
endclass
```

**Python代码（装饰器风格）:**
```python
from sv_randomizer import Randomizable
from coverage.api import covergroup, coverpoint

class Transaction(Randomizable):
    def __init__(self):
        super().__init__()

        # 定义随机变量
        self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)
        self._rand_vars['opcode'] = RandVar('opcode', VarType.BIT, bit_width=8)

        # 定义覆盖率组
        self.cg = self._create_coverage()

    @covergroup("cg", sample_event="clk")
    class _CoverageClass:
        @coverpoint("addr",
                    bins={
                        "low": [[0, 0x0FFF]],
                        "mid": [[0x1000, 0x1FFF]],
                        "high": [[0x2000, 0xFFFF]]
                    },
                    ignore_bins={
                        "reserved": [0]
                    })
        def addr(self):
            return self._txn.addr

        @coverpoint("opcode",
                    bins={"values": ["READ", "WRITE", "NOP"]})
        def opcode(self):
            return self._txn.opcode

    def _create_coverage(self):
        cg = self._CoverageClass()
        cg._txn = self
        self.add_covergroup(cg)
        return cg
```

**Python代码（简化风格 - 推荐）:**
```python
from sv_randomizer import Randomizable
from coverage.core import CoverGroup, CoverPoint

class Transaction(Randomizable):
    def __init__(self):
        super().__init__()

        # 定义随机变量
        self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)
        self._rand_vars['opcode'] = RandVar('opcode', VarType.BIT, bit_width=8)

        # 创建覆盖率组
        self.cg = CoverGroup("cg")

        # 地址覆盖点
        addr_cp = CoverPoint(
            name="addr",
            sample_expr="addr",
            bins={
                "low": [[0, 0x0FFF]],
                "mid": [[0x1000, 0x1FFF]],
                "high": [[0x2000, 0xFFFF]]
            },
            ignore_bins={"reserved": [0]}
        )
        self.cg.add_coverpoint(addr_cp)

        # 操作码覆盖点
        opcode_cp = CoverPoint(
            name="opcode",
            sample_expr="opcode",
            bins={"values": ["READ", "WRITE", "NOP"]}
        )
        self.cg.add_coverpoint(opcode_cp)

        # 添加到Randomizable（自动采样）
        self.add_covergroup(self.cg)
```

---

## 3. Bin类型详解

### 3.1 Value Bins（值箱）

**用途**: 匹配单个精确值

**SystemVerilog代码:**
```systemverilog
coverpoint opcode;
    bins read = {0};
    bins write = {1};
    bins nop = {2};
```

**Python代码:**
```python
@coverpoint("opcode", bins={
    "values": [0, 1, 2]  # 或使用命名形式
})
# 或
bins={
    "read": [0],
    "write": [1],
    "nop": [2]
}
```

### 3.2 Range Bins（范围箱）

**用途**: 匹配一个范围内的值

**SystemVerilog代码:**
```systemverilog
coverpoint addr;
    bins low[] = {[0:127]};
    bins mid[] = {[128:255]};
    bins high[] = {[256:511]};
```

**Python代码:**
```python
@coverpoint("addr", bins={
    "low": [[0, 127]],      # 注意: 使用列表 [low, high]
    "mid": [[128, 255]],
    "high": [[256, 511]]
})
```

**关键差异:**
- SV: `[0:127]` - 方括号内用冒号
- Python: `[0, 127]` - 列表形式，用逗号

### 3.3 Wildcard Bins（通配符箱）

**用途**: 使用通配符匹配模式

**SystemVerilog代码:**
```systemverilog
coverpoint addr;
    wildcard bins low[] = {8'b0000????};  // 匹配0x00-0x0F
    wildcard bins mid[] = {8'b??????00};  // 匹配能被4整除的值
```

**Python代码:**
```python
@coverpoint("addr", bins={
    "wildcards": [
        "0000????",  # 匹配0x00-0x0F
        "??????00"   # 匹配能被4整除的值
    ]
})
```

**Python代码（十六进制）:**
```python
@coverpoint("addr", bins={
    "wildcards": [
        "0???",      # 匹配0x000-0x0FF
        "8???",      # 匹配0x800-0x8FF
        "9???",      # 匹配0x900-0x9FF
    ]
})
```

**通配符规则:**
- `?` 匹配任意单个字符
- 十六进制模式: `"8???"` 匹配 0x8000-0x8FFF
- 通用模式: `"AB?D"` 匹配任意单字符

### 3.4 Auto Bins（自动分箱）

**用途**: 自动将范围分成多个等宽的bin

**SystemVerilog代码:**
```systemverilog
coverpoint data;
    option.auto_bin_max = 16;  // 自动分成16个bin
```

**Python代码:**
```python
@coverpoint("data",
            bins={"auto": 16},  # 自动分成16个bin
            auto_bin_max=64)    # 最大bin数量
```

**工作原理:**
1. 首次采样时记录最小/最大值
2. 根据总范围计算每个bin的宽度
3. 后续采样映射到对应bin

**示例:**
```python
# 假设数据范围是 0-255，分成16个bin
# 每个bin覆盖: 256/16 = 16 个值
# bin_0: [0, 15], bin_1: [16, 31], ..., bin_15: [240, 255]
```

### 3.5 Ignore Bins（忽略箱）

**用途**: 忽略特定值（不计入覆盖率）

**SystemVerilog代码:**
```systemverilog
coverpoint addr;
    bins valid[] = {[0:255]};
    ignore_bins reserved = {0};
    ignore_buffers special = {255, 254};
```

**Python代码:**
```python
@coverpoint("addr",
            bins={"ranges": [[0, 255]]},
            ignore_bins={
                "reserved": [0],
                "special": [255, 254]
            })
```

**特殊行为:**
- 匹配时跳过采样
- 不计入覆盖率统计
- `increment_hit()` 不执行任何操作

### 3.6 Illegal Bins（非法箱）

**用途:** 标记非法值（命中时报错）

**SystemVerilog代码:**
```systemverilog
coverpoint status;
    bins ok = {0};
    illegal_bins error = {255};  // 命中时报错
```

**Python代码:**
```python
@coverpoint("status",
            bins={"values": [0]},
            illegal_bins={
                "error": [255]  # 命中时抛出异常
            })
```

**异常处理:**
```python
try:
    pkt.randomize()
except IllegalBinHitError as e:
    print(f"Illegal value hit: {e}")
```

### 3.7 Bin组合使用

**SystemVerilog代码:**
```systemverilog
coverpoint addr;
    bins low[] = {[0:127]};
    bins mid[] = {[128:255]};
    bins specific = {0x100, 0x200};
    wildcard bins pattern[] = {8'b????0000};
    ignore_bins reserved = {0};
    illegal_bins bad = {0xFFFF};
```

**Python代码:**
```python
@coverpoint("addr",
            bins={
                "low": [[0, 127]],
                "mid": [[128, 255]],
                "specific": [0x100, 0x200],
                "wildcards": ["????0000"]
            },
            ignore_bins={
                "reserved": [0]
            },
            illegal_bins={
                "bad": [0xFFFF]
            })
```

---

## 4. Cross覆盖率

### 4.1 二维Cross

**SystemVerilog代码:**
```systemverilog
covergroup cg;
    coverpoint cp1;
        bins b1[] = {[0:3]};
    coverpoint cp2;
        bins b2[] = {[0:3]};
    cross cp1_cp2;
endgroup
```

**Python代码（传统API）:**
```python
from coverage.core import CoverGroup, CoverPoint, Cross

cg = CoverGroup("cg")

# 创建CoverPoints
cp1 = CoverPoint("cp1", "var1", bins={"ranges": [[0, 3]]})
cp2 = CoverPoint("cp2", "var2", bins={"ranges": [[0, 3]]})
cg.add_coverpoint(cp1)
cg.add_coverpoint(cp2)

# 创建Cross（笛卡尔积: 4x4=16个组合）
cross = Cross("cp1_cp2", ["cp1", "cp2"])
cg.add_cross(cross)
```

**采样结果示例:**
```
cp1_cp2 bins:
  (b1[0], b2[0]): 5 hits
  (b1[0], b2[1]): 3 hits
  (b1[1], b2[0]): 7 hits
  ...
```

### 4.2 多维Cross

**SystemVerilog代码:**
```systemverilog
covergroup cg;
    coverpoint addr;
    coverpoint opcode;
    coverpoint data;
    cross addr_opcode, addr_data, opcode_data;
endgroup
```

**Python代码:**
```python
cg = CoverGroup("cg")

# 添加CoverPoints...
cg.add_coverpoint(addr_cp)
cg.add_coverpoint(opcode_cp)
cg.add_coverpoint(data_cp)

# 创建多个Cross
cg.add_cross(Cross("addr_opcode", ["addr", "opcode"]))
cg.add_cross(Cross("addr_data", ["addr", "data"]))
cg.add_cross(Cross("opcode_data", ["opcode", "data"]))
```

### 4.3 Cross过滤（cross_filter）

**用途：** 过滤不需要的组合

**Python代码（CrossBuilder）:**
```python
from coverage.core import create_cross

# 使用构建器模式创建Cross
cross = (create_cross("addr_data", "addr_cp", "data_cp")
         .with_filter(lambda bins: bins[0] != bins[1])  # 过滤对角线
         .build())

cg.add_cross(cross)
```

**Python代码（直接创建）:**
```python
def filter_func(bins_tuple):
    """过滤函数 - 返回False表示排除该组合"""
    addr_bin, data_bin = bins_tuple
    # 例如：排除addr和data值相同的组合
    return addr_bin != data_bin

cross = Cross("addr_data",
              coverpoints=["addr_cp", "data_cp"],
              cross_filter=filter_func)
```

### 4.4 性能优化（懒加载）

**问题**: 大规模Cross可能导致组合爆炸

**解决方案**: Python的Cross使用懒加载优化

```python
# 当bin组合数 > 10000 时自动启用懒加载
cross = Cross("large_cross",
              coverpoints=["cp1", "cp2", "cp3"])  # 假设每个CP有100个bins
# 总组合: 100^3 = 1,000,000（自动懒加载）
```

**懒加载特性:**
- 不预先生成所有组合
- 首次遇到组合时动态添加
- 显著减少内存占用

---

## 5. 采样控制

### 5.1 自动采样（与Randomizable集成）

**Python代码:**
```python
from sv_randomizer import Randomizable
from coverage.core import CoverGroup, CoverPoint

class Packet(Randomizable):
    def __init__(self):
        super().__init__()

        # 定义随机变量
        self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)

        # 创建覆盖率组
        cg = CoverGroup("addr_cg")
        cg.add_coverpoint(CoverPoint("addr", "addr", bins={"auto": 16}))

        # 添加到Randomizable
        self.add_covergroup(cg)  # 关键：启用自动采样

# 使用
pkt = Packet()
for i in range(100):
    pkt.randomize()  # 自动采样覆盖率
```

**工作流程:**
1. `randomize()` 调用
2. `post_randomize()` 自动触发
3. `_sample_coverage()` 收集变量值
4. 调用所有CoverGroup的 `sample()` 方法

### 5.2 手动采样

**Python代码:**
```python
from coverage.api import sample_coverage

# 禁用自动采样
pkt.disable_coverage_sampling()

# 执行操作
pkt.addr = 0x1000

# 手动触发采样
sample_coverage(pkt)

# 重新启用自动采样
pkt.enable_coverage_sampling()
```

**Python代码（直接调用）:**
```python
# 直接调用CoverGroup的sample方法
pkt.addr_cg.sample(addr=pkt.addr, opcode=pkt.opcode)
```

### 5.3 启用/禁用CoverGroup

**Python代码:**
```python
# 禁用CoverGroup采样
pkt.addr_cg.disable_sampling()

# 执行操作（不会采样addr_cg）
pkt.randomize()

# 重新启用
pkt.addr_cg.enable_sampling()
```

### 5.4 启用/禁用CoverPoint

**Python代码:**
```python
# 获取CoverPoint
addr_cp = pkt.addr_cg.get_coverpoint("addr")

# 禁用CoverPoint
addr_cp.disable()

# 执行操作（不会采样addr_cp）
pkt.randomize()

# 重新启用
addr_cp.enable()
```

---

## 6. 报告生成

### 6.1 HTML报告

**Python代码:**
```python
from coverage.formatters import generate_report

# 准备数据
data = {
    "title": "Packet Coverage Report",
    "covergroups": [
        pkt.addr_cg.get_coverage_details(),
        pkt.opcode_cg.get_coverage_details()
    ]
}

# 生成HTML报告
html = generate_report(data,
                      format="html",
                      filepath="coverage_report.html")
```

**报告特性:**
- 响应式设计
- 可视化进度条（颜色编码）
- 可折叠的CoverGroup详情
- Bin命中网格显示

### 6.2 JSON报告

**Python代码:**
```python
# 生成JSON报告（CI/CD集成）
json = generate_report(data,
                      format="json",
                      filepath="coverage.json")
```

**输出格式:**
```json
{
  "title": "Packet Coverage Report",
  "generated_at": "2026-03-01T10:30:00",
  "total_coverage": 85.5,
  "covergroups": [...]
}
```

### 6.3 UCIS报告（IEEE 1687）

**Python代码:**
```python
# 生成UCIS格式报告（EDA工具互操作）
ucis = generate_report(data,
                       format="ucis",
                       filepath="coverage.ucis")
```

**UCIS JSON:**
```python
# 生成UCIS的JSON表示
ucis_json = generate_report(data,
                            format="ucis_json",
                            filepath="coverage_ucis.json")
```

### 6.4 报告生成完整示例

**Python代码:**
```python
from coverage.formatters import ReportFactory

# 创建报告生成器
reporter = ReportFactory.create_html_report("My Coverage")

# 生成报告
content = reporter.generate(data)

# 保存并自动打开
filepath = reporter.save(content,
                         filepath="reports/coverage.html",
                         auto_open=True)
```

---

## 7. 数据库持久化

### 7.1 内存数据库（默认）

**Python代码:**
```python
from coverage.database import MemoryCoverageDatabase

# 创建内存数据库
db = MemoryCoverageDatabase()

# 记录采样
db.record_sample("addr_cp", 0x1000, "addr_cg")

# 获取命中次数
count = db.get_hit_count("addr_cp", "range_0", "addr_cg")

# 获取覆盖率数据
data = db.get_coverage_data("addr_cg")
```

**特点:**
- 快速访问
- 无持久化
- 适合单次测试运行

### 7.2 文件数据库

**Python代码:**
```python
from coverage.database import FileCoverageDatabase

# 创建文件数据库
db = FileCoverageDatabase("coverage.json")

# 记录采样
db.record_sample("addr_cp", 0x1000, "addr_cg")

# 保存到文件
db.save()

# 加载已有数据
db.load()

# 合并多个数据库
db1 = FileCoverageDatabase("run1.json")
db2 = FileCoverageDatabase("run2.json")
db1.merge(db2)
db1.save("merged.json")
```

### 7.3 跨会话累积

**Python代码:**
```python
# 第一次运行
db = FileCoverageDatabase("coverage.json")
# ... 采样 ...
db.save()

# 第二次运行（追加）
db = FileCoverageDatabase("coverage.json")
db.load()  # 加载之前的覆盖率
# ... 新采样 ...
db.save()  # 保存累积结果
```

---

## 8. 迁移实战

### 8.1 迁移流程

**步骤1: 分析现有覆盖率定义**
- 识别所有CoverGroup和CoverPoint
- 记录bin类型和定义
- 识别Cross覆盖关系

**步骤2: 选择API风格**
- 装饰器API: 更接近SystemVerilog语法
- 传统API: 更灵活，适合复杂场景

**步骤3: 逐步迁移**
- 先迁移简单CoverPoint
- 再处理复杂bin定义
- 最后迁移Cross覆盖

**步骤4: 验证一致性**
- 使用相同随机种子
- 对比覆盖率结果
- 检查报告输出

### 8.2 完整迁移示例

**原始SystemVerilog代码:**
```systemverilog
class Transaction;
    rand bit [15:0] addr;
    rand bit [7:0]  opcode;
    rand bit [31:0] data;

    covergroup cg @(posedge clk);
        coverpoint addr;
            bins low[] = {[0:0x0FFF]};
            bins mid[] = {[0x1000:0x1FFF]};
            bins high[] = {[0x2000:0xFFFF]};
            ignore_bins reserved = {0};
        coverpoint opcode;
            bins valid[] = {[0:15]};
            illegal_bins bad = {255};
        cross addr_opcode;
    endgroup

    function new();
        cg = new();
    endfunction
endclass
```

**迁移后Python代码（带注释）:**
```python
from sv_randomizer import Randomizable, RandVar, VarType
from coverage.core import CoverGroup, CoverPoint, Cross

class Transaction(Randomizable):
    """
    Transaction类 - 对应SystemVerilog的Transaction
    """

    def __init__(self):
        super().__init__()

        # === 对应: rand bit [15:0] addr; ===
        self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)

        # === 对应: rand bit [7:0] opcode; ===
        self._rand_vars['opcode'] = RandVar('opcode', VarType.BIT, bit_width=8)

        # === 对应: rand bit [31:0] data; ===
        self._rand_vars['data'] = RandVar('data', VarType.BIT, bit_width=32)

        # === 创建CoverGroup (对应 covergroup cg @(posedge clk);) ===
        # 注意: sample_event="clk" 对应 @(posedge clk)
        self.cg = CoverGroup("cg")

        # === 创建地址CoverPoint ===
        # 对应: coverpoint addr;
        #       bins low[] = {[0:0x0FFF]};
        #       bins mid[] = {[0x1000:0x1FFF]};
        #       bins high[] = {[0x2000:0xFFFF]};
        #       ignore_bins reserved = {0};
        addr_cp = CoverPoint(
            name="addr",
            sample_expr="addr",
            bins={
                # SV: [0:0x0FFF] → Python: [0, 0x0FFF]
                "low": [[0, 0x0FFF]],
                # SV: [0x1000:0x1FFF] → Python: [0x1000, 0x1FFF]
                "mid": [[0x1000, 0x1FFF]],
                # SV: [0x2000:0xFFFF] → Python: [0x2000, 0xFFFF]
                "high": [[0x2000, 0xFFFF]]
            },
            ignore_bins={
                # 对应: ignore_bins reserved = {0};
                "reserved": [0]
            }
        )
        self.cg.add_coverpoint(addr_cp)

        # === 创建操作码CoverPoint ===
        # 对应: coverpoint opcode;
        #       bins valid[] = {[0:15]};
        #       illegal_bins bad = {255};
        opcode_cp = CoverPoint(
            name="opcode",
            sample_expr="opcode",
            bins={
                # SV: [0:15] → Python: [0, 15]
                "valid": [[0, 15]]
            },
            illegal_bins={
                # 对应: illegal_bins bad = {255};
                "bad": [255]
            }
        )
        self.cg.add_coverpoint(opcode_cp)

        # === 创建Cross覆盖 ===
        # 对应: cross addr_opcode;
        addr_opcode_cross = Cross(
            name="addr_opcode",
            coverpoints=["addr", "opcode"]
        )
        self.cg.add_cross(addr_opcode_cross)

        # === 添加到Randomizable（自动采样） ===
        # Python特性：添加后会自动在randomize()时采样
        self.add_covergroup(self.cg)

# === 使用示例 ===
if __name__ == "__main__":
    # 创建事务对象
    txn = Transaction()

    # 生成随机事务（自动采样覆盖率）
    for i in range(100):
        txn.randomize()

    # 获取覆盖率
    print(f"总覆盖率: {txn.get_total_coverage():.2f}%")

    # 生成报告
    from coverage.formatters import generate_report
    data = {
        "title": "Transaction Coverage",
        "covergroups": [txn.cg.get_coverage_details()]
    }
    generate_report(data, format="html", filepath="transaction_coverage.html")
```

### 8.3 常见问题和解决方案

**问题1: IllegalBin抛出异常中断测试**

SystemVerilog行为：记录警告，继续执行
Python行为：抛出 `IllegalBinHitError`

**解决方案:**
```python
try:
    txn.randomize()
except IllegalBinHitError as e:
    print(f"警告: 非法值被采样 - {e}")
    # 继续执行
```

**问题2: 范围语法混淆**

常见错误：`bins={"ranges": [0:255]}` （Python切片语法）

正确写法：`bins={"ranges": [[0, 255]]}` （嵌套列表）

**问题3: Cross覆盖率未计算**

原因：忘记将Cross添加到CoverGroup

**解决方案:**
```python
cross = Cross("name", ["cp1", "cp2"])
cg.add_cross(cross)  # 必须添加
```

**问题4: 覆盖率不增长**

可能原因：
- CoverGroup未添加到Randomizable
- 自动采样被禁用
- CoverPoint被禁用

**调试方法:**
```python
# 检查CoverGroup是否已添加
print(txn._covergroups)  # 应显示你的CoverGroup

# 检查自动采样状态
print(txn._coverage_auto_sample)  # 应为True

# 检查CoverPoint状态
cp = cg.get_coverpoint("name")
print(cp.is_enabled())  # 应为True
```

**问题5: WildcardBin不匹配**

常见错误：使用了错误的通配符格式

```python
# 错误：使用正则表达式语法
bins={"wildcards": ["8.*"]}  # 不支持

# 错误：混合使用
bins={"wildcards": ["8???", "9.*"]}  # 不一致

# 正确：统一使用?通配符
bins={"wildcards": ["8???", "9???"]}
```

---

## 9. 完整语法对照表（速查）

### 9.1 核心语法

| 功能 | SystemVerilog | Python装饰器 | Python传统API |
|:---|:---|:---|:---|
| **CoverGroup** | `covergroup name;` | `@covergroup("name")` | `CoverGroup("name")` |
| **采样事件** | `@(posedge clk)` | `sample_event="clk"` | - |
| **CoverPoint** | `coverpoint var;` | `@coverpoint("var")` | `CoverPoint("var", "var")` |
| **值bins** | `bins b = {1,2,3};` | `bins={"values": [1,2,3]}` | 同左 |
| **范围bins** | `bins b[] = {[0:255]};` | `bins={"ranges": [[0,255]]}` | 同左 |
| **通配符bins** | `wildcard bins b[] = {8???};` | `bins={"wildcards": ["8???"]}` | 同左 |
| **自动bins** | `auto_bin_max = 16` | `bins={"auto": 16}` | 同左 |
| **忽略bins** | `ignore_bins b = {0};` | `ignore_bins={"b": [0]}` | 同左 |
| **非法bins** | `illegal_bins b = {255};` | `illegal_bins={"b": [255]}` | 同左 |
| **Cross** | `cross cp1, cp2;` | `@cross("name", ["cp1","cp2"])` | `Cross("name", ["cp1","cp2"])` |
| **权重** | `option.weight = 2.0` | `weight=2.0` | 同左 |
| **手动采样** | `cg.sample();` | N/A | `cg.sample(**kwargs)` |
| **启用CP** | `cp.option.weight = 0` | `cp.disable()` | `cp.disable()` |

### 9.2 Bin类型

| Bin类型 | SystemVerilog语法 | Python参数 | 示例 |
|:---|:---|:---|:---|
| **Value** | `bins b = {1,2,3};` | `"values": [1,2,3]` | 精确值匹配 |
| **Range** | `bins b[] = {[0:255]};` | `"ranges": [[0,255]]` | 范围匹配 |
| **Wildcard** | `wildcard bins b[] = {8???};` | `"wildcards": ["8???"]` | 通配符匹配 |
| **Auto** | `auto_bin_max = 16` | `"auto": 16` | 自动分箱 |
| **Ignore** | `ignore_bins b = {0};` | `"ignore": [0]` | 忽略值 |
| **Illegal** | `illegal_bins b = {255};` | `"illegal": [255]` | 非法值 |

### 9.3 API方法

| 功能 | 方法 | 说明 |
|:---|:---|:---|
| **添加CP** | `cg.add_coverpoint(cp)` | 添加CoverPoint到CoverGroup |
| **添加Cross** | `cg.add_cross(cross)` | 添加Cross到CoverGroup |
| **获取覆盖率** | `cg.get_coverage()` | 返回覆盖率百分比 |
| **获取详情** | `cg.get_coverage_details()` | 返回详细信息字典 |
| **采样** | `cg.sample(**kwargs)` | 手动触发采样 |
| **启用/禁用CG** | `cg.enable_sampling()` / `disable_sampling()` | 控制CoverGroup采样 |
| **启用/禁用CP** | `cp.enable()` / `disable()` | 控制CoverPoint采样 |

---

## 附录

### A. 术语表

| 术语 | 说明 |
|:---|:---|
| **CoverGroup** | 覆盖率组，包含多个CoverPoint和Cross |
| **CoverPoint** | 覆盖点，定义单个变量的覆盖率 |
| **Bin** | 覆盖率箱，定义值的范围或模式 |
| **Cross** | 交叉覆盖率，多个CoverPoint的组合 |
| **采样** | 收集变量值并更新覆盖率统计 |
| **命中** | 值落入某个bin的范围 |
| **覆盖率** | 已命中bin数 / 总bin数 × 100% |

### B. 常见问题FAQ

**Q1: Python和SystemVerilog的覆盖率计算是否一致？**

A: 是的，使用相同的计算公式：`(已命中bin数 / 总bin数) × 100%`。但要注意：
- IgnoreBin不计入总bin数
- IllegalBin命中时会抛异常

**Q2: 如何迁移大型SystemVerilog覆盖率模型？**

A: 建议分步迁移：
1. 先迁移核心CoverPoint（value/range bins）
2. 再迁移复杂bin类型（wildcard/auto）
3. 最后迁移Cross覆盖

**Q3: Python覆盖率系统支持哪些SystemVerilog特性？**

A: v0.2.0支持：
- ✅ 所有6种bin类型
- ✅ Cross覆盖率（含过滤）
- ✅ 权重系统
- ✅ 多种报告格式
- ❌ binsof运算符（计划中）
- ❌ 条件覆盖率（计划中）

**Q4: 性能如何？**

A: v0.2.0性能：
- 简单采样：~246K次/秒
- 复杂采样：~84.5K次/秒
- 远超SystemVerilog仿真器

**Q5: 如何选择数据库后端？**

A: 根据场景选择：
- 单次测试：Memory数据库（快速）
- 多次累积：File数据库（持久化）
- 大规模数据：使用File + 定期合并

---

## 参考资源

- **项目主页**: https://github.com/EdaerCoser/EDA_UFMV
- **覆盖率README**: [coverage/README.md](../../coverage/README.md)
- **基础示例**: [examples/coverage/basic_coverage.py](../../examples/coverage/basic_coverage.py)
- **高级示例**: [examples/coverage/advanced_coverage.py](../../examples/coverage/advanced_coverage.py)
- **测试代码**: [tests/test_coverage/](../../tests/test_coverage/)
- **开发路线图**: [docs/development/ROADMAP.md](ROADMAP.md)

---

**文档版本**: v0.2.0
**最后更新**: 2026年3月1日
**维护者**: EDA_UFMV开发团队
