import sys
from pytmpl.cli import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 发生错误：{e}", file=sys.stderr)
        sys.exit(1) 