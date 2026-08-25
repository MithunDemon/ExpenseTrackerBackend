from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash

app = Flask(__name__)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    return mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        user="3AuVePpBYsvB5an.root",
        password="7RgTvg8iQ5Z522S0",
        database="ETAPP",
        port=4000,
        ssl_verify_cert=True,
        ssl_ca="isrgrootx1.pem"
    )


# ==========================================
# HOME
# ==========================================

@app.route("/")
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

    try:

        # Get JSON data from Android
        data = request.get_json()

        print("Received data:", data)

        # Get values
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")


        # ==========================================
        # CHECK EMPTY FIELDS
        # ==========================================

        if not name or not email or not password or not confirm_password:

            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400


        # ==========================================
        # CHECK PASSWORD
        # ==========================================

        if password != confirm_password:

            return jsonify({
                "success": False,
                "message": "Passwords do not match"
            }), 400


        # ==========================================
        # CONNECT DATABASE
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

            cursor.close()
            conn.close()

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
            (name, email, password,confirm_password)
            VALUES (%s, %s, %s,%s)
        """

        cursor.execute(
            insert_query,
            (name, email, hashed_password)
        )

        conn.commit()


        # ==========================================
        # CLOSE CONNECTION
        # ==========================================

        cursor.close()
        conn.close()


        print("User registered:", name, email)


        # ==========================================
        # RESPONSE
        # ==========================================

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "name": name,
            "email": email
        }), 201


    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )