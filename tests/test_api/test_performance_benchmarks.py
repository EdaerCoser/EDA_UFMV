"""
性能基准测试

测试不同规模下的随机化速度和约束求解性能
"""

import pytest
import time
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint
from .helpers.performance_utils import measure_randomization_rate
from .helpers.scenario_generators import create_n_vars_object


class TestRandomizationSpeed:
    """随机化速度测试"""

    @pytest.mark.parametrize("num_vars,expected_min_rate", [
        (5, 10000),
        (10, 5000),
        (15, 2000),
        (20, 1000),
    ])
    def test_randomization_rate(self, num_vars, expected_min_rate):
        """测试不同规模的随机化速度"""
        cls = create_n_vars_object(num_vars)
        obj = cls()

        iterations = 1000
        rate = measure_randomization_rate(obj, iterations)

        print(f"  {num_vars}变量: {rate:.0f} 次/秒")
        assert rate >= expected_min_rate, f"性能不达标: {rate:.0f} < {expected_min_rate}"


class TestConstraintSolvingTime:
    """约束求解时间测试"""

    def test_simple_constraint_time(self):
        """测试简单约束求解时间"""
        x_rand = rand(int)(bits=8, min=0, max=100)

        class SimpleConstraint(Randomizable):
            x: x_rand

            @constraint
            def positive(self):
                return self.x > 50

        obj = SimpleConstraint()
        iterations = 1000

        start = time.time()
        for _ in range(iterations):
            obj.randomize()
        elapsed = time.time() - start

        avg_time = elapsed / iterations
        print(f"  简单约束: {avg_time*1000:.3f}ms/次")
        assert elapsed < 0.1, f"超时: {elapsed:.3f}秒 > 0.1秒"

    def test_medium_constraint_time(self):
        """测试中等约束求解时间"""
        vars = [rand(int)(bits=8, min=0, max=100) for _ in range(10)]

        class MediumConstraint(Randomizable):
            x: vars[0]
            y: vars[1]
            z: vars[2]

            @constraint
            def sum_limit(self):
                return self.x + self.y + self.z < 200

            @constraint
            def ordering(self):
                return self.x < self.y < self.z

        obj = MediumConstraint()
        iterations = 500

        start = time.time()
        for _ in range(iterations):
            obj.randomize()
        elapsed = time.time() - start

        avg_time = elapsed / iterations
        print(f"  中等约束: {avg_time*1000:.3f}ms/次")
        assert elapsed < 0.2, f"超时: {elapsed:.3f}秒 > 0.2秒"

    def test_complex_constraint_time(self):
        """测试复杂约束求解时间"""
        vars = [rand(int)(bits=8, min=0, max=100) for _ in range(20)]

        class ComplexConstraint(Randomizable):
            x: vars[0]
            y: vars[1]
            z: vars[2]
            a: vars[3]
            b: vars[4]

            @constraint
            def complex_logic(self):
                return (self.x > 10 and self.y < 50 and self.z > 20)

            @constraint
            def combined(self):
                return (self.x + self.y < 150) and (self.z > self.x)

            @constraint
            def multi_var(self):
                return (self.a + self.b < 200) and (self.a > self.b)

        obj = ComplexConstraint()
        iterations = 100

        start = time.time()
        for _ in range(iterations):
            obj.randomize()
        elapsed = time.time() - start

        avg_time = elapsed / iterations
        print(f"  复杂约束: {avg_time*1000:.3f}ms/次")
        assert elapsed < 0.5, f"超时: {elapsed:.3f}秒 > 0.5秒"


class TestPerformanceReport:
    """性能报告生成测试"""

    def test_generate_performance_report(self):
        """生成详细性能报告"""
        results = {}

        # 测试小规模
        obj_small = create_n_vars_object(5)
        results['small'] = {'rate': measure_randomization_rate(obj_small(), 1000)}

        # 测试中等规模
        obj_medium = create_n_vars_object(15)
        results['medium'] = {'rate': measure_randomization_rate(obj_medium(), 500)}

        # 测试大规模
        obj_large = create_n_vars_object(30)
        results['large'] = {'rate': measure_randomization_rate(obj_large(), 100)}

        # 输出报告
        print("\n" + "="*60)
        print("性能测试报告")
        print("="*60)
        print("\n随机化速度:")
        for scale, data in results.items():
            print(f"  {scale:15s}: {data['rate']:>6.0f} 次/秒")
        print("="*60)
