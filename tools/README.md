# 工具脚本

本目录包含EDA_UFVM的实用工具脚本。

## 工具列表

### 规划中工具

**benchmark.py** - 性能基准测试工具
- 测试随机化性能
- 对比不同求解器
- 生成性能报告

**coverage_report.py** - 覆盖率报告工具
- 汇总覆盖率数据
- 生成HTML报告
- 导出UCIS格式

**model_generator.py** - 模型生成工具
- 从Verilog生成Python模型
- 从寄存器规格生成RGM代码
- 约束转换工具

### 使用方式

```bash
# 运行性能基准测试
python tools/benchmark.py

# 生成覆盖率报告
python tools/coverage_report.py --input coverage.db --output report.html

# 生成Python模型
python tools/model_generator.py --input dut.v --output dut_model.py
```

## 贡献新工具

欢迎贡献新的实用工具！请参考：
- [贡献指南](../docs/development/CONTRIBUTING.md)（规划中）
- 遵循现有代码风格
- 添加使用文档和测试
