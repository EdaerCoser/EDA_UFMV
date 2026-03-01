"""
EDA_UFMV 包功能演示脚本

此脚本演示了如何使用EDA_UFMV的各个模块：
1. Randomization - 随机化功能
2. Coverage - 功能覆盖率
3. RGM - 寄存器模型
4. SV to Python - SV转换器
"""

print("=" * 60)
print("EDA_UFMV v0.3.0 - 功能演示")
print("=" * 60)

# 1. 测试 Randomization 模块
print("\n[1] 测试 Randomization 模块")
print("-" * 60)

from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc, constraint

# 创建类型注解
src_addr_rand = rand(int)(bits=32, min=0x0000_0000, max=0xFFFF_FFFF)
dst_addr_rand = rand(int)(bits=32, min=0x0000_0000, max=0xFFFF_FFFF)
data_len_rand = rand(int)(bits=16, min=0, max=1500)
priority_rand = rand(int)(bits=3, min=0, max=7)

class Packet(Randomizable):
    """简单的数据包类"""
    # 变量声明 - 使用类型注解
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

# 2. 测试 Coverage 模块
print("\n[2] 测试 Coverage 模块")
print("-" * 60)

from coverage import CoverGroup, CoverPoint
from coverage.core.bin import ValueBin

cg = CoverGroup("packet_coverage")

@CoverPoint("addr_cp", cg)
class AddrCoverPoint:
    def __init__(self):
        # 使用值bin
        self.bins = {
            "local": ValueBin("local", lambda: 0x0000_0000 <= packet.src_addr < 0x1000_0000),
            "network": ValueBin("network", lambda: 0x1000_0000 <= packet.src_addr < 0x2000_0000),
        }

# 采样覆盖率
cg.sample()
print(f"[OK] 覆盖率采样: {cg.get_coverage():.1f}%")

# 3. 测试 RGM 模块
print("\n[3] 测试 RGM (Register Model) 模块")
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
print(f"  字段:")
for field in ctrl_reg.get_fields():
    print(f"    - {field.name}: [{field.bit_start}:{field.bit_end}] {field.access_type}")

# 4. 测试 SV to Python 转换器
print("\n[4] 测试 SV to Python 转换器")
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

# 转换示例
result = subprocess.run(
    [sys.executable, "-m", "sv_to_python", "convert",
     "tests/fixtures/uvm_tasks.sv", "--task", "basic_write", "--dry-run"],
    capture_output=True,
    text=True
)
print(f"\n[OK] 转换示例 (basic_write task):")
# 只显示关键部分
lines = result.stdout.split('\n')
for i, line in enumerate(lines):
    if 'def basic_write' in line:
        # 打印函数定义和下一行
        print(f"  {lines[i]}")
        if i+1 < len(lines) and 'Auto-generated' in lines[i+1]:
            print(f"    {lines[i+1]}")
        break

# 5. 完整示例：使用所有模块
print("\n[5] 完整示例：配置DMA并验证")
print("-" * 60)

channel_rand = rand(int)(bits=4, min=0, max=15)
base_addr_rand = rand(int)(bits=32, min=0x1000_0000, max=0xF000_0000)
transfer_len_rand = rand(int)(bits=32, min=64, max=4096)
direction_rand = rand(int)(bits=1, min=0, max=1)

class DMAConfig(Randomizable):
    """DMA配置类"""
    channel: channel_rand
    base_addr: base_addr_rand
    transfer_len: transfer_len_rand
    direction: direction_rand

config = DMAConfig()
config.randomize()

print(f"[OK] 随机生成DMA配置:")
print(f"  通道: {config.channel}")
print(f"  基地址: 0x{config.base_addr:08X}")
print(f"  传输长度: {config.transfer_len} 字节")
print(f"  方向: {'RX' if config.direction else 'TX'}")

print("\n" + "=" * 60)
print("所有模块测试完成！")
print("=" * 60)
print("\n提示:")
print("  - Randomization: 用于硬件激励生成")
print("  - Coverage: 功能覆盖率收集")
print("  - RGM: 寄存器模型定义和访问")
print("  - SV to Python: 自动转换SV任务到Python")
