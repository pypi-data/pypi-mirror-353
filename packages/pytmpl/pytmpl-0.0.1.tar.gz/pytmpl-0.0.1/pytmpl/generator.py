import os
import shutil
import subprocess
from typing import Dict, Any
from .utils.tools import get_logger

class ProjectGenerator:
    """
    项目模板生成器，负责根据用户输入生成项目结构。
    """
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        初始化生成器
        :param config: "配置字典，包含用户所有选择"
        """
        self.config = config
        self.base_path = os.path.join(config["project_path"], config["project_name"])
        self.src_path = os.path.join(self.base_path, "src", config["project_name"])
        self.utils_path = os.path.join(self.src_path, "utils")
        self.tests_path = os.path.join(self.base_path, "tests")
        self.logger = get_logger(self.config["project_name"])

    def generate(self) -> None:
        """
        "根据配置生成项目模板"
        "返回: None"
        """
        self.logger.info("开始生成项目模板...")
        self._create_dirs()
        self._create_files()
        if self.config.get("git_init"):
            self._init_git()
        if self.config.get("auto_install"):
            self._install_deps()
        self.logger.info("✅ 项目模板生成完成！")
        self.logger.info(f"项目路径: {self.base_path}")

    def _create_dirs(self) -> None:
        os.makedirs(self.utils_path, exist_ok=True)
        os.makedirs(self.tests_path, exist_ok=True)

    def _create_files(self) -> None:
        # __init__.py
        with open(os.path.join(self.src_path, "__init__.py"), "w", encoding="utf-8") as f:
            f.write(f"# {self.config['project_name']} 包初始化\n")
        with open(os.path.join(self.utils_path, "__init__.py"), "w", encoding="utf-8") as f:
            f.write("# utils 包初始化\n")
        # 主模块和场景相关内容
        self._create_scene_files()
        # 工具模块
        with open(os.path.join(self.utils_path, "tools.py"), "w", encoding="utf-8") as f:
            f.write(self._get_logger_template())
        # 测试模块
        with open(os.path.join(self.tests_path, "__init__.py"), "w", encoding="utf-8") as f:
            f.write("")
        with open(os.path.join(self.tests_path, f"test_{self.config['project_name']}.py"), "w", encoding="utf-8") as f:
            f.write(f"def test_dummy():\n    \"\"\"\n    示例测试用例。\n    \"\"\"\n    assert True\n")
        # .gitignore
        with open(os.path.join(self.base_path, ".gitignore"), "w", encoding="utf-8") as f:
            f.write(self._gitignore_content())
        # LICENSE
        if self.config["license"] != "不生成":
            with open(os.path.join(self.base_path, "LICENSE"), "w", encoding="utf-8") as f:
                f.write(self._license_content())
        # README.md
        with open(os.path.join(self.base_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(self._readme_content())
        # pyproject.toml
        with open(os.path.join(self.base_path, "pyproject.toml"), "w", encoding="utf-8") as f:
            f.write(self._pyproject_content())

    def _get_logger_template(self) -> str:
        return '''import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional

def init_logger(
    name: Optional[str] = None,
    log_file: Optional[str] = None,
    level: str = "INFO",
    console_level: str = "INFO",
    file_level: str = "INFO",
    fmt: str = "🟢 %(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    file_mode: str = "a",
    rotation: Optional[str] = None,
    when: str = "D",
    interval: int = 1,
    backup_count: int = 7
) -> logging.Logger:
    """
    初始化并返回一个功能完善的日志对象。

    :param name: "日志器名称，通常为__name__"
    :param log_file: "日志文件路径。如果为None，则不输出到文件"
    :param level: "日志器全局级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    :param console_level: "控制台输出级别"
    :param file_level: "文件输出级别"
    :param fmt: "日志格式"
    :param datefmt: "时间格式"
    :param file_mode: "日志文件写入模式"
    :param rotation: "日志分割方式。'size' 或 'time'。None为不分割"
    :param when: "当rotation为'time'时，分割的时间单位 (S, M, H, D, W0-W6)"
    :param interval: "当rotation为'time'时，分割的时间间隔"
    :param backup_count: "保留的备份日志文件数量"
    :return: "配置好的logging.Logger对象"
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())
    formatter = logging.Formatter(fmt, datefmt)

    if not logger.handlers:
        # 控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(console_level.upper())
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # 文件处理器
        if log_file:
            fh = None
            if rotation == "size":
                # 按大小分割
                max_bytes = 10 * 1024 * 1024  # 10MB
                fh = RotatingFileHandler(
                    log_file, maxBytes=max_bytes, backupCount=backup_count, mode=file_mode, encoding="utf-8"
                )
            elif rotation == "time":
                # 按时间分割
                fh = TimedRotatingFileHandler(
                    log_file, when=when, interval=interval, backupCount=backup_count, encoding="utf-8"
                )
            else:
                # 不分割
                fh = logging.FileHandler(log_file, mode=file_mode, encoding="utf-8")
            
            if fh:
                fh.setLevel(file_level.upper())
                fh.setFormatter(formatter)
                logger.addHandler(fh)

    return logger
'''

    def _create_scene_files(self) -> None:
        """
        根据不同场景生成主模块和相关内容
        """
        scene = self.config.get("scene", "通用后端库")
        pname = self.config["project_name"]
        content = ""

        if scene == "Flask Web应用":
            content = """\"\"\"
Flask Web应用主入口
\"\"\"
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, Flask!'

if __name__ == '__main__':
    app.run(debug=True)
"""
        elif scene == "FastAPI Web应用":
            content = """\"\"\"
FastAPI Web应用主入口
\"\"\"
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def read_root():
    return {"msg": "Hello, FastAPI!"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
"""
        elif scene == "Django Web应用":
            content = """\"\"\"
Django Web应用入口（请使用django-admin startproject）
\"\"\"
# 推荐使用django-admin startproject命令初始化Django项目
"""
        elif scene == "命令行工具":
            content = f"""\"\"\"
命令行工具主入口
\"\"\"
import argparse

def main():
    parser = argparse.ArgumentParser(description='命令行工具')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    args = parser.parse_args()
    print('Hello, CLI!')

if __name__ == '__main__':
    main()
"""
        elif scene == "数据分析":
            content = """\"\"\"
数据分析项目主入口
\"\"\"
import pandas as pd
import numpy as np

def main():
    print('数据分析项目初始化')

if __name__ == '__main__':
    main()
"""
            # 额外生成data目录
            data_dir = os.path.join(self.base_path, "data")
            os.makedirs(data_dir, exist_ok=True)
        elif scene == "机器学习":
            content = """\"\"\"
机器学习项目主入口
\"\"\"
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def main():
    print('机器学习项目初始化')

if __name__ == '__main__':
    main()
"""
        elif scene == "爬虫":
            content = """\"\"\"
爬虫项目主入口
\"\"\"
import requests

def main():
    print('爬虫项目初始化')

if __name__ == '__main__':
    main()
"""
        elif scene == "桌面应用":
            content = """\"\"\"
桌面应用项目主入口
\"\"\"
import sys
from PyQt5.QtWidgets import QApplication, QLabel

def main():
    app = QApplication(sys.argv)
    label = QLabel('Hello, PyQt!')
    label.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
"""
        elif scene == "API SDK":
            content = """\"\"\"
API SDK主模块
\"\"\"
class ApiClient:
    def __init__(self, base_url: str):
        \"\"\"初始化API客户端\"\"\"
        self.base_url = base_url

    def get(self, path: str, params: dict = None):
        \"\"\"GET请求\"\"\"
        pass

    def post(self, path: str, data: dict = None):
        \"\"\"POST请求\"\"\"
        pass
"""
        else:
            # 通用后端库
            content = f"""\"\"\"
{pname} 主模块
\"\"\"
"""
        with open(os.path.join(self.src_path, f"{pname}.py"), "w", encoding="utf-8") as f:
            f.write(content)

    def _pyproject_content(self) -> str:
        mirrors = ""
        if self.config.get("add_mirror"):
            mirrors = """
[[tool.poetry.source]]
name = "tuna"
priority = "primary"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"

[[tool.poetry.source]]
name = "pypi"
priority = "supplemental"
"""
        return f"""[project]
name = "{self.config['project_name']}"
version = "0.1.0"
description = "由pytmpl自动生成的Python项目"
authors = [{{ name = "Your Name", email = "your_email@example.com" }}]
license = {{ text = "{self.config['license']}" }}
readme = "README.md"
requires-python = ">={self.config['python_version']}"

[project.scripts]
{self.config['project_name']} = "{self.config['project_name']}.cli:main"

{mirrors}[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
"""

    def _init_git(self) -> None:
        self.logger.info("正在初始化git仓库...")
        cwd = self.base_path
        subprocess.run(["git", "init"], cwd=cwd, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=cwd, capture_output=True)
        subprocess.run(["git", "commit", "-m", "🎉 init: 项目模板初始化"], cwd=cwd, capture_output=True)
        repo_url = self.config.get("repo_url", "")
        if repo_url:
            self.logger.info(f"正在关联远程仓库: {repo_url}")
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=cwd, capture_output=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=cwd, capture_output=True)
            push_result = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=cwd, capture_output=True, text=True)
            if push_result.returncode != 0:
                self.logger.error(f"❌ 推送至远程仓库失败: {push_result.stderr}")

    def _install_deps(self) -> None:
        self.logger.info("正在自动安装依赖（poetry install）...")
        cwd = self.base_path
        result = subprocess.run(["poetry", "install"], cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            self.logger.error(f"❌ 依赖安装失败: {result.stderr}")

    def _gitignore_content(self) -> str:
        return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Poetry
poetry.lock
.venv/

# PyInstaller
*.manifest
*.spec

# Installer logs
debug.log

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# mypy
.mypy_cache/
.dmypy.json

# IDEs
.idea/
.vscode/
*.sublime-project
*.sublime-workspace
"""

    def _license_content(self) -> str:
        license_text = ""
        if self.config["license"] == "MIT":
            license_text = f"""MIT License

Copyright (c) 2024 {self.config['project_name']}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        elif self.config["license"] == "Apache-2.0":
            license_text = "Apache License 2.0\n..." # Placeholder
        elif self.config["license"] == "GPLv3":
            license_text = "GPLv3 License\n..." # Placeholder
        return license_text

    def _readme_content(self) -> str:
        return f"""# 🚀 {self.config['project_name']}

## 📦 项目简介

本项目由 `pytmpl` 自动生成。
- **场景**: {self.config['scene']}
- **丰富度**: {self.config['richness']}
- **LICENSE**: {self.config['license']}
- **Python版本**: >={self.config['python_version']}

## 🛠️ 安装方法

```bash
poetry install
```

## ✨ 使用示例

```python
# 请根据生成的项目内容编写使用示例
```

## 🪵 日志工具

项目内置了功能强大的日志工具，位于 `src/{self.config['project_name']}/utils/tools.py`。

**快速使用:**
```python
from {self.config['project_name']}.utils.tools import init_logger

logger = init_logger(__name__, log_file="app.log")
logger.info("这是一条普通信息")
logger.warning("这是一条警告信息")
```

**高级配置:**
```python
# 按10MB大小分割日志，保留7个备份
logger = init_logger("my_app", log_file="app.log", rotation="size", backup_count=7)

# 每天午夜分割日志
logger = init_logger("my_app", log_file="app.log", rotation="time", when="D")
```

## ⚙️ 项目结构

```
.
├── src
│   └── {self.config['project_name']}
│       ├── __init__.py
│       ├── {self.config['project_name']}.py  # 主模块
│       └── utils
│           ├── __init__.py
│           └── tools.py    # 日志工具
├── tests
│   ├── __init__.py
│   └── test_{self.config['project_name']}.py
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## 🧑‍💻 贡献指南

欢迎提交PR和建议！

---

> 📝 本项目由 [pytmpl](https://github.com/your-repo/pytmpl) 自动生成
""" 