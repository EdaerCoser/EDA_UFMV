# 覆盖率深入

本文档深入解释EDA_UFMV覆盖率系统的技术实现细节。

---

## 核心内容

详细的覆盖率实现文档请参考：[覆盖率迁移详细参考](../reference/coverage/migration.md)

### 快速导航

- **CoverGroup/CoverPoint/Cross**: 层次结构
- **6种Bin类型**: Value, Range, Wildcard, Auto, Ignore, Illegal
- **数据库后端**: Memory vs File
- **报告生成器**: HTML, JSON, UCIS

---

## 相关文档

- [场景2：收集覆盖率](../scenarios/02-collect-coverage.md) - 快速上手
- [SV→Python映射](sv-to-python-mapping.md) - 语法对照
