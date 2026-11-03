
from flask import Flask, jsonify, request
from db import get_db_connection

app = Flask(__name__)


# Home API
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to FeelSpace API"
    }), 200


# Health Check API
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    }), 200


# Create a New Thought (POST API)
@app.route("/api/thoughts", methods=["POST"])
def create_thought():

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data is required"}), 400

    content = data.get("content")
    mood = data.get("mood")
    anonymous = data.get("anonymous", False)

    if not content:
        return jsonify({"error": "Content is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO thoughts (user_id, content, mood, anonymous)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (1, content, mood, anonymous)
        )

        thought_id = cursor.fetchone()[0]

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Thought saved successfully!",
            "thought_id": thought_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get All Thoughts (GET API)
@app.route("/api/thoughts", methods=["GET"])
def get_thoughts():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, user_id, content, mood, anonymous, created_at
            FROM thoughts
            ORDER BY created_at DESC;
            """
        )

        rows = cursor.fetchall()

        thoughts = [
            {
                "id": row[0],
                "user_id": row[1],
                "content": row[2],
                "mood": row[3],
                "anonymous": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]

        cursor.close()
        conn.close()

        return jsonify(thoughts), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
