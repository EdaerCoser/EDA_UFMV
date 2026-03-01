"""
完整功能测试示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import Randomizable, RandVar, RandCVar, VarType
from sv_randomizer.constraints.base import ExpressionConstraint
from sv_randomizer.constraints.expressions import (
    VariableExpr, ConstantExpr, BinaryExpr, BinaryOp
)
from sv_randomizer.constraints.builders import InsideConstraint
from sv_randomizer.formatters import VerilogFormatter


def test_basic_randomization():
    """测试基础随机化"""
    print("=" * 60)
    print("Test 1: Basic Randomization")
    print("=" * 60)

    class SimpleCounter(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['value'] = RandVar('value', VarType.INT, min_val=0, max_val=100)

    counter = SimpleCounter()
    for i in range(5):
        counter.randomize()
        print(f"  Counter {i+1}: {counter.value}")
    print()


def test_randc_unique_cycle():
    """测试randc循环随机（不重复）"""
    print("=" * 60)
    print("Test 2: RandC Unique Cycle")
    print("=" * 60)

    class UniqueID(Randomizable):
        def __init__(self):
            super().__init__()
            # 3位 = 8个可能值
            self._randc_vars['id'] = RandCVar('id', VarType.BIT, bit_width=3)

    uid = UniqueID()

    print("  Generating 8 unique IDs:")
    seen = set()
    for i in range(8):
        uid.randomize()
        seen.add(uid.id)
        print(f"    ID {i+1}: {uid.id}", end="  ")
        if (i + 1) % 4 == 0:
            print()

    print(f"\n  Unique count: {len(seen)}/8")

    # 第9个应该开始重复
    uid.randomize()
    print(f"  ID 9 (should repeat): {uid.id} in seen: {uid.id in seen}")
    print()


def test_constraints():
    """测试约束功能"""
    print("=" * 60)
    print("Test 3: Constraints")
    print("=" * 60)

    class ConstrainedValue(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

            # 添加约束: x 必须是偶数
            expr = BinaryExpr(
                VariableExpr('x'),
                BinaryOp.MOD,
                ConstantExpr(2)
            )
            eq_expr = BinaryExpr(expr, BinaryOp.EQ, ConstantExpr(0))
            self.add_constraint(ExpressionConstraint("even_only", eq_expr))

    cv = ConstrainedValue()

    print("  Generating 10 even numbers (0-100):")
    for i in range(10):
        cv.randomize()
        is_even = (cv.x % 2 == 0)
        print(f"    Value {i+1}: {cv.x:3d} (even: {is_even})")
    print()


def test_inside_constraint():
    """测试inside约束"""
    print("=" * 60)
    print("Test 4: Inside Constraint")
    print("=" * 60)

    class RangedValue(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['addr'] = RandVar('addr', VarType.INT, min_val=0, max_val=1000)

            # 添加inside约束: addr 在 [0:100] 或 [500:600] 或 900
            self.add_constraint(InsideConstraint("addr_range", "addr", [(0, 100), (500, 600), 900]))

    rv = RangedValue()

    print("  Generating values with inside constraint:")
    for i in range(10):
        rv.randomize()
        in_range = (0 <= rv.addr <= 100) or (500 <= rv.addr <= 600) or (rv.addr == 900)
        print(f"    Value {i+1}: {rv.addr:4d} (in range: {in_range})")
    print()


def test_verilog_output():
    """测试Verilog格式输出"""
    print("=" * 60)
    print("Test 5: Verilog Output")
    print("=" * 60)

    class DataPacket(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['src_addr'] = RandVar('src_addr', VarType.BIT, bit_width=8, min_val=0, max_val=255)
            self._rand_vars['dst_addr'] = RandVar('dst_addr', VarType.BIT, bit_width=8, min_val=0, max_val=255)
            self._rand_vars['data'] = RandVar('data', VarType.BIT, bit_width=16, min_val=0, max_val=65535)
            self._randc_vars['pkt_id'] = RandCVar('pkt_id', VarType.BIT, bit_width=4)

    pkt = DataPacket()
    formatter = VerilogFormatter()

    for i in range(3):
        pkt.randomize()
        print(f"  Packet {i+1}:")
        print(f"    src=0x{pkt.src_addr:02x}, dst=0x{pkt.dst_addr:02x}, data=0x{pkt.data:04x}, id={pkt.pkt_id}")

        verilog = formatter.format(pkt)
        print(f"    Verilog:")
        for line in verilog.split('\n'):
            print(f"      {line}")
    print()


def test_solver_backends():
    """测试求解器后端"""
    print("=" * 60)
    print("Test 6: Solver Backends")
    print("=" * 60)

    from sv_randomizer.solvers import SolverFactory

    print(f"  Available backends: {SolverFactory.list_backends()}")
    print(f"  Default backend: {SolverFactory.get_default_backend()}")

    # 测试PurePython后端
    print(f"\n  Testing PurePython backend:")

    class TestValue(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=50)

    tv = TestValue()
    tv.set_solver_backend("pure_python")

    for i in range(5):
        tv.randomize()
        print(f"    Value {i+1}: {tv.x}")

    # 检查Z3是否可用
    if SolverFactory.is_backend_available("z3"):
        print(f"\n  Z3 backend is available!")
        tv.set_solver_backend("z3")
        for i in range(5):
            tv.randomize()
            print(f"    Value {i+1}: {tv.x}")
    else:
        print(f"\n  Z3 backend not available (install with: pip install z3-solver)")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SV Randomizer - Complete Feature Test")
    print("=" * 60)
    print()

    test_basic_randomization()
    test_randc_unique_cycle()
    test_constraints()
    test_inside_constraint()
    test_verilog_output()
    test_solver_backends()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
