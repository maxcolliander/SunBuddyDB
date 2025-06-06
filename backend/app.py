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
            INSERT INTO useraccount (skin_type, created_at)
            VALUES (%s, %s)
        """, (skin_type, created_at))
        user_id = cursor.lastrowid

        # Insert into progressData (let DB assign ID)
        for i in range(5):
            progress = data_simulation.simulate_progressdata(user_id)
            cursor.execute(
            """
                INSERT INTO progressData (user_id, tan_level, date)
                VALUES (%s, %s, %s)
            """, (user_id, progress[1], progress[2]))
            progress_id = cursor.lastrowid
            print("Progress: ", progress)
        

        # Insert into preferences
        preferences = data_simulation.simulate_preferences(user_id)
        cursor.execute(
        """
            INSERT INTO preferences (user_id, min_time, max_time, weight_time, min_temp, max_temp, weight_temp, min_uv, max_uv, weight_uv)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, *preferences[1:]))
        print("Preferences: ", preferences)

        # Insert into session
        session_ids = []
        for i in range(10):
            session = data_simulation.simulate_session(None, None, progress_id)
            location = session[3]
            date = session[4]

            # Ensure weatherData exists for this location and date
            cursor.execute(
            """
                SELECT 1 FROM weatherData WHERE location = %s AND date = %s
            """, (location, date))
            if not cursor.fetchone():
                weather_key, location, date, uv_index_per_hour, temp_per_hour, weather_condition = data_simulation.simulate_weatherdata(location, date)
                cursor.execute(
                """
                    INSERT INTO weatherData (weatherkey, location, date, uv_index_per_hour, temp_per_hour, weather_condition)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (weather_key, location, date, uv_index_per_hour, temp_per_hour, weather_condition))

            cursor.execute(
            """
                INSERT INTO session (user_id, location, date, start_time, end_time, is_scheduled)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, location, date, session[5], session[6], session[7]))
            session_ids.append(cursor.lastrowid)
            print("Session: ", session)

        for i in range(10):
            notification = data_simulation.simulate_notifications(None, user_id)
            cursor.execute(
            """
                INSERT INTO notifications (user_id, message, created_at, is_read)
                VALUES (%s, %s, %s, %s)
            """, notification[1:])
            print("Notification: ", notification)

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


        # God tier sorting query
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
    
@app.route('/api/user/<int:user_id>/preferences', methods=['GET'])
def get_user_preferences(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Get user preferences
    cursor.execute(
    """
        SELECT min_time, max_time, weight_time,
               min_temp, max_temp, weight_temp,
               min_uv, max_uv, weight_uv
        FROM preferences
        WHERE user_id = %s
    """, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    print(result)

    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Preferences not found"}), 404
    
@app.route('/api/user/<int:user_id>/preferences', methods=['PUT'])
def update_user_preferences(user_id):
    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT preferences_id FROM preferences WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({"error": "No preferences found for user"}), 404

    preferences_id = row[0]

    # Update preferences
    cursor.execute(
    """
        UPDATE preferences
        SET min_time = %s,
            max_time = %s,
            weight_time = %s,
            min_temp = %s,
            max_temp = %s,
            weight_temp = %s,
            min_uv = %s,
            max_uv = %s,
            weight_uv = %s
        WHERE preferences_id = %s
    """, (
        data['min_time'],
        data['max_time'],
        data['weight_time'],
        data['min_temp'],
        data['max_temp'],
        data['weight_temp'],
        data['min_uv'],
        data['max_uv'],
        data['weight_uv'],
        preferences_id
    ))

    conn.commit()
    cursor.close()

    return jsonify({"message": "Preferences updated successfully"}), 200

@app.route('/api/user/<int:user_id>/sessions')
def get_user_sessions(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch sessions for the user and sort by date
    cursor.execute(
    """
        SELECT session_id, location, date, is_scheduled
        FROM session
        WHERE user_id = %s
        ORDER BY date ASC
    """, (user_id,))

    sessions = cursor.fetchall()
    cursor.close()
    return jsonify(sessions)

@app.route('/api/session/<int:session_id>/details')
def get_session_details(session_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Call stored procedure instead of raw SQL
        cursor.callproc('getSessionData', [session_id])

        # Fetch the result from stored procedure
        result = None
        for res in cursor.stored_results():
            result = res.fetchone()

        cursor.close()

        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Session not found"}), 404

    except Exception as e:
        print(f"Error retrieving session details: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/api/session/<int:session_id>/uv_exposure')
def get_uv_exposure(session_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT calculateUvExposure(%s)", (session_id,))
        result = cursor.fetchone()
        uv_exposure = int(result[0]) if result and result[0] is not None else None

        cursor.close()
        return jsonify({"session_id": session_id, "uv_exposure": uv_exposure})

    except Exception as e:
        print(f"Error calculating UV exposure: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/user/<int:user_id>/notifications')
def get_user_notifications(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
    """
        SELECT notifications_id, message, created_at, is_read
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    
    results = cursor.fetchall()
    cursor.close()
    return jsonify(results)

@app.route('/api/notification/<int:notification_id>/read', methods=['POST'])
def mark_notification_as_read(notification_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
    """
        UPDATE notifications
        SET is_read = TRUE
        WHERE notifications_id = %s
    """, (notification_id,))
    conn.commit()
    cursor.close()
    return jsonify({"status": "ok"})

@app.route('/api/notification/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
    """
        DELETE FROM notifications
        WHERE notifications_id = %s
    """, (notification_id,))
    conn.commit()
    cursor.close()
    return jsonify({"status": "deleted"})

@app.route('/api/user/<int:user_id>/notifications/read_all', methods=['POST'])
def mark_all_notifications_as_read(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc('markNotificationsAsRead', [user_id])
    conn.commit()
    cursor.close()
    return jsonify({"status": "all read"})

@app.route('/api/users/average_uv_exposure')
def average_uv_exposure():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
              u.user_id,
              AVG(calculateUvExposure(s.session_id)) AS avg_uv_exposure
            FROM useraccount u
            JOIN session s ON s.user_id = u.user_id
            WHERE s.is_scheduled = FALSE
            GROUP BY u.user_id
            ORDER BY avg_uv_exposure DESC;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            row['avg_uv_exposure'] = int(row['avg_uv_exposure']) if row['avg_uv_exposure'] is not None else None

        cursor.close()
        return jsonify(results)

    except Exception as e:
        print(f"Error calculating average UV exposure: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/api/user/<int:user_id>')
def get_user_info(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
        """
            SELECT user_id, skin_type, created_at
            FROM useraccount
            WHERE user_id = %s
        """, (user_id,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        print(f"Error fetching user info for user {user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/api/user/<int:user_id>/progress')
def get_user_progress(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
    """
        SELECT date, tan_level
        FROM progressData
        WHERE user_id = %s
        ORDER BY date
    """, (user_id,))
    
    results = cursor.fetchall()
    cursor.close()
    return jsonify(results)

if __name__ == '__main__':
    try:
        conn = get_connection()
        print("Connection successful.")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")
    app.run(debug=True)