"""
摸高测试 - 寻找系统极限

通过渐进式增加约束复杂度，找出系统的极限能力
"""

import pytest
import time
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint


class StressLevel1(Randomizable):
    """压力级别1: 15变量/5约束"""
    v1 = rand(int)(bits=8)
    v2 = rand(int)(bits=8)
    v3 = rand(int)(bits=8)
    v4 = rand(int)(bits=8)
    v5 = rand(int)(bits=8)
    v6 = rand(int)(bits=8)
    v7 = rand(int)(bits=8)
    v8 = rand(int)(bits=8)
    v9 = rand(int)(bits=8)
    v10 = rand(int)(bits=8)
    v11 = rand(int)(bits=8)
    v12 = rand(int)(bits=8)
    v13 = rand(int)(bits=8)
    v14 = rand(int)(bits=8)
    v15 = rand(int)(bits=8)

    @constraint
    def sum_limit(self):
        return self.v1 + self.v2 < 200

    @constraint
    def ordering(self):
        return self.v3 < self.v4 < self.v5

    @constraint
    def range_check(self):
        return 50 <= self.v6 <= 150

    @constraint
    def weighted_sum(self):
        return self.v7 + 2*self.v8 + 3*self.v9 < 300

    @constraint
    def logical(self):
        return (self.v10 > 20) and (self.v11 < 200)


class StressLevel2(Randomizable):
    """压力级别2: 30变量/10约束"""
    v1 = rand(int)(bits=8)
    # Create 30 variables total
    v2 = rand(int)(bits=8)
    v3 = rand(int)(bits=8)
    v4 = rand(int)(bits=8)
    v5 = rand(int)(bits=8)
    v6 = rand(int)(bits=8)
    v7 = rand(int)(bits=8)
    v8 = rand(int)(bits=8)
    v9 = rand(int)(bits=8)
    v10 = rand(int)(bits=8)
    v11 = rand(int)(bits=8)
    v12 = rand(int)(bits=8)
    v13 = rand(int)(bits=8)
    v14 = rand(int)(bits=8)
    v15 = rand(int)(bits=8)
    v16 = rand(int)(bits=8)
    v17 = rand(int)(bits=8)
    v18 = rand(int)(bits=8)
    v19 = rand(int)(bits=8)
    v20 = rand(int)(bits=8)
    v21 = rand(int)(bits=8)
    v22 = rand(int)(bits=8)
    v23 = rand(int)(bits=8)
    v24 = rand(int)(bits=8)
    v25 = rand(int)(bits=8)
    v26 = rand(int)(bits=8)
    v27 = rand(int)(bits=8)
    v28 = rand(int)(bits=8)
    v29 = rand(int)(bits=8)
    v30 = rand(int)(bits=8)

    @constraint
    def sum_limit(self):
        return self.v1 + self.v2 < 400

    @constraint
    def ordering1(self):
        return self.v3 < self.v4 < self.v5

    @constraint
    def ordering2(self):
        return self.v6 < self.v7 < self.v8

    @constraint
    def range_check(self):
        return 50 <= self.v9 <= 150

    @constraint
    def weighted_sum1(self):
        return self.v10 + 2*self.v11 + 3*self.v12 < 400

    @constraint
    def weighted_sum2(self):
        return self.v13 + 2*self.v14 < 300

    @constraint
    def logical1(self):
        return (self.v15 > 20) and (self.v16 < 200)

    @constraint
    def logical2(self):
        return (self.v17 > 30) or (self.v18 < 100)

    @constraint
    def combined(self):
        return (self.v19 + self.v20 < 250) and (self.v21 > self.v22)


class StressLevel3(Randomizable):
    """压力级别3: 50变量/15约束"""
    # Create 50 variables
    v1 = rand(int)(bits=8)
    v2 = rand(int)(bits=8)
    v3 = rand(int)(bits=8)
    v4 = rand(int)(bits=8)
    v5 = rand(int)(bits=8)
    v6 = rand(int)(bits=8)
    v7 = rand(int)(bits=8)
    v8 = rand(int)(bits=8)
    v9 = rand(int)(bits=8)
    v10 = rand(int)(bits=8)
    v11 = rand(int)(bits=8)
    v12 = rand(int)(bits=8)
    v13 = rand(int)(bits=8)
    v14 = rand(int)(bits=8)
    v15 = rand(int)(bits=8)
    v16 = rand(int)(bits=8)
    v17 = rand(int)(bits=8)
    v18 = rand(int)(bits=8)
    v19 = rand(int)(bits=8)
    v20 = rand(int)(bits=8)
    v21 = rand(int)(bits=8)
    v22 = rand(int)(bits=8)
    v23 = rand(int)(bits=8)
    v24 = rand(int)(bits=8)
    v25 = rand(int)(bits=8)
    v26 = rand(int)(bits=8)
    v27 = rand(int)(bits=8)
    v28 = rand(int)(bits=8)
    v29 = rand(int)(bits=8)
    v30 = rand(int)(bits=8)
    v31 = rand(int)(bits=8)
    v32 = rand(int)(bits=8)
    v33 = rand(int)(bits=8)
    v34 = rand(int)(bits=8)
    v35 = rand(int)(bits=8)
    v36 = rand(int)(bits=8)
    v37 = rand(int)(bits=8)
    v38 = rand(int)(bits=8)
    v39 = rand(int)(bits=8)
    v40 = rand(int)(bits=8)
    v41 = rand(int)(bits=8)
    v42 = rand(int)(bits=8)
    v43 = rand(int)(bits=8)
    v44 = rand(int)(bits=8)
    v45 = rand(int)(bits=8)
    v46 = rand(int)(bits=8)
    v47 = rand(int)(bits=8)
    v48 = rand(int)(bits=8)
    v49 = rand(int)(bits=8)
    v50 = rand(int)(bits=8)

    @constraint
    def sum_limit1(self):
        return self.v1 + self.v2 < 300

    @constraint
    def sum_limit2(self):
        return self.v3 + self.v4 < 300

    @constraint
    def sum_limit3(self):
        return self.v5 + self.v6 < 300

    @constraint
    def ordering1(self):
        return self.v7 < self.v8 < self.v9

    @constraint
    def ordering2(self):
        return self.v10 < self.v11 < self.v12

    @constraint
    def ordering3(self):
        return self.v13 < self.v14 < self.v15

    @constraint
    def range_check1(self):
        return 50 <= self.v16 <= 150

    @constraint
    def range_check2(self):
        return 30 <= self.v17 <= 120

    @constraint
    def range_check3(self):
        return 40 <= self.v18 <= 140

    @constraint
    def weighted_sum1(self):
        return self.v19 + 2*self.v20 + 3*self.v21 < 400

    @constraint
    def weighted_sum2(self):
        return self.v22 + 2*self.v23 < 300

    @constraint
    def weighted_sum3(self):
        return 2*self.v24 + self.v25 < 350

    @constraint
    def logical1(self):
        return (self.v26 > 20) and (self.v27 < 200)

    @constraint
    def logical2(self):
        return (self.v28 > 30) or (self.v29 < 100)

    @constraint
    def combined(self):
        return (self.v30 + self.v31 < 250) and (self.v32 > self.v33)


class TestGradualStress:
    """渐进式压力测试"""

    @pytest.mark.slow
    def test_gradual_stress_from_small_to_large(self):
        """从低到高逐步增加压力"""
        levels = [
            (StressLevel1, "15变量/5约束", 5.0, 10),
            (StressLevel2, "30变量/10约束", 15.0, 5),
            (StressLevel3, "50变量/15约束", 30.0, 3),
        ]

        for cls, desc, timeout, min_success in levels:
            obj = cls()
            start = time.time()

            success_count = 0
            attempts = 0
            max_attempts = 100

            while attempts < max_attempts and (time.time() - start) < timeout:
                if obj.randomize():
                    success_count += 1
                    if success_count >= min_success:
                        break
                attempts += 1

            elapsed = time.time() - start

            print(f"\n{desc}:")
            print(f"  Result: {'PASS' if success_count >= min_success else 'FAIL'}")
            print(f"  Time: {elapsed:.3f}s")
            print(f"  Success: {success_count}/{attempts}")

            if success_count >= min_success:
                assert elapsed < timeout, f"超时: {elapsed:.3f}秒 > {timeout}秒"
            else:
                print(f"  系统极限: {desc}")
                break

    def test_find_system_limit(self):
        """自动寻找系统的极限能力"""
        print("\n开始寻找系统极限...")

        # Test different scales
        test_cases = [
            (10, 3, "10变量"),
            (20, 5, "20变量"),
            (30, 10, "30变量"),
        ]

        for n_vars, n_constraints, desc in test_cases:
            # Use scenario generator
            from .helpers.scenario_generators import create_n_vars_object

            cls = create_n_vars_object(n_vars)

            success_count = 0
            attempts = 0
            max_attempts = 50

            obj = cls()
            for _ in range(max_attempts):
                if obj.randomize():
                    success_count += 1
                attempts += 1

            success_rate = success_count / attempts if attempts > 0 else 0
            print(f"  {desc}: {success_count}/{attempts} 成功 ({success_rate*100:.1f}%)")

            if success_rate < 0.1:  # Less than 10% success rate
                print(f"\n系统极限发现: {desc}")
                break
