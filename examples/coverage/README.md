# 覆盖率系统示例

本目录包含EDA_UFVM功能覆盖率系统的使用示例。

---

## 示例文件

### basic_coverage.py - 基础示例

演示覆盖率系统的基本用法：

- CoverGroup和CoverPoint定义
- 范围bins（range bins）
- 值bins（value bins）
- 忽略bins（ignore bins）
- 自动采样和报告生成

**运行**：
```bash
python basic_coverage.py
```

### advanced_coverage.py - 高级示例

演示覆盖率系统的高级功能：

- 装饰器风格定义（SystemVerilog语法）
- 自动分箱（auto bins）
- 通配符bins（wildcard bins）
- 非法bins（illegal bins）
- 多覆盖率组管理
- 启用/禁用控制

**运行**：
```bash
python advanced_coverage.py
```

---

## SystemVerilog到Python快速参考

| SystemVerilog | Python | 说明 |
|:---|:---|:---|
| `covergroup name;` | `CoverGroup("name")` | 定义覆盖率组 |
| `coverpoint var;` | `CoverPoint("var", "var")` | 定义覆盖点 |
| `bins b[] = {[0:255]};` | `bins={"ranges": [[0,255]]}` | 范围bins |
| `cross cp1, cp2;` | `Cross("name", ["cp1","cp2"])` | 交叉覆盖 |
| `ignore_bins b = {0};` | `ignore_bins={"b": [0]}` | 忽略bins |

**完整语法对照**: [SystemVerilog迁移指南](../../docs/reference/coverage/migration.md)

---

## 更多信息

- [场景2：收集功能覆盖率](../../docs/scenarios/02-collect-coverage.md) - 快速上手
- [SV→Python概念映射](../../docs/concepts/sv-to-python-mapping.md) - 概念对照
- [覆盖率迁移详细参考](../../docs/reference/coverage/migration.md) - SV迁移详解
- [单元测试](../../tests/test_coverage/)
