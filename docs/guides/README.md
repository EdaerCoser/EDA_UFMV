# 使用指南 (已迁移)

> **⚠️ 文档结构已更新**
>
> 本目录已迁移到新的三层文档架构。请使用以下链接访问最新文档：

---

## 📚 新文档结构

### 快速上手 (scenarios/)

按"我想做什么"快速找到解决方案：

- 🎲 [生成随机激励](../scenarios/01-generate-random.md) - 随机化快速上手
- 📊 [收集功能覆盖率](../scenarios/02-collect-coverage.md) - 覆盖率收集入门
- 🗄️ [创建寄存器模型](../scenarios/03-create-regmodel.md) - RGM快速指南
- 🔄 [从SystemVerilog迁移](../scenarios/04-migrate-from-sv.md) - SV到Python迁移
- 🤖 [自动化SV→Python转换](../scenarios/05-automate-conversion.md) - 使用转换工具
- 📋 [完整验证流程](../scenarios/06-complete-workflow.md) - 端到端示例

### 深入理解 (concepts/)

理解技术原理和设计思想：

- 🔄 [SystemVerilog→Python映射表](../concepts/sv-to-python-mapping.md) - **必读**
- 🎲 [随机化深入](../concepts/randomization-deep-dive.md) - 框架、算法、设计模式
- 📊 [覆盖率深入](../concepts/coverage-deep-dive.md) - 架构、实现细节
- 🗄️ [RGM深入](../concepts/rgm-deep-dive.md) - 寄存器模型深度

### 技术参考 (reference/)

完整API文档和详细指南：

- 🎲 [随机化完整参考](../reference/randomization.md)
- 📊 [覆盖率迁移详细参考](../reference/coverage/migration.md)
- 🤖 [SV→Python转换器](../reference/sv-converter.md)
- 🗄️ [SSH适配器指南](../reference/rgm/SSH_ADAPTER_GUIDE.md)

---

## 🔗 URL映射表

| 旧路径 | 新路径 |
|:---|:---|
| `guides/randomization.md` | → [scenarios/01](../scenarios/01-generate-random.md) 或 [reference/](../reference/randomization.md) |
| `guides/coverage/systemverilog-migration.md` | → [concepts/](../concepts/sv-to-python-mapping.md) 或 [scenarios/02](../scenarios/02-collect-coverage.md) |
| `guides/sv-to-python-guide.md` | → [reference/sv-converter.md](../reference/sv-converter.md) |
| `guides/rgm/SSH_ADAPTER_GUIDE.md` | → [reference/rgm/](../reference/rgm/SSH_ADAPTER_GUIDE.md) |

---

## 📖 迁移说明

EDA_UFMV文档已从单一指南结构重构为**三层文档架构**：

- **scenarios/** - 任务导向（快速上手）"我想做什么"
- **concepts/** - 概念深入（理解原理）"如何工作"
- **reference/** - 技术参考（查阅细节）"完整接口"

详见：[文档迁移指南](../../DOCUMENTATION_MIGRATION.md)

---

**返回**: [文档主页](../README.md) | [项目README](../../README.md)
