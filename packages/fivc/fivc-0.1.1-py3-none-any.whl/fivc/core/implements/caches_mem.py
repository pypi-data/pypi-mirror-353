from __future__ import annotations

import time
from typing import TYPE_CHECKING

from fivc.core import IComponentSite, utils
from fivc.core.interfaces import caches

if TYPE_CHECKING:
    from datetime import timedelta


class _CacheItem:
    """缓存项, 包含值和过期时间"""

    def __init__(self, value: bytes | None, expire_time: float):
        self.value = value
        self.expire_time = expire_time

    def is_expired(self) -> bool:
        """检查是否已过期"""
        return time.time() > self.expire_time


@utils.implements(caches.ICache)
class CacheImpl:
    """内存缓存实现"""

    def __init__(
        self,
        _component_site: IComponentSite,
        **_kwargs,
    ):
        print("create cache of memory")  # noqa
        self._cache: dict[str, _CacheItem] = {}

    def get_value(
        self,
        key_name: str,
    ) -> bytes | None:
        """根据键名获取缓存值"""
        # 清理过期项
        self._cleanup_expired()

        item = self._cache.get(key_name)
        if item is None or item.is_expired():
            # 如果项不存在或已过期, 删除并返回None
            if key_name in self._cache:
                del self._cache[key_name]
            return None

        return item.value

    def set_value(
        self,
        key_name: str,
        value: bytes | None,
        expire: timedelta,
    ) -> bool:
        """设置缓存值"""
        if value is None:
            # 删除缓存项
            if key_name in self._cache:
                del self._cache[key_name]
            return True

        # 计算过期时间
        expire_time = time.time() + expire.total_seconds()

        # 存储缓存项
        self._cache[key_name] = _CacheItem(value, expire_time)
        return True

    def _cleanup_expired(self):
        """清理过期的缓存项"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if current_time > item.expire_time
        ]

        for key in expired_keys:
            del self._cache[key]
