# EDA_UFMV

<div align="center">

**用于FPGA/原型验证的通用工具库**

[Universal Verification Framework for FPGA/Prototype Verification]

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-186%2B%20passed-success.svg)](tests/test_rgm/)

[快速开始](#快速开始) • [文档](docs/) • [示例](examples/) • [贡献](#贡献)

</div>

---

## 项目概述

**EDA_UFMV** 是一款基于Python的FPGA/原型验证通用工具库，提供从测试生成、覆盖率收集、寄存器管理到DUT配置转换的完整解决方案。该工具将SystemVerilog的验证能力带入Python生态系统，使工程师能够利用Python的丰富生态进行高效的硬件验证工作。

### 核心价值

| 特性 | 优势 |
|:---|:---|
| **Python生态集成** | 与pytest、numpy、scipy、matplotlib无缝集成 |
| **快速开发** | 比SystemVerilog/UVM学习曲线更平缓，开发效率提升3-5倍 |
| **高可扩展性** | 模块化设计，易于扩展和定制 |
| **工具链互操作** | 支持VCS、Verilator、Vivado等主流EDA工具 |
| **开源免费** | MIT许可证，无商业工具成本压力 |

---

## 主要特性

### 当前版本 (v0.3.0)

**核心随机化模块** (`sv_randomizer`):

- ✅ rand/randc变量 - 标准随机变量和循环随机变量
- ✅ 约束系统 - 支持`inside`、`dist`、关系/逻辑运算符
- ✅ 双求解器架构 - 纯Python后端 + Z3后端（工业级）
- ✅ 种子管理 - 全局/对象级/临时种子
- ✅ 字符串约束表达式 - 支持类似SystemVerilog的语法

**功能覆盖率系统** (`coverage` - 独立模块):

- ✅ CoverGroup/CoverPoint - SystemVerilog风格的覆盖率定义
- ✅ 6种Bin类型 - 值/范围/通配符/自动/忽略/非法
- ✅ Cross覆盖 - 多变量交叉覆盖率
- ✅ 多格式报告 - HTML/JSON/UCIS
- ✅ 数据库后端 - 内存/文件双后端

**寄存器模型系统** (`rgm` - 独立模块):

- ✅ 层次化寄存器建模 - Field/Register/RegisterBlock
- ✅ 15种访问类型 - RW, RO, WO, W1C, W1S, W0C, W0S, RC, RS等
- ✅ UVM兼容接口 - set/get/update/mirror/poke/peek
- ✅ 硬件适配器 - AXI, APB, UART, SSH远程访问
- ✅ 代码生成器 - Verilog RTL, C头文件, Python模型

**SV→Python转换器** (`sv_to_python` - 独立工具):

- ✅ SystemVerilog解析 - 提取UVM寄存器操作和任务
- ✅ Python代码生成 - 自动生成Python等价代码
- ✅ 命令行工具 - `sv-to-python` CLI支持批量转换
- ✅ IDE集成 - 支持从SV测试代码迁移到Python

### 规划中功能

- 📋 覆盖率引导随机化 (v0.4.0)
- 📋 DUT配置转换 (v0.5.0)

---

## 快速开始

### 安装

```bash
git clone https://github.com/EdaerCoser/EDA_UFMV.git
cd EDA_UFMV
pip install -e .
```

详细安装说明请参阅 [安装指南](docs/user/installation.md)

### 第一个示例

```python
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint

# 定义类型注解
src_addr_rand = rand(int)(bits=16, min=0, max=65535)
dest_addr_rand = rand(int)(bits=16, min=0, max=65535)
packet_id_randc = randc(int)(bits=4)

class Packet(Randomizable):
    # 使用类型注解定义变量
    src_addr: src_addr_rand
    dest_addr: dest_addr_rand
    packet_id: packet_id_randc

    # 使用原生Python表达式定义约束
    @constraint
    def valid_addr(self):
        return self.src_addr >= 0x1000 and self.src_addr != self.dest_addr

# 使用
pkt = Packet()
for i in range(5):
    pkt.randomize()
    print(f"src=0x{pkt.src_addr:04x}, dst=0x{pkt.dest_addr:04x}, id={pkt.packet_id}")
```

更多示例请参阅:
- [快速开始指南](docs/user/quick-start.md)
- [示例代码](examples/)

---

## 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行覆盖率系统测试
python run_coverage_tests.py

# 使用回归测试agent
python .claude/skills/test-agent/runner.py --all
```

**测试覆盖**: 186+个测试通过（覆盖率系统141 + RGM 186+）

---

## 文档

### 📚 文档架构

EDA_UFMV采用**三层文档架构**，帮助您快速找到所需信息：

```
docs/
├── scenarios/         # 场景化文档 - 按"我想做什么"组织（推荐新手）
├── concepts/          # 概念参考 - 深入技术原理（理解原理）
├── reference/         # 技术参考 - 完整API文档（查阅细节）
├── product/           # 产品文档 - 概述、功能、场景
└── development/       # 开发文档 - 路线图、架构
```

---

### 🎯 场景化文档（推荐新手）

按"我想做什么"快速找到解决方案：

- 🎲 [生成随机测试激励](docs/scenarios/01-generate-random.md) - 生成符合约束的随机数据
- 📊 [收集功能覆盖率](docs/scenarios/02-collect-coverage.md) - 测量验证完整性
- 🗄️ [创建寄存器模型](docs/scenarios/03-create-regmodel.md) - DUT配置管理
- 🔄 [从SystemVerilog迁移](docs/scenarios/04-migrate-from-sv.md) - SV到Python迁移指南
- 🤖 [自动化SV→Python转换](docs/scenarios/05-automate-conversion.md) - 使用转换工具
- 📋 [完整验证流程](docs/scenarios/06-complete-workflow.md) - 端到端示例

**完整场景索引**: [docs/scenarios/](docs/scenarios/)

---

### 🧠 概念参考

深入理解技术原理：

- 🔄 [SystemVerilog→Python映射表](docs/concepts/sv-to-python-mapping.md) - **必读**
- 🎲 [随机化深入](docs/concepts/randomization-deep-dive.md) - 框架、算法、设计模式
- 📊 [覆盖率深入](docs/concepts/coverage-deep-dive.md) - 架构、实现细节
- 🗄️ [RGM深入](docs/concepts/rgm-deep-dive.md) - 寄存器模型深度

---

### 📖 技术参考

完整API文档和详细指南：

- 🎲 [随机化完整参考](docs/reference/randomization.md)
- 📊 [覆盖率迁移详细参考](docs/reference/coverage/migration.md)
- 🤖 [SV→Python转换器](docs/reference/sv-converter.md)
- 🗄️ [SSH适配器指南](docs/reference/rgm/SSH_ADAPTER_GUIDE.md)

---

### 📋 产品文档

- 📖 [产品概述](docs/product/overview.md) - 产品定位和核心价值
- ✨ [功能清单](docs/product/features.md) - 完整功能列表
- 🎯 [应用场景](docs/product/use-cases.md) - 典型使用案例
- 🔄 [与UVM对比](docs/product/comparison.md) - 竞品对比

---

### 👨‍💻 开发文档

- 🗺️ [开发路线图](docs/development/ROADMAP.md) - 版本规划和里程碑
- 🏗️ [架构设计](docs/development/ARCHITECTURE.md) - 系统架构说明

### 版本信息
- 📝 [变更日志](CHANGELOG.md)
- ⚖️ [许可证](LICENSE)

**完整文档导航**: [docs/README.md](docs/)

---

## 示例

### 随机化示例

| 示例 | 说明 | 功能点 |
|:---|:---|:---|
| [simple_test.py](examples/rand/simple_test.py) | 简单随机变量 | 基础rand/randc |
| [packet_generator.py](examples/rand/packet_generator.py) | 数据包生成 | 约束系统 |
| [seed_demo.py](examples/rand/seed_demo.py) | 种子控制 | 可重现性 |
| [test_six_variables.py](examples/rand/test_six_variables.py) | 复杂约束 | 约束求解 |
| [solve_inequalities.py](examples/rand/solve_inequalities.py) | 范围约束 | Inside约束 |

### 覆盖率示例

| 示例 | 说明 | 功能点 |
|:---|:---|:---|
| [basic_coverage.py](examples/coverage/basic_coverage.py) | 基础覆盖率 | CoverGroup/CoverPoint |
| [advanced_coverage.py](examples/coverage/advanced_coverage.py) | 高级覆盖率 | Bin类型/Cross |

### 寄存器模型示例

| 示例 | 说明 | 功能点 |
|:---|:---|:---|
| [basic_rgm_example.py](examples/rgm/basic_rgm_example.py) | 基础RGM | Field/Register/RegisterBlock |
| [code_generator_example.py](examples/rgm/code_generator_example.py) | 代码生成 | Verilog/C/Python生成 |

更多示例请参阅:
- [随机化示例](examples/rand/) - 完整的随机化系统示例
- [覆盖率示例](examples/coverage/) - 完整的覆盖率系统示例
- [寄存器模型示例](examples/rgm/) - 完整的RGM系统示例

---

## 产品路线图

| 版本 | 功能 | 状态 |
|:---|:---|:---|
| v0.1.0 | 随机化框架 | ✅ 已发布 |
| v0.2.0 | 功能覆盖率系统 | ✅ 已发布 |
| v0.3.0 | 寄存器模型系统 | ✅ 已发布 |
| v0.4.0 | 覆盖率引导随机化 | 📋 规划中 |
| v0.5.0 | DUT配置转换 | 📋 规划中 |
| v1.0.0 | 完整平台 | 📋 规划中 |

**附注**: SV→Python转换器 (`sv_to_python`) 是独立的工具模块 (v0.1.0)，用于SystemVerilog测试代码迁移，不属于主版本序列。

详见 [开发路线图](docs/development/ROADMAP.md)

---

## 性能指标

| 指标 | 数值 | 说明 |
|:---|:---|:---|
| 随机化速度 | ~10,000次/秒 | 纯Python求解器 |
| 覆盖率采样 | ~246K次/秒 | 简单场景 (<10 bins) |
| 内存占用 | <10MB | 100个变量 |
| 相比UVM | 10倍+ faster | Python vs SV仿真器 |

---

## 与UVM对比

EDA_UFMV相比UVM具有显著优势：
- **语言**: Python (生态丰富) vs SystemVerilog (EDA专用)
- **学习曲线**: 平缓 (Python基础) vs 陡峭 (OOP+验证方法学)
- **开发效率**: 3-5倍提升
- **成本**: 开源免费 vs 商业工具昂贵

详细对比请参阅 [竞品对比](docs/product/comparison.md)

---

## 贡献

欢迎贡献！请查看 [开发路线图](docs/development/ROADMAP.md)

### 贡献方式

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 许可证

本项目采用 **MIT License** - 详见 [LICENSE](LICENSE) 文件。

---

## 联系方式

- **项目主页**: https://github.com/EdaerCoser/EDA_UFMV
- **问题反馈**: https://github.com/EdaerCoser/EDA_UFMV/issues
- **讨论区**: https://github.com/EdaerCoser/EDA_UFMV/discussions

---

<div align="center">

**[⬆ 返回顶部](#eda_ufmv)**

Made with ❤️ by EDA_UFMV Team

</div>
