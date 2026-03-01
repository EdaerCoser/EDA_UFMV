"""
数据包生成示例 - 新API版本

演示如何使用SV Randomizer v0.3+的新类型注解API生成随机网络数据包
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc, constraint
from sv_randomizer.formatters import VerilogFormatter


class Packet(Randomizable):
    """
    网络数据包类 - 使用新API

    包含以下字段：
    - src_addr: 源地址 (16位)
    - dest_addr: 目标地址 (16位)
    - length: 数据长度 (8位)
    - packet_id: 包ID (randc, 4位，确保0-15不重复)
    """

    # 变量声明 - 使用类型注解
    src_addr: rand[int](bits=16, min=0x1000, max=0xFFFF)
    dest_addr: rand[int](bits=16)
    length: rand[int](bits=8, min=64, max=1500)
    packet_id: randc[int](bits=4)

    # 约束 - 使用原生Python表达式
    @constraint
    def addr_not_equal(self):
        """源地址和目标地址不能相同"""
        return self.src_addr != self.dest_addr

    @constraint
    def valid_length_range(self):
        """长度必须在有效范围内"""
        return (self.length == 64 or
                self.length == 128 or
                self.length == 256 or
                (512 <= self.length <= 1518))

    def pre_randomize(self):
        """随机化前回调"""
        pass

    def post_randomize(self):
        """随机化后回调"""
        pass


def generate_packets(num_packets: int = 10):
    """
    生成随机数据包

    Args:
        num_packets: 要生成的数据包数量
    """
    print(f"Generating {num_packets} random packets...\n")

    pkt = Packet()
    formatter = VerilogFormatter()

    for i in range(num_packets):
        success = pkt.randomize()

        if success:
            print(f"Packet {i + 1}:")
            print(f"  Src Addr:    0x{pkt.src_addr:04x}")
            print(f"  Dest Addr:   0x{pkt.dest_addr:04x}")
            print(f"  Length:      {pkt.length}")
            print(f"  Packet ID:   {pkt.packet_id}")

            # 输出Verilog格式
            verilog = formatter.format(pkt)
            print(f"  Verilog:")
            for line in verilog.split("\n"):
                print(f"    {line}")
            print()
        else:
            print(f"Failed to randomize packet {i + 1}\n")


def generate_verilog_testbench(num_packets: int = 5):
    """
    生成完整的Verilog testbench

    Args:
        num_packets: 测试向量数量
    """
    print(f"Generating Verilog testbench with {num_packets} vectors...\n")

    packets = []
    for _ in range(num_packets):
        pkt = Packet()
        if pkt.randomize():
            packets.append(pkt)

    formatter = VerilogFormatter()
    testbench = formatter.format_testbench(packets[0], test_name="packet_test")

    print(testbench)


def demonstrate_constraints():
    """演示约束的使用"""
    print("=== Demonstrating Constraints ===\n")

    # 1. 基础随机化
    print("1. Basic randomization:")
    pkt = Packet()
    pkt.randomize()
    print(f"   Addr: 0x{pkt.src_addr:04x}, ID: {pkt.packet_id}\n")

    # 2. 使用内联约束
    print("2. With inline constraint (src_addr = 0x2000):")
    pkt.randomize(with_constraints={"src_addr": 0x2000})
    print(f"   Addr: 0x{pkt.src_addr:04x}\n")

    # 3. 禁用约束
    print("3. With addr_not_equal constraint disabled:")
    pkt.constraint_mode("addr_not_equal", False)
    pkt.randomize()
    print(f"   Src: 0x{pkt.src_addr:04x}, Dest: 0x{pkt.dest_addr:04x}")
    print(f"   Are they equal? {pkt.src_addr == pkt.dest_addr}\n")

    # 4. 验证randc循环
    print("4. Demonstrating randc (4-bit = 16 unique values):")
    pkt2 = Packet()
    seen = set()
    for i in range(16):
        pkt2.randomize()
        seen.add(pkt2.packet_id)
        print(f"   ID: {pkt2.packet_id}", end="  ")
        if (i + 1) % 8 == 0:
            print()
    print(f"\n   Unique IDs: {len(seen)}")


def demonstrate_seed_control():
    """演示seed控制"""
    print("\n=== Demonstrating Seed Control ===\n")

    # 设置全局seed
    seed(42)
    print("1. Using global seed(42):")
    pkt1 = Packet()
    pkt1.randomize()
    print(f"   Addr: 0x{pkt1.src_addr:04x}")

    seed(42)
    pkt2 = Packet()
    pkt2.randomize()
    print(f"   Addr: 0x{pkt2.src_addr:04x} (same seed, same value)")

    # 使用实例级seed
    print("\n2. Using instance-level seed:")
    pkt3 = Packet()
    pkt3.randomize(seed=100)
    print(f"   Addr: 0x{pkt3.src_addr:04x}")

    pkt3.randomize(seed=100)
    print(f"   Addr: 0x{pkt3.src_addr:04x} (same seed, same value)")


if __name__ == "__main__":
    print("=" * 60)
    print("SV Randomizer - Packet Generator Example (New API)")
    print("=" * 60)
    print()

    # 生成数据包
    generate_packets(5)

    print("\n" + "=" * 60)
    print()

    # 生成Verilog testbench
    generate_verilog_testbench(3)

    print("\n" + "=" * 60)
    print()

    # 演示约束
    demonstrate_constraints()

    # 演示seed控制
    demonstrate_seed_control()

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
