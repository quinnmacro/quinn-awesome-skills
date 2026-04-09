#!/usr/bin/env python3
"""
Presearch Skill 打包和安装工具
符合 Claude Code skills 最佳实践
"""

import os
import sys
import shutil
import json
import tarfile
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
SKILL_NAME = "presearch"
MODULES_DIR = "presearch_modules"
COMMANDS_DIR = "commands"
REQUIRED_FILES = [
    "presearch_core.py",
    "keyword_extractor.py",
    "http_client.py",
    "formatter.py",
    "npm_client.py",
    "pypi_client.py",
    "docker_client.py",
    "__version__.py",
]
REQUIRED_DIRS = [
    "cache",
    "config",
    "cli",
    "plugins",
]

def get_claude_dir():
    """获取 Claude Code 配置目录"""
    home = Path.home()

    # 检查环境变量
    if "CLAUDE_CONFIG_DIR" in os.environ:
        return Path(os.environ["CLAUDE_CONFIG_DIR"])

    # 默认位置
    claude_dir = home / ".claude"
    return claude_dir

def check_source_files(source_dir):
    """检查源文件是否完整"""
    modules_path = Path(source_dir) / MODULES_DIR

    if not modules_path.exists():
        print(f"❌ 错误: 找不到模块目录 {modules_path}")
        return False

    # 检查必需文件
    missing = []
    for file in REQUIRED_FILES:
        if not (modules_path / file).exists():
            missing.append(file)

    # 检查必需目录
    for dir_name in REQUIRED_DIRS:
        if not (modules_path / dir_name).exists():
            missing.append(f"{dir_name}/")

    # 检查 skill 定义文件
    skill_file = Path(source_dir) / COMMANDS_DIR / f"{SKILL_NAME}.md"
    if not skill_file.exists():
        missing.append(f"commands/{SKILL_NAME}.md")

    if missing:
        print(f"❌ 错误: 缺少以下文件/目录:")
        for item in missing:
            print(f"   - {item}")
        return False

    print(f"✅ 所有必需文件都存在")
    return True

def get_dependencies():
    """获取依赖列表"""
    return [
        "pydantic-settings>=2.0.0",
        "rich>=13.0.0",
        "platformdirs>=3.0.0",
    ]

def create_manifest(source_dir, output_dir):
    """创建清单文件"""
    manifest = {
        "name": SKILL_NAME,
        "version": "3.1.0",
        "description": "智能开发资源搜索工具 - 支持多数据源并行搜索",
        "author": "presearch-team",
        "created_at": datetime.now().isoformat(),
        "dependencies": get_dependencies(),
        "structure": {
            "commands": [f"{SKILL_NAME}.md"],
            "modules": MODULES_DIR,
        },
        "install": {
            "claude_dir": "~/.claude",
            "commands_dir": "~/.claude/commands",
            "modules_dir": f"~/.claude/{MODULES_DIR}",
        },
        "entry_point": f"python3 ~/.claude/{MODULES_DIR}/presearch_core.py",
    }

    manifest_path = Path(output_dir) / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest_path

def create_requirements(output_dir):
    """创建 requirements.txt"""
    deps = get_dependencies()
    req_path = Path(output_dir) / "requirements.txt"
    with open(req_path, "w", encoding="utf-8") as f:
        f.write("\n".join(deps))
    return req_path

def create_install_script(output_dir):
    """创建安装脚本"""
    script_content = '''#!/usr/bin/env python3
"""
Presearch Skill 安装脚本
用法: python3 install.py [--uninstall]
"""

import os
import sys
import shutil
import json
from pathlib import Path

SKILL_NAME = "presearch"
MODULES_DIR = "presearch_modules"

def get_claude_dir():
    """获取 Claude Code 配置目录"""
    home = Path.home()

    # 检查环境变量
    if "CLAUDE_CONFIG_DIR" in os.environ:
        return Path(os.environ["CLAUDE_CONFIG_DIR"])

    return home / ".claude"

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import pydantic_settings
        import rich
        import platformdirs
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"⚠️  缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def install_skill():
    """安装 skill"""
    claude_dir = get_claude_dir()
    commands_dir = claude_dir / "commands"
    modules_dir = claude_dir / MODULES_DIR

    # 创建目录
    commands_dir.mkdir(parents=True, exist_ok=True)

    # 获取当前目录（包含安装文件的目录）
    source_dir = Path(__file__).parent

    # 复制 skill 定义文件
    skill_source = source_dir / "commands" / f"{SKILL_NAME}.md"
    skill_target = commands_dir / f"{SKILL_NAME}.md"

    if skill_source.exists():
        shutil.copy2(skill_source, skill_target)
        print(f"✅ 已安装 skill 定义: {skill_target}")
    else:
        print(f"❌ 找不到 skill 定义文件: {skill_source}")
        return False

    # 复制模块文件
    modules_source = source_dir / MODULES_DIR
    if modules_source.exists():
        # 如果目标目录存在，先删除
        if modules_dir.exists():
            print(f"⚠️  已存在旧版本，正在更新...")
            shutil.rmtree(modules_dir)

        shutil.copytree(modules_source, modules_dir)
        print(f"✅ 已安装模块: {modules_dir}")
    else:
        print(f"❌ 找不到模块目录: {modules_source}")
        return False

    print(f"\\n🎉 {SKILL_NAME} skill 安装成功!")
    print(f"\\n使用方法:")
    print(f"  /{SKILL_NAME} \\"Python web framework\\"")
    print(f"  /{SKILL_NAME} \\"React\\" emoji")
    print(f"  /{SKILL_NAME} \\"Docker\\" meme")

    return True

def uninstall_skill():
    """卸载 skill"""
    claude_dir = get_claude_dir()
    commands_dir = claude_dir / "commands"
    modules_dir = claude_dir / MODULES_DIR

    # 删除 skill 定义文件
    skill_file = commands_dir / f"{SKILL_NAME}.md"
    if skill_file.exists():
        skill_file.unlink()
        print(f"✅ 已删除 skill 定义: {skill_file}")

    # 删除模块目录
    if modules_dir.exists():
        shutil.rmtree(modules_dir)
        print(f"✅ 已删除模块: {modules_dir}")

    print(f"\\n🗑️  {SKILL_NAME} skill 已卸载")
    return True

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        uninstall_skill()
    else:
        if install_skill():
            check_dependencies()

if __name__ == "__main__":
    main()
'''

    script_path = Path(output_dir) / "install.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    # 设置可执行权限
    os.chmod(script_path, 0o755)
    return script_path

def create_readme(output_dir):
    """创建 README"""
    readme_content = '''# Presearch Skill

智能开发资源搜索工具 - Claude Code Skill

## 功能特性

- 🔍 多数据源并行搜索（GitHub、arXiv、npm、PyPI、Docker Hub）
- 🎨 8种输出格式（table、json、csv、markdown、emoji、meme、poetry、fortune）
- ⚡ 两级缓存系统（内存 + 磁盘）
- 📊 项目健康度评估
- 📝 搜索历史记录

## 快速安装

```bash
# 解压后进入目录
cd presearch-skill/

# 安装依赖
pip install -r requirements.txt

# 安装 skill
python3 install.py
```

## 使用方法

```bash
# 基本搜索
/presearch "Python web framework"

# 使用趣味格式
/presearch "React" emoji
/presearch "Docker" meme
/presearch "ML library" poetry
```

## 文件结构

```
presearch-skill/
├── commands/
│   └── presearch.md          # Skill 定义文件
├── presearch_modules/         # 核心代码模块
│   ├── presearch_core.py
│   ├── cache/
│   ├── config/
│   ├── cli/
│   └── plugins/
├── install.py                 # 安装脚本
├── requirements.txt           # 依赖列表
└── manifest.json             # 清单文件
```

## 卸载

```bash
python3 install.py --uninstall
```

## 依赖

- Python 3.9+
- pydantic-settings
- rich
- platformdirs
'''

    readme_path = Path(output_dir) / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    return readme_path

def package_skill(source_dir=None, output_file=None):
    """打包 skill"""
    if source_dir is None:
        # 默认从 ~/.claude 读取
        source_dir = get_claude_dir()

    source_path = Path(source_dir)

    print(f"📦 正在打包 Presearch Skill...")
    print(f"   源目录: {source_path}")

    # 检查文件完整性
    if not check_source_files(source_path):
        return False

    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="presearch_skill_")
    temp_path = Path(temp_dir)

    try:
        # 创建目录结构
        (temp_path / "commands").mkdir()
        (temp_path / MODULES_DIR).mkdir()

        # 复制 skill 定义文件
        skill_source = source_path / COMMANDS_DIR / f"{SKILL_NAME}.md"
        skill_target = temp_path / "commands" / f"{SKILL_NAME}.md"
        shutil.copy2(skill_source, skill_target)

        # 复制模块文件
        modules_source = source_path / MODULES_DIR
        modules_target = temp_path / MODULES_DIR

        for item in modules_source.iterdir():
            if item.name.startswith('.') or item.name == '__pycache__':
                continue
            if item.is_file():
                # 只复制 Python 文件和必需文件
                if item.suffix in ['.py', '.md', '.txt', '.json'] or item.name in ['__version__']:
                    shutil.copy2(item, modules_target / item.name)
            elif item.is_dir():
                # 递归复制目录，但排除不需要的文件
                def ignore_patterns(dir, contents):
                    return ['.git', '__pycache__', '.pytest_cache', '.idea', '.vscode', '*.pyc', '*~']
                shutil.copytree(item, modules_target / item.name, ignore=shutil.ignore_patterns(*ignore_patterns('', [])))

        # 创建清单文件
        manifest_path = create_manifest(source_path, temp_path)
        print(f"✅ 创建清单: {manifest_path.name}")

        # 创建 requirements.txt
        req_path = create_requirements(temp_path)
        print(f"✅ 创建依赖文件: {req_path.name}")

        # 创建安装脚本
        install_script = create_install_script(temp_path)
        print(f"✅ 创建安装脚本: {install_script.name}")

        # 创建 README
        readme_path = create_readme(temp_path)
        print(f"✅ 创建 README: {readme_path.name}")

        # 创建 tar.gz 包
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"presearch-skill-v3.1.0-{timestamp}.tar.gz"

        output_path = Path(output_file).resolve()

        def exclude_filter(tarinfo):
            """排除不需要的文件"""
            name = tarinfo.name
            # 排除 git 目录
            if '.git' in name:
                return None
            # 排除 Python 缓存
            if '__pycache__' in name or name.endswith('.pyc'):
                return None
            # 排除测试文件
            if 'test_' in name or '_test.py' in name:
                return None
            # 排除 IDE 配置
            if '.idea' in name or '.vscode' in name:
                return None
            # 排除备份文件
            if name.endswith('.backup') or name.endswith('~'):
                return None
            return tarinfo

        with tarfile.open(output_path, "w:gz") as tar:
            for item in temp_path.iterdir():
                tar.add(item, arcname=item.name, filter=exclude_filter)

        print(f"\\n🎉 打包成功!")
        print(f"   输出文件: {output_path}")
        print(f"\\n安装方法:")
        print(f"   1. 解压: tar xzvf {output_path.name}")
        print(f"   2. 进入目录: cd presearch-skill/")
        print(f"   3. 安装: python3 install.py")

        return True

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

def install_skill(package_file=None):
    """安装 skill"""
    claude_dir = get_claude_dir()
    commands_dir = claude_dir / COMMANDS_DIR
    modules_dir = claude_dir / MODULES_DIR

    print(f"📥 正在安装 Presearch Skill...")
    print(f"   目标目录: {claude_dir}")

    # 创建目录
    commands_dir.mkdir(parents=True, exist_ok=True)
    modules_dir.mkdir(parents=True, exist_ok=True)

    if package_file:
        # 从压缩包安装
        import tempfile
        temp_dir = tempfile.mkdtemp()

        try:
            with tarfile.open(package_file, "r:gz") as tar:
                tar.extractall(temp_dir)

            source_dir = Path(temp_dir)

            # 查找解压后的目录
            subdirs = [d for d in source_dir.iterdir() if d.is_dir()]
            if subdirs:
                source_dir = subdirs[0]
        except Exception as e:
            print(f"❌ 解压失败: {e}")
            return False
    else:
        # 从当前目录安装（开发模式）
        source_dir = Path.cwd()

    # 复制 skill 定义文件
    skill_source = source_dir / "commands" / f"{SKILL_NAME}.md"
    skill_target = commands_dir / f"{SKILL_NAME}.md"

    if skill_source.exists():
        shutil.copy2(skill_source, skill_target)
        print(f"✅ 已安装 skill 定义")
    else:
        print(f"❌ 找不到 skill 定义文件")
        return False

    # 复制模块文件
    modules_source = source_dir / MODULES_DIR
    if modules_source.exists():
        # 如果目标目录存在，先备份
        if modules_dir.exists():
            backup_dir = modules_dir.with_suffix(".backup")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.move(modules_dir, backup_dir)
            print(f"⚠️  已备份旧版本到: {backup_dir}")

        shutil.copytree(modules_source, modules_dir)
        print(f"✅ 已安装模块文件")
    else:
        print(f"❌ 找不到模块目录")
        return False

    print(f"\\n🎉 安装成功!")
    print(f"\\n使用方法:")
    print(f"   /{SKILL_NAME} \"Python web framework\"")
    print(f"   /{SKILL_NAME} \"React\" emoji")
    print(f"   /{SKILL_NAME} \"Docker\" meme")

    return True

def uninstall_skill():
    """卸载 skill"""
    claude_dir = get_claude_dir()
    commands_dir = claude_dir / COMMANDS_DIR
    modules_dir = claude_dir / MODULES_DIR

    print(f"🗑️  正在卸载 Presearch Skill...")

    # 删除 skill 定义文件
    skill_file = commands_dir / f"{SKILL_NAME}.md"
    if skill_file.exists():
        skill_file.unlink()
        print(f"✅ 已删除 skill 定义")

    # 删除模块目录
    if modules_dir.exists():
        shutil.rmtree(modules_dir)
        print(f"✅ 已删除模块文件")

    print(f"\\n✅ 卸载完成")
    return True

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Presearch Skill 打包和安装工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 打包 skill
  python3 skill_manager.py package

  # 从压缩包安装
  python3 skill_manager.py install --file presearch-skill-v3.1.0.tar.gz

  # 从当前目录安装（开发模式）
  python3 skill_manager.py install

  # 卸载
  python3 skill_manager.py uninstall
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # package 命令
    package_parser = subparsers.add_parser("package", help="打包 skill")
    package_parser.add_argument("-s", "--source", help="源目录（默认: ~/.claude）")
    package_parser.add_argument("-o", "--output", help="输出文件名")

    # install 命令
    install_parser = subparsers.add_parser("install", help="安装 skill")
    install_parser.add_argument("-f", "--file", help="压缩包文件路径")

    # uninstall 命令
    subparsers.add_parser("uninstall", help="卸载 skill")

    args = parser.parse_args()

    if args.command == "package":
        package_skill(args.source, args.output)
    elif args.command == "install":
        install_skill(args.file)
    elif args.command == "uninstall":
        uninstall_skill()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
