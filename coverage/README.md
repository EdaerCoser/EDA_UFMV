# Coverage System

**SystemVerilog风格的功能覆盖率系统**

[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](../CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-141%20passed-success.svg)](../tests/test_coverage/)

---

## 📖 概述

这是一个独立的功能覆盖率系统，提供与SystemVerilog兼容的覆盖率定义、收集和报告功能。该系统可以从EDA_UFMV的sv_randomizer模块中分离出来，作为一个通用的覆盖率库使用。

### 核心特性

- ✅ **SystemVerilog语法兼容** - `@covergroup`, `@coverpoint`, `@cross`装饰器
- ✅ **6种Bin类型** - value, range, wildcard, auto, ignore, illegal
- ✅ **Cross覆盖** - 多变量交叉覆盖率，支持笛卡尔积
- ✅ **多格式报告** - HTML/JSON/UCIS（IEEE 1687标准）
- ✅ **双数据库后端** - 内存（快速）+ 文件（持久化）
- ✅ **141个测试** - 全部通过，高质量代码保证

---

## 🚀 快速开始

### 安装

```bash
# 作为独立模块使用
pip install -e .

# 或作为EDA_UFMV的一部分
cd eda_ufmv
pip install -e .
```

### 基础示例

```python
from coverage.core import CoverGroup, CoverPoint
from sv_randomizer import Randomizable

class Packet(Randomizable):
    def __init__(self):
        super().__init__()

        # 定义覆盖率组
        self.cg = CoverGroup("packet_cg")

        # 添加地址覆盖率点
        addr_cp = CoverPoint("addr", "addr", bins={
            "ranges": [[0, 0xFF], [0x100, 0x1FF]]
        })
        self.cg.add_coverpoint(addr_cp)

        # 添加到Randomizable
        self.add_covergroup(self.cg)

# 使用
pkt = Packet()
for _ in range(100):
    pkt.randomize()  # 自动采样覆盖率

print(f"Coverage: {pkt.get_total_coverage():.2f}%")
```

### 生成报告

```python
from coverage.formatters import generate_report

# 准备数据
data = {
    "title": "Packet Coverage",
    "covergroups": [pkt.cg.get_coverage_details()]
}

# 生成HTML报告
html = generate_report(data, format="html", filepath="coverage.html")

# 生成JSON报告
json = generate_report(data, format="json", filepath="coverage.json")
```

---

## 📁 模块结构

```
coverage/
├── __init__.py              # 模块入口
├── core/                    # 核心功能
│   ├── bin.py              # 6种Bin类型
│   ├── coverpoint.py       # CoverPoint实现
│   ├── covergroup.py       # CoverGroup容器
│   └── cross.py            # Cross覆盖
├── database/               # 数据库后端
│   ├── base.py             # 数据库接口
│   ├── memory_db.py        # 内存数据库
│   ├── file_db.py          # 文件数据库
│   └── factory.py          # 数据库工厂
├── formatters/             # 报告生成器
│   ├── base.py             # 报告基类
│   ├── html_report.py      # HTML报告
│   ├── json_report.py      # JSON报告
│   ├── ucis_report.py      # UCIS报告
│   └── factory.py          # 报告工厂
└── api/                    # 装饰器API
    └── decorators.py        # @covergroup/@coverpoint装饰器
```

---

## 🎯 设计模式

| 模式 | 应用 |
|:---|:---|
| **策略模式** | 可插拔数据库后端 |
| **装饰器模式** | SystemVerilog风格API |
| **工厂模式** | 数据库/报告工厂 |
| **观察者模式** | 采样回调机制 |
| **组合模式** | CoverGroup包含CoverPoints和Crosses |

---

## 📚 API文档

### 核心类

**CoverGroup** - 覆盖率组容器
```python
cg = CoverGroup(name="my_cg")
cg.add_coverpoint(CoverPoint("cp", "value", bins={"values": [1,2,3]}))
cg.sample(value=1)
```

**CoverPoint** - 单点覆盖率
```python
cp = CoverPoint(
    name="my_cp",
    sample_expr="addr",
    bins={"ranges": [[0, 0xFF]]}
)
```

**Cross** - 交叉覆盖率
```python
cross = Cross(
    name="addr_data_cross",
    coverpoints=["addr_cp", "data_cp"]
)
```

### 报告生成

```python
from coverage.formatters import ReportFactory

# 创建报告器
reporter = ReportFactory.create_html_report("My Report")

# 生成报告
data = {...}  # 覆盖率数据
content = reporter.generate(data)

# 保存文件
reporter.save(content, filepath="report.html")
```

---

## 🔗 与sv_randomizer集成

覆盖率系统与EDA_UFMV的sv_randomizer模块无缝集成：

```python
from sv_randomizer import Randomizable
from coverage.core import CoverGroup, CoverPoint

class MyTransaction(Randomizable):
    def __init__(self):
        super().__init__()

        # 添加覆盖率
        cg = CoverGroup("my_cg")
        cg.add_coverpoint(CoverPoint("cp", "value", bins={"values": [1,2,3]}))
        self.add_covergroup(cg)

# randomize()时自动采样覆盖率
txn = MyTransaction()
txn.randomize()
coverage = txn.get_total_coverage()
```

---

## 📖 更多信息

- [完整示例](../examples/coverage/)
- [测试代码](../tests/test_coverage/)
- [项目README](../README.md)
- [开发路线图](../docs/development/ROADMAP.md)

---

## 📄 许可证

MIT License - 详见项目根目录
