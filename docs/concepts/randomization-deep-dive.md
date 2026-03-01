# 随机化深入

本文档深入解释EDA_UFMV随机化系统的技术实现细节。

---

## 核心内容

详细的随机化实现文档请参考：[randomization.md](../reference/randomization.md)

### 快速导航

- **约束求解算法**: [参考文档第4节](../reference/randomization.md)
- **双求解器架构**: PurePython + Z3
- **性能优化**: [参考文档第6节](../reference/randomization.md)
- **设计模式**: 策略、装饰器、工厂模式

---

## 相关文档

- [场景1：生成随机激励](../scenarios/01-generate-random.md) - 快速上手
- [SV→Python映射](sv-to-python-mapping.md) - 概念对照
