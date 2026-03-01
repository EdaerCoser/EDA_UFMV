# 场景6：完整验证流程案例

## 阅读路径

```
🟢 基础使用    → 只读"快速开始"（10分钟）
🟡 进阶应用    → 读"快速开始"+"常见任务"（30分钟）
🟠 理解原理    → 读"技术实现"（1小时）
🔴 深入定制    → 读"扩展机制"+API参考
```

---

## 1. 场景目标

端到端的DMA控制器验证流程，展示如何集成所有模块。

> "我想看一个完整的验证环境示例"

---

## 2. 完整流程

### 2.1 流程概述

```
随机化激励 → DUT仿真 → 覆盖率收集 → 结果分析
     ↓            ↓           ↓           ↓
  Randomizable   Verilog     CoverGroup    报告
```

### 2.2 集成示例

完整示例请参考：
- 📖 [examples/rand/](../../examples/rand/) - 随机化示例
- 📊 [examples/coverage/](../../examples/coverage/) - 覆盖率示例
- 🗄️ [examples/rgm/](../../examples/rgm/) - 寄存器模型示例

---

## 3. 深入理解

- **随机化**: [场景1](01-generate-random.md)
- **覆盖率**: [场景2](02-collect-coverage.md)
- **寄存器**: [场景3](03-create-regmodel.md)
