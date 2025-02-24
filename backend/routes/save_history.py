from flask import request, jsonify
import mysql.connector
from utils.mysql_connection import connect_to_database
from __main__ import app

@app.route('/api/save', methods=['POST'])
def save_history():
    data = request.json
    user_id = data.get('user_id')
    user_id = user_id[0]
    prompt_id = data.get('prompt_id')
    prompt = data.get('prompt')
    systematic_review = data.get('systematic_review')

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
    finally:
        cursor.close()
        conn.close()
