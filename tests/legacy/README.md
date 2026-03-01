# 遗留测试

本目录包含v0.1.0版本的单元测试，保持向后兼容。

**测试文件**：
- `test_variables.py` - 随机变量系统测试
- `test_constraints.py` - 约束系统测试
- `test_seeding.py` - 种子管理测试

**运行方式**：
```bash
# 运行所有遗留测试
python -m pytest tests/legacy/ -v

# 或直接运行
python tests/legacy/test_variables.py
python tests/legacy/test_constraints.py
python tests/legacy/test_seeding.py
```

**测试覆盖**：
- 36个单元测试
- 100%通过率
- 基础功能验证
