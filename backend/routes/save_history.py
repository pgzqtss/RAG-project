from flask import request, jsonify
import mysql.connector
from utils.mysql_connection import connect_to_database
from __main__ import app

@app.route('/api/save', methods=['POST'])
def save_history():
    data = request.json

    required_fields = ["user_id", "prompt_id", "prompt", "systematic_review"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    user_id_list = data.get("user_id")
    prompt_id = data.get("prompt_id")
    prompt = data.get("prompt")
    systematic_review = data.get("systematic_review")

    try:
        if not isinstance(user_id_list, list):
            raise TypeError("user_id must be a list")
        if not all(isinstance(uid, int) for uid in user_id_list):
            raise TypeError("user_id must be a list of integers")
        if not isinstance(prompt_id, int):
            raise TypeError("prompt_id must be an integer")
    except TypeError as e:
        return jsonify({"error": str(e)}), 400

    user_id = user_id_list[0]

    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO history (user_id, prompt_id, user_input, model_output) VALUES (%s, %s, %s, %s)',
            (user_id, prompt_id, prompt, systematic_review)
        )
        conn.commit()
        return jsonify({'message': 'Systematic review has been stored successfully'})
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Systematic review already exists'}), 409
    except mysql.connector.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()