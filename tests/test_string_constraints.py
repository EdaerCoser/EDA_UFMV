"""
字符串约束系统综合测试

验证新的字符串表达式约束功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import Randomizable, rand, randc, constraint


def test_basic_string_constraint():
    """测试基本字符串约束"""
    print("=== Test 1: Basic String Constraints ===")

    class TestPacket(Randomizable):
        @rand(min_val=0, max_val=100)
        def x(self):
            return 0

        @constraint("gt_10", "x > 10")
        def gt_10_c(self):
            pass

    pkt = TestPacket()
    for i in range(10):
        pkt.randomize()
        assert pkt.x > 10, f"x={pkt.x} should be > 10"
    print("  PASS: x > 10 constraint works")


def test_complex_string_constraint():
    """测试复杂字符串约束"""
    print("=== Test 2: Complex String Constraints ===")

    class TestPacket(Randomizable):
        @rand(min_val=0, max_val=1000)
        def addr(self):
            return 0

        @rand(min_val=0, max_val=1000)
        def data(self):
            return 0

        @rand(min_val=0, max_val=100)
        def length(self):
            return 0

        @constraint("valid", "addr >= 0x100 && addr <= 0xFFFF && data < 500 && length > 10")
        def valid_c(self):
            pass

    pkt = TestPacket()
    for i in range(20):
        success = pkt.randomize()
        if success:
            assert pkt.addr >= 0x100, f"addr={pkt.addr} should be >= 0x100"
            assert pkt.addr <= 0xFFFF, f"addr={pkt.addr} should be <= 0xFFFF"
            assert pkt.data < 500, f"data={pkt.data} should be < 500"
            assert pkt.length > 10, f"length={pkt.length} should be > 10"

    print("  PASS: Complex constraint works")


def test_logical_operators():
    """测试逻辑运算符"""
    print("=== Test 3: Logical Operators ===")

    class TestPacket(Randomizable):
        @rand(min_val=0, max_val=100)
        def x(self):
            return 0

        @rand(min_val=0, max_val=100)
        def y(self):
            return 0

        @rand(min_val=0, max_val=100)
        def z(self):
            return 0

        @constraint("and_test", "x > 10 && y > 10 && z > 10")
        def and_c(self):
            pass

    pkt = TestPacket()
    for i in range(10):
        pkt.randomize()
        assert pkt.x > 10 and pkt.y > 10 and pkt.z > 10

    print("  PASS: Logical AND works")

    class TestPacket2(Randomizable):
        @rand(min_val=0, max_val=100)
        def x(self):
            return 0

        @constraint("or_test", "x < 10 || x > 90")
        def or_c(self):
            pass

    pkt2 = TestPacket2()
    for i in range(10):
        pkt2.randomize()
        assert pkt2.x < 10 or pkt2.x > 90

    print("  PASS: Logical OR works")


def test_arithmetic_operators():
    """测试算术运算符"""
    print("=== Test 4: Arithmetic Operators ===")

    class TestPacket(Randomizable):
        @rand(min_val=0, max_val=100)
        def x(self):
            return 0

        @rand(min_val=0, max_val=100)
        def y(self):
            return 0

        @constraint("sum_constraint", "x + y < 100")
        def sum_c(self):
            pass

    pkt = TestPacket()
    for i in range(10):
        pkt.randomize()
        assert pkt.x + pkt.y < 100

    print("  PASS: Arithmetic operators work")


def test_backward_compatibility():
    """测试向后兼容性"""
    print("=== Test 5: Backward Compatibility ===")

    from sv_randomizer.api import VarProxy

    class OldStyle(Randomizable):
        @rand(min_val=0, max_val=100)
        def x(self):
            return 0

        @constraint("old_style")
        def old_c(self):
            return VarProxy("x") > 10

    pkt = OldStyle()
    for i in range(5):
        pkt.randomize()
        assert pkt.x > 10

    print("  PASS: Old function-style constraints still work")


def test_mixed_constraints():
    """测试混合约束"""
    print("=== Test 6: Mixed Constraints ===")

    class MixedPacket(Randomizable):
        @rand(min_val=0, max_val=100)
        def x(self):
            return 0

        @rand(min_val=0, max_val=100)
        def y(self):
            return 0

        # 字符串约束
        @constraint("str_c", "x > 10")
        def str_c(self):
            pass

        # 函数约束
        @constraint("func_c")
        def func_c(self):
            from sv_randomizer.api import VarProxy
            return VarProxy("y") < 90

    pkt = MixedPacket()
    for i in range(10):
        pkt.randomize()
        assert pkt.x > 10 and pkt.y < 90

    print("  PASS: Mixed string and function constraints work")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("String Constraint System - Comprehensive Tests")
    print("=" * 60)
    print()

    try:
        test_basic_string_constraint()
        test_complex_string_constraint()
        test_logical_operators()
        test_arithmetic_operators()
        test_backward_compatibility()
        test_mixed_constraints()

        print()
        print("=" * 60)
        print("All tests PASSED!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"Test FAILED: {e}")
        print("=" * 60)
        return False
    except Exception as e:
        print()
        print("=" * 60)
        print(f"Test ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
