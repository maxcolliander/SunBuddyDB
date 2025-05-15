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

@app.route('/randomize-user', methods=['POST'])
def randomize_user():
    """Generate random user data."""
    try:
        
        user = data_simulation.simulate_useraccount()
        user_data = {
            "user_id": user[0],
            "skin_type": user[1],
            "created_at": user[2],
        }
        print(f"User data: {user_data}")
        return jsonify(user_data)
    except Exception as e:
        print(f"Error in /randomize-user: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/add-user', methods=['POST'])
def add_user():
    """Insert a new user into the useraccount table."""
    try:
        data = request.get_json()
        user_id = data['user_id']
        skin_type = data['skin_type']
        created_at = data['created_at']

        conn = get_connection()
        cursor = conn.cursor()

        # Insert into progressData table
        cursor.execute("""
            INSERT INTO progressData (progress_id, tan_level, date)
            VALUES (%s, %s, %s)
        """, (user_id, None, None))  # Default tan_level is 0

        # Insert into preferences table
        cursor.execute("""
            INSERT INTO preferences (preferences_id, min_time, max_time, weight_time, min_temp, max_temp, weight_temp, min_uv, max_uv, weight_uv)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, None, None, None, None, None, None, None, None, None))  # Default preferences

        cursor.execute("""
            INSERT INTO session (session_id, location, date, start_time, end_time, is_scheduled)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, None, None, None, None, None))  # Default session values


        # Insert into useraccount table
        cursor.execute("""
            INSERT INTO useraccount (user_id, skin_type, created_at, progress_id, preferences_id, session_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, skin_type, created_at, user_id, user_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error in /add-user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    try:
        conn = get_connection()
        print("Connection successful.")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")
    app.run(debug=True)