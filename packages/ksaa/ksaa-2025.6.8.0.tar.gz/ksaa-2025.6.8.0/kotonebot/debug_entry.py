import runpy
import logging
import argparse

from kotonebot.kaa.common import BaseConfig


def run_script(script_path: str) -> None:
    """
    使用 runpy 运行指定的 Python 脚本

    Args:
        script_path: Python 脚本的路径
    """
    # 获取模块名
    module_name = script_path.strip('.py').replace('\\', '/').strip('/').replace('/', '.')

    print(f"正在运行脚本: {script_path}")
    # 运行脚本
    from kotonebot.backend.context import init_context
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logging.getLogger('kotonebot').setLevel(logging.DEBUG)
    init_context(config_type=BaseConfig)
    runpy.run_module(module_name, run_name="__main__")

def main():
    parser = argparse.ArgumentParser(description='运行指定的 Python 脚本')
    parser.add_argument('script_path', help='要运行的 Python 脚本路径')

    args = parser.parse_args()
    run_script(args.script_path)


if __name__ == '__main__':
    main()