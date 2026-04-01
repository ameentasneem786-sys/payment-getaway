# from datetime import datetime, timedelta
# import os
# import jwt
# import mysql.connector
# from dotenv import load_dotenv
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from werkzeug.security import check_password_hash, generate_password_hash

# load_dotenv()

# app = Flask(__name__)
# SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")
# PAYMENT_METHOD_LABELS = {
#     "wallet": "Wallet",
#     "debit-card": "Debit Card",
#     "credit-card": "Credit Card",
#     "google-pay": "Google Pay",
#     "phonepe": "PhonePe",
#     "paytm": "Paytm",
# }

# db = None
# cursor = None


# def build_allowed_origins():
#     origins = {
#         "http://paymentgetwayindia.netlify.app",
#         "http://localhost:5173",
#         "http://127.0.0.1:5173",
#         "http://localhost:3000",
#     }

#     extra_origins = os.getenv("CORS_ORIGINS", "")

#     for origin in extra_origins.split(","):
#         cleaned_origin = origin.strip()

#         if cleaned_origin:
#             origins.add(cleaned_origin)

#     return sorted(origins)


# CORS(app, origins="*")


# def get_db_config():
#     return {
#         "host": os.getenv("DB_HOST", "localhost"),
#         "user": os.getenv("DB_USER", "root"),
#         "password": os.getenv("DB_PASSWORD", ""),
#         "database": os.getenv("DB_NAME", "payment-getaway"),
#     }


# def column_exists(table_name, column_name):
#     cursor.execute(
#         """
#         SELECT COUNT(*)
#         FROM information_schema.COLUMNS
#         WHERE TABLE_SCHEMA = DATABASE()
#           AND TABLE_NAME = %s
#           AND COLUMN_NAME = %s
#         """,
#         (table_name, column_name),
#     )
#     return cursor.fetchone()[0] > 0


# def ensure_column(table_name, column_name, definition):
#     if not column_exists(table_name, column_name):
#         cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {definition}")


# def init_db():
#     global db, cursor

#     try:
#         db = mysql.connector.connect(**get_db_config())
#         cursor = db.cursor()

#         cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS users (
#                 id INT PRIMARY KEY AUTO_INCREMENT,
#                 name VARCHAR(255) NOT NULL,
#                 email VARCHAR(255) UNIQUE NOT NULL,
#                 password VARCHAR(255) NOT NULL,
#                 phone VARCHAR(10),
#                 balance DECIMAL(10,2) NOT NULL DEFAULT 5000.00,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#             """
#         )

#         cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS transactions (
#                 id INT PRIMARY KEY AUTO_INCREMENT,
#                 user_id INT NULL,
#                 mobile VARCHAR(10) NOT NULL,
#                 amount DECIMAL(10,2) NOT NULL,
#                 payment_method VARCHAR(50) NOT NULL DEFAULT 'wallet',
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#             """
#         )

#         cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS recharge (
#                 id INT PRIMARY KEY AUTO_INCREMENT,
#                 user_id INT NULL,
#                 mobile VARCHAR(10) NOT NULL,
#                 amount DECIMAL(10,2) NOT NULL,
#                 payment_method VARCHAR(50) NOT NULL DEFAULT 'wallet',
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#             """
#         )

#         cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS add_money (
#                 id INT PRIMARY KEY AUTO_INCREMENT,
#                 user_id INT NOT NULL,
#                 amount DECIMAL(10,2) NOT NULL,
#                 status VARCHAR(50) DEFAULT 'Success',
#                 payment_method VARCHAR(50) NOT NULL DEFAULT 'debit-card',
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#             """
#         )

#         ensure_column("users", "phone", "phone VARCHAR(10) NULL")
#         ensure_column(
#             "users",
#             "balance",
#             "balance DECIMAL(10,2) NOT NULL DEFAULT 5000.00",
#         )
#         ensure_column(
#             "users",
#             "created_at",
#             "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
#         )

#         cursor.execute("ALTER TABLE users MODIFY COLUMN password VARCHAR(255) NOT NULL")

#         ensure_column("transactions", "user_id", "user_id INT NULL")
#         ensure_column("transactions", "mobile", "mobile VARCHAR(10) NULL")
#         ensure_column(
#             "transactions",
#             "payment_method",
#             "payment_method VARCHAR(50) NOT NULL DEFAULT 'wallet'",
#         )
#         ensure_column(
#             "transactions",
#             "created_at",
#             "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
#         )

#         if column_exists("transactions", "sender"):
#             cursor.execute(
#                 """
#                 UPDATE transactions
#                 SET mobile = sender
#                 WHERE (mobile IS NULL OR mobile = '')
#                   AND sender IS NOT NULL
#                 """
#             )

#         ensure_column("recharge", "user_id", "user_id INT NULL")
#         ensure_column(
#             "recharge",
#             "payment_method",
#             "payment_method VARCHAR(50) NOT NULL DEFAULT 'wallet'",
#         )
#         ensure_column(
#             "recharge",
#             "created_at",
#             "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
#         )

#         ensure_column(
#             "add_money",
#             "payment_method",
#             "payment_method VARCHAR(50) NOT NULL DEFAULT 'debit-card'",
#         )
#         ensure_column(
#             "add_money",
#             "created_at",
#             "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
#         )

#         db.commit()
#         print("Database connected successfully")
#         return True
#     except mysql.connector.Error as error:
#         print(f"Database connection error: {error}")
#         db = None
#         cursor = None
#         return False


# def ensure_db():
#     global db

#     try:
#         if db is not None and db.is_connected() and cursor is not None:
#             return True
#     except mysql.connector.Error:
#         pass

#     return init_db()


# def json_error(message, status_code):
#     return jsonify({"error": message}), status_code


# def serialize_user(user_row):
#     return {
#         "id": user_row[0],
#         "name": user_row[1],
#         "email": user_row[2],
#         "phone": user_row[3],
#         "balance": float(user_row[4] or 0),
#         "created_at": user_row[5].isoformat() if user_row[5] else None,
#     }


# def fetch_user(user_id):
#     cursor.execute(
#         """
#         SELECT id, name, email, phone, balance, created_at
#         FROM users
#         WHERE id = %s
#         """,
#         (user_id,),
#     )
#     return cursor.fetchone()


# def fetch_login_user(email):
#     cursor.execute(
#         """
#         SELECT id, name, email, phone, password, balance, created_at
#         FROM users
#         WHERE email = %s
#         """,
#         (email,),
#     )
#     return cursor.fetchone()


# def get_auth_payload(required=False):
#     auth_header = request.headers.get("Authorization", "")

#     if not auth_header.startswith("Bearer "):
#         if required:
#             return None, json_error("Missing authentication token", 401)
#         return None, None

#     token = auth_header.split(" ", 1)[1].strip()

#     try:
#         return jwt.decode(token, SECRET_KEY, algorithms=["HS256"]), None
#     except jwt.ExpiredSignatureError:
#         return None, json_error("Authentication token expired", 401)
#     except jwt.InvalidTokenError:
#         return None, json_error("Invalid authentication token", 401)


# def get_current_user(required=False):
#     payload, error = get_auth_payload(required=required)

#     if error:
#         return None, error

#     if not payload:
#         return None, None

#     user = fetch_user(payload["user_id"])

#     if not user:
#         return None, json_error("User not found", 404)

#     return user, None


# def parse_amount(raw_amount, max_amount):
#     try:
#         amount = round(float(raw_amount), 2)
#     except (TypeError, ValueError):
#         return None, json_error("Amount must be a valid number", 400)

#     if amount <= 0:
#         return None, json_error("Amount must be greater than 0", 400)

#     if amount > max_amount:
#         return None, json_error(f"Amount cannot exceed {max_amount}", 400)

#     return amount, None


# def parse_payment_method(raw_method, default_method="wallet"):
#     payment_method = (raw_method or default_method).strip().lower()

#     if payment_method not in PAYMENT_METHOD_LABELS:
#         return None, json_error("Unsupported payment method selected", 400)

#     return payment_method, None


# def format_payment_method(payment_method):
#     return PAYMENT_METHOD_LABELS.get(
#         (payment_method or "").strip().lower(),
#         PAYMENT_METHOD_LABELS["wallet"],
#     )


# def serialize_transaction(row, transaction_type):
#     created_at = row[4]

#     return {
#         "id": row[0],
#         "mobile": row[1],
#         "amount": float(row[2] or 0),
#         "payment_method": format_payment_method(row[3]),
#         "type": transaction_type,
#         "created_at": created_at.isoformat() if created_at else None,
#         "_sort_value": created_at or datetime.min,
#     }


# init_db()


# @app.route("/")
# def home():
#     return jsonify({"message": "Backend running"})


# @app.route("/health")
# def health():
#     return jsonify({"status": "ok"})


# @app.route("/register", methods=["POST"])
# def register():
#     if not ensure_db():
#         return json_error("Database connection failed", 500)

#     data = request.get_json(silent=False) or {}
#     name = data.get("name", "").strip()
#     email = data.get("email", "").strip().lower()
#     password = data.get("password", "")
#     phone = data.get("phone", "").strip()

#     if not name or not email or not password:
#         return json_error("Missing required fields", 400)

#     if len(name) < 3:
#         return json_error("Name must be at least 3 characters", 400)

#     if len(password) < 6:
#         return json_error("Password must be at least 6 characters", 400)

#     if "@" not in email:
#         return json_error("Invalid email format", 400)

#     if phone and not phone.isdigit():
#         return json_error("Phone must contain only digits", 400)

#     if phone and len(phone) != 10:
#         return json_error("Phone must be 10 digits", 400)

#     cursor.execute("SELECT id FROM users WHERE email = %s", (email,))

#     if cursor.fetchone():
#         return json_error("Email already registered", 400)

#     hashed_password = generate_password_hash(password)

#     cursor.execute(
#         """
#         INSERT INTO users (name, email, password, phone)
#         VALUES (%s, %s, %s, %s)
#         """,
#         (name, email, hashed_password, phone or None),
#     )
#     db.commit()

#     return jsonify({"message": "Account created successfully"}), 201


# @app.route("/login", methods=["POST"])
# def login():
#     if not ensure_db():
#         return json_error("Database connection failed", 500)

#     data = request.get_json(silent=False) or {}
#     email = data.get("email", "").strip().lower()
#     password = data.get("password", "")

#     if not email or not password:
#         return json_error("Missing email or password", 400)

#     user = fetch_login_user(email)

#     if not user or not check_password_hash(user[4], password):
#         return json_error("Invalid email or password", 401)

#     token = jwt.encode(
#         {
#             "user_id": user[0],
#             "email": user[2],
#             "exp": datetime.utcnow() + timedelta(days=7),
#         },
#         SECRET_KEY,
#         algorithm="HS256",
#     )

#     return (
#         jsonify(
#             {
#                 "message": "Login successful",
#                 "token": token,
#                 "user": serialize_user(
#                     (user[0], user[1], user[2], user[3], user[5], user[6])
#                 ),
#             }
#         ),
#         200,
#     )


# @app.route("/profile", methods=["GET"])
# def get_profile():
#     if not ensure_db():
#         return json_error("Database connection failed", 500)

#     user, error = get_current_user(required=False)

#     if error:
#         return error

#     user_id = user[0]

#     cursor.execute(
#         """
#         SELECT COUNT(*), COALESCE(SUM(amount), 0)
#         FROM transactions
#         WHERE user_id = %s
#         """,
#         (user_id,),
#     )
#     send_count, send_amount = cursor.fetchone()

#     cursor.execute(
#         """
#         SELECT COUNT(*), COALESCE(SUM(amount), 0)
#         FROM recharge
#         WHERE user_id = %s
#         """,
#         (user_id,),
#     )
#     recharge_count, recharge_amount = cursor.fetchone()

#     return (
#         jsonify(
#             {
#                 "user": serialize_user(user),
#                 "stats": {
#                     "send_transactions": send_count,
#                     "recharge_transactions": recharge_count,
#                     "total_sent": float(send_amount or 0),
#                     "total_recharged": float(recharge_amount or 0),
#                 },
#             }
#         ),
#         200,
#     )


# @app.route("/profile", methods=["PUT"])
# def update_profile():
#     if not ensure_db():
#         return json_error("Database connection failed", 500)

#     user, error = get_current_user(required=False)

#     if error:
#         return error

#     data = request.get_json(silent=False) or {}
#     update_fields = []
#     update_values = []

#     if "name" in data:
#         name = data.get("name", "").strip()

#         if not name:
#             return json_error("Name is required", 400)

#         if len(name) < 3:
#             return json_error("Name must be at least 3 characters", 400)

#         update_fields.append("name = %s")
#         update_values.append(name)

#     if "phone" in data:
#         phone = data.get("phone", "").strip()

#         if phone and (not phone.isdigit() or len(phone) != 10):
#             return json_error("Phone must be 10 digits", 400)

#         update_fields.append("phone = %s")
#         update_values.append(phone or None)

#     if not update_fields:
#         return json_error("No fields to update", 400)

#     update_values.append(user[0])

#     cursor.execute(
#         f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s",
#         update_values,
#     )
#     db.commit()

#     updated_user = fetch_user(user[0])

#     return jsonify({"message": "Profile updated successfully", "user": serialize_user(updated_user)}), 200


# @app.route("/change-password", methods=["POST"])
# def change_password():
#     if not ensure_db():
#         return json_error("Database connection failed", 500)

#     user, error = get_current_user(required=False)

#     if error:
#         return error

#     data = request.get_json(silent=False) or {}
#     old_password = data.get("old_password", "")
#     new_password = data.get("new_password", "")

#     if not old_password or not new_password:
#         return json_error("Missing required fields", 400)

#     cursor.execute("SELECT password FROM users WHERE id = %s", (user[0],))
#     password_row = cursor.fetchone()

#     if not password_row or not check_password_hash(password_row[0], old_password):
#         return json_error("Current password is incorrect", 401)

#     if len(new_password) < 6:
#         return json_error("New password must be at least 6 characters", 400)

#     hashed_password = generate_password_hash(new_password)
#     cursor.execute(
#         "UPDATE users SET password = %s WHERE id = %s",
#         (hashed_password, user[0]),
#     )
#     db.commit()

#     return jsonify({"message": "Password changed successfully"}), 200


# # @app.route("/send-money", methods=["POST"])
# # def send_money():
# #     if not ensure_db():
# #         return json_error("Database connection failed", 500)

# #     data = request.get_json(silent=True) or {}
# #     mobile = data.get("mobile", "").strip()
# #     amount, error = parse_amount(data.get("amount"), 100000)

# #     if error:
# #         return error

# #     if not mobile or not mobile.isdigit() or len(mobile) != 10:
# #         return json_error("Mobile number must be 10 digits", 400)

# #     user, auth_error = get_current_user(required=False)

# #     if auth_error:
# #         return auth_error

# #     payment_method, method_error = parse_payment_method(
# #         data.get("payment_method"),
# #         default_method="wallet",
# #     )


#     @app.route("/send-money", methods=["POST"])
# def send_money():
#     ensure_db()

#     # 🔥 ye line missing thi
#     data = request.get_json(silent=True) or {}

#     mobile = data.get("mobile", "").strip()
#     amount = float(data.get("amount", 0))

#     if not mobile or len(mobile) != 10:
#         return jsonify({"error": "Invalid mobile"}), 400

#     cursor.execute(
#         "INSERT INTO transactions (mobile, amount) VALUES (%s, %s)",
#         (mobile, amount)
#     )
#     db.commit()

#     return jsonify({"message": "Payment Success"}), 201
#     if method_error:
#         return method_error

#     if user and payment_method == "wallet":
#         current_balance = float(user[4] or 0)

#         if current_balance < amount:
#             return json_error("Insufficient balance", 400)

#         cursor.execute(
#             """
#             INSERT INTO transactions (user_id, mobile, amount, payment_method)
#             VALUES (%s, %s, %s, %s)
#             """,
#             (user[0], mobile, amount, payment_method),
#         )
#         cursor.execute(
#             "UPDATE users SET balance = balance - %s WHERE id = %s",
#             (amount, user[0]),
#         )
#         db.commit()

#         updated_user = fetch_user(user[0])

#         return (
#             jsonify(
#                 {
#                     "message": "Payment Successful",
#                     "user": serialize_user(updated_user),
#                     "payment_method": format_payment_method(payment_method),
#                 }
#             ),
#             201,
#         )

#     if user:
#         cursor.execute(
#             """
#             INSERT INTO transactions (user_id, mobile, amount, payment_method)
#             VALUES (%s, %s, %s, %s)
#             """,
#             (user[0], mobile, amount, payment_method),
#         )
#         db.commit()

#         refreshed_user = fetch_user(user[0])

#         return (
#             jsonify(
#                 {
#                     "message": "Payment Successful",
#                     "user": serialize_user(refreshed_user),
#                     "payment_method": format_payment_method(payment_method),
#                 }
#             ),
#             201,
#         )

#     cursor.execute(
#         """
#         INSERT INTO transactions (mobile, amount, payment_method)
#         VALUES (%s, %s, %s)
#         """,
#         (mobile, amount, payment_method),
#     )
#     db.commit()

#     return (
#         jsonify(
#             {
#                 "message": "Payment Successful",
#                 "payment_method": format_payment_method(payment_method),
#             }
#         ),
#         201,
#     )


# @app.route("/recharge", methods=["POST"])
# def recharge():
#     if not ensure_db():
#         return json_error("Database connection failed", 500)

#     data = request.get_json(silent=True) or {}
#     mobile = data.get("mobile", "").strip()
#     amount, error = parse_amount(data.get("amount"), 50000)

#     if error:
#         return error

#     if not mobile or not mobile.isdigit() or len(mobile) != 10:
#         return json_error("Mobile number must be 10 digits", 400)

#     user, auth_error = get_current_user(required=False)

#     if auth_error:
#         return auth_error

#     payment_method, method_error = parse_payment_method(
#         data.get("payment_method"),
#         default_method="wallet",
#     )

#     if method_error:
#         return method_error

#     if user and payment_method == "wallet":
#         current_balance = float(user[4] or 0)

#         if current_balance < amount:
#             return json_error("Insufficient balance", 400)

#         cursor.execute(
#             """
#             INSERT INTO recharge (user_id, mobile, amount, payment_method)
#             VALUES (%s, %s, %s, %s)
#             """,
#             (user[0], mobile, amount, payment_method),
#         )
#         cursor.execute(
#             "UPDATE users SET balance = balance - %s WHERE id = %s",
#             (amount, user[0]),
#         )
#         db.commit()

#         updated_user = fetch_user(user[0])

#         return (
#             jsonify(
#                 {
#                     "message": "Recharge Successful",
#                     "user": serialize_user(updated_user),
#                     "payment_method": format_payment_method(payment_method),
#                 }
#             ),
#             201,
#         )

#     if user:
#         cursor.execute(
#             """
#             INSERT INTO recharge (user_id, mobile, amount, payment_method)
#             VALUES (%s, %s, %s, %s)
#             """,
#             (user[0], mobile, amount, payment_method),
#         )
#         db.commit()

#         refreshed_user = fetch_user(user[0])

#         return (
#             jsonify(
#                 {
#                     "message": "Recharge Successful",
#                     "user": serialize_user(refreshed_user),
#                     "payment_method": format_payment_method(payment_method),
#                 }
#             ),
#             201,
#         )

#     cursor.execute(
#         """
#         INSERT INTO recharge (mobile, amount, payment_method)
#         VALUES (%s, %s, %s)
#         """,
#         (mobile, amount, payment_method),
#     )
#     db.commit()

#     return (
#         jsonify(
#             {
#                 "message": "Recharge Successful",
#                 "payment_method": format_payment_method(payment_method),
#             }
#         ),
#         201,
#     )


# @app.route("/transactions", methods=["GET"])
# def transactions():
#     if not ensure_db():
#         return json_error("Database connection failed", 500)

#     user, auth_error = get_current_user(required=False)

#     if auth_error:
#         return auth_error

#     if user:
#         cursor.execute(
#             """
#             SELECT id, mobile, amount, payment_method, created_at
#             FROM recharge
#             WHERE user_id = %s
#             ORDER BY created_at DESC, id DESC
#             """,
#             (user[0],),
#         )
#         recharge_rows = cursor.fetchall()

#         cursor.execute(
#             """
#             SELECT id, mobile, amount, payment_method, created_at
#             FROM transactions
#             WHERE user_id = %s
#             ORDER BY created_at DESC, id DESC
#             """,
#             (user[0],),
#         )
#         transaction_rows = cursor.fetchall()
#     else:
#         cursor.execute(
#             """
#             SELECT id, mobile, amount, payment_method, created_at
#             FROM recharge
#             ORDER BY created_at DESC, id DESC
#             """
#         )
#         recharge_rows = cursor.fetchall()

#         cursor.execute(
#             """
#             SELECT id, mobile, amount, payment_method, created_at
#             FROM transactions
#             ORDER BY created_at DESC, id DESC
#             """
#         )
#         transaction_rows = cursor.fetchall()

#     data = [serialize_transaction(row, "Recharge") for row in recharge_rows]
#     data.extend(
#         [serialize_transaction(row, "Send Money") for row in transaction_rows]
#     )
#     data.sort(key=lambda item: (item["_sort_value"], item["id"]), reverse=True)

#     for item in data:
#         item.pop("_sort_value", None)

#     return jsonify(data), 200


# @app.route("/add-money", methods=["POST"])
# def add_money():
#     if not ensure_db():
#         return json_error("Database connection failed", 500)

#     user, error = get_current_user(required=False)

#     if error:
#         return error

#     data = request.get_json(silent=True) or {}
#     amount, parse_error = parse_amount(data.get("amount"), 100000)

#     if parse_error:
#         return parse_error

#     payment_method, method_error = parse_payment_method(
#         data.get("payment_method"),
#         default_method="debit-card",
#     )

#     if method_error:
#         return method_error

#     cursor.execute(
#         "UPDATE users SET balance = balance + %s WHERE id = %s",
#         (amount, user[0]),
#     )
#     cursor.execute(
#         """
#         INSERT INTO add_money (user_id, amount, status, payment_method)
#         VALUES (%s, %s, %s, %s)
#         """,
#         (user[0], amount, "Success", payment_method),
#     )
#     db.commit()

#     updated_user = fetch_user(user[0])

#     return (
#         jsonify(
#             {
#                 "message": "Money added successfully",
#                 "user": serialize_user(updated_user),
#                 "payment_method": format_payment_method(payment_method),
#             }
#         ),
#         200,
#     )


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000)) 
#     app.run(host="0.0.0.0", port=port)

# # if __name__ == "__main__":
# #     app.run(
# #         host=os.getenv("HOST", "0.0.0.0"),
# #         port=int(os.getenv("PORT", "5000")),
# #         debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
# #     )


























import os
import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")

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

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        password VARCHAR(255)
    )
    """)

    # SEND MONEY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        mobile VARCHAR(10),
        amount DECIMAL(10,2)
    )
    """)

    # RECHARGE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recharge (
        id INT AUTO_INCREMENT PRIMARY KEY,
        mobile VARCHAR(10),
        amount DECIMAL(10,2)
    )
    """)

    # ADD MONEY
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


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ✅ SEND MONEY@app.route("/send-money", methods=["POST"])
def send_money():
    try:
        if not ensure_db():
            return jsonify({"error": "DB error"}), 500

        # ✅ FIX (missing tha)
        data = request.get_json(silent=True) or {}

        mobile = data.get("mobile", "").strip()

        try:
            amount = float(data.get("amount", 0))
        except:
            return jsonify({"error": "Invalid amount"}), 400

        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            return jsonify({"error": "Invalid mobile number"}), 400

        if amount <= 0:
            return jsonify({"error": "Amount must be greater than 0"}), 400

        cursor.execute(
            "INSERT INTO transactions (mobile, amount) VALUES (%s, %s)",
            (mobile, amount)
        )
        db.commit()

        return jsonify({"message": "Payment Successful"}), 201

    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({"error": str(e)}), 500

# ✅ RECHARGE
@app.route("/recharge", methods=["POST"])
def recharge():
    if not ensure_db():
        return jsonify({"error": "DB error"}), 500

    data = request.get_json(silent=True) or {}

    mobile = data.get("mobile", "").strip()

    try:
        amount = float(data.get("amount", 0))
    except:
        return jsonify({"error": "Invalid amount"}), 400

    if not mobile or not mobile.isdigit() or len(mobile) != 10:
        return jsonify({"error": "Invalid mobile number"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400

    try:
        cursor.execute(
            "INSERT INTO recharge (mobile, amount) VALUES (%s, %s)",
            (mobile, amount)
        )
        db.commit()
    except Exception as e:
        print("DB ERROR:", e)
        return jsonify({"error": "Database error"}), 500

    return jsonify({"message": "Recharge Successful"}), 201


# ✅ ADD MONEY
@app.route("/add-money", methods=["POST"])
def add_money():
    if not ensure_db():
        return jsonify({"error": "DB error"}), 500

    data = request.get_json(silent=True) or {}

    try:
        amount = float(data.get("amount", 0))
    except:
        return jsonify({"error": "Invalid amount"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400

    try:
        cursor.execute(
            "INSERT INTO add_money (amount) VALUES (%s)",
            (amount,)
        )
        db.commit()
    except Exception as e:
        print("DB ERROR:", e)
        return jsonify({"error": "Database error"}), 500

    return jsonify({"message": "Money Added Successfully"}), 200


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
