import time
import unittest
from datetime import timedelta

from fivc.core import utils
from fivc.core.implements.utils import load_component_site
from fivc.core.interfaces import caches


class TestCaches(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.component_site = load_component_site(fmt="yaml")

    def test_cache_redis(self):
        cache = utils.query_component(self.component_site, caches.ICache, "Redis")
        assert cache is not None
        cache.get_value("test")

    def test_cache_memory_basic(self):
        """测试内存缓存的基本功能"""
        cache = utils.query_component(self.component_site, caches.ICache, "Memory")
        assert cache is not None

        # 测试设置和获取值
        test_value = b"test_data"
        result = cache.set_value("test_key", test_value, timedelta(seconds=10))
        assert result is True

        retrieved_value = cache.get_value("test_key")
        assert retrieved_value == test_value

    def test_cache_memory_expiration(self):
        """测试内存缓存的过期功能"""
        cache = utils.query_component(self.component_site, caches.ICache, "Memory")
        assert cache is not None

        # 设置一个很短的过期时间
        test_value = b"expire_test"
        cache.set_value("expire_key", test_value, timedelta(milliseconds=100))

        # 立即获取应该能得到值
        retrieved_value = cache.get_value("expire_key")
        assert retrieved_value == test_value

        # 等待过期
        time.sleep(0.2)

        # 再次获取应该返回None
        expired_value = cache.get_value("expire_key")
        assert expired_value is None

    def test_cache_memory_delete(self):
        """测试内存缓存的删除功能"""
        cache = utils.query_component(self.component_site, caches.ICache, "Memory")
        assert cache is not None

        # 设置值
        test_value = b"delete_test"
        cache.set_value("delete_key", test_value, timedelta(seconds=10))

        # 确认值存在
        retrieved_value = cache.get_value("delete_key")
        assert retrieved_value == test_value

        # 删除值 (设置为None)
        result = cache.set_value("delete_key", None, timedelta(seconds=1))
        assert result is True

        # 确认值已被删除
        deleted_value = cache.get_value("delete_key")
        assert deleted_value is None

    def test_cache_memory_nonexistent_key(self):
        """测试获取不存在的键"""
        cache = utils.query_component(self.component_site, caches.ICache, "Memory")
        assert cache is not None

        # 获取不存在的键应该返回None
        nonexistent_value = cache.get_value("nonexistent_key")
        assert nonexistent_value is None
