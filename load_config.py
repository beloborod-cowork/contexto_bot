import json
def load_config():
    with open("data/config.json","r") as j:
        return json.load(j)
    
def load_rewards():
    with open("data/rewards.json","r") as j:
        return json.load(j)

def save_config(config):
    with open("data/config.json","w") as f:
        json.dump(config,f)