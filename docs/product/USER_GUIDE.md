# 用户指南

**版本**: v0.1.0
**状态**: 规划中
**预计完成**: v0.2.0

---

## 概述

本指南提供EDA_UFMV的详细使用说明，包括快速入门、最佳实践和常见用例。

---

## 目录

1. [快速入门](#快速入门)
2. [基础概念](#基础概念)
3. [随机化指南](#随机化指南)
4. [约束系统](#约束系统)
5. [种子管理](#种子管理)
6. [最佳实践](#最佳实践)
7. [常见问题](#常见问题)

---

## 快速入门

### 安装

```bash
pip install eda-ufmv
```

### 第一个示例

```python
from sv_randomizer import Randomizable, rand

class Packet(Randomizable):
    @rand(bit_width=16)
    def addr(self): return 0

pkt = Packet()
pkt.randomize()
print(f"Generated address: 0x{pkt.addr:04X}")
```

---

## 基础概念

### 随机变量

EDA_UFMV提供两种类型的随机变量：

- **rand** - 普通随机变量，每次随机化独立生成
- **randc** - 循环随机变量，遍历所有可能值后才重复

### 约束系统

约束用于限制随机变量的取值范围：

- **inside** - 值范围约束
- **dist** - 权重分布约束
- **表达式** - 关系和逻辑运算

---

## 更多内容

完整的用户指南正在开发中，预计在v0.2.0版本发布。

### 规划章节

- [ ] 高级约束技巧
- [ ] 求解器选择指南
- [ ] 性能优化建议
- [ ] 调试技巧
- [ ] 与pytest集成
- [ ] 生成Verilog测试平台

---

## 参考资源

- [产品说明书](PRODUCT_MANUAL.md)
- [API参考手册](API_REFERENCE.md)（规划中）
- [示例代码](../../examples/)

---

**最后更新**: 2026年3月1日
**维护者**: EDA_UFMV开发团队
