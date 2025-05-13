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
  created_at TIMESTAMP,
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

INSERT