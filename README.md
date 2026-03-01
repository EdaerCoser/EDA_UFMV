# EDA_UFMV

<div align="center">

**用于FPGA/原型验证的通用工具库**

[Universal Verification Framework for FPGA/Prototype Verification]

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-141%20passed-success.svg)](tests/test_coverage/)

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

### 当前版本 (v0.2.0)

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

### 规划中功能

- 📋 寄存器模型系统 (v0.3.0)
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
from sv_randomizer import Randomizable, rand, constraint

class Packet(Randomizable):
    @rand(bit_width=16, min_val=0, max_val=65535)
    def src_addr(self): return 0

    @rand(bit_width=16, min_val=0, max_val=65535)
    def dest_addr(self): return 0

    @constraint("valid_addr", "src_addr >= 0x1000 && src_addr != dest_addr")
    def valid_addr_c(self): pass

# 使用
pkt = Packet()
for i in range(5):
    pkt.randomize()
    print(f"src=0x{pkt.src_addr:04x}, dst=0x{pkt.dest_addr:04x}")
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

**测试覆盖**: 141个测试，100%通过率

---

## 文档

### 用户文档
- 📖 [产品概述](docs/product/overview.md)
- 🚀 [快速开始](docs/user/quick-start.md)
- ✨ [功能清单](docs/product/features.md)
- 🎯 [应用场景](docs/product/use-cases.md)

### 使用指南
- 🎲 [随机化系统](docs/guides/randomization.md)
- 📊 [覆盖率系统](docs/guides/coverage/)
  - [覆盖率概述](docs/guides/coverage/README.md)
  - [SystemVerilog迁移指南](docs/guides/coverage/systemverilog-migration.md)

### 开发文档
- 🗺️ [开发路线图](docs/development/ROADMAP.md)
- 🏗️ [架构设计](docs/development/ARCHITECTURE.md)

### 版本信息
- 📝 [变更日志](CHANGELOG.md)
- ⚖️ [许可证](LICENSE)

**完整文档导航**: [docs/README.md](docs/)

---

## 示例

| 示例 | 说明 | 功能点 |
|:---|:---|:---|
| [simple_test.py](examples/rand/simple_test.py) | 简单随机变量 | 基础rand/randc |
| [packet_generator.py](examples/rand/packet_generator.py) | 数据包生成 | 约束系统 |
| [basic_coverage.py](examples/coverage/basic_coverage.py) | 基础覆盖率 | CoverGroup/CoverPoint |
| [advanced_coverage.py](examples/coverage/advanced_coverage.py) | 高级覆盖率 | Bin类型/Cross |

更多示例请参阅 [examples/](examples/)

---

## 产品路线图

| 版本 | 功能 | 状态 |
|:---|:---|:---|
| v0.1.0 | 随机化框架 | ✅ 已发布 |
| v0.2.0 | 功能覆盖率系统 | ✅ 已发布 |
| v0.3.0 | 寄存器模型系统 | 📋 规划中 |
| v0.4.0 | 覆盖率引导随机化 | 📋 规划中 |
| v0.5.0 | DUT配置转换 | 📋 规划中 |
| v1.0.0 | 完整平台 | 📋 规划中 |

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
