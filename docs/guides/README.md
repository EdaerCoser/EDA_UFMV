# 使用指南

本部分包含EDA_UFMV各系统的详细使用指南。

---

## 指南列表

### 核心系统指南

- 🎲 [随机化系统](randomization.md)
  - rand/randc变量
  - 约束定义和使用
  - 种子管理
  - 求解器选择

- 📊 [覆盖率系统](coverage/)
  - [覆盖率概述](coverage/README.md) - 覆盖率系统架构
  - [SystemVerilog迁移指南](coverage/systemverilog-migration.md) - SV到Python语法对照
  - [覆盖率API参考](coverage/api-reference.md) - 完整API文档

- ⚖️ [约束系统](constraints.md)
  - 约束表达式
  - 关系运算和逻辑运算
  - inside和dist约束

- 🌱 [种子管理](seeding.md)
  - 全局种子设置
  - 对象级种子
  - 可复现的随机化

---

## 按主题查找

### 随机化相关

| 主题 | 指南 | 章节 |
|:---|:---|:---|
| 定义随机变量 | [随机化系统](randomization.md) | 变量定义 |
| 添加约束 | [约束系统](constraints.md) | 约束类型 |
| 控制随机化 | [随机化系统](randomization.md) | pre/post_randomize |
| 设置种子 | [种子管理](seeding.md) | 种子类型 |

### 覆盖率相关

| 主题 | 指南 | 章节 |
|:---|:---|:---|
| 定义CoverGroup | [覆盖率概述](coverage/README.md) | 基础用法 |
| 使用Bin类型 | [SV迁移指南](coverage/systemverilog-migration.md) | Bin类型详解 |
| Cross覆盖率 | [SV迁移指南](coverage/systemverilog-migration.md) | Cross覆盖率 |
| 生成报告 | [覆盖率API](coverage/api-reference.md) | 报告生成 |

---

## 学习建议

1. **从示例开始**: 所有指南都包含可运行的代码示例
2. **循序渐进**: 按照推荐的学习路径逐步深入
3. **动手实践**: 边学边写代码，加深理解
4. **查阅API**: 遇到具体问题时查阅API参考

---

## 相关文档

- 📋 [功能清单](../product/features.md) - 完整功能列表
- 🎯 [应用场景](../product/use-cases.md) - 实际使用案例
- 🔧 [API参考](../api/) - 完整API文档
