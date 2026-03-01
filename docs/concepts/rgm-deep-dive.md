# RGM深入

本文档深入解释EDA_UFMV寄存器模型系统的技术实现细节。

---

## 核心内容

详细的RGM实现文档请参考：[RGM用户指南](../product/RGM_GUIDE.md)

### 快速导航

- **Field/Register/RegisterBlock**: 三层架构
- **15种访问类型**: RW, RO, WO, RC, RS, W1C等
- **硬件适配器模式**: 远程访问
- **代码生成器**: Verilog/C/Python生成

---

## 相关文档

- [场景3：创建寄存器模型](../scenarios/03-create-regmodel.md) - 快速上手
- [SSH适配器指南](../reference/rgm/SSH_ADAPTER_GUIDE.md) - 远程访问
