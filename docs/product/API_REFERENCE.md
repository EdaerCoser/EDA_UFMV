# API参考手册

**版本**: v0.1.0
**状态**: 规划中
**预计完成**: v0.2.0

---

## 概述

本手册提供EDA_UFMV的完整API参考文档，包括所有公开类、方法和函数的详细说明。

---

## 目录

### 核心模块

- [Randomizable](#randomizable) - 可随机化基类
- [RandVar](#randvar) - 普通随机变量
- [RandCVar](#randcvar) - 循环随机变量
- [VarType](#vartype) - 变量类型枚举

### 约束系统

- [Constraint](#constraint) - 约束基类
- [InsideConstraint](#insideconstraint) - 范围约束
- [DistConstraint](#distconstraint) - 权重分布约束
- [ArrayConstraint](#arrayconstraint) - 数组约束

### 表达式系统

- [Expr](#expr) - 表达式基类
- [VariableExpr](#variableexpr) - 变量表达式
- [ConstantExpr](#constantexpr) - 常量表达式
- [BinaryExpr](#binaryexpr) - 二元运算表达式
- [UnaryExpr](#unaryexpr) - 一元运算表达式

### 求解器

- [SolverBackend](#solverbackend) - 求解器后端接口
- [PurePythonBackend](#purepythonbackend) - 纯Python求解器
- [Z3Backend](#z3backend) - Z3 SMT求解器

### API装饰器

- [@rand](#rand) - 随机变量装饰器
- [@randc](#randc) - 循环随机变量装饰器
- [@constraint](#constraint-1) - 约束装饰器

---

## API文档

### Randomizable

**基类**，所有可随机化对象的父类。

#### 方法

##### `__init__(seed=None)`

初始化随机化对象。

**参数**:
- `seed` (int, optional): 随机种子

**示例**:
```python
class Packet(Randomizable):
    def __init__(self, seed=None):
        super().__init__(seed=seed)
```

##### `randomize(seed=None)`

执行随机化。

**参数**:
- `seed` (int, optional): 临时随机种子

**返回**:
- `bool`: 随机化是否成功

**示例**:
```python
pkt = Packet()
if pkt.randomize():
    print(f"成功: addr={pkt.addr}")
```

---

## 更多内容

完整API文档正在开发中，预计在v0.2.0版本发布。

如果您想帮助完善API文档，请参考：
- [贡献指南](../development/CONTRIBUTING.md)（规划中）
- [开发路线图](../development/ROADMAP.md)

---

**最后更新**: 2026年3月1日
**维护者**: EDA_UFMV开发团队
