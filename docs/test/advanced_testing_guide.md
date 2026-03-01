# 高级测试套件用户指南

## 概述

高级测试套件提供复杂约束测试和性能测试，验证系统在各种场景下的正确性和性能。

**测试覆盖:**

- 复杂约束场景 (5-8变量)
- 硬件协议模拟 (AXI, UART, DMA)
- 摸高测试 (15-50变量)
- 性能基准测试
- 内存和稳定性测试

## 运行测试

### 运行所有高级测试

```bash
pytest tests/test_api/test_complex_*.py tests/test_api/test_performance_*.py -v
```

### 运行特定类别的测试

```bash
# 只运行硬件协议测试
pytest tests/test_api/test_complex_protocols.py -v

# 只运行数学约束测试
pytest tests/test_api/test_complex_constraints.py -v

# 只运行性能基准测试
pytest tests/test_api/test_performance_benchmarks.py -v

# 只运行摸高测试
pytest tests/test_api/test_complex_stress.py -v
```

### 包含慢速测试

某些测试标记为 `@pytest.mark.slow`，默认跳过。运行时使用：

```bash
pytest tests/test_api/ -v --include-slow
```

## 性能基线

基线数据保存在 `tests/test_api/helpers/baseline_data.json`。

### 当前基线值

| 指标 | 值 |
|------|-----|
| 5变量随机化速率 | 41,697 次/秒 |
| 10变量随机化速率 | 31,542 次/秒 |
| 15变量随机化速率 | 25,137 次/秒 |
| 20变量随机化速率 | 19,946 次/秒 |
| 简单约束求解时间 | 0.019 ms |
| 中等约束求解时间 | 0.038 ms |
| 复杂约束求解时间 | 0.066 ms |

### 更新基线

如果系统性能合理提升，可以更新基线：

1. 运行性能测试收集新数据
2. 更新 `baseline_data.json` 中的值
3. 提交更改到版本控制

### 检测性能退化

性能测试会自动检测退化。运行时如果性能下降超过10%，测试会失败。

## 测试场景

### 硬件协议测试

**test_complex_protocols.py** 模拟真实硬件协议：

- **AXI总线事务**: 地址对齐、突发边界检查
- **UART配置**: 波特率与校验位约束
- **DMA传输**: 地址不重叠、对齐约束

### 数学约束测试

**test_complex_constraints.py** 测试高维数学场景：

- **加权约束**: 5-6变量加权和约束
- **资源分配**: 6-8变量资源总和与最小分配
- **逻辑约束**: 8变量不等式系统
- **条件约束**: 7变量条件逻辑

### 摸高测试

**test_complex_stress.py** 寻找系统极限：

- **Level 1**: 15变量/5约束 (~10次/5秒)
- **Level 2**: 30变量/10约束 (~5次/15秒)
- **Level 3**: 50变量/15约束 (~3次/30秒)

## 故障排除

### 测试超时

如果测试超时：

1. 检查系统负载
2. 跳过慢速测试: `pytest -m "not slow"`
3. 减少测试迭代次数

### 性能测试失败

如果性能测试失败：

1. 检查基线数据是否适合当前平台
2. 考虑更新基线（如果性能确实提升）
3. 检查是否有后台进程影响性能

### 内存测试失败

如果内存测试失败：

1. 检查是否有内存泄漏
2. 验证tracemalloc是否正常工作
3. 调整expected_max_mb阈值（如果合理）

## 贡献指南

添加新的测试场景：

1. 在相应的测试文件中添加测试方法
2. 使用适当的约束复杂度
3. 添加清晰的文档字符串
4. 运行所有测试确保没有回归
5. 更新基线数据（如果需要）

## 参考资料

- [设计文档](../../plans/2026-03-01-advanced-testing-design.md)
- [实施计划](../../plans/2026-03-01-advanced-testing-implementation.md)
- [性能基线数据](../tests/test_api/helpers/baseline_data.json)
