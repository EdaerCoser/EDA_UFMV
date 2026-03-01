"""
Unit tests for Coverage Database

测试内存数据库和文件数据库的功能。
"""

import pytest
import tempfile
import os
from datetime import datetime

from sv_randomizer.coverage.database import (
    MemoryCoverageDatabase,
    FileCoverageDatabase,
    DatabaseFactory,
    DatabaseError,
    DatabaseMergeError
)


class TestMemoryCoverageDatabase:
    """测试内存数据库"""

    def test_init(self):
        """测试初始化"""
        db = MemoryCoverageDatabase()
        assert db is not None
        assert db.get_statistics()['total_samples'] == 0

    def test_record_sample(self):
        """测试记录采样"""
        db = MemoryCoverageDatabase()

        # 记录单个采样
        db.record_sample("addr_cp", 42, "test_cg")

        stats = db.get_statistics()
        assert stats['total_samples'] == 1
        assert stats['total_covergroups'] == 1

    def test_get_hit_count(self):
        """测试获取命中次数"""
        db = MemoryCoverageDatabase()

        # 记录多个采样
        db.record_sample("addr_cp", "value_0", "test_cg")
        db.record_sample("addr_cp", "value_0", "test_cg")
        db.record_sample("addr_cp", "value_1", "test_cg")

        # 获取特定bin的命中次数
        count = db.get_hit_count("addr_cp", "value_0", "test_cg")
        assert count == 2

        # 获取所有bins的命中次数
        total = db.get_hit_count("addr_cp", covergroup_name="test_cg")
        assert total == 3

    def test_get_coverage_data(self):
        """测试获取覆盖率数据"""
        db = MemoryCoverageDatabase()

        # 记录采样
        db.record_sample("addr_cp", "bin_0", "test_cg")
        db.record_sample("addr_cp", "bin_1", "test_cg")

        # 获取覆盖率数据
        data = db.get_coverage_data("test_cg")

        assert data['covergroup'] == "test_cg"
        assert data['sample_count'] == 2
        assert "addr_cp" in data['coverpoints']

    def test_get_bin_hits(self):
        """测试获取bin命中数据"""
        db = MemoryCoverageDatabase()

        db.record_sample("addr_cp", "bin_0", "test_cg")
        db.record_sample("addr_cp", "bin_1", "test_cg")
        db.record_sample("addr_cp", "bin_0", "test_cg")

        # 获取所有bin命中
        bin_hits = db.get_bin_hits("addr_cp", "test_cg")

        assert bin_hits.get("bin_0") == 2
        assert bin_hits.get("bin_1") == 1

    def test_clear(self):
        """测试清空数据库"""
        db = MemoryCoverageDatabase()

        db.record_sample("addr_cp", "bin_0", "test_cg")
        assert db.get_statistics()['total_samples'] == 1

        db.clear()
        assert db.get_statistics()['total_samples'] == 0

    def test_merge(self):
        """测试数据库合并"""
        db1 = MemoryCoverageDatabase()
        db2 = MemoryCoverageDatabase()

        # 记录不同的数据
        db1.record_sample("addr_cp", "bin_0", "test_cg")
        db2.record_sample("addr_cp", "bin_1", "test_cg")

        # 合并
        db1.merge(db2)

        # 验证合并结果
        total = db1.get_hit_count("addr_cp", covergroup_name="test_cg")
        assert total == 2

    def test_create_snapshot(self):
        """测试创建快照"""
        db = MemoryCoverageDatabase()

        db.record_sample("addr_cp", "bin_0", "test_cg")

        snapshot = db.create_snapshot()

        assert 'data' in snapshot
        assert 'created_at' in snapshot
        assert 'test_cg' in snapshot['data']

    def test_restore_snapshot(self):
        """测试恢复快照"""
        db1 = MemoryCoverageDatabase()

        db1.record_sample("addr_cp", "bin_0", "test_cg")
        snapshot = db1.create_snapshot()

        # 创建新数据库并恢复
        db2 = MemoryCoverageDatabase()
        db2.restore_snapshot(snapshot)

        # 验证恢复结果
        count = db2.get_hit_count("addr_cp", "bin_0", "test_cg")
        assert count == 1

    def test_cross_sample(self):
        """测试交叉覆盖率采样"""
        db = MemoryCoverageDatabase()

        # 记录交叉采样
        db.record_cross_sample("addr_cross", ("bin_0", "bin_1"), "test_cg")

        # 获取交叉数据
        cross_data = db.get_cross_data("addr_cross", "test_cg")

        assert cross_data['cross'] == "addr_cross"
        assert cross_data['total_samples'] == 1


class TestFileCoverageDatabase:
    """测试文件数据库"""

    def test_init(self):
        """测试初始化"""
        db = FileCoverageDatabase()
        assert db is not None

    def test_set_filepath(self):
        """测试设置文件路径"""
        db = FileCoverageDatabase()
        db.set_filepath("test_coverage.json")

        assert db.get_filepath() == "test_coverage.json"

    def test_save_and_load(self):
        """测试保存和加载"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_coverage.json")

            # 创建数据库并保存数据
            db1 = FileCoverageDatabase(filepath)
            db1.record_sample("addr_cp", "bin_0", "test_cg")
            db1.record_sample("addr_cp", "bin_1", "test_cg")
            db1.save()

            # 创建新数据库并加载数据
            db2 = FileCoverageDatabase(filepath)
            db2.load()

            # 验证数据
            count = db2.get_hit_count("addr_cp", covergroup_name="test_cg")
            assert count == 2

    def test_save_without_filepath_raises_error(self):
        """测试没有文件路径时保存失败"""
        db = FileCoverageDatabase()
        db.record_sample("addr_cp", "bin_0", "test_cg")

        with pytest.raises(DatabaseError):
            db.save()

    def test_load_nonexistent_file_raises_error(self):
        """测试加载不存在的文件失败"""
        db = FileCoverageDatabase("nonexistent.json")

        with pytest.raises(DatabaseError):
            db.load()

    def test_is_dirty(self):
        """测试脏标记"""
        db = FileCoverageDatabase()

        assert not db.is_dirty()

        db.record_sample("addr_cp", "bin_0", "test_cg")
        assert db.is_dirty()

        db.save("test_temp.json")
        assert not db.is_dirty()

    def test_merge_with_file_database(self):
        """测试文件数据库合并"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath1 = os.path.join(tmpdir, "test1.json")
            filepath2 = os.path.join(tmpdir, "test2.json")

            db1 = FileCoverageDatabase(filepath1)
            db2 = FileCoverageDatabase(filepath2)

            db1.record_sample("addr_cp", "bin_0", "test_cg")
            db2.record_sample("addr_cp", "bin_1", "test_cg")

            # 合并
            db1.merge(db2)
            db1.save()

            # 加载并验证
            db3 = FileCoverageDatabase(filepath1)
            db3.load()

            total = db3.get_hit_count("addr_cp", covergroup_name="test_cg")
            assert total == 2

    def test_clear_marks_dirty(self):
        """测试清空操作标记为脏"""
        db = FileCoverageDatabase("test.json")

        db.record_sample("addr_cp", "bin_0", "test_cg")
        db.clear()

        assert db.is_dirty()


class TestDatabaseFactory:
    """测试数据库工厂"""

    def test_get_memory_database(self):
        """测试获取内存数据库"""
        db = DatabaseFactory.get_database("memory")
        assert isinstance(db, MemoryCoverageDatabase)

    def test_get_file_database(self):
        """测试获取文件数据库"""
        db = DatabaseFactory.get_database("file", filepath="test.json")
        assert isinstance(db, FileCoverageDatabase)

    def test_auto_backend_without_filepath(self):
        """测试auto后端无文件路径时选择内存数据库"""
        db = DatabaseFactory.get_database("auto")
        assert isinstance(db, MemoryCoverageDatabase)

    def test_auto_backend_with_filepath(self):
        """测试auto后端有文件路径时选择文件数据库"""
        db = DatabaseFactory.get_database("auto", filepath="test.json")
        assert isinstance(db, FileCoverageDatabase)

    def test_invalid_backend_raises_error(self):
        """测试无效的后端类型抛出异常"""
        with pytest.raises(ValueError):
            DatabaseFactory.get_database("invalid_backend")

    def test_create_memory_database(self):
        """测试便捷方法创建内存数据库"""
        db = DatabaseFactory.create_memory_database()
        assert isinstance(db, MemoryCoverageDatabase)

    def test_create_file_database(self):
        """测试便捷方法创建文件数据库"""
        db = DatabaseFactory.create_file_database("test.json")
        assert isinstance(db, FileCoverageDatabase)

    def test_get_available_backends(self):
        """测试获取可用后端列表"""
        backends = DatabaseFactory.get_available_backends()
        assert "memory" in backends
        assert "file" in backends
        assert "auto" in backends

    def test_register_custom_backend(self):
        """测试注册自定义后端"""
        from sv_randomizer.coverage.database.base import CoverageDatabase

        class CustomDatabase(CoverageDatabase):
            def record_sample(self, *args, **kwargs):
                pass

            def record_cross_sample(self, *args, **kwargs):
                pass

            def get_hit_count(self, *args, **kwargs):
                return 0

            def get_coverage_data(self, *args, **kwargs):
                return {}

            def get_bin_hits(self, *args, **kwargs):
                return {}

            def get_cross_data(self, *args, **kwargs):
                return {}

            def save(self, *args, **kwargs):
                pass

            def load(self, *args, **kwargs):
                pass

            def merge(self, *args, **kwargs):
                pass

            def clear(self):
                pass

            def get_statistics(self):
                return {}

            def create_snapshot(self):
                return {}

            def restore_snapshot(self, *args, **kwargs):
                pass

        DatabaseFactory.register_backend("custom", CustomDatabase)

        db = DatabaseFactory.get_database("custom")
        assert isinstance(db, CustomDatabase)

    def test_register_invalid_backend_raises_error(self):
        """测试注册无效后端抛出异常"""
        class NotADatabase:
            pass

        with pytest.raises(ValueError):
            DatabaseFactory.register_backend("invalid", NotADatabase)


class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_create_database(self):
        """测试create_database函数"""
        from sv_randomizer.coverage.database import create_database

        db = create_database("memory")
        assert isinstance(db, MemoryCoverageDatabase)

    def test_create_memory_database_func(self):
        """测试create_memory_database函数"""
        from sv_randomizer.coverage.database import create_memory_database

        db = create_memory_database()
        assert isinstance(db, MemoryCoverageDatabase)

    def test_create_file_database_func(self):
        """测试create_file_database函数"""
        from sv_randomizer.coverage.database import create_file_database

        db = create_file_database("test.json")
        assert isinstance(db, FileCoverageDatabase)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
