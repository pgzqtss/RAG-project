from flask import request, jsonify
from utils.mysql_connection import connect_to_database
from __main__ import app

@app.route('/api/delete_user_history', methods=['POST'])
def delete_user_history():
    data = request.json
    prompt_id = data.get('prompt_id')

    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'DELETE FROM history WHERE prompt_id = %s',
            (prompt_id,)
        )
        conn.commit()
        result = cursor.fetchall()
        print(f'Result: {result}')
        return jsonify({'message': 'Systematic review successfully',
                        'result': result}), 200
    except:
        return jsonify({'error': 'No systematic review found'}), 404
    finally:
        cursor.close()
        conn.close()