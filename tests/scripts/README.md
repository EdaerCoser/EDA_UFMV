# 测试验证脚本

这个目录包含了用于验证特定功能和场景的测试脚本。

## 可用脚本

### test_constraints_verify.py
验证约束系统的功能，包括：
- 简单约束
- 复杂约束
- 约束组合

```bash
python tests/scripts/test_constraints_verify.py
```

### test_install_verify.py
验证包的安装是否正确。

```bash
python tests/scripts/test_install_verify.py
```

### test_venv_demo.py / test_venv_demo_simple.py
虚拟环境演示脚本，展示如何在不同环境中使用 EDA_UFMV。

```bash
python tests/scripts/test_venv_demo.py
python tests/scripts/test_venv_demo_simple.py
```

## 用途

这些脚本主要用于：
- **功能验证**: 确保特定功能正常工作
- **环境测试**: 验证在不同环境中的兼容性
- **演示使用**: 展示 API 的使用方法
- **快速诊断**: 快速检查系统状态

## 与 pytest 测试的区别

| 特性 | pytest 测试 | 验证脚本 |
|------|-------------|----------|
| 位置 | tests/*/ | tests/scripts/ |
| 用途 | 单元测试、集成测试 | 功能验证、演示 |
| 运行方式 | pytest 命令 | 直接运行 Python |
| 断言 | 使用 assert | 打印输出 |
| 报告 | pytest 报告 | 自定义输出 |

## 运行所有验证脚本

```bash
cd tests/scripts
for script in test_*.py; do
    echo "Running $script..."
    python "$script"
    echo "---"
done
```

## 注意事项

- 这些脚本不替代 pytest 测试套件
- 它们主要用于开发验证和演示
- 要运行完整的测试套件，请使用项目根目录下的 scripts/ 中的脚本
