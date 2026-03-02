"""
EDA_UFVM 包功能演示脚本（简化版）

演示主要模块的导入和基本功能
"""

print("=" * 60)
print("EDA_UFVM v0.3.0 - 功能演示")
print("=" * 60)

# 1. 测试 Randomization 模块
print("\n[1] 测试 Randomization 模块")
print("-" * 60)

from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc

src_addr_rand = rand(int)(bits=32, min=0x0000_0000, max=0xFFFF_FFFF)
dst_addr_rand = rand(int)(bits=32, min=0x0000_0000, max=0xFFFF_FFFF)
data_len_rand = rand(int)(bits=16, min=0, max=1500)
priority_rand = rand(int)(bits=3, min=0, max=7)

class Packet(Randomizable):
    """简单的数据包类"""
    src_addr: src_addr_rand
    dst_addr: dst_addr_rand
    data_len: data_len_rand
    priority: priority_rand

packet = Packet()
packet.randomize()
print(f"[OK] 随机化数据包:")
print(f"  源地址: 0x{packet.src_addr:08X}")
print(f"  目标地址: 0x{packet.dst_addr:08X}")
print(f"  数据长度: {packet.data_len}")
print(f"  优先级: {packet.priority}")

# 2. 测试 RGM 模块
print("\n[2] 测试 RGM (Register Model) 模块")
print("-" * 60)

from rgm import RegisterBlock, Register, Field, AccessType

# 创建DMA寄存器块
dma_block = RegisterBlock("DMA", base_address=0x4000_0000)

# 创建控制寄存器
ctrl_reg = Register("CTRL", offset=0x00, width=32, reset_value=0x00000000)
ctrl_reg.add_field(Field("ENABLE", 0, 1, AccessType.RW, 0))
ctrl_reg.add_field(Field("START", 1, 1, AccessType.RW, 0))
ctrl_reg.add_field(Field("STOP", 2, 1, AccessType.RW, 0))
ctrl_reg.add_field(Field("RESERVED", 3, 29, AccessType.RO, 0))

dma_block.add_register(ctrl_reg)

print(f"[OK] 创建寄存器块: {dma_block.name} @ 0x{dma_block.base_address:08X}")
print(f"  寄存器: {ctrl_reg.name} @ 0x{ctrl_reg.offset:08X}")
print(f"  字段数: {len(ctrl_reg.get_fields())}")

# 3. 测试 SV to Python 转换器
print("\n[3] 测试 SV to Python 转换器")
print("-" * 60)

import subprocess
import sys

# 列出可用的tasks
result = subprocess.run(
    [sys.executable, "-m", "sv_to_python", "list", "tests/fixtures/uvm_tasks.sv"],
    capture_output=True,
    text=True
)
print("[OK] 可用的 SystemVerilog tasks:")
for line in result.stdout.split('\n')[:10]:
    if line.strip():
        print(f"  {line}")

# 4. 完整示例：配置DMA
print("\n[4] 完整示例：配置DMA")
print("-" * 60)

channel_rand = rand(int)(bits=4, min=0, max=15)
base_addr_rand = rand(int)(bits=32, min=0x1000_0000, max=0xF000_0000)

class DMAConfig(Randomizable):
    """DMA配置类"""
    channel: channel_rand
    base_addr: base_addr_rand

config = DMAConfig()
config.randomize()

print(f"[OK] 随机生成DMA配置:")
print(f"  通道: {config.channel}")
print(f"  基地址: 0x{config.base_addr:08X}")

print("\n" + "=" * 60)
print("模块测试完成！")
print("=" * 60)
print("\n安装位置:")
print(f"  虚拟环境: {sys.prefix}")
print("\n使用提示:")
print("  - Randomization: 用于硬件激励生成")
print("  - RGM: 寄存器模型定义和访问")
print("  - SV to Python: 自动转换SV任务到Python")
print("\nCLI命令:")
print("  python -m sv_to_python list <file.sv>")
print("  python -m sv_to_python convert <file.sv> -o output.py")
