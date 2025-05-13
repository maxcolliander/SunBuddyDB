import random
from datetime import datetime, timedelta
import json

def simulate_preferences(preferences_id):
    max_time = random.choice(range(30, 601, 15))
    min_time = random.choice(range(0, 301, 15))
    weight_time = random.choice([1, 2, 3])
    max_temp = random.choice(range(10, 41, 1))
    min_temp = random.choice(range(0, 21, 1))
    weight_temp = random.choice([1, 2, 3])
    min_uv = random.choice(range(0, 6, 1))
    max_uv = random.choice(range(2, 15, 1))
    weight_uv = random.choice([1, 2, 3])
    return [preferences_id, min_time, max_time, weight_time, min_temp, max_temp, weight_temp, min_uv, max_uv, weight_uv]

def simulate_progressdata(progress_id):
    tan_level = random.randint(0, 5)
    start_date = datetime(2025, 1, 1)
    random_days = random.randint(0, (datetime(2030, 12, 31) - start_date).days)
    random_date = start_date + timedelta(days=random_days)
    return [progress_id, tan_level, random_date.strftime('%Y-%m-%d')]

def simulate_session(session_id, scheduled_id, progress_id):
    location = random.choice(["Los Angeles", "Karlskrona", "Falkenberg", "Toronto", "Stockholm", "Madrid", "Paris", "Rom", "Oslo", "Copenhagen", "Washington"])
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2030, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    date = random_date.strftime('%Y-%m-%d')
    hours_start = random.randint(0, 23)
    minutes_start = random.randint(0, 59)
    seconds_start = random.randint(0, 59)
    time_start = f"{hours_start:02}:{minutes_start:02}:{seconds_start:02}"
    hours_end = random.randint(0, 23)
    minutes_end = random.randint(0, 59)
    seconds_end = random.randint(0, 59)
    time_end = f"{hours_end:02}:{minutes_end:02}:{seconds_end:02}"
    start_time = f"{date} {time_start}"
    end_time = f"{date} {time_end}"
    return[session_id, scheduled_id, progress_id, location, start_time, end_time]

def simulate_notifications(notifications_id, user_id):
    message = random.choice(["Your tanning session starts in 30 minutes, get ready!", 
                             "UV-levels peak at 5 today, don't miss out on it but remember your sunscreen!", 
                             "Your weekly tanning summary is ready, go check it out!"])
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2030, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    date = random_date.strftime('%Y-%m-%d')
    hours_start = random.randint(0, 23)
    minutes_start = random.randint(0, 59)
    seconds_start = random.randint(0, 59)
    time_start = f"{hours_start:02}:{minutes_start:02}:{seconds_start:02}"
    start_time = f"{date} {time_start}"
    created_at = start_time
    is_read = random.choice([True, False])
    return(notifications_id, user_id, message, created_at, is_read)

def simulate_useraccount(user_id, progress_id, scheduled_id, preferences_id):
    skin_type = random.choice(range(1, 7))
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2030, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    date = random_date.strftime('%Y-%m-%d')
    hours_start = random.randint(0, 23)
    minutes_start = random.randint(0, 59)
    seconds_start = random.randint(0, 59)
    time_start = f"{hours_start:02}:{minutes_start:02}:{seconds_start:02}"
    start_time = f"{date} {time_start}"
    created_at = start_time
    return [user_id, skin_type, created_at, progress_id, scheduled_id, preferences_id]

def simulate_weatherdata():
    pass


if __name__ == "__main__":
    all_users = []
    for i in range(1, 101):
        user_id = i
        progress_id = i
        preferences_id = i
        session_id = i
        notifications_id = i

        user = simulate_useraccount(user_id, progress_id, session_id, preferences_id)
        preferences = simulate_preferences(preferences_id)
        session = simulate_session(session_id, session_id, progress_id)
        progress = simulate_progressdata(progress_id)
        notification = simulate_notifications(notifications_id, user_id)
        
        all_users.append({
            "user_id": user[0],
            "skin_type": user[1],
            "created_at": user[2],
            "session": {
                "location": session[3],
                "start_time": session[4],
                "end_time": session[5]
            },
            "progress": {
                "tan_level": progress[1],
                "date": progress[2]
            },
            "preferences": {
                "min_time": preferences[1],
                "max_time": preferences[2],
                "weight_time": preferences[3],
                "min_temp": preferences[4],
                "max_temp": preferences[5],
                "weight_temp": preferences[6],
                "min_uv": preferences[7],
                "max_uv": preferences[8],
                "weight_uv": preferences[9]
            },
            "notifications": {
                "message": notification[2],
                "created_at": notification[3],
                "is_read": notification[4]
            }
        })
    with open("users.json", "w") as f:
        json.dump(all_users, f, indent=2)