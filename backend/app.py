from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

if __name__ == '__main__':
    from routes import (
        query_history,
        query_user,
        delete_user_history,
        query_user_history,
        save_history,
        register_user,
        login_user,
        upsert_vectors,
        gen_systematic_review
    )
    app.run(debug=True, port=5000)