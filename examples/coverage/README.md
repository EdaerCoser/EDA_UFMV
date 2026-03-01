# 覆盖率系统示例

本目录包含EDA_UFMV功能覆盖率系统的使用示例。

## 示例文件

### 1. basic_coverage.py - 基础示例

演示覆盖率系统的基本用法：

- 定义CoverGroup和CoverPoint
- 使用范围bins（range bins）
- 使用值bins（value bins）
- 使用忽略bins（ignore bins）
- 自动采样覆盖率
- 生成覆盖率报告

**运行**：
```bash
python basic_coverage.py
```

### 2. advanced_coverage.py - 高级示例

演示覆盖率系统的高级功能：

- 使用装饰器定义覆盖率（SystemVerilog语法风格）
- 自动分箱（auto bins）
- 通配符bins（wildcard bins）
- 非法bins（illegal bins）
- 多个覆盖率组管理
- 权重分配
- 手动采样
- 启用/禁用CoverGroup和CoverPoint

**运行**：
```bash
python advanced_coverage.py
```

## SystemVerilog到Python语法映射

| SystemVerilog | Python | 说明 |
|:---|:---|:---|
| `covergroup name;` | `CoverGroup("name")` | 定义覆盖率组 |
| `coverpoint var;` | `CoverPoint("var", sample_expr="var")` | 定义覆盖点 |
| `bins b = {1,2,3};` | `bins={"values": [1,2,3]}` | 值bins |
| `bins b[] = {[0:255]};` | `bins={"ranges": [[0,255]]}` | 范围bins |
| `wildcard bins b[] = {8???};` | `bins={"wildcards": ["8???"]}` | 通配符bins |
| `auto_bin_max = 16` | `bins={"auto": 16}` | 自动分箱 |
| `ignore_bins b = {0};` | `ignore_bins={"b": [0]}` | 忽略bins |
| `illegal_bins b = {255};` | `illegal_bins={"b": [255]}` | 非法bins |
| `option.weight = 2.0` | `weight=2.0` | 权重 |
| `cg.sample()` | `cg.sample(**kwargs)` | 手动采样 |

## 更多信息

- API文档：../../docs/product/PRODUCT_MANUAL.md
- 开发计划：../../docs/development/ROADMAP.md
- 单元测试：../../tests/test_coverage/
