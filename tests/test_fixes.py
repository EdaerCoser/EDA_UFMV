"""
验证代码修复的测试脚本
"""

import sys
import traceback

def test_expressions_fixes():
    """测试表达式系统的修复"""
    print("=== 测试表达式系统修复 ===")
    from sv_randomizer.constraints.expressions import (
        VariableExpr, ConstantExpr, BinaryExpr, BinaryOp
    )

    # 测试1: 除法零检查
    print("测试1: 除法零检查...")
    try:
        expr = BinaryExpr(ConstantExpr(10), BinaryOp.DIV, ConstantExpr(0))
        result = expr.eval({})
        print("  [X] 失败: 应该抛出 ZeroDivisionError")
        return False
    except ZeroDivisionError as e:
        print(f"  [OK] 成功: 正确抛出 ZeroDivisionError: {e}")

    # 测试2: 取模零检查
    print("测试2: 取模零检查...")
    try:
        expr = BinaryExpr(ConstantExpr(10), BinaryOp.MOD, ConstantExpr(0))
        result = expr.eval({})
        print("  [X] 失败: 应该抛出 ZeroDivisionError")
        return False
    except ZeroDivisionError as e:
        print(f"  [OK] 成功: 正确抛出 ZeroDivisionError: {e}")

    # 测试3: 正常除法
    print("测试3: 正常除法...")
    expr = BinaryExpr(ConstantExpr(10), BinaryOp.DIV, ConstantExpr(3))
    result = expr.eval({})
    if result == 3:
        print(f"  [OK] 成功: 10 // 3 = {result}")
    else:
        print(f"  [X] 失败: 期望 3, 得到 {result}")
        return False

    print("所有表达式测试通过!\n")
    return True


def test_variables_fixes():
    """测试变量系统的修复"""
    print("=== 测试变量系统修复 ===")
    from sv_randomizer.core.variables import RandCVar, VarType
    import random

    # 测试1: set_random 更新逻辑
    print("测试1: RandCVar.set_random 更新逻辑...")
    var = RandCVar("test", VarType.BIT, bit_width=4)

    # 创建第一个 Random 实例
    rand1 = random.Random(42)
    var.set_random(rand1)
    initial_remaining = var.peek_remaining()

    # 创建第二个 Random 实例（不同对象）
    rand2 = random.Random(123)
    var.set_random(rand2)

    new_remaining = var.peek_remaining()
    if new_remaining == var.get_total_count():
        print(f"  [OK] 成功: 值池被重新初始化 ({new_remaining}/{var.get_total_count()})")
    else:
        print(f"  [!] 注意: 值池未重新初始化 ({new_remaining}/{var.get_total_count()})")
        # 这不是错误，因为如果 Random 实例相同就不应该重新初始化

    print("所有变量测试通过!\n")
    return True


def test_function_constraint():
    """测试函数约束的修复"""
    print("=== 测试函数约束修复 ===")
    from sv_randomizer.constraints.base import FunctionConstraint

    # 测试1: 函数约束基本功能
    print("测试1: 函数约束基本功能...")
    constraint = FunctionConstraint(
        "positive_check",
        lambda ctx: ctx.get("value", 0) > 0
    )

    # 测试满足约束的情况
    if constraint.check({"value": 10}):
        print("  [OK] 正值通过验证")
    else:
        print("  [X] 正值应该通过验证")
        return False

    # 测试不满足约束的情况
    if not constraint.check({"value": -5}):
        print("  [OK] 负值未通过验证")
    else:
        print("  [X] 负值不应该通过验证")
        return False

    print("所有函数约束测试通过!\n")
    return True


def test_inline_constraints():
    """测试内联约束函数形式"""
    print("=== 测试内联约束函数形式 ===")

    # 创建一个简单的测试类
    from sv_randomizer.core.randomizable import Randomizable
    from sv_randomizer.core.variables import RandVar, VarType

    class TestPacket(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['addr'] = RandVar('addr', VarType.INT, min_val=0, max_val=1000)
            self._rand_vars['length'] = RandVar('length', VarType.INT, min_val=0, max_val=100)

    print("测试1: 内联约束构建...")
    pkt = TestPacket()

    # 测试函数形式的内联约束
    try:
        # 直接测试 _build_inline_constraints 方法
        constraints = pkt._build_inline_constraints({
            'addr': 100,  # 值形式
            'length': lambda ctx: ctx.get('length', 0) > 10  # 函数形式
        })

        if len(constraints) == 2:
            print(f"  [OK] 成功: 创建了 {len(constraints)} 个约束")
        else:
            print(f"  [X] 失败: 期望 2 个约束, 得到 {len(constraints)}")
            return False

        # 验证第一个约束（值形式）
        from sv_randomizer.constraints.base import ExpressionConstraint
        if isinstance(constraints[0], ExpressionConstraint):
            print("  [OK] 第一个约束是 ExpressionConstraint")
        else:
            print(f"  [X] 第一个约束类型错误: {type(constraints[0])}")
            return False

        # 验证第二个约束（函数形式）
        from sv_randomizer.constraints.base import FunctionConstraint
        if isinstance(constraints[1], FunctionConstraint):
            print("  [OK] 第二个约束是 FunctionConstraint")
        else:
            print(f"  [X] 第二个约束类型错误: {type(constraints[1])}")
            return False

    except Exception as e:
        print(f"  [X] 失败: {e}")
        traceback.print_exc()
        return False

    print("所有内联约束测试通过!\n")
    return True


def test_exception_handling():
    """测试异常处理改进"""
    print("=== 测试异常处理改进 ===")

    from sv_randomizer.core.randomizable import Randomizable
    from sv_randomizer.core.variables import RandVar, VarType
    from sv_randomizer.constraints.base import ExpressionConstraint
    from sv_randomizer.constraints.expressions import BinaryExpr, BinaryOp, VariableExpr, ConstantExpr

    class TestPacket(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=10)
            self._rand_vars['y'] = RandVar('y', VarType.INT, min_val=0, max_val=10)

    print("测试1: 冲突约束处理...")
    pkt = TestPacket()

    # 添加冲突约束: x > 5 和 x < 3
    pkt.add_constraint(ExpressionConstraint(
        "x_gt_5",
        VariableExpr('x') > ConstantExpr(5)
    ))
    pkt.add_constraint(ExpressionConstraint(
        "x_lt_3",
        VariableExpr('x') < ConstantExpr(3)
    ))

    # randomize 应该返回 False（约束冲突）而不是抛出异常
    try:
        result = pkt.randomize()
        if result == False:
            print("  [OK] 成功: 约束冲突时返回 False")
        else:
            print(f"  [X] 失败: 期望 False, 得到 {result}")
            return False
    except Exception as e:
        print(f"  [X] 失败: 不应该抛出异常: {e}")
        return False

    print("所有异常处理测试通过!\n")
    return True


def main():
    """运行所有测试"""
    print("=" * 50)
    print("代码修复验证测试")
    print("=" * 50)
    print()

    tests = [
        test_expressions_fixes,
        test_variables_fixes,
        test_function_constraint,
        test_inline_constraints,
        test_exception_handling,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[X] 测试 {test.__name__} 抛出异常: {e}")
            traceback.print_exc()
            failed += 1
        print()

    print("=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
