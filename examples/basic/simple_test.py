"""
简单测试示例 - 验证基本功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import Randomizable, RandVar, RandCVar, VarType
from sv_randomizer.constraints.base import ExpressionConstraint
from sv_randomizer.constraints.expressions import VariableExpr, ConstantExpr, BinaryExpr, BinaryOp


class SimplePacket(Randomizable):
    """简单的数据包类"""

    def __init__(self):
        super().__init__()
        # 手动创建rand变量
        self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16, min_val=0, max_val=65535)
        self._randc_vars['id'] = RandCVar('id', VarType.BIT, bit_width=4)

    def pre_randomize(self):
        pass

    def post_randomize(self):
        pass


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
    """测试带约束的随机化"""
    print("=== Test 3: With Constraints ===")

    class ConstrainedPacket(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)
            self._rand_vars['y'] = RandVar('y', VarType.INT, min_val=0, max_val=100)

            # 添加约束: x + y < 100
            expr = BinaryExpr(
                BinaryExpr(VariableExpr('x'), BinaryOp.ADD, VariableExpr('y')),
                BinaryOp.LT,
                ConstantExpr(100)
            )
            self.add_constraint(ExpressionConstraint("sum_constraint", expr))

    pkt = ConstrainedPacket()

    for i in range(10):
        if pkt.randomize():
            print(f"  x={pkt.x}, y={pkt.y}, sum={pkt.x + pkt.y} (should be < 100)")
        else:
            print(f"  FAILED to randomize")
    print()


if __name__ == "__main__":
    test_basic_randomization()
    test_randc_cycle()
    test_with_constraints()
