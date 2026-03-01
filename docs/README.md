# EDA_UFMV 文档导航

欢迎来到EDA_UFMV项目文档！本文档帮助你快速找到所需信息。

---

## 快速导航

### 我是新用户 → 开始这里

- 📖 [项目概述](../README.md) - 了解EDA_UFMV是什么
- 💡 [示例代码](../examples/) - 从示例中学习
- ✨ [功能清单](product/features.md) - 查看完整功能列表

### 我想了解产品 → 产品文档

- 📋 [产品概述](product/overview.md) - 产品定位和核心价值
- ✨ [功能清单](product/features.md) - 完整功能列表
- 🎯 [应用场景](product/use-cases.md) - 典型使用案例
- 🔄 [竞品对比](product/comparison.md) - 与UVM等工具对比
- 📖 [RGM用户指南](product/RGM_GUIDE.md) - 寄存器模型系统完整指南

### 我想使用系统 → 使用指南

- 🎲 [随机化系统](guides/randomization.md) - rand/randc变量、约束
- 📊 [覆盖率系统](guides/coverage/) - 功能覆盖率完整指南
  - [覆盖率概述](guides/coverage/README.md)
  - [SystemVerilog迁移指南](guides/coverage/systemverilog-migration.md)
  - [覆盖率API参考](guides/coverage/api-reference.md)
- 🗄️ [寄存器模型系统](guides/rgm/) - RGM使用指南
  - [RGM概述](guides/rgm/README.md)
  - [SSH适配器指南](guides/rgm/SSH_ADAPTER_GUIDE.md)

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
├── product/           # 产品文档 - 概述、功能、场景
├── guides/            # 使用指南 - 系统使用教程
│   ├── coverage/      # 覆盖率专题
│   └── rgm/          # RGM专题
├── development/       # 开发文档 - 路线图、架构
│   └── history/      # 开发历史记录
└── legacy/           # 历史文档 - 归档资料
```

---

## 按任务查找

| 我想... | 查看文档 |
|:---|:---|
| 第一次使用EDA_UFMV | [项目概述](../README.md) → [示例代码](../examples/) |
| 从SystemVerilog迁移 | [SV迁移指南](guides/coverage/systemverilog-migration.md) |
| 使用随机化功能 | [随机化系统](guides/randomization.md) |
| 添加覆盖率 | [覆盖率系统](guides/coverage/) |
| 使用寄存器模型 | [RGM用户指南](product/RGM_GUIDE.md) |
| SSH访问FPGA板卡 | [SSH适配器指南](guides/rgm/SSH_ADAPTER_GUIDE.md) |
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

- 📧 [问题反馈](https://github.com/EdaerCoser/EDA_UFMV/issues) - 报告bug或功能请求
- 💬 [讨论区](https://github.com/EdaerCoser/EDA_UFMV/discussions) - 交流使用经验
- 📖 [完整文档](../README.md) - 返回项目主页

---

## 文档维护

本文档遵循 [文档维护指南](development/DOCUMENTATION_GUIDELINES.md)。

如发现文档问题，请：

1. 检查是否有已存在的 issue
2. 提交新的 issue 或 pull request
3. 参考文档指南进行修改
