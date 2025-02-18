from model import init,word_hint
from database import fetch_data
import string
import logging
import json
from math import inf
from load_config import load_rewards
#from clans import create_clan
#print(fetch_data("users","telegram_id"))

#top_num = 10
#similarities = [("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101),("абадбаб",10101)]
#range_search = similarities[:top_num-1] if top_num>=len(similarities) else similarities

#print(string.ascii_lowercase)
#print(string.punctuation)
#create_clan(804897951,"Тест","'Не менее тестовое описание'","NULL")
conf = {
    "difficulty": 1000,
    "exp_multiplier": 1.0,
    "money_multiplier": 1.0,
    "hints_from_words": False
}
level_rewards = {
    1: {
        "xp_req": 100,
        "coins": 100,
        "hints": 1,
    },
    2: {
        "xp_req": 500,
        "coins": 150,
        "hints": 1
    },
    3: {
        "xp_req": 1500,
        "coins": 200,
        "hints": 1
    },
    4: {
        "xp_req": 4000,
        "coins": 250,
        "hints": 2
    },
    5: {
        "xp_req": 7500,
        "coins": 350,
        "hints": 3
    },
    6: {
        "xp_req": 10000,
        "coins": 250,
        "hints": 2
    },
    7: {"xp_req": 15000,
        "coins": 300,
        "hints": 2
    },
    8: {
        "xp_req": 25000,
        "coins": 150,
        "hints": 3
    },
    9: {
        "xp_req": 40000,
        "coins": 500,
        "hints": 0
    },
    10: {
        "xp_req": 75000,
        "coins": 1000,
        "hints": 10
    },
    "else": {
        "xp_req": inf,
        "coins": 0,
        "hints": 0
    }

}
#with open("data\\config.json","w") as j:
    #json.dump(conf,j,ensure_ascii=False)

#with open("data\\rewards.json","w") as j:
    #json.dump(level_rewards,j,ensure_ascii=False)

print(load_rewards())
