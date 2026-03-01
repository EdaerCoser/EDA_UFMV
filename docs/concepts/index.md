# 概念参考

概念文档深入解释EDA_UFMV的技术实现细节，帮助您理解框架是如何工作的。

## 核心概念

### [SV→Python概念映射](sv-to-python-mapping.md)
**必读** - SystemVerilog到Python的完整对照表

如果你熟悉SystemVerilog/UVM，从这里开始：
- 随机化概念映射
- 覆盖率概念映射
- 寄存器模型概念映射
- 关键差异说明

## 深入主题

### [随机化深入](randomization-deep-dive.md)
- 双求解器架构（PurePython + Z3）
- 约束AST系统
- 约束求解算法
- 设计模式应用

### [覆盖率深入](coverage-deep-dive.md)
- CoverGroup/CoverPoint/Cross层次
- 6种Bin类型实现
- 数据库后端设计
- 报告生成器架构

### [RGM深入](rgm-deep-dive.md)
- Field/Register/RegisterBlock设计
- 15种访问类型实现
- 硬件适配器模式
- 代码生成器设计

---

## 阅读建议

- **场景文档** → "如何使用"
- **概念文档** → "如何工作"
- **API文档** → "完整接口"

建议先阅读场景文档解决问题，再查阅概念文档理解原理。
