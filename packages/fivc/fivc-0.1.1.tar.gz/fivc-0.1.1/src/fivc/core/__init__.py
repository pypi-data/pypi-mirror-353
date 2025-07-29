"""
FIVC核心模块

本模块包含FIVC框架的核心组件, 包括:

接口定义模块 (interfaces/):
- IComponent: 基础组件接口
- IComponentSite: 组件站点接口, 用于组件注册和查询
- IComponentSiteBuilder: 组件站点构建器接口
- IConfig: 配置管理接口
- ICache: 缓存管理接口
- ILogger: 日志记录接口
- IMutex: 互斥锁接口

实现模块 (implements/):
- ComponentSite: 组件站点的默认实现
- 各种配置实现: JsonFileConfig, YamlFileConfig
- 各种缓存实现: MemoryCache, RedisCache
- 各种日志实现: BuiltinLogger
- 各种锁实现: RedisMutex

工具函数模块 (utils):
- load_component_site: 加载组件站点
- query_component: 查询组件
- cast_component: 组件类型转换
- implements: 检查组件实现

Author: Charlie ZHANG <sunnypig2002@gmail.com>
"""

# 导出的公共接口
__all__ = [
    # 核心接口
    "IComponent",
    "IComponentSite",
    "IComponentSiteBuilder",
    # 工具模块
    "utils",
]

# 导入核心接口
from fivc.core.interfaces import (
    IComponent,
    IComponentSite,
    IComponentSiteBuilder,
    utils,
)
