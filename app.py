import os

from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    return mysql.connector.connect(
        host=os.getenv("TIDB_HOST"),
        user=os.getenv("TIDB_USER"),
        password=os.getenv("TIDB_PASSWORD"),
        database=os.getenv("TIDB_DATABASE"),
        port=int(os.getenv("TIDB_PORT", "4000")),
        ssl_verify_cert=True,
        ssl_ca="isrgrootx1.pem"
    )


# ==========================================
# HOME
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "Expense Tracker Flask Server is working!"
    })


# ==========================================
# REGISTER
# ==========================================

@app.route("/register", methods=["POST"])
def register():

    conn = None
    cursor = None

    try:

        # ==========================================
        # GET JSON DATA
        # ==========================================

        data = request.get_json()

        print("Received data:", data)

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON data received"
            }), 400


        # ==========================================
        # GET FORM VALUES
        # ==========================================

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")


        # ==========================================
        # REMOVE EXTRA SPACES
        # ==========================================

        if name:
            name = name.strip()

        if email:
            email = email.strip().lower()


        # ==========================================
        # CHECK EMPTY FIELDS
        # ==========================================

        if not name:
            return jsonify({
                "success": False,
                "message": "Name is required"
            }), 400


        if not email:
            return jsonify({
                "success": False,
                "message": "Email is required"
            }), 400


        if not password:
            return jsonify({
                "success": False,
                "message": "Password is required"
            }), 400


        if not confirm_password:
            return jsonify({
                "success": False,
                "message": "Confirm password is required"
            }), 400


        # ==========================================
        # CHECK PASSWORD MATCH
        # ==========================================

        if password != confirm_password:

            return jsonify({
                "success": False,
                "message": "Passwords do not match"
            }), 400


        # ==========================================
        # CONNECT TO TIDB
        # ==========================================

        conn = get_connection()
        cursor = conn.cursor()


        # ==========================================
        # CHECK EMAIL ALREADY EXISTS
        # ==========================================

        check_query = """
            SELECT id
            FROM users
            WHERE email = %s
        """

        cursor.execute(check_query, (email,))

        existing_user = cursor.fetchone()


        if existing_user:

            return jsonify({
                "success": False,
                "message": "Email already registered"
            }), 409


        # ==========================================
        # HASH PASSWORD
        # ==========================================

        hashed_password = generate_password_hash(password)


        # ==========================================
        # INSERT USER
        # ==========================================

        insert_query = """
            INSERT INTO users
            (name, email, password)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            insert_query,
            (
                name,
                email,
                hashed_password
            )
        )


        # ==========================================
        # SAVE DATA
        # ==========================================

        conn.commit()


        print("User registered successfully:", name, email)


        # ==========================================
        # SUCCESS RESPONSE
        # ==========================================

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "name": name,
            "email": email
        }), 201


    except Exception as e:

        # ==========================================
        # ROLLBACK IF ERROR
        # ==========================================

        if conn:
            try:
                conn.rollback()
            except Exception:
                pass


        print("ERROR:", str(e))


        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


    finally:

        # ==========================================
        # CLOSE CURSOR
        # ==========================================

        if cursor:

            try:
                cursor.close()
            except Exception:
                pass


        # ==========================================
        # CLOSE CONNECTION
        # ==========================================

        if conn:

            try:
                conn.close()
            except Exception:
                pass


# ==========================================
# LOCAL SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )