"""
简单测试示例 - 验证基本功能

使用新类型注解 API 和原生Python表达式约束
"""

import sys
import os
# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sv_randomizer import Randomizable
from sv_randomizer.api import rand, randc, constraint


class SimplePacket(Randomizable):
    """简单的数据包类 - 使用新类型注解API"""

    addr: rand[int](bits=16, min=0, max=65535)
    id: randc[int](bits=4)


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
    """测试带约束的随机化 - 使用原生Python表达式"""
    print("=== Test 3: With Native Python Constraints ===")

    x_rand = rand(int)(min=0, max=100)
    y_rand = rand(int)(min=0, max=100)

    class ConstrainedPacket(Randomizable):
        x: x_rand
        y: y_rand

        @constraint
        def sum_constraint(self):
            return self.x + self.y < 100

    pkt = ConstrainedPacket()

    for i in range(10):
        if pkt.randomize():
            print(f"  x={pkt.x}, y={pkt.y}, sum={pkt.x + pkt.y} (should be < 100)")
        else:
            print(f"  FAILED to randomize")
    print()


def test_complex_constraints():
    """测试复杂约束"""
    print("=== Test 4: Complex Native Python Constraints ===")

    addr_rand = rand(int)(min=0, max=1000)
    data_rand = rand(int)(min=0, max=1000)
    length_rand = rand(int)(min=0, max=100)

    class ComplexPacket(Randomizable):
        addr: addr_rand
        data: data_rand
        length: length_rand

        @constraint
        def valid(self):
            return self.addr >= 0x100 and self.addr <= 0xFFFF and self.data < 500 and self.length > 10

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
