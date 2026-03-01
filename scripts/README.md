# 测试运行脚本

这个目录包含了用于运行不同测试套件的便捷脚本。

## 可用脚本

### run_all_tests.py
运行所有测试套件（包括随机化、覆盖率、RGM等）。

```bash
python scripts/run_all_tests.py
```

### run_api_tests.py
运行 v0.3.1 新 API 的集成测试。

```bash
python scripts/run_api_tests.py
```

### run_rgm_tests.py
运行寄存器模型系统（RGM）的测试。

```bash
python scripts/run_rgm_tests.py
```

### run_stress_test.py
运行摸高测试（压力测试）。

```bash
python scripts/run_stress_test.py
```

### run_test_complex_protocols.py
运行复杂协议测试（AXI、UART、DMA）。

```bash
python scripts/run_test_complex_protocols.py
```

## 使用建议

- **日常开发**: 使用 `run_api_tests.py` 快速验证 API 功能
- **完整验证**: 使用 `run_all_tests.py` 运行所有测试
- **性能测试**: 使用 `run_stress_test.py` 进行压力测试
- **特定模块**: 使用对应的模块测试脚本

## 注意事项

这些脚本是为了方便使用而提供的包装器。你也可以直接使用 pytest：

```bash
# 运行所有 API 测试
pytest tests/test_api/ -v

# 运行特定测试文件
pytest tests/test_api/test_complex_protocols.py -v

# 包含慢速测试
pytest tests/test_api/ -v --include-slow
```

## 环境变量

如果在 Windows 上遇到 pytest-qt 插件问题，可以使用：

```bash
# Linux/macOS
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

# Windows CMD
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

# Windows PowerShell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1=1
```

或者脚本会自动处理这个问题。
