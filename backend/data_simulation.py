import random
from datetime import datetime, timedelta
import json
import math

def simulate_preferences(preferences_id):
    min_time = random.choice(range(15, 240, 1))
    max_time = random.choice(range(min_time, 481, 1))
    weight_time = random.choice([1, 2, 3])
    min_temp = random.choice(range(0, 21, 1))
    max_temp = random.choice(range(10, 41, 1))
    weight_temp = random.choice([1, 2, 3])
    min_uv = random.choice(range(0, 6, 1))
    max_uv = random.choice(range(2, 15, 1))
    weight_uv = random.choice([1, 2, 3])
    return [preferences_id, min_time, max_time, weight_time, min_temp, max_temp, weight_temp, min_uv, max_uv, weight_uv]

def simulate_progressdata(progress_id):
    tan_level = random.randint(0, 100)
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
    # Assume `date` is a string in YYYY-MM-DD format
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    # Random start time
    start_minutes = random.randint(0, 23 * 60 + 30)  # allow up to 23:30
    start_dt = date_obj + timedelta(minutes=start_minutes)

    duration = random.randint(15, 480)
    end_dt = start_dt + timedelta(minutes=duration)

    # Format timestamps
    start_time = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    is_scheduled = random.choice([True, False])
    return[session_id, scheduled_id, progress_id, location, date, start_time, end_time, is_scheduled]

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

def simulate_useraccount(progress_id=None, session_id=None, preferences_id=None):
    progress_id = progress_id or random.randint(1, 1000)
    session_id = session_id or random.randint(1, 1000)
    preferences_id = preferences_id or random.randint(1, 1000)
    skin_type = random.choice(range(1, 7))
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2030, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    date = random_date.strftime('%Y-%m-%d')
    start_time = f"{date}"
    created_at = start_time
    return [skin_type, created_at, progress_id, session_id, preferences_id]

def simulate_weatherdata(location, date):
    if location is None:
        location = random.choice([
            "Los Angeles", "Karlskrona", "Falkenberg", "Toronto", "Stockholm",
            "Madrid", "Paris", "Rom", "Oslo", "Copenhagen", "Washington"
        ])
    if date is None:
        start_date = datetime(2025, 1, 1)
        random_days = random.randint(0, (datetime(2030, 12, 31) - start_date).days)
        random_date = start_date + timedelta(days=random_days)
        date = random_date.strftime('%Y-%m-%d')

    weather_condition = random.choice(["Sunny", "Partly cloudy", "Cloudy", "Rainy", "Windy"])

    # Temp
    temperatures = {}
    base_temp = random.uniform(10, 20)
    amplitude = random.uniform(5, 10)
    for hour in range(24):
        temp = base_temp + amplitude * math.cos((hour - 14) * math.pi / 12)
        temp += random.uniform(-1.5, 1.5)
        temperatures[str(hour)] = round(temp, 1)

    # UV
    uv_index = {}
    peak_uv = random.uniform(6, 10)
    for hour in range(24):
        if 6 <= hour <= 19:
            uv = peak_uv * math.exp(-((hour - 13) ** 2) / 8)
            uv += random.uniform(-0.3, 0.3)
            uv = max(0, uv)
        else:
            uv = 0.0
        uv_index[str(hour)] = round(uv, 1)
    
    weather_key = f"{location}_{date}"

    return [
        weather_key,
        location,
        date,
        json.dumps(uv_index),
        json.dumps(temperatures),
        weather_condition
    ]