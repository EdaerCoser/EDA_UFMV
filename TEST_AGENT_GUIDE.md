# 回归测试Agent使用指南

## 概述

回归测试Agent是一个Claude Code自定义skill，用于在代码变更时自动运行相关测试，确保代码改动不会破坏现有功能。

## 功能特性

### 支持的测试场景
- ✅ **单元测试** - 测试单个函数和类的功能
- ✅ **约束求解验证** - 验证复杂约束下的求解正确性
- ✅ **种子可重现性** - 验证不同种子的一致性和可重现性
- ✅ **性能压力测试** - 测试大规模约束和变量的性能

### 核心功能
- 自动检测Git代码变更
- 智能分析影响范围
- 自动选择相关测试
- 生成详细测试报告
- 性能监控和警告

## 使用方法

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
python .claude/skills/test-agent/runner.py -t tests/test_seeding.py

# 指定项目根目录
python .claude/skills/test-agent/runner.py -p /path/to/project
```

## 输出示例

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

[1/2] 运行 tests/test_variables.py...
  [OK] 9/9 通过 (耗时: 0.06s)

[2/2] 运行 tests/test_seeding.py...
  [OK] 11/11 通过 (耗时: 0.13s)

======================================================================
回归测试报告
======================================================================
[时间] 2026-03-01 14:51:58
[变更] 变更文件: sv_randomizer/core/variables.py

[分析] 影响分析:
  - 涉及模块: core/

[测试] 测试结果:
  [OK] tests/test_variables.py: 9/9 通过 (耗时: 0.06s)
  [OK] tests/test_seeding.py: 11/11 通过 (耗时: 0.13s)

[汇总] 统计汇总:
  总计: 20/20 通过 (总耗时: 0.19s)

[OK] 所有测试通过，代码变更安全
======================================================================
```

## 测试映射规则

| 修改的文件路径 | 运行的测试 |
|--------------|----------|
| `sv_randomizer/core/randomizable.py` | `test_variables.py`, `test_seeding.py` |
| `sv_randomizer/core/variables.py` | `test_variables.py`, `test_seeding.py` |
| `sv_randomizer/constraints/` | `test_constraints.py`, `test_expressions.py` |
| `sv_randomizer/solvers/` | `test_solvers.py`, `test_seeding.py` |
| `sv_randomizer/formatters/` | `test_formatters.py` |
| `examples/` | 运行修改的示例文件 |

## 配置文件

在项目根目录创建 `.test-config.json`:

```json
{
  "test_mapping": {
    "core/": [
      "tests/test_variables.py",
      "tests/test_randomizable.py",
      "tests/test_seeding.py"
    ],
    "constraints/": [
      "tests/test_constraints.py",
      "tests/test_expressions.py"
    ],
    "solvers/": [
      "tests/test_solvers.py",
      "tests/test_seeding.py"
    ]
  },
  "performance_threshold": {
    "warning": 1.0,
    "critical": 5.0
  },
  "enable_coverage": false,
  "parallel_execution": false
}
```

## 性能监控

- ⚠️ 警告: 单个测试耗时 > 1.0s
- 🚨 严重: 单个测试耗时 > 5.0s

## 当前测试覆盖

项目包含以下测试文件：
- `tests/test_variables.py` - 9个测试
- `tests/test_constraints.py` - 16个测试
- `tests/test_seeding.py` - 11个测试

总计: **36个测试**

## 集成到开发工作流

### Git钩子集成

在 `.git/hooks/pre-push` 中添加：
```bash
#!/bin/bash
python .claude/skills/test-agent/runner.py
if [ $? -ne 0 ]; then
    echo "测试失败，拒绝推送"
    exit 1
fi
```

### VSCode任务

在 `.vscode/tasks.json` 中添加：
```json
{
    "label": "运行回归测试",
    "type": "shell",
    "command": "python .claude/skills/test-agent/runner.py --all",
    "group": "test",
    "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true
    }
}
```

## 故障排除

### 问题: 测试文件未找到

确保 `tests/` 目录存在，并且包含 `test_*.py` 文件。

### 问题: Git检测失败

确保项目在Git仓库中，并且Git已正确安装。

### 问题: pytest错误

该Agent不依赖pytest，直接使用Python运行测试。如果遇到pytest相关问题，请忽略。

## 技术细节

- **语言**: Python 3.7+
- **依赖**: 无（仅使用标准库）
- **测试框架**: unittest + 自定义测试函数
- **版本控制**: Git（用于变更检测）

## 未来扩展

可以添加的功能：
- 并行测试执行
- 覆盖率报告生成
- 测试结果历史记录
- CI/CD集成
- 性能趋势分析
