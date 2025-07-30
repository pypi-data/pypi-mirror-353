from typing import Dict, Any
import os

def interactive_dialog() -> Dict[str, Any]:
    """
    交互式对话流程，收集用户输入的所有参数。
    :return: 配置字典
    """
    config: Dict[str, Any] = {}
    # 项目名
    while True:
        name = input("📝 请输入项目名（必填）：")
        if name.strip():
            config["project_name"] = name.strip()
            break
        print("❌ 项目名不能为空，请重新输入。")
    # 项目路径
    default_path = os.getcwd()
    path = input(f"📂 请输入项目创建路径（默认：{default_path}）：").strip()
    config["project_path"] = path if path else default_path
    # 场景选择
    scenes = [
        "通用后端库", "Flask Web应用", "FastAPI Web应用", "Django Web应用", "命令行工具", "数据分析", "机器学习", "爬虫", "桌面应用", "API SDK"
    ]
    print("🚀 请选择项目场景：")
    for idx, scene in enumerate(scenes, 1):
        print(f"  {idx}. {scene}")
    scene_idx = input(f"输入序号（默认1）：").strip()
    try:
        scene_idx = int(scene_idx)
        if 1 <= scene_idx <= len(scenes):
            config["scene"] = scenes[scene_idx-1]
        else:
            config["scene"] = scenes[0]
    except:
        config["scene"] = scenes[0]
    # 丰富度
    richness = ["最小", "标准", "完整"]
    print("🧩 请选择模板丰富度：")
    for idx, r in enumerate(richness, 1):
        print(f"  {idx}. {r}")
    rich_idx = input(f"输入序号（默认2）：").strip()
    try:
        rich_idx = int(rich_idx)
        if 1 <= rich_idx <= len(richness):
            config["richness"] = richness[rich_idx-1]
        else:
            config["richness"] = richness[1]
    except:
        config["richness"] = richness[1]
    # LICENSE
    licenses = ["MIT", "Apache-2.0", "GPLv3", "不生成"]
    print("📜 请选择LICENSE类型：")
    for idx, lic in enumerate(licenses, 1):
        print(f"  {idx}. {lic}")
    lic_idx = input(f"输入序号（默认1）：").strip()
    try:
        lic_idx = int(lic_idx)
        if 1 <= lic_idx <= len(licenses):
            config["license"] = licenses[lic_idx-1]
        else:
            config["license"] = licenses[0]
    except:
        config["license"] = licenses[0]
    # Python版本
    pyver = input("🐍 请输入Python版本（默认3.8）：").strip()
    config["python_version"] = pyver if pyver else "3.8"
    # 是否自动安装依赖
    auto_install = input("🔧 是否自动安装依赖？(y/N，默认N)：").strip().lower()
    config["auto_install"] = auto_install == "y"
    # 是否初始化git
    git_init = input("📦 是否自动初始化git仓库？(y/N，默认N)：").strip().lower()
    config["git_init"] = (git_init == "y")
    # 远程仓库地址（仅在git_init为True时询问）
    if config["git_init"]:
        repo_url = input("🌐 请输入远程仓库地址（可选，直接回车跳过）：").strip()
        config["repo_url"] = repo_url
    else:
        config["repo_url"] = ""
    # 是否添加镜像源
    add_mirror = input("🪞 是否添加国内镜像源（推荐，Y/n，默认Y）：").strip().lower()
    config["add_mirror"] = (add_mirror != "n")
    return config 