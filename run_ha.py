# coding=utf-8
# author: Lan_zhijiang
# description: start the whole system
# date: 2021/11/4

from init import HAInit
from lib import common_func
# import sys

# sys.path.append("/home/ha/SmartChildrenHome/assistant/data")


def run():
        try:
            HAInit.run()
        except KeyboardInterrupt:
            # 执行退出流程
            common_func.Pixels.off()


if __name__ == "__main__":
    run()