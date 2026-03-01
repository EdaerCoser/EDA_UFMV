"""
数据包生成示例

演示如何使用SV Randomizer生成随机网络数据包
"""

import sys
import os

# 添加父目录到路径以导入sv_randomizer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import Randomizable, rand, randc, constraint, VarProxy, inside, dist
from sv_randomizer.formatters import VerilogFormatter


class Packet(Randomizable):
    """
    网络数据包类

    包含以下字段：
    - src_addr: 源地址 (16位)
    - dest_addr: 目标地址 (16位)
    - length: 数据长度 (8位)
    - packet_id: 包ID (randc, 4位，确保0-15不重复)
    - opcode: 操作码 (枚举)
    """

    def __init__(self):
        super().__init__()

    # 定义rand变量
    @rand(bit_width=16)
    def src_addr(self):
        return 0

    @rand(bit_width=16)
    def dest_addr(self):
        return 0

    @rand(bit_width=8, min_val=0, max_val=1500)
    def length(self):
        return 64

    # 定义randc变量 - 确保ID唯一
    @randc(bit_width=4)
    def packet_id(self):
        return 0

    # 定义枚举类型的rand变量
    @rand(enum_values=["READ", "WRITE", "ACK", "NACK"])
    def opcode(self):
        return "READ"

    # 回调函数
    def pre_randomize(self):
        """随机化前回调"""
        pass

    def post_randomize(self):
        """随机化后回调"""
        pass

    # 定义约束
    @constraint("valid_addr_range")
    def valid_addr_range_c(self):
        """地址范围约束：源地址必须在有效范围内"""
        return (VarProxy("src_addr") >= 0x1000) & (VarProxy("src_addr") <= 0xFFFF)

    @constraint("addr_not_equal")
    def addr_not_equal_c(self):
        """源地址和目标地址不能相同"""
        return VarProxy("src_addr") != VarProxy("dest_addr")

    @constraint("valid_length")
    def valid_length_c(self):
        """长度约束：使用inside约束"""
        return inside([(64, 64), (128, 255), (512, 1518)]) == VarProxy("length")


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
            print(f"  Opcode:      {pkt.opcode}")

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
    print(f"   Addr: 0x{pkt.src_addr:04x}, ID: {pkt.packet_id}, Opcode: {pkt.opcode}\n")

    # 2. 使用内联约束
    print("2. With inline constraint (src_addr = 0x2000):")
    pkt.randomize(with_constraints={"src_addr": 0x2000})
    print(f"   Addr: 0x{pkt.src_addr:04x}\n")

    # 3. 禁用约束
    print("3. With addr_not_equal constraint disabled:")
    pkt.addr_not_equal_c()
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


def demonstrate_solver_backends():
    """演示不同求解器后端"""
    print("\n=== Demonstrating Solver Backends ===\n")

    from sv_randomizer.solvers import SolverFactory

    # 列出可用的后端
    print(f"Available backends: {SolverFactory.list_backends()}")
    print(f"Default backend: {SolverFactory.get_default_backend()}\n")

    # 使用PurePython后端
    print("Using PurePython backend:")
    pkt = Packet()
    pkt.set_solver_backend("pure_python")
    for i in range(3):
        pkt.randomize()
        print(f"  Packet {i+1}: addr=0x{pkt.src_addr:04x}, id={pkt.packet_id}")

    # 尝试使用Z3后端（如果可用）
    if SolverFactory.is_backend_available("z3"):
        print("\nUsing Z3 backend:")
        pkt.set_solver_backend("z3")
        for i in range(3):
            pkt.randomize()
            print(f"  Packet {i+1}: addr=0x{pkt.src_addr:04x}, id={pkt.packet_id}")
    else:
        print("\nZ3 backend not available. Install with: pip install z3-solver")


if __name__ == "__main__":
    print("=" * 60)
    print("SV Randomizer - Packet Generator Example")
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

    # 演示求解器后端
    demonstrate_solver_backends()

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
