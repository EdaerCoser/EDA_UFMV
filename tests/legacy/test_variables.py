"""
变量系统单元测试
"""

import sys
import os
import unittest

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer.core.variables import RandVar, RandCVar, VarType


class TestRandVar(unittest.TestCase):
    """测试RandVar类"""

    def test_basic_generation(self):
        """测试基本随机值生成"""
        var = RandVar("x", VarType.INT, min_val=0, max_val=100)

        values = set()
        for _ in range(100):
            val = var.generate_unconstrained()
            self.assertGreaterEqual(val, 0)
            self.assertLessEqual(val, 100)
            values.add(val)

        # 应该生成多个不同的值
        self.assertGreater(len(values), 10)

    def test_bit_vector(self):
        """测试位向量类型"""
        var = RandVar("addr", VarType.BIT, bit_width=16)

        for _ in range(10):
            val = var.generate_unconstrained()
            self.assertGreaterEqual(val, 0)
            self.assertLessEqual(val, 0xFFFF)

    def test_enum_type(self):
        """测试枚举类型"""
        enum_vals = ["READ", "WRITE", "ACK", "NACK"]
        var = RandVar("opcode", VarType.ENUM, enum_values=enum_vals)

        for _ in range(20):
            val = var.generate_unconstrained()
            self.assertIn(val, enum_vals)

    def test_get_range(self):
        """测试范围获取"""
        var = RandVar("x", VarType.INT, min_val=10, max_val=100)
        min_val, max_val = var.get_range()
        self.assertEqual(min_val, 10)
        self.assertEqual(max_val, 100)


class TestRandCVar(unittest.TestCase):
    """测试RandCVar类"""

    def test_no_repeat_in_cycle(self):
        """验证randc在完整周期内不重复"""
        var = RandCVar("id", VarType.BIT, bit_width=3)  # 2^3 = 8个可能值

        seen = set()
        for _ in range(8):
            val = var.get_next()
            self.assertNotIn(val, seen, f"重复值: {val}")
            seen.add(val)

        # 应该看到所有8个值
        self.assertEqual(len(seen), 8)

    def test_cycle_repeat(self):
        """验证值池耗尽后重新开始"""
        var = RandCVar("id", VarType.BIT, bit_width=2)  # 4个可能值

        first_cycle = []
        for _ in range(4):
            first_cycle.append(var.get_next())

        # 第5个值应该开始新的循环
        fifth_val = var.get_next()
        # 新循环应该包含之前出现过的值
        self.assertIn(fifth_val, first_cycle)

    def test_peek_remaining(self):
        """测试查看剩余值数量"""
        var = RandCVar("id", VarType.BIT, bit_width=4)  # 16个值

        self.assertEqual(var.peek_remaining(), 16)

        var.get_next()
        self.assertEqual(var.peek_remaining(), 15)

        var.get_next()
        var.get_next()
        self.assertEqual(var.peek_remaining(), 13)

    def test_reset(self):
        """测试重置功能"""
        var = RandCVar("id", VarType.BIT, bit_width=3)

        # 取几个值
        values = []
        for _ in range(3):
            values.append(var.get_next())

        # 重置
        var.reset()

        # 重置后应该又能获得完整的16个值
        self.assertEqual(var.peek_remaining(), 8)

    def test_enum_randc(self):
        """测试枚举类型的randc"""
        enum_vals = ["A", "B", "C"]
        var = RandCVar("mode", VarType.ENUM, enum_values=enum_vals)

        seen = []
        for _ in range(3):
            seen.append(var.get_next())

        # 应该包含所有枚举值
        self.assertEqual(len(set(seen)), 3)
        for val in enum_vals:
            self.assertIn(val, seen)


if __name__ == "__main__":
    unittest.main()
