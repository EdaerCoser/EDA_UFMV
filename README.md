# EDA_UFMV

用于上板的通用验证框架 (Universal Verification Framework for Board-Level Testing)

## 项目概述

EDA_UFMV是一个基于Python的SystemVerilog风格随机约束求解器，专为硬件验证和上板测试设计。该工具提供了类似SystemVerilog的随机化和约束功能，可用于生成复杂的测试向量。

## 主要特性

- **rand/randc变量**: 标准随机变量和循环随机变量
- **约束系统**: 支持`inside`、`dist`、关系/逻辑运算符和条件约束
- **可插拔求解器**: 纯Python后端（无依赖）和Z3后端（工业级）
- **输出格式**: 生成Verilog格式的测试向量用于仿真
- **种子控制**: 支持全局、对象级和临时随机种子，确保测试可重现性
- **回归测试**: 内置测试守护agent，自动检测代码变更并运行相关测试

## 安装

```bash
# 基础安装（纯Python，无外部依赖）
pip install -e .

# 使用Z3求解器后端以获得更好的性能
pip install -e ".[z3]"

# 包含统计验证工具
pip install -e ".[stat]"

# 开发环境安装
pip install -e ".[dev]"
```

## 快速开始

```python
from sv_randomizer import Randomizable, RandVar, RandCVar, VarType
from sv_randomizer.constraints.base import ExpressionConstraint
from sv_randomizer.constraints.expressions import VariableExpr, ConstantExpr, BinaryExpr, BinaryOp

class Packet(Randomizable):
    def __init__(self):
        super().__init__()
        self._rand_vars['src_addr'] = RandVar('src_addr', VarType.INT, min_val=0, max_val=65535)
        self._rand_vars['dest_addr'] = RandVar('dest_addr', VarType.INT, min_val=0, max_val=65535)
        self._randc_vars['packet_id'] = RandCVar('packet_id', VarType.BIT, bit_width=4)

        # 添加约束：源地址必须 >= 0x1000
        expr = BinaryExpr(
            VariableExpr('src_addr'),
            BinaryOp.GE,
            ConstantExpr(0x1000)
        )
        self.add_constraint(ExpressionConstraint("valid_addr", expr))

# 生成随机数据包
pkt = Packet()
for i in range(10):
    if pkt.randomize():
        print(f"数据包 {i+1}: 源地址=0x{pkt.src_addr:04x}, 目标地址=0x{pkt.dest_addr:04x}, "
              f"ID={pkt.packet_id}")
```

## 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 或直接运行测试文件
python tests/test_variables.py
python tests/test_constraints.py
python tests/test_seeding.py

# 使用回归测试agent
python .claude/skills/test-agent/runner.py --all
```

## 文档

- [架构设计](docs/ARCHITECTURE.md) - 系统架构和设计原理
- [实现计划](docs/IMPLEMENTATION_PLAN.md) - 详细实现方案
- [种子控制](docs/SEED_CONTROL.md) - 随机种子功能说明
- [测试Agent指南](TEST_AGENT_GUIDE.md) - 回归测试工具使用说明

## 示例

查看`examples/`目录获取更多使用示例：
- `simple_test.py` - 基础使用示例
- `packet_generator.py` - 数据包生成示例
- `seed_demo.py` - 随机种子控制演示
- `test_six_variables.py` - 六元方程组约束求解测试

## 许可证

MIT License

## 贡献

欢迎贡献！请随时提交Pull Request。
