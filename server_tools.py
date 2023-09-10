import redis 
from IPython import embed 
import json 
import datetime 
r = redis.Redis(decode_responses=True)

def find_users_activate(date):
    all_history = r.keys("history:*")
    user_num = len(all_history)
    users_activate = []
    for history_key in all_history:
        url,genid = [json.loads(i) for i in r.lrange(history_key,0,-1)]
        gen_time = r.hget(f"image:{genid}","gentime")
        if gen_time.split(" ")[0]==date:
            users_activate.append(history_key.split(":")[1])
            break 
    # print("用户总数:",user_num)
    # print(f"活跃用户数({date}): {len(users_activate)}")
    return user_num, len(users_activate)

def report_last_days(days):
    for i in range(days):
        date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        user_num, user_activate = find_users_activate(date)
        print(f"{date} 活跃用户数: {user_activate}; 用户总数: {user_num}")

if __name__ == "__main__":
    report_last_days(7)
