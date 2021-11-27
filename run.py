# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: HA's startup script
# date: 2021/11/4

from backend.init import HAInit

if __name__ == "__main__":
    init = HAInit()
    init.run()