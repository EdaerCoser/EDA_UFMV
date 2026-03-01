"""
六元一次方程组约束求解测试

测试复杂约束下的随机化，并验证种子功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import (
    Randomizable, RandVar, VarType,
    set_global_seed, get_global_seed, reset_global_seed
)
from sv_randomizer.constraints.base import ExpressionConstraint
from sv_randomizer.constraints.expressions import (
    VariableExpr, ConstantExpr, BinaryExpr, BinaryOp
)


class SixVariableSystem(Randomizable):
    """
    六元一次方程组求解器

    变量：x1, x2, x3, x4, x5, x6
    取值范围：约1000左右
    """

    def __init__(self, seed=None):
        super().__init__(seed=seed)

        # 定义6个变量，范围在0-2000之间
        for i in range(1, 7):
            var_name = f"x{i}"
            self._rand_vars[var_name] = RandVar(
                var_name,
                VarType.INT,
                min_val=0,
                max_val=2000
            )

        # 约束1: 所有变量 > 100
        for i in range(1, 7):
            var_name = f"x{i}"
            expr = BinaryExpr(
                VariableExpr(var_name),
                BinaryOp.GT,
                ConstantExpr(100)
            )
            self.add_constraint(ExpressionConstraint(f"{var_name}_gt_100", expr))

        # 约束2: x1 + x2 + x3 + x4 + x5 + x6 < 6000
        sum_expr = VariableExpr("x1")
        for var in ["x2", "x3", "x4", "x5", "x6"]:
            sum_expr = BinaryExpr(sum_expr, BinaryOp.ADD, VariableExpr(var))

        constraint_sum = BinaryExpr(sum_expr, BinaryOp.LT, ConstantExpr(6000))
        self.add_constraint(ExpressionConstraint("sum_lt_6000", constraint_sum))

        # 约束3: x1 + x2 > 1000
        x1_x2_sum = BinaryExpr(
            VariableExpr("x1"),
            BinaryOp.ADD,
            VariableExpr("x2")
        )
        constraint_x1_x2 = BinaryExpr(x1_x2_sum, BinaryOp.GT, ConstantExpr(1000))
        self.add_constraint(ExpressionConstraint("x1_x2_gt_1000", constraint_x1_x2))

        # 约束4: x5 * x6 < 500000
        x5_x6_product = BinaryExpr(
            VariableExpr("x5"),
            BinaryOp.MUL,
            VariableExpr("x6")
        )
        constraint_x5_x6 = BinaryExpr(x5_x6_product, BinaryOp.LT, ConstantExpr(500000))
        self.add_constraint(ExpressionConstraint("x5_x6_lt_500k", constraint_x5_x6))

        # 约束5: x3 >= x4 >= x5 (递减序列)
        self.add_constraint(ExpressionConstraint(
            "x3_ge_x4",
            BinaryExpr(VariableExpr("x3"), BinaryOp.GE, VariableExpr("x4"))
        ))
        self.add_constraint(ExpressionConstraint(
            "x4_ge_x5",
            BinaryExpr(VariableExpr("x4"), BinaryOp.GE, VariableExpr("x5"))
        ))

        # 约束6: x6 在 [200, 800] 范围内
        x6_ge_200 = BinaryExpr(VariableExpr("x6"), BinaryOp.GE, ConstantExpr(200))
        x6_le_800 = BinaryExpr(VariableExpr("x6"), BinaryOp.LE, ConstantExpr(800))
        x6_range = BinaryExpr(x6_ge_200, BinaryOp.AND, x6_le_800)
        self.add_constraint(ExpressionConstraint("x6_range", x6_range))


def test_with_seed(seed_value, num_solutions=5):
    """使用指定种子生成解"""
    print(f"\n使用种子 {seed_value} 生成 {num_solutions} 个解:")
    print("=" * 70)

    solver = SixVariableSystem(seed=seed_value)

    solutions = []
    attempts = 0
    max_attempts = 200

    while len(solutions) < num_solutions and attempts < max_attempts:
        attempts += 1
        if solver.randomize():
            # 验证所有约束
            total = solver.x1 + solver.x2 + solver.x3 + solver.x4 + solver.x5 + solver.x6
            valid = (
                solver.x1 > 100 and solver.x2 > 100 and solver.x3 > 100 and
                solver.x4 > 100 and solver.x5 > 100 and solver.x6 > 100 and
                total < 6000 and
                solver.x1 + solver.x2 > 1000 and
                solver.x5 * solver.x6 < 500000 and
                solver.x3 >= solver.x4 >= solver.x5 and
                200 <= solver.x6 <= 800
            )

            if valid:
                solution = {
                    'x1': solver.x1, 'x2': solver.x2, 'x3': solver.x3,
                    'x4': solver.x4, 'x5': solver.x5, 'x6': solver.x6,
                    'sum': total,
                    'x1+x2': solver.x1 + solver.x2,
                    'x5*x6': solver.x5 * solver.x6
                }
                solutions.append(solution)

    # 显示结果
    if solutions:
        for i, sol in enumerate(solutions, 1):
            print(f"\n解 {i}:")
            print(f"  (x1, x2, x3, x4, x5, x6) = "
                  f"({sol['x1']:4d}, {sol['x2']:4d}, {sol['x3']:4d}, "
                  f"{sol['x4']:4d}, {sol['x5']:4d}, {sol['x6']:4d})")
            print(f"  验证:")
            print(f"    总和 = {sol['sum']} < 6000")
            print(f"    x1+x2 = {sol['x1+x2']} > 1000")
            print(f"    x5*x6 = {sol['x5*x6']} < 500000")
            print(f"    递减 = {sol['x3']} >= {sol['x4']} >= {sol['x5']}")
            print(f"    x6范围 = 200 <= {sol['x6']} <= 800")
    else:
        print("未找到满足条件的解")

    print(f"\n尝试次数: {attempts}, 成功: {len(solutions)}")
    return solutions


def test_reproducibility():
    """测试可重现性"""
    print("\n" + "=" * 70)
    print("可重现性测试：相同种子应产生相同结果")
    print("=" * 70)

    seed = 12345

    # 第一次生成
    print(f"\n第一次运行（种子={seed}）:")
    solutions1 = test_with_seed(seed, num_solutions=3)

    # 第二次生成（使用相同种子）
    print(f"\n第二次运行（种子={seed}）:")
    solutions2 = test_with_seed(seed, num_solutions=3)

    # 验证一致性
    print("\n验证结果:")
    if len(solutions1) == len(solutions2) and len(solutions1) > 0:
        all_match = True
        for i, (s1, s2) in enumerate(zip(solutions1, solutions2), 1):
            match = (
                s1['x1'] == s2['x1'] and
                s1['x2'] == s2['x2'] and
                s1['x3'] == s2['x3'] and
                s1['x4'] == s2['x4'] and
                s1['x5'] == s2['x5'] and
                s1['x6'] == s2['x6']
            )
            status = "[OK]" if match else "[FAIL]"
            print(f"  解{i} 匹配: {status}")
            if not match:
                print(f"    第一次: {s1}")
                print(f"    第二次: {s2}")
                all_match = False

        if all_match:
            print("\n[成功] 所有解都完全匹配！种子功能正常工作")
        else:
            print("\n[失败] 存在不匹配的解")
    else:
        print("[失败] 解数量不一致或无解")


def main():
    print("=" * 70)
    print("六元一次方程组约束求解测试")
    print("=" * 70)

    print("\n问题定义:")
    print("  变量: x1, x2, x3, x4, x5, x6")
    print("  取值范围: [0, 2000]")
    print("\n约束条件:")
    print("  1. 所有变量 > 100")
    print("  2. x1 + x2 + x3 + x4 + x5 + x6 < 6000")
    print("  3. x1 + x2 > 1000")
    print("  4. x5 * x6 < 500000")
    print("  5. x3 >= x4 >= x5 (递减序列)")
    print("  6. 200 <= x6 <= 800")

    # 测试三个不同的种子
    seeds = [11111, 22222, 33333]

    for seed in seeds:
        test_with_seed(seed, num_solutions=3)

    # 测试可重现性
    test_reproducibility()

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
