# EDA_UFMV 文档导航

欢迎来到EDA_UFMV项目文档！本文档帮助你快速找到所需信息。

---

## 快速导航

### 我是新用户 → 开始这里

- 📖 [项目概述](../README.md) - 了解EDA_UFMV是什么
- 🚀 [快速开始](user/quick-start.md) - 5分钟上手指南
- 📦 [安装指南](user/installation.md) - 安装和配置
- 💡 [示例代码](../examples/) - 学习最佳实践

### 我想了解产品 → 产品文档

- 📋 [产品概述](product/overview.md) - 产品定位和核心价值
- ✨ [功能清单](product/features.md) - 完整功能列表
- 🎯 [应用场景](product/use-cases.md) - 典型使用案例
- 🔄 [竞品对比](product/comparison.md) - 与UVM等工具对比

### 我想使用系统 → 使用指南

- 🎲 [随机化系统](guides/randomization.md) - rand/randc变量、约束
- 📊 [覆盖率系统](guides/coverage/) - 功能覆盖率完整指南
  - [覆盖率概述](guides/coverage/README.md)
  - [SystemVerilog迁移指南](guides/coverage/systemverilog-migration.md)
  - [覆盖率API参考](guides/coverage/api-reference.md)
- ⚖️ [约束系统](guides/constraints.md) - 约束表达式和求解
- 🌱 [种子管理](guides/seeding.md) - 可复现的随机化

### 我想参与开发 → 开发文档

- 🗺️ [开发路线图](development/ROADMAP.md) - 版本规划和里程碑
- 🏗️ [架构设计](development/architecture.md) - 系统架构说明
- 🤝 [贡献指南](development/contributing.md) - 如何贡献代码
- 📜 [变更历史](../CHANGELOG.md) - 版本更新记录

### 我想查找API → API参考

- 🔧 [随机化API](api/randomization.md) - Randomizable、RandVar等
- 📊 [覆盖率API](api/coverage.md) - CoverGroup、CoverPoint等
- ⚖️ [约束API](api/constraints.md) - 约束表达式和求解器

---

## 文档结构

```
docs/
├── user/              # 用户文档 - 快速开始、安装
├── product/           # 产品文档 - 概述、功能、场景
├── guides/            # 使用指南 - 系统使用教程
│   └── coverage/      # 覆盖率专题
├── development/       # 开发文档 - 路线图、架构
├── api/              # API参考 - 接口文档
└── legacy/           # 历史文档 - 归档资料
```

---

## 按任务查找

| 我想... | 查看文档 |
|:---|:---|
| 第一次使用EDA_UFMV | [快速开始](user/quick-start.md) |
| 从SystemVerilog迁移 | [SV迁移指南](guides/coverage/systemverilog-migration.md) |
| 了解覆盖率功能 | [覆盖率系统](guides/coverage/) |
| 添加约束 | [约束系统](guides/constraints.md) |
| 报告问题或建议 | [贡献指南](development/contributing.md) |
| 了解新版本特性 | [变更日志](../CHANGELOG.md) |

---

## 版本信息

- **当前版本**: v0.2.0
- **最新更新**: 2026年3月1日
- **文档状态**: 持续更新中

---

## 获取帮助

- 📧 [问题反馈](https://github.com/EdaerCoser/EDA_UFMV/issues) - 报告bug或功能请求
- 💬 [讨论区](https://github.com/EdaerCoser/EDA_UFMV/discussions) - 交流使用经验
- 📖 [完整文档](../README.md) - 返回项目主页
