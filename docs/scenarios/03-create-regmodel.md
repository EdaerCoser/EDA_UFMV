# 场景3：创建寄存器模型

## 阅读路径

```
🟢 基础使用    → 只读"快速开始"（10分钟）
🟡 进阶应用    → 读"快速开始"+"常见任务"（30分钟）
🟠 理解原理    → 读"技术实现"（1小时）
🔴 深入定制    → 读"扩展机制"+API参考
```

---

## 1. 场景目标

定义和管理DUT的寄存器模型，实现自动化的寄存器配置和读写访问。

> "我需要为DMA控制器创建寄存器模型，实现Python脚本自动配置"

---

## 2. SystemVerilog对应（5分钟理解）

| SystemVerilog (UVM) | Python | 说明 |
|---------------------|--------|------|
| `uvm_reg_block` | `RegisterBlock` | 寄存器块 |
| `uvm_reg` | `Register` | 寄存器 |
| `uvm_reg_field` | `Field` | 字段 |
| `RW, RO, WO` | `AccessType.RW, .RO, .WO` | 访问类型 |
| `write(status, value)` | `reg.write(value)` | 写入 |
| `read(status, value)` | `value = reg.read()` | 读取 |
| `set(value)` | `reg.set(value)` | 设置期望值 |
| `get()` | `value = reg.get()` | 获取期望值 |

---

## 3. 快速开始

### 3.1 最简单的寄存器

```python
from rgm import Register, Field, AccessType

# 创建32位控制寄存器
ctrl_reg = Register("DMA_CTRL", offset=0x00, width=32)
ctrl_reg.add_field(Field("ENABLE", 0, 1, AccessType.RW, 0))
ctrl_reg.add_field(Field("START", 1, 1, AccessType.RW, 0))
ctrl_reg.add_field(Field("CLEAR", 2, 1, AccessType.WO, 0))
```

### 3.2 完整DMA寄存器块

详细示例请参考：
- 📖 [RGM用户指南](../product/RGM_GUIDE.md) - 完整API和示例
- 💻 [examples/rgm/basic_rgm_example.py](../../examples/rgm/basic_rgm_example.py)

---

## 4. 深入理解

想了解更多实现细节？

- **完整指南**: [RGM用户指南](../product/RGM_GUIDE.md)
- **概念深入**: [RGM深入](../concepts/rgm-deep-dive.md)
- **SSH访问**: [SSH适配器指南](../reference/rgm/SSH_ADAPTER_GUIDE.md)
- **更多示例**: [examples/rgm/](../../examples/rgm/)

---

## 5. 下一步

现在你已经掌握了RGM基础，继续学习：

- **场景4**：[从SystemVerilog迁移](04-migrate-from-sv.md) - 迁移UVM寄存器模型
- **场景6**：[完整验证流程](06-complete-workflow.md) - 端到端示例
