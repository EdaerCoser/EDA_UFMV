# 随机化示例

本目录包含EDA_UFMV的随机化和约束系统使用示例。

## 示例文件

| 示例文件 | 说明 | 功能点 |
|:---|:---|:---|
| `simple_test.py` | 简单随机变量示例 | 基础rand/randc变量使用 |
| `packet_generator.py` | 数据包生成示例 | 约束系统和随机化组合 |
| `seed_demo.py` | 随机种子控制演示 | 种子管理和可重现性 |
| `test_six_variables.py` | 六元方程组约束求解 | 复杂约束系统验证 |
| `solve_inequalities.py` | 不等式求解 | Inside约束使用 |

## 运行示例

```bash
# 运行所有示例
python examples/rand/simple_test.py
python examples/rand/packet_generator.py
python examples/rand/seed_demo.py
python examples/rand/test_six_variables.py
python examples/rand/solve_inequalities.py
```

## 示例说明

### 1. simple_test.py

最简单的随机化示例，演示：
- 创建Randomizable类
- 定义rand和randc变量
- 执行randomize()

### 2. packet_generator.py

数据包生成示例，演示：
- 多个随机变量组合
- 地址约束
- 循环随机变量（randc）

### 3. seed_demo.py

种子控制演示，展示：
- 全局种子设置
- 对象级种子
- 临时种子
- 可重现性验证

### 4. test_six_variables.py

六元方程组测试，验证：
- 复杂约束求解
- 多变量约束系统
- 求解器性能

### 5. solve_inequalities.py

不等式求解示例，包含：
- Inside约束使用
- 范围约束
- 多种约束组合

## 更多示例

- `examples/coverage/` - 功能覆盖率示例（规划中v0.2.0）
- `examples/rgm/` - 寄存器模型示例（规划中v0.3.0）
- `examples/parser/` - DUT解析示例（规划中v0.5.0）
- `examples/enhanced_rand/` - 覆盖率引导随机化（规划中v0.4.0）

详细文档请参考：
- [产品说明书 - 随机化系统](../../docs/product/PRODUCT_MANUAL.md)
- [用户指南](../../docs/product/USER_GUIDE.md)（规划中）
