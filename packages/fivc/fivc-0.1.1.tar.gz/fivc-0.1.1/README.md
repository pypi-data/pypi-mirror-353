# FIVC - Five Component Framework

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/development-beta-orange.svg)](https://github.com/5C-Plus/fivc)

FIVC 是一个轻量级的 Python 组件管理框架，提供了灵活的组件注册、查询和依赖注入机制。

## 特性

- 🔧 **组件接口抽象**: 基于抽象基类的组件接口定义
- 🔌 **依赖注入**: 灵活的组件注册和查询机制
- 📁 **配置管理**: 支持 JSON 和 YAML 格式的配置文件
- 🗄️ **缓存系统**: 内置内存和 Redis 缓存支持
- 📝 **日志系统**: 内置日志组件
- 🔒 **互斥锁**: 分布式锁支持
- 🎯 **类型安全**: 完整的类型注解支持

## 安装

### 使用 pip 安装

```bash
pip install fivc
```

### 使用 uv 安装（推荐）

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 FIVC
uv add fivc
```

### 从源码安装

#### 使用 uv（推荐）

```bash
git clone https://github.com/5C-Plus/fivc.git
cd fivc

# 创建虚拟环境并安装依赖
uv venv
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

#### 使用 pip

```bash
git clone https://github.com/5C-Plus/fivc.git
cd fivc
pip install -e .
```

## 快速开始

### 基本使用

```python
from fivc.core import IComponent, IComponentSite
from fivc.core.implements.utils import load_component_site
from fivc.core.interfaces.utils import query_component

# 加载组件站点
component_site = load_component_site(fmt="yaml")

# 查询组件
config = query_component(component_site, IConfig, "Json")
if config:
    session = config.get_session("app")
    value = session.get_value("database_url")
```

### 配置文件示例

#### YAML 配置 (config.yml)
```yaml
components:
  - interface: "fivc.core.interfaces.configs.IConfig"
    implement: "fivc.core.implements.configs_yamlfile.YamlFileConfig"
    name: "Yaml"
    config:
      file_path: "app_config.yml"
```

#### JSON 配置 (config.json)
```json
{
  "components": [
    {
      "interface": "fivc.core.interfaces.configs.IConfig",
      "implement": "fivc.core.implements.configs_jsonfile.JsonFileConfig",
      "name": "Json",
      "config": {
        "file_path": "app_config.json"
      }
    }
  ]
}
```

## 核心组件

### 配置管理
- `IConfig`: 配置接口
- `JsonFileConfig`: JSON 文件配置实现
- `YamlFileConfig`: YAML 文件配置实现

### 缓存系统
- `ICache`: 缓存接口
- `MemoryCache`: 内存缓存实现
- `RedisCache`: Redis 缓存实现

### 日志系统
- `ILogger`: 日志接口
- `BuiltinLogger`: 内置日志实现

### 互斥锁
- `IMutex`: 互斥锁接口
- `RedisMutex`: Redis 分布式锁实现

## 开发

本项目使用 [uv](https://docs.astral.sh/uv/) 进行依赖管理和构建。

### 环境设置

#### 使用 uv（推荐）

```bash
# 克隆仓库
git clone https://github.com/5C-Plus/fivc.git
cd fivc

# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装开发依赖
uv venv
uv sync --all-extras

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

#### 使用 Make 命令（Linux/macOS）

```bash
# 查看所有可用命令
make help

# 完整开发环境设置
make dev-setup

# 安装开发依赖
make install-dev
```

#### 传统方式

```bash
# 克隆仓库
git clone https://github.com/5C-Plus/fivc.git
cd fivc

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e ".[dev,test]"
```

### 运行测试

#### 使用 uv

```bash
# 运行所有测试
uv run pytest tests/

# 运行特定测试
uv run pytest tests/test_configs.py

# 运行测试并生成覆盖率报告
uv run pytest --cov=fivc --cov-report=html tests/
```

#### 使用 Make

```bash
# 运行测试
make test

# 运行测试并生成覆盖率报告
make test-cov

# 快速测试（跳过慢速测试）
make test-fast
```

### 代码检查和格式化

#### 使用 uv

```bash
# 代码格式化
uv run black .
uv run isort .
uv run ruff check --fix .

# 代码检查
uv run ruff check .
uv run black --check .
uv run mypy src/fivc tests
```

#### 使用 Make

```bash
# 格式化代码
make format

# 运行所有检查
make lint
```

### 构建项目

#### 使用 uv

```bash
# 构建项目
uv build

# 检查构建结果
ls dist/
```

#### 使用 Make

```bash
# 使用 uv 构建
make build-uv

# 传统构建
make build
```

## 项目结构

```
fivc/
├── src/fivc/           # 主要源代码
│   ├── core/           # 核心模块
│   │   ├── interfaces/ # 接口定义
│   │   ├── implements/ # 接口实现
│   │   └── fixtures/   # 测试夹具
│   ├── __about__.py    # 版本信息
│   └── cli.py          # 命令行接口
├── tests/              # 测试代码
├── scripts/            # 脚本工具
├── fixtures/           # 测试数据
├── .github/            # GitHub Actions
├── Makefile            # Make 构建脚本
├── pyproject.toml      # 项目配置
└── uv.lock             # uv 锁定文件
```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 使用 `make format` 格式化代码
4. 使用 `make lint` 检查代码质量
5. 使用 `make test` 运行测试
6. 提交更改 (`git commit -m 'Add some amazing feature'`)
7. 推送到分支 (`git push origin feature/amazing-feature`)
8. 开启 Pull Request

### 开发规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写单元测试
- 更新文档

## 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 作者

- **Charlie ZHANG** - *初始工作* - [sunnypig2002@gmail.com](mailto:sunnypig2002@gmail.com)

## 链接

- [文档](https://github.com/5C-Plus/fivc#readme)
- [问题反馈](https://github.com/5C-Plus/fivc/issues)
- [源代码](https://github.com/5C-Plus/fivc)
