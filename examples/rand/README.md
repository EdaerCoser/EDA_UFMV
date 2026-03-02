# 随机化示例

本目录包含EDA_UFVM的随机化和约束系统使用示例。

---

## 示例文件

| 示例文件 | 说明 | 功能点 |
|:---|:---|:---|
| [simple_test.py](simple_test.py) | 简单随机变量示例 | 基础rand/randc变量使用 |
| [packet_generator.py](packet_generator.py) | 数据包生成示例 | 约束系统和随机化组合 |
| [seed_demo.py](seed_demo.py) | 随机种子控制演示 | 种子管理和可重现性 |
| [test_six_variables.py](test_six_variables.py) | 六元方程组约束求解 | 复杂约束系统验证 |
| [solve_inequalities.py](solve_inequalities.py) | 不等式求解 | Inside约束使用 |

---

## 运行示例

```bash
# 运行所有示例
python examples/rand/simple_test.py
python examples/rand/packet_generator.py
python examples/rand/seed_demo.py
python examples/rand/test_six_variables.py
python examples/rand/solve_inequalities.py
```

---

## 示例说明

### 1. simple_test.py - 简单随机变量

**功能**: 最简单的随机化示例

演示内容：
- 创建Randomizable类
- 定义rand和randc变量
- 执行randomize()

**适用场景**: 学习基础随机化

---

### 2. packet_generator.py - 数据包生成

**功能**: 数据包生成示例

演示内容：
- 多个随机变量组合
- 地址约束（源地址 >= 0x1000）
- 循环随机变量（randc）

**适用场景**: 学习约束系统

---

### 3. seed_demo.py - 随机种子控制

**功能**: 种子控制演示

演示内容：
- 全局种子设置（set_global_seed）
- 对象级种子（Packet(seed=123)）
- 临时种子（randomize(seed=456)）
- 可重现性验证

**适用场景**: 学习种子管理和测试可重现性

---

### 4. test_six_variables.py - 六元方程组

**功能**: 复杂约束系统验证

演示内容：
- 六个变量的复杂约束
- 多变量约束系统
- 求解器性能验证

**适用场景**: 验证约束求解能力

---

### 5. solve_inequalities.py - 不等式求解

**功能**: Inside约束使用

演示内容：
- Inside约束使用
- 范围约束
- 多种约束组合

**适用场景**: 学习范围约束

---

## 更多示例

- [examples/coverage/](../coverage/) - 功能覆盖率示例
- 详细文档请参考:
  - [场景1：生成随机激励](../../docs/scenarios/01-generate-random.md) - 快速上手
  - [随机化完整参考](../../docs/reference/randomization.md) - API详细说明
  - [产品功能清单](../../docs/product/features.md)
