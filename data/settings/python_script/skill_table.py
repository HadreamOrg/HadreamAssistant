# author: Lanzhijiang
# desc: 意图对应技能的配置文件  global下的都是一个技能的dict，这个dict就是skill_func_table，是二级技能到技能函数的对应

from skill.skills.orgin import music
from skill.skills.orgin import smarthome
from skill.skills.orgin import turing


skill_list = [
    "smarthome", "music", "schedule", "weather", "translate"
]


music_ = {
    "skill_file": music,
    "play": music,
}


smarthome_ = {
    "skill_file": smarthome,
    "turn_on_device": smarthome.turn_on_device,
    "turn_off_device": smarthome.turn_off_device,
    "set_resource": smarthome.set_resouce,
    "throw_it_to_aqara": smarthome.throw_it_to_aqara
}

turing_ = {
    "skill_file": turing,
    "chat": turing.chat
}


# 一个技能可以对应多个意图
l1_intent_to_skill = {
    "smarthome": smarthome_,
    "music": music_,
    "chat": turing_
}
