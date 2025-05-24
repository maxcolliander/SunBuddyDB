# SunBuddyDB

## Features

- User profile management
- Session and progress tracking
- Weather and UV data
- Preferences and notifications

## Installation

### 1. Clone the Repository
```sh
git clone https://github.com/maxcolliander/SunBuddyDB.git
cd SunBuddyDB
```

### 2. Install Python Depandencies

```sh
pip install -r requirements.txt
```

**Main dependencies:**
- Flask
- mysql-connector-python
- python-dotenv

### 3. Set Up Environment Variables

Create a `.env` file in the `backend` directory with your database credentials:

```
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=sunbuddydb
```

### 4. Set Up the Database

- Ensure MySQL is running.
- Run the SQL scripts in `backend/queries.sql` to create tables and stored procedures.

### 5. Run the app.py file

## Project Structure

```
SunBuddyDB/
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── .vscode/
│   └── settings.json
│
├── backend/
│   ├── .env
│   ├── app.py
│   ├── data_simulation.py
│   └── queries.sql
│
├── static/
│   ├── script.js
│   ├── style.css
│   └── user.js
│
├── templates/
│   ├── index.html
│   └── user.html
```

---

## License

MIT License

---