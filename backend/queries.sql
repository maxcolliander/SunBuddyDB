CREATE TABLE useraccount (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  skin_type INT,
  created_at DATE
);

CREATE TABLE preferences (
  preferences_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  min_time INT,
  max_time INT,
  weight_time INT,
  min_temp INT,
  max_temp INT,
  weight_temp INT,
  min_uv INT,
  max_uv INT,
  weight_uv INT,
  FOREIGN KEY (user_id) REFERENCES useraccount(user_id)
);

CREATE TABLE progressData (
  progress_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  tan_level INT,
  date DATE,
  FOREIGN KEY (user_id) REFERENCES useraccount(user_id)
);

CREATE TABLE session (
  session_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  location VARCHAR(100),
  date DATE,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  is_scheduled BOOLEAN
);

CREATE TABLE weatherData (
  weatherkey VARCHAR(255) PRIMARY KEY,
  location VARCHAR(100),
  date DATE,
  uv_index_per_hour JSON,
  temp_per_hour JSON,
  weather_condition VARCHAR(100)
);

CREATE TABLE notifications (
  notifications_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  message TEXT,
  created_at DATETIME,
  is_read BOOLEAN
);

DROP TABLE IF EXISTS preferences;
DROP TABLE IF EXISTS progressData;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS weatherData;
DROP TABLE IF EXISTS useraccount;
DROP TABLE IF EXISTS session;

DROP PROCEDURE IF EXISTS getSessionData;
-- getSessionData
CREATE PROCEDURE getSessionData(IN sessionID INT)
BEGIN
    SELECT 
        s.session_id,
        s.date,
        s.start_time,
        s.end_time,
        s.location,
        w.uv_index_per_hour,
        w.temp_per_hour,
        w.weather_condition
    FROM session s
    JOIN weatherData w 
      ON s.location = w.location 
      AND s.date = w.date
    WHERE s.session_id = sessionID;
END;

-- markNotificationsAsRead
CREATE PROCEDURE markNotificationsAsRead (
  IN userid INT
)
BEGIN
  UPDATE notifications
  SET is_read = TRUE
  WHERE user_id = userid AND is_read = FALSE;
END;

-- calculateUvExposure
CREATE FUNCTION calculateUvExposure(sessionID INT)
RETURNS FLOAT
DETERMINISTIC
BEGIN
  DECLARE s_start DATETIME;
  DECLARE s_end DATETIME;
  DECLARE s_date DATE;
  DECLARE s_location VARCHAR(100);
  DECLARE uv_json JSON;
  DECLARE hour_key VARCHAR(5);
  DECLARE uv_value FLOAT DEFAULT 0;
  DECLARE total FLOAT DEFAULT 0;
  DECLARE current_hour DATETIME;

  SELECT start_time, end_time, date, location
  INTO s_start, s_end, s_date, s_location
  FROM session
  WHERE session_id = sessionID;

  SELECT uv_index_per_hour
  INTO uv_json
  FROM weatherData
  WHERE location = s_location AND date = s_date;

  SET current_hour = TIMESTAMP(DATE(s_start), MAKETIME(HOUR(s_start), 0, 0));

  WHILE current_hour <= s_end DO
    SET hour_key = CAST(HOUR(current_hour) AS CHAR);

    SET uv_value = CAST(
      JSON_UNQUOTE(JSON_EXTRACT(uv_json, CONCAT('$."', hour_key, '"')))
      AS DECIMAL(10,2)
    );

    IF uv_value IS NOT NULL THEN
      SET total = total + (uv_value * 60); 
    END IF;

    SET current_hour = DATE_ADD(current_hour, INTERVAL 1 HOUR);
  END WHILE;

  RETURN total;
END;

-- avgUvExposurePerUser
SELECT 
  u.user_id,
  AVG(calculateUvExposure(s.session_id)) AS avg_uv_exposure
FROM useraccount u
JOIN session s ON s.user_id = u.user_id
WHERE s.is_scheduled = FALSE
GROUP BY u.user_id
ORDER BY avg_uv_exposure DESC;