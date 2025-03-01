from database import create_clans_db,create_clan_db,insert_data,fetch_data,cur
'''def insert_clan_in_db(name,desc,photo):
    cur.execute(f"INSERT OR IGNORE INTO clans(name,desc,photo,members,members_limit,bank) VALUES ('{name}',{desc},{photo},0,10,0)")

def create_clan(creator_id,name,desc,photo):
    create_clans_db()
    create_clan_db()
    insert_clan_in_db(name,desc,photo)
    id = fetch_data("clans","id","WHERE id=(SELECT max(id) FROM clans)")[0][0]
    insert_data(f"clan_{id}","id,role",f"{creator_id},'owner'")

def clan_info(clan_id):
    clan_info = fetch_data("clans","*",condition=f"WHERE id = {clan_id}")[0]


'''
#TODO