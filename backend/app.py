from flask import Flask, render_template
import os
import mysql.connector
from dotenv import load_dotenv

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

if __name__ == '__main__':
    try:
        conn = get_connection()
        print("Connection successful.")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")
    app.run(debug=True)