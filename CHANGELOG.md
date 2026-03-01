# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 项目初始化，基础随机化框架
- 随机变量系统（rand/randc）
- 约束系统（inside, dist, 表达式）
- 双求解器架构（PurePython + Z3）
- 种子管理功能
- 回归测试Agent

## [0.1.0] - 2026-02-XX

### Added
- **核心框架**
  - Randomizable基类，支持随机化和约束管理
  - RandVar（普通随机变量）实现
  - RandCVar（循环随机变量）实现
  - 完整的类型系统（INT, BIT, LOGIC, BOOL, ENUM, ARRAY）

- **约束系统**
  - 表达式AST系统（变量、常量、二元/一元运算）
  - 约束基类和表达式约束
  - InsideConstraint（范围约束）
  - DistConstraint（权重分布约束）
  - ArrayConstraint（数组约束：size, foreach, unique）

- **求解器**
  - SolverBackend抽象接口
  - PurePythonBackend（纯Python求解器）
  - Z3Backend（Z3 SMT求解器）
  - SolverFactory（求解器工厂）

- **API层**
  - @rand装饰器
  - @randc装饰器
  - @constraint装饰器
  - DSL语法糖（inside, dist, VarProxy）

- **格式化器**
  - VerilogFormatter（Verilog代码生成）
  - 测试平台生成

- **种子管理**
  - 全局种子（set_global_seed）
  - 对象级种子（Randomizable(seed=...)）
  - 临时种子（randomize(seed=...)）
  - Random实例管理

- **测试工具**
  - 回归测试Agent
  - 自动测试发现和运行
  - 测试报告生成

- **示例代码**
  - 基础随机化示例
  - 约束求解示例
  - 六元方程组测试
  - 种子功能演示

- **文档**
  - 架构设计文档
  - 实现计划文档
  - 种子控制功能文档
  - 测试Agent使用指南
  - 产品README

### Statistics
- **文件数**: 43个
- **代码行数**: 8220行
- **测试数量**: 36个单元测试
- **测试通过率**: 100%
- **文档页数**: 5个技术文档

### Tech Stack
- Python 3.7+
- pytest（测试框架）
- z3-solver（可选，用于Z3后端）
- 标准库（random, typing, subprocess等）

---

## [0.2.0] - Planned 2026 Q2

### Planned
- 功能覆盖率系统
  - CoverGroup/CoverPoint实现
  - Cross覆盖支持
  - Bin系统（值bins、范围bins、auto bins）
  - 覆盖率数据库
  - HTML/UCIS报告生成

---

## [0.3.0] - Planned 2026 Q3

### Planned
- 寄存器模型系统
  - Field/Field/Register/RegisterBlock实现
  - 访问控制（RW, RO, WO, W1C, W1S等）
  - 前门/后门访问
  - 层次化组织
  - 代码生成器（Verilog/C/Header）

---

## [0.4.0] - Planned 2026 Q3

### Planned
- 随机化增强
  - 覆盖率引导随机化
  - 智能约束求解
  - 动态权重调整
  - 场景感知随机化

---

## [0.5.0] - Planned 2026 Q4

### Planned
- DUT配置转换
  - Verilog/SystemVerilog解析器
  - Python模型生成器
  - 约束自动转换
  - 测试框架生成

---

## [1.0.0] - Planned 2027 Q1

### Planned
- 系统集成
- 性能优化
- 文档完善
- 生产就绪
- PyPI发布

---

## 版本说明

### 版本命名规则

- **主版本（Major）**: 重大架构变更，不兼容的API更改
- **次版本（Minor）**: 新功能添加，向后兼容
- **修订版本（Patch）**: bug修复、文档改进

### 发布节奏

- **Alpha版本**: 内部测试，功能可能变动
- **Beta版本**: 公开测试，功能基本稳定
- **RC版本**: 候选版本，生产环境测试
- **正式版本**: 稳定版本，生产环境可用

### 变更类型

- **Added**: 新增功能
- **Changed**: 现有功能的修改
- **Deprecated**: 即将废弃的功能
- **Removed**: 已删除的功能
- **Fixed**: bug修复
- **Security**: 安全问题修复

---

## 贡献指南

如果您想为项目贡献代码或文档，请阅读 [CONTRIBUTING.md](development/CONTRIBUTING.md)。

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](../LICENSE) 文件。
