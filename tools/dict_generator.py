# coding=utf-8
# {PROJECT_NAME}-{NAME}
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: {YEAR}/{MONTH}/{DAY}
# description: To generate your slot dict for word comparing(prefix tree)

import json

result = {}

while True:
    word_list = input("Word(SMW should be split by ',' after first word)>").split(",")
    real_word = word_list[0]
    for word in word_list:
        word_length = len(word)
        for i in range(0, word_length):
            chara = word[i]
            if i == 1:
                if chara not in result:
                    # add new staring-point
                    result[chara] = {}
            elif i == word_length:
                result[chara] = real_word
            else:
                if chara in result[word[i-1]]:
                    pass


# {"A": {"B": {"D": ["ABE"], "C": ["ABF"]}}}