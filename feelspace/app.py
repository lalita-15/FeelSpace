
import os
from datetime import timedelta

from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from db import get_db_connection


# =====================================
# APPLICATION CONFIGURATION
# =====================================

load_dotenv()

app = Flask(__name__)

secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    raise ValueError("SECRET_KEY is missing from .env file")

app.config["SECRET_KEY"] = secret_key
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Set True when using HTTPS
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12)


# =====================================
# HOME PAGE
# =====================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================
# SIGNUP
# =====================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password or not confirm_password:
            flash("Please fill in all fields.", "error")
            return render_template("signup.html")

        if len(username) < 3 or len(username) > 100:
            flash("Username must be between 3 and 100 characters.", "error")
            return render_template("signup.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        password_hash = generate_password_hash(password)

        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s)
                RETURNING id, username;
                """,
                (username, email, password_hash)
            )

            user = cursor.fetchone()
            conn.commit()

            session.clear()
            session["user_id"] = user[0]
            session["username"] = user[1]
            session.permanent = True

            flash("Your FeelSpace account has been created!", "success")

            return redirect(url_for("home"))

        except Exception as error:

            if conn:
                conn.rollback()

            # PostgreSQL unique constraint violation
            if getattr(error, "sqlstate", None) == "23505":
                flash(
                    "This username or email is already registered.",
                    "error"
                )
                return render_template("signup.html")

            app.logger.exception("Signup failed")
            flash("Unable to create account. Please try again.", "error")
            return render_template("signup.html")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("signup.html")


# =====================================
# LOGIN
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "error")
            return render_template("login.html")

        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, username, password
                FROM users
                WHERE email = %s;
                """,
                (email,)
            )

            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):

                session.clear()
                session["user_id"] = user[0]
                session["username"] = user[1]
                session.permanent = True

                return redirect(url_for("home"))

            flash("Invalid email or password.", "error")

        except Exception:
            app.logger.exception("Login failed")
            flash("Unable to login. Please try again.", "error")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("login.html")


# =====================================
# LOGOUT
# =====================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("login"))


# =====================================
# HEALTH CHECK
# =====================================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy"
    }), 200


# =====================================
# CREATE A NEW THOUGHT
# =====================================

@app.route("/api/thoughts", methods=["POST"])
def create_thought():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "Please login before sharing a thought."
        }), 401

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON data is required."
        }), 400

    content = data.get("content", "").strip()
    mood = data.get("mood")
    anonymous = data.get("anonymous", False)

    if not content:
        return jsonify({
            "error": "Content is required."
        }), 400

    if len(content) > 2000:
        return jsonify({
            "error": "Thought cannot exceed 2000 characters."
        }), 400

    if not mood:
        return jsonify({
            "error": "Please select a mood."
        }), 400

    if not isinstance(anonymous, bool):
        return jsonify({
            "error": "Anonymous must be true or false."
        }), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO thoughts (user_id, content, mood, anonymous)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (user_id, content, mood, anonymous)
        )

        thought_id = cursor.fetchone()[0]

        conn.commit()

        return jsonify({
            "message": "Thought shared successfully!",
            "thought_id": thought_id
        }), 201

    except Exception:

        if conn:
            conn.rollback()

        app.logger.exception("Failed to save thought")

        return jsonify({
            "error": "Unable to save thought."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =====================================
# GET COMMUNITY THOUGHTS
# =====================================

@app.route("/api/thoughts", methods=["GET"])
def get_thoughts():

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                thoughts.id,
                thoughts.user_id,
                thoughts.content,
                thoughts.mood,
                thoughts.anonymous,
                thoughts.created_at,
                users.username
            FROM thoughts
            LEFT JOIN users
                ON thoughts.user_id = users.id
            ORDER BY thoughts.created_at DESC;
            """
        )

        rows = cursor.fetchall()

        thoughts = []

        for row in rows:

            thoughts.append({
                "id": row[0],
                "user_id": row[1],
                "content": row[2],
                "mood": row[3],
                "anonymous": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "username": "Anonymous" if row[4] else row[6]
            })

        return jsonify(thoughts), 200

    except Exception:

        app.logger.exception("Failed to fetch thoughts")

        return jsonify({
            "error": "Unable to fetch thoughts."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":
    app.run(debug=True)
