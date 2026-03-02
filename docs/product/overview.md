# 产品概述

**版本**: v0.2.0
**更新日期**: 2026年3月1日

---

## 产品定位

EDA_UFVM是一款基于Python的**FPGA/原型验证通用工具库**，提供从测试生成、覆盖率收集、寄存器管理到DUT配置转换的完整解决方案。

该工具填补了Python生态中硬件验证工具的空白，将SystemVerilog的验证能力带入Python生态系统，使工程师能够利用Python的丰富生态进行高效的硬件验证工作。

---

## 目标用户

- **FPGA验证工程师**：快速生成测试向量，进行原型验证
- **IC验证工程师**：功能验证、覆盖率收集、回归测试
- **硬件设计工程师**：上板测试、现场配置验证
- **算法工程师**：硬件算法原型验证

---

## 核心价值

| 特性 | 优势 |
|------|------|
| **Python生态集成** | 与pytest、numpy、scipy、matplotlib无缝集成 |
| **快速开发** | 比SystemVerilog/UVM学习曲线更平缓，开发效率提升3-5倍 |
| **高可扩展性** | 模块化设计，易于扩展和定制 |
| **工具链互操作** | 支持VCS、Verilator、Vivado等主流EDA工具 |
| **开源免费** | MIT许可证，无商业工具成本压力 |

---

## 产品架构

EDA_UFVM采用模块化设计，核心包含两个独立的顶级模块：

```
EDA_UFVM/
├── sv_randomizer/     # 随机化框架
│   ├── 核心随机化 (rand/randc)
│   ├── 约束系统
│   └── 双求解器架构
│
└── coverage/          # 覆盖率系统
    ├── CoverGroup/CoverPoint
    ├── 6种Bin类型
    ├── Cross覆盖率
    ├── 报告生成
    └── 数据库持久化
```

### v0.2.0 已完成功能

- ✅ 随机化与约束系统 (v0.1.0)
  - rand/randc变量
  - 丰富约束类型 (inside, dist, 关系/逻辑/蕴含运算)
  - 双求解器 (PurePython/Z3)
  - 种子管理

- ✅ 功能覆盖率系统 (v0.2.0)
  - CoverGroup/CoverPoint/Cross
  - 6种Bin类型 (Value, Range, Wildcard, Auto, Ignore, Illegal)
  - 多格式报告 (HTML, JSON, UCIS)
  - 数据库持久化 (Memory, File)

### 规划中的功能

- 📋 寄存器模型系统 (v0.3.0)
- 📋 覆盖率引导随机化 (v0.4.0)
- 📋 DUT配置转换 (v0.5.0)

---

## 与竞品对比

详见 [竞品对比文档](comparison.md)

---

## 快速链接

- 🚀 [快速开始](../user/quick-start.md)
- ✨ [功能清单](features.md)
- 🎯 [应用场景](use-cases.md)
- 🔄 [与UVM对比](comparison.md)
- 📖 [使用指南](../guides/)
