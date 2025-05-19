from flask import Flask, render_template, jsonify, request
import os
import mysql.connector
from dotenv import load_dotenv
import data_simulation


load_dotenv()

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<int:user_id>')
def user_page(user_id):
    return render_template('user.html', user_id=user_id)

@app.route('/randomize-user', methods=['POST'])
def randomize_user():
    """Generate random user data."""
    try:
        
        user = data_simulation.simulate_useraccount()
        user_data = {
            "skin_type": user[0],
            "created_at": user[1],
        }
        print(f"User data: {user_data}")
        return jsonify(user_data)
    except Exception as e:
        print(f"Error in /randomize-user: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/add-user', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
    
        skin_type = data['skin_type']
        created_at = data['created_at']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT IFNULL(MAX(user_id), 0) + 1 FROM useraccount")
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO useraccount (skin_type, created_at, progress_id, preferences_id, session_id)
            VALUES (%s, %s, NULL, NULL, NULL)
        """, (skin_type, created_at))
        user_id = cursor.lastrowid

        # Insert into progressData (let DB assign ID)
        for i in range(5):
            progress = data_simulation.simulate_progressdata(user_id)
            cursor.execute("""
                INSERT INTO progressData (user_id, tan_level, date)
                VALUES (%s, %s, %s)
            """, (user_id, progress[1], progress[2]))
            progress_id = cursor.lastrowid
            print("Progress: ", progress)
        

        # Insert into preferences¨
        preferences = data_simulation.simulate_preferences(user_id)
        cursor.execute("""
            INSERT INTO preferences (min_time, max_time, weight_time, min_temp, max_temp, weight_temp, min_uv, max_uv, weight_uv)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, preferences[1:])
        preferences_id = cursor.lastrowid
        print("Preferences: ", preferences)

        # Insert into session
        session_ids = []
        for i in range(10):
            session = data_simulation.simulate_session(None, None, progress_id)
            location = session[3]
            date = session[4]

            # Ensure weatherData exists for this location and date
            cursor.execute("""
                SELECT 1 FROM weatherData WHERE location = %s AND date = %s
            """, (location, date))
            if not cursor.fetchone():
                # Simulate weather data (adjust this function as needed)
                weather_key, location, date, uv_index_per_hour, temp_per_hour, weather_condition = data_simulation.simulate_weatherdata(location, date)
                cursor.execute("""
                    INSERT INTO weatherData (weatherkey, location, date, uv_index_per_hour, temp_per_hour, weather_condition)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (weather_key, location, date, uv_index_per_hour, temp_per_hour, weather_condition))

            cursor.execute("""
                INSERT INTO session (user_id, location, date, start_time, end_time, is_scheduled)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, location, date, session[5], session[6], session[7]))
            session_ids.append(cursor.lastrowid)
            print("Session: ", session)

        for i in range(10):
            notification = data_simulation.simulate_notifications(None, user_id)
            cursor.execute("""
                INSERT INTO notifications (user_id, message, created_at, is_read)
                VALUES (%s, %s, %s, %s)
            """, notification[1:])
            print("Notification: ", notification)
        
        cursor.execute("""
            UPDATE useraccount
            SET progress_id = %s, preferences_id = %s, session_id = %s
            WHERE user_id = %s
        """, (progress_id, preferences_id, session_ids[0], user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error in /add-user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    

@app.route('/get-max-user-id', methods=['GET'])
def get_max_user_id():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(user_id) FROM useraccount")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        max_id = result[0] if result[0] is not None else 0
        return jsonify({"max_user_id": max_id}), 200
    except Exception as e:
        print(f"Error fetching max user_id: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/get-users', methods=['GET'])
def get_users():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit

        # Sorting
        allowed_sort = {'user_id', 'created_at'}
        sort_by = request.args.get('sort_by', 'user_id')
        sort_order = request.args.get('sort_order', 'asc')
        if sort_by not in allowed_sort:
            sort_by = 'user_id'
        if sort_order not in {'asc', 'desc'}:
            sort_order = 'asc'

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM useraccount")
        total = cursor.fetchone()['total']

        query = f"SELECT * FROM useraccount ORDER BY {sort_by} {sort_order.upper()} LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({
            "users": users,
            "total": total,
            "page": page,
            "limit": limit
        }), 200
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        conn = get_connection()
        print("Connection successful.")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")
    app.run(debug=True)