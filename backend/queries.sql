CREATE TABLE preferences (
  preferences_id INT PRIMARY KEY,
  max_time TIMESTAMP,
  min_time TIMESTAMP,
  weight_time INT,
  max_temp INT,
  min_temp INT,
  weight_temp INT,
  min_uv INT,
  max_uv INT,
  weight_uv INT
);

CREATE TABLE progressData (
  progress_id INT PRIMARY KEY,
  tan_level INT,
  date DATE
);

CREATE TABLE session (
  session_id INT PRIMARY KEY,
  location VARCHAR(100),
  date DATE,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  is_scheduled BOOLEAN
);

CREATE TABLE useraccount (
  user_id INT PRIMARY KEY,
  skin_type INT,
  created_at DATE,
  progress_id INT NOT NULL,
  preferences_id INT NOT NULL,
  session_id INT NOT NULL,
  FOREIGN KEY (progress_id) REFERENCES progressData(progress_id),
  FOREIGN KEY (preferences_id) REFERENCES preferences(preferences_id),
  FOREIGN KEY (session_id) REFERENCES session(session_id)
);

CREATE TABLE weatherData (
  location VARCHAR(100),
  date DATE,
  uv_index_per_hour JSON,
  temp_per_hour JSON,
  weather_condition VARCHAR(100),
  PRIMARY KEY (location, date)
);

CREATE TABLE notifications (
  notifications_id INT PRIMARY KEY,
  user_id INT,
  message TEXT,
  created_at TIMESTAMP,
  is_read BOOLEAN,
  FOREIGN KEY (user_id) REFERENCES useraccount(user_id)
);

-- loadUserPreviousSessions
SELECT 
  s.session_id,
  s.date,
  s.start_time,
  s.end_time,
  s.location,
  w.uv_index_per_hour,
  w.temp_per_hour
FROM session s
JOIN weatherData w 
  ON s.location = w.location 
  AND s.date = w.date
JOIN useraccount u 
  ON s.session_id = u.session_id
WHERE s.is_scheduled = FALSE
  AND u.user_id = ?
ORDER BY s.date;

-- loadUserScheduledSessions
SELECT 
  s.session_id,
  s.date,
  s.start_time,
  s.end_time,
  s.location,
  w.uv_index_per_hour,
  w.temp_per_hour
FROM session s
JOIN weatherData w 
  ON s.location = w.location 
  AND s.date = w.date
JOIN useraccount u 
  ON s.session_id = u.session_id
WHERE s.is_scheduled = TRUE
  AND u.user_id = ?
  AND s.date >= CURRENT_DATE
ORDER BY s.date
LIMIT 5;

-- markNotificationsAsRead
CREATE PROCEDURE markNotificationsAsRead (
  IN uid INT
)
BEGIN
  UPDATE notifications
  SET is_read = TRUE
  WHERE user_id = uid AND is_read = FALSE;
END;

-- calculateUvExposureForSession
CREATE FUNCTION calculateUvExposureForSession (
  IN sessID INT
)
RETURNS FLOAT
BEGIN
  DECLARE s_start TIMESTAMP;
  DECLARE s_end TIMESTAMP;
  DECLARE s_date DATE;
  DECLARE s_location VARCHAR(100);
  DECLARE uv_json JSON;
  DECLARE hour TEXT;
  DECLARE uv_value FLOAT DEFAULT 0;
  DECLARE total FLOAT DEFAULT 0;
  DECLARE current_hour TIMESTAMP;

  SELECT start_time, end_time, date, location
  INTO s_start, s_end, s_date, s_location
  FROM session
  WHERE session_id = sessID;

  SELECT uv_index_per_hour
  INTO uv_json
  FROM weatherData
  WHERE location = s_location AND date = s_date;

  SET current_hour := DATE_TRUNC('hour', s_start);

  WHILE current_hour <= s_end DO
    SET hour := TO_CHAR(current_hour, 'HH24:MI');
    SET uv_value := (uv_json ->> hour)::FLOAT;
    IF uv_value IS NOT NULL THEN
      SET total := total + (uv_value * 60);  -- Assume 60 min per hour
    END IF;
    SET current_hour := current_hour + INTERVAL '1 hour';
  END WHILE;

  RETURN total;
END;

-- avgUvExposurePerUser
SELECT 
  u.user_id,
  AVG(calculateUvExposureForSession(s.session_id)) AS avg_uv_exposure
FROM session s
JOIN useraccount u ON s.session_id = u.session_id
WHERE s.is_scheduled = FALSE
GROUP BY u.user_id
ORDER BY u.user_id;