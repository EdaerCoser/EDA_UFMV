"""
简单测试示例 - 验证基本功能

使用装饰器 API 和字符串约束语法
"""

import sys
import os
# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sv_randomizer import Randomizable, rand, randc, constraint


class SimplePacket(Randomizable):
    """简单的数据包类 - 使用装饰器 API"""

    @rand(bit_width=16, min_val=0, max_val=65535)
    def addr(self):
        """16位地址"""
        return 0

    @randc(bit_width=4)
    def id(self):
        """4位循环ID (0-15，遍历完才重复)"""
        return 0


def test_basic_randomization():
    """测试基础随机化"""
    print("=== Test 1: Basic Randomization ===")
    pkt = SimplePacket()

    for i in range(5):
        success = pkt.randomize()
        if success:
            print(f"  Packet {i+1}: addr={pkt.addr}, id={pkt.id}")
        else:
            print(f"  Packet {i+1}: FAILED")
    print()


def test_randc_cycle():
    """测试randc循环"""
    print("=== Test 2: RandC Cycle (4-bit = 16 values) ===")
    pkt = SimplePacket()

    seen = set()
    for i in range(16):
        pkt.randomize()
        seen.add(pkt.id)
        print(f"  ID {i+1}: {pkt.id}", end="  ")
        if (i + 1) % 8 == 0:
            print()

    print(f"\n  Unique values: {len(seen)}")
    print()


def test_with_constraints():
    """测试带约束的随机化 - 使用字符串约束语法"""
    print("=== Test 3: With String Constraints ===")

    class ConstrainedPacket(Randomizable):
        @rand(min_val=0, max_val=100)
        def x(self):
            return 0

        @rand(min_val=0, max_val=100)
        def y(self):
            return 0

        # 字符串约束语法 (新)
        @constraint('sum_constraint', 'x + y < 100')
        def sum_c(self):
            pass

    pkt = ConstrainedPacket()

    for i in range(10):
        if pkt.randomize():
            print(f"  x={pkt.x}, y={pkt.y}, sum={pkt.x + pkt.y} (should be < 100)")
        else:
            print(f"  FAILED to randomize")
    print()


def test_complex_constraints():
    """测试复杂约束"""
    print("=== Test 4: Complex String Constraints ===")

    class ComplexPacket(Randomizable):
        @rand(min_val=0, max_val=1000)
        def addr(self):
            return 0

        @rand(min_val=0, max_val=1000)
        def data(self):
            return 0

        @rand(min_val=0, max_val=100)
        def length(self):
            return 0

        # 多条件约束
        @constraint('valid', 'addr >= 0x100 && addr <= 0xFFFF && data < 500 && length > 10')
        def valid_c(self):
            pass

    pkt = ComplexPacket()

    for i in range(5):
        if pkt.randomize():
            print(f"  addr=0x{pkt.addr:04x}, data={pkt.data}, length={pkt.length}")
        else:
            print(f"  FAILED to randomize")
    print()


if __name__ == "__main__":
    test_basic_randomization()
    test_randc_cycle()
    test_with_constraints()
    test_complex_constraints()

    print("\n=== All tests completed ===")
