import redis 
from IPython import embed 
import json 
import datetime 
from tqdm import tqdm 
r = redis.Redis(decode_responses=True)

def find_users_activate(date):
    all_history = r.keys("history:*")
    users_activate = set()
    for history_key in tqdm(all_history):
        his_and_genids = [(i,json.loads(i)[1]) for i in r.lrange(history_key,0,-1)]
        for his,genid in his_and_genids:

            gen_time = r.hget(f"image:{genid}","gentime")
            if gen_time is None:
                print("None error: ",genid)
                val = r.lrem(history_key,0,his)
                print(f"Delete {val} history records")
                continue 
            if gen_time.split(" ")[0]==date:
                users_activate.add(history_key.split(":")[1])
                break

    return  len(users_activate)

def report_last_days(days):
    for i in range(days):
        date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        user_activate = find_users_activate(date)
        print(f"{date} 活跃用户数: {user_activate}")

if __name__ == "__main__":
    report_last_days(7)
