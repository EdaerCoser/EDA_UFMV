"""
Pytest配置和共享fixtures
"""

import pytest
from .helpers.scenario_generators import create_n_vars_object


@pytest.fixture(scope="session")
def performance_baseline():
    """性能基线对象（会话级，所有测试共享）"""
    from .helpers.performance_utils import PerformanceBaseline
    return PerformanceBaseline()


@pytest.fixture
def small_object():
    """小规模测试对象（5变量）"""
    return create_n_vars_object(5)


@pytest.fixture
def medium_object():
    """中规模测试对象（15变量）"""
    return create_n_vars_object(15)


@pytest.fixture
def large_object():
    """大规模测试对象（30变量）"""
    return create_n_vars_object(30)


@pytest.fixture
def stress_object():
    """压力测试对象（50变量）"""
    return create_n_vars_object(50)


@pytest.fixture
def simple_5var():
    """5变量简单对象（实例）"""
    cls = create_n_vars_object(5)
    return cls()


@pytest.fixture
def complex_15var():
    """15变量对象（实例）"""
    cls = create_n_vars_object(15)
    return cls()


@pytest.fixture
def complex_30var():
    """30变量对象（实例）"""
    cls = create_n_vars_object(30)
    return cls()
