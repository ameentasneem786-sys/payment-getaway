import os
import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)  # 🔥 FIRST

# ✅ THEN CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    return response


# ✅ DB CONFIG (TiDB)
def get_db_config():
    return {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": 4000,
        "ssl_disabled": False
    }

db = None
cursor = None

def init_db():
    global db, cursor
    db = mysql.connector.connect(**get_db_config())
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        mobile VARCHAR(10),
        amount DECIMAL(10,2)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recharge (
        id INT AUTO_INCREMENT PRIMARY KEY,
        mobile VARCHAR(10),
        amount DECIMAL(10,2)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS add_money (
        id INT AUTO_INCREMENT PRIMARY KEY,
        amount DECIMAL(10,2)
    )
    """)

    db.commit()
    print("✅ Database Connected")

def ensure_db():
    global db
    try:
        if db and db.is_connected():
            return True
    except:
        pass
    init_db()
    return True


@app.route("/")
def home():
    return jsonify({"message": "Backend Running"})


# ✅ SEND MONEY
@app.route("/send-money", methods=["POST", "OPTIONS"])
def send_money():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        if not ensure_db():
            return jsonify({"error": "DB error"}), 500

        data = request.get_json(silent=True) or {}

        mobile = str(data.get("mobile", "")).strip()
        amount = float(data.get("amount", 0))

        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            return jsonify({"error": "Invalid mobile"}), 400

        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        cursor.execute(
            "INSERT INTO transactions (mobile, amount) VALUES (%s, %s)",
            (mobile, amount)
        )
        db.commit()

        return jsonify({"message": "Payment Successful"}), 201

    except Exception as e:
        print("🔥 SEND ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ✅ ADD MONEY
@app.route("/add-money", methods=["POST", "OPTIONS"])
def add_money():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        if not ensure_db():
            return jsonify({"error": "DB error"}), 500

        data = request.get_json(silent=True) or {}

        amount = float(data.get("amount", 0))

        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        cursor.execute(
            "INSERT INTO add_money (amount) VALUES (%s)",
            (amount,)
        )
        db.commit()

        return jsonify({"message": "Money Added Successfully"}), 200

    except Exception as e:
        print("🔥 ADD MONEY ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ✅ RECHARGE
@app.route("/recharge", methods=["POST"])
def recharge():
    try:
        if not ensure_db():
            return jsonify({"error": "DB error"}), 500

        data = request.get_json(silent=True) or {}

        mobile = data.get("mobile", "").strip()
        amount = float(data.get("amount", 0))

        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            return jsonify({"error": "Invalid mobile"}), 400

        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        cursor.execute(
            "INSERT INTO recharge (mobile, amount) VALUES (%s, %s)",
            (mobile, amount)
        )
        db.commit()

        return jsonify({"message": "Recharge Successful"}), 201

    except Exception as e:
        print("🔥 RECHARGE ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ✅ TRANSACTIONS
@app.route("/transactions", methods=["GET"])
def transactions():
    if not ensure_db():
        return jsonify({"error": "DB error"}), 500

    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()

    return jsonify(data), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
