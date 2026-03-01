# 场景4：从SystemVerilog迁移

## 阅读路径

```
🟢 基础使用    → 只读"快速开始"（10分钟）
🟡 进阶应用    → 读"快速开始"+"常见任务"（30分钟）
🟠 理解原理    → 读"技术实现"（1小时）
🔴 深入定制    → 读"扩展机制"+API参考
```

---

## 1. 场景目标

将现有的SystemVerilog验证环境迁移到EDA_UFMV Python环境。

> "我有一个UVM验证环境，想逐步迁移到Python"

---

## 2. 核心步骤

### 2.1 理解概念映射

**必读**: [SystemVerilog→Python映射表](../concepts/sv-to-python-mapping.md)

### 2.2 迁移顺序

建议按以下顺序迁移：

1. **随机化** → [场景1：生成随机激励](01-generate-random.md)
2. **覆盖率** → [场景2：收集覆盖率](02-collect-coverage.md)
3. **寄存器模型** → [场景3：创建寄存器模型](03-create-regmodel.md)

### 2.3 使用转换工具

详细使用方法：[场景5：自动化SV→Python转换](05-automate-conversion.md)

---

## 3. 常见迁移任务

### 3.1 迁移随机化类

**SystemVerilog**:
```systemverilog
class Packet;
  rand bit [31:0] addr;
  constraint addr_valid { addr > 0; }
endclass
```

**Python**:
```python
class Packet(Randomizable):
    addr: rand(int)(bits=32, min=0, max=0xFFFF_FFFF)

    @constraint
    def addr_valid(self):
        return self.addr > 0
```

### 3.2 迁移覆盖率

详见：[覆盖率迁移详细参考](../reference/coverage/migration.md)

### 3.3 迁移UVM寄存器模型

详见：[RGM用户指南](../product/RGM_GUIDE.md)

---

## 4. 深入理解

- **完整对照表**: [SV→Python映射表](../concepts/sv-to-python-mapping.md)
- **覆盖率迁移**: [覆盖率迁移详细参考](../reference/coverage/migration.md)
- **转换工具**: [SV→Python转换器](../reference/sv-converter.md)

---

## 5. 下一步

- **场景5**：[自动化SV→Python转换](05-automate-conversion.md) - 使用转换工具
- **场景6**：[完整验证流程](06-complete-workflow.md) - 端到端示例
