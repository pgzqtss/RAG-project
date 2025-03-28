from flask import request, jsonify
import mysql.connector
from utils.mysql_connection import connect_to_database
from __main__ import app
import bcrypt

@app.route('/api/save', methods=['POST'])
def save_history():
    print(f"Raw data: {request.data}")
    print(f"Request JSON: {request.get_json()}")

    data = request.json

    if data is None:
        return jsonify({"error": "Invalid JSON data received"}), 400

    required_fields = ["user_id", "prompt_id", "prompt", "systematic_review"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        print(f"Missing fields: {missing}") 
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
        print(f"Type error: {str(e)}")  
        return jsonify({"error": str(e)}), 400

    user_id = user_id_list[0]

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            INSERT INTO history (user_id, prompt_id, user_input, model_output) 
            VALUES (%s, %s, %s, %s)
            ''',
            (user_id, prompt_id, prompt, systematic_review)
        )
        conn.commit()
        print("Systematic review stored successfully")
        return jsonify({'message': 'Systematic review has been stored successfully'})

    except mysql.connector.IntegrityError as e:
        print(f"Integrity error: {str(e)}")
        return jsonify({'error': f'Integrity error: {str(e)}'}), 409
    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()
