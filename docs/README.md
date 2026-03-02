# EDA_UFVM 文档导航

欢迎来到EDA_UFVM项目文档！本文档帮助你快速找到所需信息。

---

## 快速导航

### 我是新用户 → 开始这里

- 📖 [项目概述](../README.md) - 了解EDA_UFVM是什么
- 💡 [示例代码](../examples/) - 从示例中学习
- ✨ [功能清单](product/features.md) - 查看完整功能列表

### 我想了解产品 → 产品文档

- 📋 [产品概述](product/overview.md) - 产品定位和核心价值
- ✨ [功能清单](product/features.md) - 完整功能列表
- 🎯 [应用场景](product/use-cases.md) - 典型使用案例
- 🔄 [竞品对比](product/comparison.md) - 与UVM等工具对比
- 📖 [RGM用户指南](product/RGM_GUIDE.md) - 寄存器模型系统完整指南

### 我想使用系统 → 场景化文档

- 🎲 [生成随机测试激励](scenarios/01-generate-random.md) - 随机化快速上手
- 📊 [收集功能覆盖率](scenarios/02-collect-coverage.md) - 覆盖率快速上手
- 🗄️ [创建寄存器模型](scenarios/03-create-regmodel.md) - RGM快速上手
- 🔄 [从SystemVerilog迁移](scenarios/04-migrate-from-sv.md) - 迁移指南
- 🤖 [自动化SV→Python转换](scenarios/05-automate-conversion.md) - 转换器使用
- 📋 [完整验证流程](scenarios/06-complete-workflow.md) - 端到端示例

**更多场景**: [场景索引](scenarios/)

### 我想深入理解 → 概念参考

- 🔄 [SystemVerilog→Python映射表](concepts/sv-to-python-mapping.md) - **必读**
- 🎲 [随机化深入](concepts/randomization-deep-dive.md) - 框架、算法、设计模式
- 📊 [覆盖率深入](concepts/coverage-deep-dive.md) - 架构、实现细节
- 🗄️ [RGM深入](concepts/rgm-deep-dive.md) - 寄存器模型深度

### 我想查阅API → 技术参考

- 🎲 [随机化完整参考](reference/randomization.md) - API详细说明
- 📊 [覆盖率迁移详细参考](reference/coverage/migration.md) - SV迁移详解
- 🤖 [SV→Python转换器](reference/sv-converter.md) - 转换工具文档
- 🗄️ [SSH适配器指南](reference/rgm/SSH_ADAPTER_GUIDE.md) - 远程访问指南

### 我想参与开发 → 开发文档

- 🗺️ [开发路线图](development/ROADMAP.md) - 版本规划和里程碑
- 🏗️ [架构设计](development/ARCHITECTURE.md) - 系统架构说明
- 🤝 [贡献指南](development/CONTRIBUTING.md) - 如何贡献代码
- 🧪 [测试指南](development/TEST_GUIDE.md) - 完整的测试体系文档
- 📜 [变更历史](../CHANGELOG.md) - 版本更新记录
- 📝 [文档维护指南](development/DOCUMENTATION_GUIDELINES.md) - 文档编写规范

---

## 文档结构

```
docs/
├── scenarios/         # 场景化文档 - 按"我想做什么"组织
├── concepts/          # 概念参考 - 深入技术原理
├── reference/         # 技术参考 - 完整API文档
│   ├── coverage/      # 覆盖率专题
│   └── rgm/          # RGM专题
├── product/           # 产品文档 - 概述、功能、场景
├── development/       # 开发文档 - 路线图、架构
│   └── migration/     # 迁移文档
└── legacy/           # 历史文档 - 归档资料
```

---

## 按任务查找

| 我想... | 查看文档 |
|:---|:---|
| 第一次使用EDA_UFVM | [项目概述](../README.md) → [场景文档](scenarios/) |
| 生成随机测试激励 | [场景1：生成随机激励](scenarios/01-generate-random.md) |
| 收集功能覆盖率 | [场景2：收集覆盖率](scenarios/02-collect-coverage.md) |
| 创建寄存器模型 | [场景3：创建寄存器模型](scenarios/03-create-regmodel.md) |
| 从SystemVerilog迁移 | [场景4：从SV迁移](scenarios/04-migrate-from-sv.md) |
| 了解SV→Python映射 | [SV→Python映射表](concepts/sv-to-python-mapping.md) |
| 查看API详细说明 | [技术参考](reference/) |
| SSH访问FPGA板卡 | [SSH适配器指南](reference/rgm/SSH_ADAPTER_GUIDE.md) |
| 运行或编写测试 | [测试指南](development/TEST_GUIDE.md) |
| 报告问题或建议 | [贡献指南](development/CONTRIBUTING.md) |
| 了解新版本特性 | [变更日志](../CHANGELOG.md) |
| 贡献文档 | [文档维护指南](development/DOCUMENTATION_GUIDELINES.md) |

---

## 版本信息

- **当前版本**: v0.3.0
- **最新更新**: 2026年3月1日
- **文档状态**: 持续更新中

---

## 获取帮助

- 📧 [问题反馈](https://github.com/EdaerCoser/EDA_UFVM/issues) - 报告bug或功能请求
- 💬 [讨论区](https://github.com/EdaerCoser/EDA_UFVM/discussions) - 交流使用经验
- 📖 [完整文档](../README.md) - 返回项目主页

---

## 文档维护

本文档遵循 [文档维护指南](development/DOCUMENTATION_GUIDELINES.md)。

如发现文档问题，请：

1. 检查是否有已存在的 issue
2. 提交新的 issue 或 pull request
3. 参考文档指南进行修改
