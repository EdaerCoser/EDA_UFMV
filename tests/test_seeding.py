"""
随机种子功能单元测试
"""

import pytest
import sys
import os

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import (
    Randomizable, RandVar, RandCVar, VarType,
    set_global_seed, get_global_seed, reset_global_seed
)
from sv_randomizer.constraints.base import ExpressionConstraint
from sv_randomizer.constraints.expressions import (
    VariableExpr, ConstantExpr, BinaryExpr, BinaryOp
)
from sv_randomizer.constraints.builders import DistConstraint


def test_same_seed_same_sequence():
    """测试相同种子产生相同序列"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj1 = TestObj(seed=42)
    values1 = []
    for _ in range(10):
        obj1.randomize()
        values1.append(obj1.x)

    obj2 = TestObj(seed=42)
    values2 = []
    for _ in range(10):
        obj2.randomize()
        values2.append(obj2.x)

    assert values1 == values2, f"序列不匹配: {values1} vs {values2}"
    print("[OK] test_same_seed_same_sequence 通过")


def test_different_seed_different_sequence():
    """测试不同种子产生不同序列"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj1 = TestObj(seed=42)
    values1 = []
    for _ in range(10):
        obj1.randomize()
        values1.append(obj1.x)

    obj2 = TestObj(seed=123)
    values2 = []
    for _ in range(10):
        obj2.randomize()
        values2.append(obj2.x)

    assert values1 != values2, f"序列不应相同: {values1}"
    print("[OK] test_different_seed_different_sequence 通过")


def test_global_seed():
    """测试全局种子功能"""
    reset_global_seed()
    set_global_seed(42)

    class TestObj(Randomizable):
        def __init__(self):
            super().__init__()  # 使用全局种子
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj1 = TestObj()
    obj1.randomize()
    value1 = obj1.x

    # 重置并创建新对象
    reset_global_seed()
    set_global_seed(42)
    obj2 = TestObj()
    obj2.randomize()
    value2 = obj2.x

    assert value1 == value2, f"全局种子失效: {value1} != {value2}"
    print("[OK] test_global_seed 通过")

    # 清理
    reset_global_seed()


def test_temporary_seed_no_side_effect():
    """测试临时种子不影响对象状态"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj = TestObj(seed=42)

    # 正常randomize
    obj.randomize()
    value1 = obj.x

    # 使用临时种子
    obj.randomize(seed=123)
    value2 = obj.x

    # 恢复正常
    obj.randomize()
    value3 = obj.x

    # 再次使用相同临时种子
    obj.randomize(seed=123)
    value4 = obj.x

    assert value2 == value4, f"临时种子不一致: {value2} != {value4}"
    print("[OK] test_temporary_seed_no_side_effect 通过")


def test_randc_with_seed():
    """测试RandCVar的种子支持"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._randc_vars['id'] = RandCVar('id', VarType.BIT, bit_width=3)

    obj1 = TestObj(seed=42)
    values1 = []
    for _ in range(8):
        obj1.randomize()
        values1.append(obj1.id)

    obj2 = TestObj(seed=42)
    values2 = []
    for _ in range(8):
        obj2.randomize()
        values2.append(obj2.id)

    assert values1 == values2, f"RandC序列不匹配: {values1} vs {values2}"
    assert len(set(values1)) == 8, f"RandC应有8个唯一值: {values1}"
    print("[OK] test_randc_with_seed 通过")


def test_randc_full_cycle():
    """测试RandCVar完整循环"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._randc_vars['id'] = RandCVar('id', VarType.BIT, bit_width=3)

    obj = TestObj(seed=42)

    # 生成8个值，应全部不重复
    seen = set()
    for _ in range(8):
        obj.randomize()
        seen.add(obj.id)

    assert len(seen) == 8, f"RandC应有8个唯一值: {seen}"

    # 第9个值应该开始重复
    obj.randomize()
    assert obj.id in seen, f"第9个值应在之前出现过: {obj.id}"
    print("[OK] test_randc_full_cycle 通过")


def test_solver_backend_with_seed():
    """测试PurePythonBackend的种子功能"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)
            self._rand_vars['y'] = RandVar('y', VarType.INT, min_val=0, max_val=100)

            # 添加约束: x + y < 100
            expr = BinaryExpr(
                BinaryExpr(VariableExpr('x'), BinaryOp.ADD, VariableExpr('y')),
                BinaryOp.LT,
                ConstantExpr(100)
            )
            self.add_constraint(ExpressionConstraint("sum_constraint", expr))

    obj1 = TestObj(seed=42)
    values1 = []
    for _ in range(10):
        obj1.randomize()
        values1.append((obj1.x, obj1.y))

    obj2 = TestObj(seed=42)
    values2 = []
    for _ in range(10):
        obj2.randomize()
        values2.append((obj2.x, obj2.y))

    assert values1 == values2, f"带约束的序列不匹配"
    # 验证所有解满足约束
    for x, y in values1:
        assert x + y < 100, f"约束违反: {x} + {y} >= 100"
    print("[OK] test_solver_backend_with_seed 通过")


def test_set_seed_method():
    """测试set_seed方法"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj = TestObj()

    # 设置种子并生成值
    obj.set_seed(42)
    obj.randomize()
    value1 = obj.x

    # 重置并使用相同种子
    obj.set_seed(42)
    obj.randomize()
    value2 = obj.x

    assert value1 == value2, f"set_seed失效: {value1} != {value2}"
    print("[OK] test_set_seed_method 通过")


def test_get_seed_method():
    """测试get_seed方法"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj1 = TestObj(seed=42)
    assert obj1.get_seed() == 42, "get_seed应返回42"

    obj2 = TestObj()  # 无种子
    assert obj2.get_seed() is None, "get_seed应返回None"

    obj2.set_seed(123)
    assert obj2.get_seed() == 123, "get_seed应返回123"
    print("[OK] test_get_seed_method 通过")


def test_get_random_method():
    """测试get_random方法"""
    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=100)

    obj = TestObj(seed=42)
    rand1 = obj.get_random()
    value1 = rand1.randint(0, 100)

    # 同一对象应返回相同的Random实例
    rand2 = obj.get_random()
    value2 = rand2.randint(0, 100)

    # Random实例应该是同一个（对象引用相同）
    assert rand1 is rand2, "get_random应返回同一实例"
    print("[OK] test_get_random_method 通过")


def test_no_seed_reproducibility():
    """测试无种子时的不可重复性（使用系统熵）"""
    import random as python_random

    class TestObj(Randomizable):
        def __init__(self, seed=None):
            super().__init__(seed=seed)
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=1000000)

    # 使用大范围增加不重复概率
    obj = TestObj()

    # 生成多个值
    values = []
    for _ in range(20):
        obj.randomize()
        values.append(obj.x)

    # 验证至少有一些不同的值（极不可能全部相同）
    unique_count = len(set(values))
    assert unique_count > 1, f"无种子时应生成不同值: {values}"
    print(f"[OK] test_no_seed_reproducibility 通过 (生成了{unique_count}个唯一值)")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("随机种子功能测试套件")
    print("=" * 60)
    print()

    tests = [
        test_same_seed_same_sequence,
        test_different_seed_different_sequence,
        test_global_seed,
        test_temporary_seed_no_side_effect,
        test_randc_with_seed,
        test_randc_full_cycle,
        test_solver_backend_with_seed,
        test_set_seed_method,
        test_get_seed_method,
        test_get_random_method,
        test_no_seed_reproducibility,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test_func.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"[FAIL] {test_func.__name__} 错误: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
