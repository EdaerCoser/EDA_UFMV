"""
使用SV Randomizer求解五元一次不等式组

示例问题：
求解满足以下条件的五元组 (x1, x2, x3, x4, x5)：

约束条件：
1. x1 + x2 + x3 + x4 + x5 < 100
2. x1 > 0, x2 > 0, x3 > 0, x4 > 0, x5 > 0
3. x1 >= x2 >= x3 >= x4 >= x5 (递减序列)
4. x1 + x2 > 50
5. x4 + x5 < 20
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import Randomizable, RandVar, VarType
from sv_randomizer.constraints.base import ExpressionConstraint
from sv_randomizer.constraints.expressions import (
    VariableExpr, ConstantExpr, BinaryExpr, BinaryOp
)


class FiveVariableInequality(Randomizable):
    """五元一次不等式求解器"""

    def __init__(self):
        super().__init__()

        # 定义5个变量：x1, x2, x3, x4, x5
        # 范围：1-99
        for i in range(1, 6):
            var_name = f"x{i}"
            self._rand_vars[var_name] = RandVar(
                var_name,
                VarType.INT,
                min_val=1,
                max_val=99
            )

        # 定义约束

        # 约束1: x1 + x2 + x3 + x4 + x5 < 100
        sum_expr = VariableExpr("x1")
        for var in ["x2", "x3", "x4", "x5"]:
            sum_expr = BinaryExpr(sum_expr, BinaryOp.ADD, VariableExpr(var))

        constraint1 = ExpressionConstraint(
            "sum_less_than_100",
            BinaryExpr(sum_expr, BinaryOp.LT, ConstantExpr(100))
        )
        self.add_constraint(constraint1)

        # 约束2: 所有变量 > 0
        for i in range(1, 6):
            c = ExpressionConstraint(
                f"x{i}_positive",
                BinaryExpr(VariableExpr(f"x{i}"), BinaryOp.GT, ConstantExpr(0))
            )
            self.add_constraint(c)

        # 约束3: x1 >= x2 >= x3 >= x4 >= x5 (递减序列)
        self.add_constraint(ExpressionConstraint(
            "x1_ge_x2",
            BinaryExpr(VariableExpr("x1"), BinaryOp.GE, VariableExpr("x2"))
        ))
        self.add_constraint(ExpressionConstraint(
            "x2_ge_x3",
            BinaryExpr(VariableExpr("x2"), BinaryOp.GE, VariableExpr("x3"))
        ))
        self.add_constraint(ExpressionConstraint(
            "x3_ge_x4",
            BinaryExpr(VariableExpr("x3"), BinaryOp.GE, VariableExpr("x4"))
        ))
        self.add_constraint(ExpressionConstraint(
            "x4_ge_x5",
            BinaryExpr(VariableExpr("x4"), BinaryOp.GE, VariableExpr("x5"))
        ))

        # 约束4: x1 + x2 > 50
        x1_x2_sum = BinaryExpr(VariableExpr("x1"), BinaryOp.ADD, VariableExpr("x2"))
        self.add_constraint(ExpressionConstraint(
            "x1_x2_greater_than_50",
            BinaryExpr(x1_x2_sum, BinaryOp.GT, ConstantExpr(50))
        ))

        # 约束5: x4 + x5 < 20
        x4_x5_sum = BinaryExpr(VariableExpr("x4"), BinaryOp.ADD, VariableExpr("x5"))
        self.add_constraint(ExpressionConstraint(
            "x4_x5_less_than_20",
            BinaryExpr(x4_x5_sum, BinaryOp.LT, ConstantExpr(20))
        ))


def solve_and_display():
    """求解并显示结果"""
    print("=" * 70)
    print("五元一次不等式求解")
    print("=" * 70)
    print("\n问题：求解满足以下条件的五元组 (x1, x2, x3, x4, x5)")
    print()
    print("约束条件：")
    print("  1. x1 + x2 + x3 + x4 + x5 < 100")
    print("  2. x1, x2, x3, x4, x5 > 0")
    print("  3. x1 >= x2 >= x3 >= x4 >= x5 (递减序列)")
    print("  4. x1 + x2 > 50")
    print("  5. x4 + x5 < 20")
    print()
    print("=" * 70)
    print()

    solver = FiveVariableInequality()

    print("求解中...\n")

    # 生成10个解
    solutions = []
    for i in range(50):  # 尝试50次，收集成功的解
        if solver.randomize():
            # 验证约束
            total = solver.x1 + solver.x2 + solver.x3 + solver.x4 + solver.x5
            valid = (
                total < 100 and
                solver.x1 > 0 and solver.x2 > 0 and solver.x3 > 0 and
                solver.x4 > 0 and solver.x5 > 0 and
                solver.x1 >= solver.x2 >= solver.x3 >= solver.x4 >= solver.x5 and
                solver.x1 + solver.x2 > 50 and
                solver.x4 + solver.x5 < 20
            )

            if valid:
                solution = {
                    'x1': solver.x1, 'x2': solver.x2, 'x3': solver.x3,
                    'x4': solver.x4, 'x5': solver.x5, 'sum': total
                }
                if solution not in solutions:
                    solutions.append(solution)

            if len(solutions) >= 10:
                break

    # 显示结果
    if solutions:
        print(f"找到 {len(solutions)} 个不同的解：\n")
        for i, sol in enumerate(solutions[:10], 1):
            print(f"解 {i}:")
            print(f"  (x1, x2, x3, x4, x5) = ({sol['x1']:2d}, {sol['x2']:2d}, {sol['x3']:2d}, {sol['x4']:2d}, {sol['x5']:2d})")
            print(f"  验证:")
            print(f"    总和 = {sol['sum']} < 100 [OK]")
            print(f"    递减 = {sol['x1']} >= {sol['x2']} >= {sol['x3']} >= {sol['x4']} >= {sol['x5']} [OK]")
            print(f"    x1+x2 = {sol['x1']+sol['x2']} > 50 [OK]")
            print(f"    x4+x5 = {sol['x4']+sol['x5']} < 20 [OK]")
            print()
    else:
        print("未找到满足条件的解（可能需要更多迭代或调整约束）")

    print("=" * 70)


def solve_custom_inequality():
    """自定义不等式求解示例"""
    print("\n" + "=" * 70)
    print("自定义不等式求解")
    print("=" * 70)
    print("\n示例：求 2a + 3b - c < 50，其中 a>0, b>0, c>0, a<b<c\n")

    class CustomInequality(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['a'] = RandVar('a', VarType.INT, min_val=1, max_val=30)
            self._rand_vars['b'] = RandVar('b', VarType.INT, min_val=1, max_val=30)
            self._rand_vars['c'] = RandVar('c', VarType.INT, min_val=1, max_val=50)

            # 2a + 3b - c < 50
            expr = BinaryExpr(
                BinaryExpr(
                    BinaryExpr(ConstantExpr(2), BinaryOp.MUL, VariableExpr('a')),
                    BinaryOp.ADD,
                    BinaryExpr(ConstantExpr(3), BinaryOp.MUL, VariableExpr('b'))
                ),
                BinaryOp.SUB,
                VariableExpr('c')
            )
            self.add_constraint(ExpressionConstraint("main", BinaryExpr(expr, BinaryOp.LT, ConstantExpr(50))))

            # a < b < c
            self.add_constraint(ExpressionConstraint("a_lt_b", BinaryExpr(VariableExpr('a'), BinaryOp.LT, VariableExpr('b'))))
            self.add_constraint(ExpressionConstraint("b_lt_c", BinaryExpr(VariableExpr('b'), BinaryOp.LT, VariableExpr('c'))))

    solver = CustomInequality()

    print("找到的解：")
    for i in range(10):
        if solver.randomize():
            result = 2 * solver.a + 3 * solver.b - solver.c
            print(f"  a={solver.a:2d}, b={solver.b:2d}, c={solver.c:2d} => 2a+3b-c = {result} < 50 [OK]")

    print("=" * 70)


if __name__ == "__main__":
    solve_and_display()
    solve_custom_inequality()
