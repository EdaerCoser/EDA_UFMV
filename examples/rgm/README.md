# RGM 寄存器模型示例

本目录包含EDA_UFVM RGM (Register Model) 系统的使用示例。

## 示例列表

### 基础示例

| 示例文件 | 说明 | 主要功能 |
|:---|:---|:---|
| [basic_rgm_example.py](basic_rgm_example.py) | RGM基础用法 | Field, Register, RegisterBlock, 访问类型 |
| [code_generator_example.py](code_generator_example.py) | 代码生成器 | Verilog, C, Python代码生成 |

### 硬件访问示例

| 示例文件 | 说明 | 主要功能 |
|:---|:---|:---|
| [axi_access_example.py](axi_access_example.py) | AXI总线访问 | AXIAdapter, FrontDoor |
| [ssh_access_example.py](ssh_access_example.py) | SSH远程访问 | SSHAdapter, 远程单板访问 |

## 快速开始

```bash
cd examples/rgm
python basic_rgm_example.py
```

## 参考文档

- [场景3：创建寄存器模型](../../docs/scenarios/03-create-regmodel.md) - 快速上手
- [RGM用户指南](../../docs/product/RGM_GUIDE.md)
- [SSH适配器指南](../../docs/reference/rgm/SSH_ADAPTER_GUIDE.md)
