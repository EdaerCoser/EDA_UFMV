# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 覆盖率引导随机化 (v0.4.0 规划中)
- DUT配置转换 (v0.5.0 规划中)

---

## [0.3.0] - 2026-02-28

### Added
- **寄存器模型系统 (RGM)**
  - 层次化寄存器建模（Field/Register/RegisterBlock）
  - 15种访问类型（RW, RO, WO, W1C, W1S, W0C, W0S, RC, RS, WC, WS, WRC, WRS, WSRC, WCRS）
  - FrontDoor（前门访问）和BackDoor（后门访问）接口
  - UVM兼容接口（set/get/update/mirror/poke/peek）

- **硬件适配器**
  - AXIAdapter（AXI总线访问）
  - APBAdapter（APB总线访问）
  - UARTAdapter（UART串口访问）
  - SSHAdapter（SSH远程板卡访问）

- **代码生成器**
  - VerilogGenerator（Verilog RTL代码生成）
  - CHeaderGenerator（C头文件生成）
  - PythonGenerator（Python模型生成）
  - GeneratorFactory（生成器工厂）

- **寄存器映射**
  - RegisterMap（寄存器地址映射表）
  - 自动地址分配
  - 重叠检测

- **API接口**
  - 字段定义和管理
  - 寄存器访问和操作
  - 寄存器块层次化管理

- **测试和文档**
  - 186+个RGM测试用例
  - [RGM用户指南](docs/product/RGM_GUIDE.md)
  - [SSH适配器指南](docs/guides/rgm/SSH_ADAPTER_GUIDE.md)
  - 完整的使用示例

### Statistics
- **新增文件数**: 42个
- **新增代码行数**: ~8,500行
- **测试数量**: 186+个RGM测试
- **测试通过率**: 100%

### Tech Stack
- Python 3.8+
- paramiko（SSH连接）
- pytest（测试框架）

---

## [0.2.0] - 2026-02-15

### Added
- **功能覆盖率系统**
  - CoverGroup/CoverPoint/Cross核心类
  - 6种Bin类型（ValueBin, RangeBin, WildcardBin, AutoBin, IgnoreBin, IllegalBin）
  - SystemVerilog风格的装饰器API（@covergroup, @coverpoint, @cross）
  - 覆盖率自动采样（集成Randomizable）
  - 百分比计算和报告

- **数据库后端**
  - MemoryDatabase（内存数据库，快速）
  - FileDatabase（文件持久化，支持合并）
  - DatabaseFactory（数据库工厂）

- **报告生成器**
  - HTML报告（交互式，可视化）
  - JSON报告（CI/CD集成）
  - UCIS报告（IEEE 1687标准）
  - ReportFactory（报告工厂）

- **高级功能**
  - Cross覆盖率（笛卡尔积）
  - Bin覆盖检测（hit/unhit）
  - 覆盖率合并（多次运行）
  - 延迟加载（性能优化）

- **测试和文档**
  - 141个覆盖率测试用例
  - 性能测试（~246K次/秒）
  - [覆盖率API参考](docs/guides/coverage/api-reference.md)
  - [SystemVerilog迁移指南](docs/guides/coverage/systemverilog-migration.md)
  - 完整的使用示例

### Statistics
- **新增文件数**: 28个
- **新增代码行数**: ~6,200行
- **测试数量**: 141个覆盖率测试
- **测试通过率**: 100%
- **性能指标**: ~246K samples/sec (简单场景)

### Tech Stack
- Python 3.8+
- json（数据持久化）
- pytest（测试框架）

---

## [0.1.0] - 2026-02-01

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
- **代码行数**: 8,220行
- **测试数量**: 36个单元测试
- **测试通过率**: 100%
- **文档页数**: 5个技术文档

### Tech Stack
- Python 3.7+
- pytest（测试框架）
- z3-solver（可选，用于Z3后端）
- 标准库（random, typing, subprocess等）

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

如果您想为项目贡献代码或文档，请阅读 [CONTRIBUTING.md](docs/development/CONTRIBUTING.md)。

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。
