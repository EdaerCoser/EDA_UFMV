# Coverage System

**SystemVerilog风格的功能覆盖率系统**

[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](../CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-141%20passed-success.svg)](../tests/test_coverage/)

---

## 概述

独立的功能覆盖率系统，提供与SystemVerilog兼容的覆盖率定义、收集和报告功能。可作为EDA_UFMV的一部分使用，也可作为独立库集成到其他项目。

### 核心特性

- SystemVerilog语法兼容 - `@covergroup`, `@coverpoint`, `@cross`装饰器
- 6种Bin类型 - value, range, wildcard, auto, ignore, illegal
- Cross覆盖 - 多变量交叉覆盖率
- 多格式报告 - HTML/JSON/UCIS（IEEE 1687标准）
- 双数据库后端 - 内存（快速）+ 文件（持久化）

---

## 模块结构

```
coverage/
├── core/          # 核心功能 (CoverGroup, CoverPoint, Cross, Bin)
├── database/      # 数据库后端 (Memory, File)
├── formatters/    # 报告生成器 (HTML, JSON, UCIS)
└── api/           # 装饰器API (@covergroup, @coverpoint, @cross)
```

---

## 快速开始

### 基础示例

```python
from coverage.core import CoverGroup, CoverPoint
from sv_randomizer import Randomizable

class Packet(Randomizable):
    def __init__(self):
        super().__init__()
        self.cg = CoverGroup("packet_cg")
        addr_cp = CoverPoint("addr", "addr", bins={"ranges": [[0, 0xFF]]})
        self.cg.add_coverpoint(addr_cp)
        self.add_covergroup(self.cg)

pkt = Packet()
for _ in range(100):
    pkt.randomize()  # 自动采样
```

### 生成报告

```python
from coverage.formatters import generate_report

data = {"title": "Coverage", "covergroups": [pkt.cg.get_coverage_details()]}
generate_report(data, format="html", filepath="coverage.html")
```

---

## 与sv_randomizer集成

覆盖率系统与EDA_UFMV的随机化模块无缝集成。添加覆盖率后，`randomize()`会自动采样覆盖率。

详见: [场景2：收集功能覆盖率](../docs/scenarios/02-collect-coverage.md)

---

## 设计模式

- 策略模式 - 可插拔数据库后端
- 装饰器模式 - SystemVerilog风格API
- 工厂模式 - 数据库/报告工厂
- 观察者模式 - 采样回调机制

---

## 文档

- [场景2：收集功能覆盖率](../docs/scenarios/02-collect-coverage.md) - 快速上手
- [SV→Python概念映射](../docs/concepts/sv-to-python-mapping.md) - 语法对照
- [覆盖率迁移详细参考](../docs/reference/coverage/migration.md) - SV迁移详解
- [完整示例](../examples/coverage/) - 示例代码

---

## 许可证

MIT License
