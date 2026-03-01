# 回归测试Agent使用指南

**版本**: v0.1.0
**最后更新**: 2026年3月1日
**项目**: EDA_UFMV

---

## 📖 概述

回归测试Agent是一个Claude Code自定义skill，用于在代码变更时自动运行相关测试，确保代码改动不会破坏现有功能。

### 🎯 核心价值

- **自动化** - 无需手动选择测试，自动检测变更并运行相关测试
- **智能化** - 基于文件变更影响分析，精准选择测试集
- **高效性** - 只运行必要的测试，节省开发时间
- **可靠性** - 在代码推送前捕获潜在问题

---

## ✨ 功能特性

### 支持的测试场景

- ✅ **单元测试** - 测试单个函数和类的功能
- ✅ **约束求解验证** - 验证复杂约束下的求解正确性
- ✅ **种子可重现性** - 验证不同种子的一致性和可重现性
- ✅ **性能压力测试** - 测试大规模约束和变量的性能

### 核心功能

| 功能 | 说明 |
|:---|:---|
| **自动变更检测** | 使用Git status检测代码变更 |
| **智能影响分析** | 基于文件路径映射分析影响范围 |
| **自动测试选择** | 根据影响范围选择相关测试 |
| **详细测试报告** | 生成包含性能指标的测试报告 |
| **性能监控** | 警告慢速测试，识别性能退化 |

---

## 🚀 使用方法

### 方法1: 作为Claude Code Skill使用（推荐）

在Claude Code中运行：

```
/test-agent
```

### 方法2: 作为独立脚本使用

```bash
# 运行回归测试（基于Git变更）
python .claude/skills/test-agent/runner.py

# 运行所有测试
python .claude/skills/test-agent/runner.py --all

# 运行指定测试
python .claude/skills/test-agent/runner.py -t tests/legacy/test_seeding.py

# 指定项目根目录
python .claude/skills/test-agent/runner.py -p /path/to/project
```

### 方法3: 命令行参数

```
usage: runner.py [-h] [--all] [-t TEST] [-p PROJECT]

回归测试Agent - 自动检测变更并运行相关测试

optional arguments:
  -h, --help            显示帮助信息
  --all                 运行所有测试
  -t TEST, --test TEST  运行指定测试文件
  -p PROJECT, --project PROJECT
                        指定项目根目录（默认为当前目录）
```

---

## 📊 输出示例

### 正常运行输出

```
======================================================================
[Agent] 回归测试守护 Agent
============================================================

[检测] 检测到 1 个文件变更:
  - sv_randomizer/core/variables.py

[分析] 影响分析: core/
[测试] 将运行 2 个测试文件

============================================================
开始运行 2 个测试文件...
============================================================

[1/2] 运行 tests/legacy/test_variables.py...
  [OK] 9/9 通过 (耗时: 0.06s)

[2/2] 运行 tests/legacy/test_seeding.py...
  [OK] 11/11 通过 (耗时: 0.13s)

======================================================================
回归测试报告
======================================================================
[时间] 2026-03-01 14:51:58
[变更] 变更文件: sv_randomizer/core/variables.py

[分析] 影响分析:
  - 涉及模块: core/

[测试] 测试结果:
  [OK] tests/legacy/test_variables.py: 9/9 通过 (耗时: 0.06s)
  [OK] tests/legacy/test_seeding.py: 11/11 通过 (耗时: 0.13s)

[汇总] 统计汇总:
  总计: 20/20 通过 (总耗时: 0.19s)

[OK] 所有测试通过，代码变更安全
======================================================================
```

### 无变更输出

```
======================================================================
[Agent] 回归测试守护 Agent
============================================================

[检测] 未检测到代码变更
[提示] 使用 --all 运行所有测试
======================================================================
```

### 性能警告输出

```
[2/3] 运行 tests/legacy/test_constraints.py...
  [OK] 16/16 通过 (耗时: 1.23s) ⚠️ 警告: 测试耗时超过1.0秒
```

---

## 🗂️ 测试映射规则

| 修改的文件路径 | 运行的测试 |
|:---|:---|
| `sv_randomizer/core/randomizable.py` | `tests/legacy/test_variables.py`, `tests/legacy/test_seeding.py` |
| `sv_randomizer/core/variables.py` | `tests/legacy/test_variables.py`, `tests/legacy/test_seeding.py` |
| `sv_randomizer/constraints/` | `tests/legacy/test_constraints.py` |
| `sv_randomizer/solvers/` | `tests/legacy/test_constraints.py`, `tests/legacy/test_seeding.py` |
| `sv_randomizer/formatters/` | 相关示例测试 |
| `examples/` | 运行修改的示例文件 |

---

## ⚙️ 配置文件

在项目根目录创建 `.test-config.json`:

```json
{
  "test_mapping": {
    "core/": [
      "tests/legacy/test_variables.py",
      "tests/legacy/test_randomizable.py",
      "tests/legacy/test_seeding.py"
    ],
    "constraints/": [
      "tests/legacy/test_constraints.py",
      "tests/legacy/test_expressions.py"
    ],
    "solvers/": [
      "tests/legacy/test_solvers.py",
      "tests/legacy/test_seeding.py"
    ],
    "formatters/": [
      "tests/legacy/test_formatters.py"
    ]
  },
  "performance_threshold": {
    "warning": 1.0,
    "critical": 5.0
  },
  "enable_coverage": false,
  "parallel_execution": false,
  "project_root": "."
}
```

### 配置参数说明

| 参数 | 类型 | 说明 |
|:---|:---|:---|
| `test_mapping` | object | 文件路径到测试文件的映射 |
| `performance_threshold.warning` | float | 性能警告阈值（秒） |
| `performance_threshold.critical` | float | 性能严重阈值（秒） |
| `enable_coverage` | bool | 是否启用覆盖率收集 |
| `parallel_execution` | bool | 是否并行执行测试 |
| `project_root` | string | 项目根目录路径 |

---

## 📈 性能监控

### 性能指标

- ⚠️ **警告**: 单个测试耗时 > 1.0s
- 🚨 **严重**: 单个测试耗时 > 5.0s

### 性能基线

| 测试文件 | 预期耗时 | 状态 |
|:---|:---|:---|
| `test_variables.py` | < 0.1s | ✅ |
| `test_constraints.py` | < 0.5s | ✅ |
| `test_seeding.py` | < 0.2s | ✅ |

---

## 📋 当前测试覆盖

项目包含以下测试文件：

| 测试文件 | 测试数量 | 覆盖内容 |
|:---|:---|:---|
| `tests/legacy/test_variables.py` | 9个 | RandVar, RandCVar |
| `tests/legacy/test_constraints.py` | 16个 | Inside, Dist, 表达式约束 |
| `tests/legacy/test_seeding.py` | 11个 | 种子管理, 可重现性 |

**总计**: 36个测试 ✅

---

## 🔧 集成到开发工作流

### Git钩子集成

在 `.git/hooks/pre-push` 中添加：

```bash
#!/bin/bash
echo "运行回归测试..."
python .claude/skills/test-agent/runner.py
if [ $? -ne 0 ]; then
    echo "❌ 测试失败，拒绝推送"
    exit 1
fi
echo "✅ 所有测试通过"
```

别忘了赋予执行权限：

```bash
chmod +x .git/hooks/pre-push
```

### VSCode任务

在 `.vscode/tasks.json` 中添加：

```json
{
    "label": "运行回归测试",
    "type": "shell",
    "command": "python .claude/skills/test-agent/runner.py --all",
    "group": {
        "kind": "test",
        "isDefault": true
    },
    "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "new"
    }
}
```

### GitHub Actions（规划中）

创建 `.github/workflows/regression-test.yml`:

```yaml
name: Regression Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Run regression tests
        run: python .claude/skills/test-agent/runner.py --all
```

---

## 🔍 故障排除

### 问题: 测试文件未找到

**症状**: `Error: Test file not found: tests/xxx.py`

**解决方案**:
1. 确保 `tests/` 目录存在
2. 检查 `.test-config.json` 中的路径配置
3. 确认测试文件以 `test_` 开头

### 问题: Git检测失败

**症状**: `Error: Not a git repository`

**解决方案**:
1. 确保项目在Git仓库中
2. 运行 `git status` 验证Git配置
3. 检查项目根目录是否有 `.git` 文件夹

### 问题: pytest错误

**症状**: pytest相关的错误信息

**说明**: 该Agent不依赖pytest，直接使用Python运行测试。

### 问题: 测试输出解析失败

**症状**: 测试结果显示为 `0/0`

**解决方案**:
1. 确保测试文件使用标准输出格式
2. unittest测试会自动解析
3. 自定义测试需输出 `测试结果: X 通过, Y 失败` 格式

---

## 🛠️ 技术细节

### 技术栈

| 技术 | 版本 | 用途 |
|:---|:---|:---|
| Python | 3.7+ | 核心语言 |
| unittest | 标准库 | 测试框架 |
| Git | 任意 | 版本控制和变更检测 |
| subprocess | 标准库 | 测试执行 |

### 架构设计

```
runner.py (主入口)
  ├── detect_changes()      # 检测Git变更
  ├── analyze_impact()      # 分析影响范围
  ├── run_test()           # 执行单个测试
  ├── generate_report()    # 生成测试报告
  └── parse_output()       # 解析测试输出
```

---

## 🚀 未来扩展

### 计划中的功能

- [ ] **并行测试执行** - 多线程/多进程运行测试
- [ ] **覆盖率报告** - 生成代码覆盖率报告
- [ ] **测试历史记录** - 记录测试结果历史
- [ ] **CI/CD集成** - 支持更多CI平台
- [ ] **性能趋势分析** - 跟踪测试性能变化
- [ ] **智能测试推荐** - 基于代码变更推荐测试
- [ ] **测试依赖分析** - 分析测试之间的依赖关系

### 贡献指南

欢迎贡献新功能！请参考：
- [开发路线图](docs/development/ROADMAP.md)
- [贡献指南](docs/development/CONTRIBUTING.md)（规划中）

---

## 📞 联系方式

- **项目主页**: <https://github.com/EdaerCoser/EDA_UFMV>
- **问题反馈**: <https://github.com/EdaerCoser/EDA_UFMV/issues>
- **讨论区**: <https://github.com/EdaerCoser/EDA_UFMV/discussions>

---

**最后更新**: 2026年3月1日
**维护者**: EDA_UFMV开发团队
