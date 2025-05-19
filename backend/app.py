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

        # Insert into progressData (let DB assign ID)
        cursor.execute("""
            INSERT INTO progressData (tan_level, date)
            VALUES (%s, %s)
        """, (None, None))
        progress_id = cursor.lastrowid

        # Insert into preferences
        cursor.execute("""
            INSERT INTO preferences (min_time, max_time, weight_time, min_temp, max_temp, weight_temp, min_uv, max_uv, weight_uv)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (None, None, None, None, None, None, None, None, None))
        preferences_id = cursor.lastrowid

        # Insert into session
        cursor.execute("""
            INSERT INTO session (location, date, start_time, end_time, is_scheduled)
            VALUES (%s, %s, %s, %s, %s)
        """, (None, None, None, None, None))
        session_id = cursor.lastrowid

        # Now insert into useraccount using those IDs
        cursor.execute("""
            INSERT INTO useraccount (skin_type, created_at, progress_id, preferences_id, session_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (skin_type, created_at, progress_id, preferences_id, session_id))
        user_id = cursor.lastrowid   

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