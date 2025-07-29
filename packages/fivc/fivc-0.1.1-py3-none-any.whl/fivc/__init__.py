"""
FIVC - Five Component Framework

一个轻量级的Python组件管理框架, 提供组件注册、查询和依赖注入机制。

主要特性:
- 🔧 组件接口抽象: 基于抽象基类的组件接口定义
- 🔌 依赖注入: 灵活的组件注册和查询机制
- 📁 配置管理: 支持JSON和YAML格式的配置文件
- 🗄️ 缓存系统: 内置内存和Redis缓存支持
- 📝 日志系统: 内置日志组件
- 🔒 互斥锁: 分布式锁支持
- 🎯 类型安全: 完整的类型注解支持

基本使用示例:
    from fivc.core.implements.utils import load_component_site
    from fivc.core.interfaces.utils import query_component
    from fivc.core.interfaces.configs import IConfig

    # 加载组件站点
    component_site = load_component_site(fmt="yaml")

    # 查询配置组件
    config = query_component(component_site, IConfig, "Json")
    if config:
        session = config.get_session("app")
        value = session.get_value("database_url")

Author: Charlie ZHANG <sunnypig2002@gmail.com>
License: MIT
Repository: https://github.com/5C-Plus/fivc
"""

# 导入版本信息
from fivc.__about__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __url__,
    __version__,
    __version_info__,
)

# 公开的API
__all__ = [
    # 版本信息
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__url__",
    "__version__",
    "__version_info__",
]
