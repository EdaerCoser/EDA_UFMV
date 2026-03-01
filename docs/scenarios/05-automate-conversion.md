# 场景5：自动化SV→Python转换

## 阅读路径

```
🟢 基础使用    → 只读"快速开始"（10分钟）
🟡 进阶应用    → 读"快速开始"+"常见任务"（30分钟）
🟠 理解原理    → 读"技术实现"（1小时）
🔴 深入定制    → 读"扩展机制"+API参考
```

---

## 1. 场景目标

使用自动化工具将SystemVerilog代码转换为Python配置脚本。

> "我需要批量转换UVM寄存器模型任务"

---

## 2. 快速开始

### 2.1 安装转换器

```bash
pip install pyverilog jinja2 click
```

### 2.2 基本用法

```bash
# 转换SV文件到Python
python -m sv_to_python convert dma_tasks.sv -o dma_tasks.py

# 查看文件中的tasks
python -m sv_to_python list dma_tasks.sv

# 验证生成的代码
python -m sv_to_python validate dma_tasks.py --check-syntax
```

---

## 3. 深入理解

- **完整指南**: [SV→Python转换器](../reference/sv-converter.md)
- **迁移场景**: [场景4：从SV迁移](04-migrate-from-sv.md)

---

## 4. 下一步

- **场景6**：[完整验证流程](06-complete-workflow.md) - 端到端示例
