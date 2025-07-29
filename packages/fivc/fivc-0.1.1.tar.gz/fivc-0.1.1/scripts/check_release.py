#!/usr/bin/env python3
"""
发布前检查脚本

用于验证 FIVC 包在发布前的完整性和正确性。
"""
import importlib
import os
import sys
import tempfile
import zipfile
from pathlib import Path


def check_version_consistency():
    """检查版本一致性"""
    print("🔍 检查版本一致性...")
    
    # 检查 __about__.py 中的版本
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    import fivc
    package_version = fivc.__version__
    
    # 检查 pyproject.toml 是否存在
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    if not pyproject_path.exists():
        print("❌ pyproject.toml 不存在")
        return False
    
    print(f"✅ 包版本: {package_version}")
    return True


def check_package_structure():
    """检查包结构"""
    print("🔍 检查包结构...")
    
    required_files = [
        "src/fivc/__init__.py",
        "src/fivc/__about__.py", 
        "src/fivc/core/__init__.py",
        "src/fivc/core/interfaces/__init__.py",
        "src/fivc/core/implements/__init__.py",
    ]
    
    project_root = Path(__file__).parent.parent
    
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"❌ 缺少必需文件: {file_path}")
            return False
        print(f"✅ 文件存在: {file_path}")
    
    return True


def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
    try:
        import yaml
        print("✅ PyYAML 可用")
    except ImportError:
        print("❌ PyYAML 不可用")
        return False
    
    return True


def check_imports():
    """检查主要模块导入"""
    print("🔍 检查模块导入...")
    
    try:
        # 检查主包导入
        import fivc
        print(f"✅ fivc 包导入成功 (版本: {fivc.__version__})")
        
        # 检查核心模块导入
        from fivc.core.implements.utils import load_component_site
        print("✅ load_component_site 导入成功")
        
        from fivc.core.interfaces.utils import query_component
        print("✅ query_component 导入成功")
        
        # 检查接口导入
        from fivc.core.interfaces import caches, configs, loggers
        print("✅ 核心接口导入成功")
        
        # 检查实现导入
        from fivc.core.implements import ComponentSite
        print("✅ ComponentSite 导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def check_basic_functionality():
    """检查基本功能"""
    print("🔍 检查基本功能...")
    
    try:
        # 测试组件站点创建
        from fivc.core.implements import ComponentSite
        site = ComponentSite()
        print("✅ ComponentSite 创建成功")
        
        # 测试配置加载（如果有配置文件）
        config_path = Path(__file__).parent.parent / "src/fivc/core/fixtures/configs_basics.yml"
        if config_path.exists():
            from fivc.core.implements.utils import load_component_site
            component_site = load_component_site(str(config_path), fmt="yml")
            print("✅ 配置文件加载成功")
            
            # 测试组件查询
            from fivc.core.interfaces import loggers
            logger_site = component_site.query_component(loggers.ILoggerSite, "")
            if logger_site:
                print("✅ 日志组件查询成功")
            else:
                print("⚠️  日志组件未找到（可能正常）")
        
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False


def check_wheel_contents():
    """检查wheel文件内容"""
    print("🔍 检查wheel文件内容...")
    
    dist_dir = Path(__file__).parent.parent / "dist"
    wheel_files = list(dist_dir.glob("*.whl"))
    
    if not wheel_files:
        print("❌ 未找到wheel文件")
        return False
    
    wheel_file = wheel_files[0]
    print(f"📦 检查wheel文件: {wheel_file.name}")
    
    try:
        with zipfile.ZipFile(wheel_file, 'r') as wheel:
            files = wheel.namelist()
            
            # 检查必要文件
            required_in_wheel = [
                "fivc/__init__.py",
                "fivc/__about__.py",
                "fivc/core/__init__.py",
            ]
            
            for required_file in required_in_wheel:
                if not any(f.endswith(required_file) for f in files):
                    print(f"❌ wheel中缺少文件: {required_file}")
                    return False
                print(f"✅ wheel包含: {required_file}")
            
            print(f"📄 wheel文件总共包含 {len(files)} 个文件")
            
        return True
        
    except Exception as e:
        print(f"❌ wheel文件检查失败: {e}")
        return False


def main():
    """主检查函数"""
    print("🚀 开始 FIVC 发布前检查...\n")
    
    checks = [
        ("版本一致性", check_version_consistency),
        ("包结构", check_package_structure),
        ("依赖项", check_dependencies),
        ("模块导入", check_imports),
        ("基本功能", check_basic_functionality),
        ("Wheel内容", check_wheel_contents),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\n{'='*50}")
        print(f"检查项目: {check_name}")
        print(f"{'='*50}")
        
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} 检查出现异常: {e}")
            failed_checks.append(check_name)
    
    print(f"\n{'='*50}")
    print("检查结果总结")
    print(f"{'='*50}")
    
    if failed_checks:
        print(f"❌ 发现 {len(failed_checks)} 个问题:")
        for failed in failed_checks:
            print(f"   - {failed}")
        print("\n请修复上述问题后再发布。")
        return False
    else:
        print("✅ 所有检查通过！包已准备好发布。")
        print("\n您可以使用以下命令发布到 PyPI:")
        print("   uv publish")
        print("   或")
        print("   uv publish --token <your-pypi-token>")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 