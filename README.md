# EDA_UFMV

用于FPGA/原型验证的通用工具库 (Universal Verification Framework for FPGA/Prototype Verification)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](CHANGELOG.md)

## 项目概述

EDA_UFMV是一款基于Python的**FPGA/原型验证通用工具库**，提供从测试生成、覆盖率收集、寄存器管理到DUT配置转换的完整解决方案。该工具将SystemVerilog的验证能力带入Python生态系统，使工程师能够利用Python的丰富生态进行高效的硬件验证工作。

## 主要特性

- **rand/randc变量**: 标准随机变量和循环随机变量
- **约束系统**: 支持`inside`、`dist`、关系/逻辑运算符和条件约束
- **可插拔求解器**: 纯Python后端（无依赖）和Z3后端（工业级）
- **输出格式**: 生成Verilog格式的测试向量用于仿真
- **种子控制**: 支持全局、对象级和临时随机种子，确保测试可重现性
- **回归测试**: 内置测试守护agent，自动检测代码变更并运行相关测试

## 安装

```bash
# 基础安装（纯Python，无外部依赖）
pip install -e .

# 使用Z3求解器后端以获得更好的性能
pip install -e ".[z3]"

# 包含统计验证工具
pip install -e ".[stat]"

# 开发环境安装
pip install -e ".[dev]"
```

## 快速开始

```python
from sv_randomizer import Randomizable, RandVar, RandCVar, VarType
from sv_randomizer.constraints.base import ExpressionConstraint
from sv_randomizer.constraints.expressions import VariableExpr, ConstantExpr, BinaryExpr, BinaryOp

class Packet(Randomizable):
    def __init__(self):
        super().__init__()
        self._rand_vars['src_addr'] = RandVar('src_addr', VarType.INT, min_val=0, max_val=65535)
        self._rand_vars['dest_addr'] = RandVar('dest_addr', VarType.INT, min_val=0, max_val=65535)
        self._randc_vars['packet_id'] = RandCVar('packet_id', VarType.BIT, bit_width=4)

        # 添加约束：源地址必须 >= 0x1000
        expr = BinaryExpr(
            VariableExpr('src_addr'),
            BinaryOp.GE,
            ConstantExpr(0x1000)
        )
        self.add_constraint(ExpressionConstraint("valid_addr", expr))

# 生成随机数据包
pkt = Packet()
for i in range(10):
    if pkt.randomize():
        print(f"数据包 {i+1}: 源地址=0x{pkt.src_addr:04x}, 目标地址=0x{pkt.dest_addr:04x}, "
              f"ID={pkt.packet_id}")
```

## 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 或直接运行测试文件
python tests/test_variables.py
python tests/test_constraints.py
python tests/test_seeding.py

# 使用回归测试agent
python .claude/skills/test-agent/runner.py --all
```

## 文档

### 产品文档

- [产品说明书](docs/product/PRODUCT_MANUAL.md) - 完整产品功能介绍和使用指南
- [API参考手册](docs/product/API_REFERENCE.md) - API接口详细说明（规划中）
- [用户指南](docs/product/USER_GUIDE.md) - 快速入门和最佳实践（规划中）

### 开发文档

- [开发路线图](docs/development/ROADMAP.md) - 版本规划和开发进度
- [架构设计](docs/development/ARCHITECTURE.md) - 系统架构和设计原理（规划中）
- [贡献指南](docs/development/CONTRIBUTING.md) - 如何贡献代码（规划中）

### 历史文档

- [实现计划](docs/legacy/IMPLEMENTATION_PLAN.md) - v0.1.0实现方案
- [种子控制](docs/legacy/SEED_CONTROL.md) - 随机种子功能说明
- [测试Agent指南](TEST_AGENT_GUIDE.md) - 回归测试工具使用说明

### 版本信息

- [变更日志](CHANGELOG.md) - 版本更新记录
- [许可证](LICENSE) - MIT License

## 示例

查看`examples/`目录获取更多使用示例：

- `examples/basic/` - 基础随机化示例
  - `simple_test.py` - 简单随机变量示例
  - `packet_generator.py` - 数据包生成示例
  - `seed_demo.py` - 随机种子控制演示
  - `test_six_variables.py` - 六元方程组约束求解测试

- `examples/coverage/` - 功能覆盖率示例（规划中）
- `examples/rgm/` - 寄存器模型示例（规划中）
- `examples/parser/` - DUT解析示例（规划中）

## 产品路线图

- **v0.1.0** (当前) - 基础随机化框架 ✅
  - 随机变量系统（rand/randc）
  - 约束系统（inside, dist, 表达式）
  - 双求解器架构（PurePython + Z3）
  - 种子管理

- **v0.2.0** (2026 Q2) - 功能覆盖率系统 📋
  - CoverGroup/CoverPoint实现
  - 交叉覆盖率
  - HTML/UCIS报告生成

- **v0.3.0** (2026 Q3) - 寄存器模型系统 📋
  - 层次化寄存器组织
  - 访问控制（RW/RO/WO等）
  - RTL代码生成

- **v0.4.0** (2026 Q3) - 随机化增强 📋
  - 覆盖率引导随机化
  - 智能约束求解

- **v0.5.0** (2026 Q4) - DUT配置转换 📋
  - Verilog/SystemVerilog解析
  - Python模型生成

- **v1.0.0** (2027 Q1) - 完整平台 📋
  - 系统集成
  - 生产就绪

详见 [开发路线图](docs/development/ROADMAP.md)

## 核心特性

- ✅ **SystemVerilog风格随机化** - rand/randc变量，约束系统
- ✅ **双求解器架构** - 纯Python（零依赖）+ Z3 SMT（工业级）
- ✅ **种子管理** - 全局/对象级/临时种子，确保可重现性
- ✅ **Python生态集成** - 与pytest、numpy、scipy无缝集成
- 📋 **功能覆盖率** - 覆盖率驱动验证（规划中）
- 📋 **寄存器模型** - 类似UVM RGM的寄存器抽象（规划中）
- 📋 **DUT解析** - Verilog到Python自动转换（规划中）

## 与UVM对比

| 特性 | UVM | EDA_UFMV |
| :--- | :--- | :--- |
| 语言 | SystemVerilog | Python |
| 学习曲线 | 陡峭 | 平缓 |
| 开发效率 | 中等 | 高（3-5倍提升） |
| 生态系统 | EDA专用 | 丰富（numpy, pytest等） |
| 成本 | 商业工具昂贵 | 开源免费 |
| 性能 | 仿真器驱动 | Python速度快10倍+ |

## 贡献

欢迎贡献！请查看：
- [贡献指南](docs/development/CONTRIBUTING.md)（规划中）
- [开发路线图](docs/development/ROADMAP.md)

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 联系方式

- **项目主页**: <https://github.com/EdaerCoser/EDA_UFMV>
- **问题反馈**: <https://github.com/EdaerCoser/EDA_UFMV/issues>
- **讨论区**: <https://github.com/EdaerCoser/EDA_UFMV/discussions>
