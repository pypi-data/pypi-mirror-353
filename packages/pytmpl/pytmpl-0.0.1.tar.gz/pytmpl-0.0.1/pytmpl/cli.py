import sys
from .dialog import interactive_dialog
from .generator import ProjectGenerator

def main() -> None:
    """
    命令行主入口，负责交互式创建项目模板。
    :return: None
    """
    print("🚀 欢迎使用 pytmpl 项目模板生成器！\n")
    try:
        config = interactive_dialog()
        if "git_init" not in config:
            config["git_init"] = False
        generator = ProjectGenerator(config)
        generator.generate()
    except KeyboardInterrupt:
        print("\n👋 用户中断，已退出。")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 发生错误：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 