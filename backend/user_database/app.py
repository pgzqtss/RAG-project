from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="user_data"
    )

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        flash(f"User '{username}' registered successfully!", "success")
    except mysql.connector.IntegrityError:
        flash(f"Username '{username}' is already taken.", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        flash(f"User '{username}' logged in successfully!", "success")
        return redirect(url_for('index'))
    else:
        flash("Invalid username or password.", "error")
        return redirect(url_for('index'))

@app.route('/query', methods=['POST'])
def query():
    user_input = request.form['user_input']
    user_id = int(request.form['user_id'])
    model_output = generate_model_output(user_input)
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (user_id, user_input, model_output) VALUES (%s, %s, %s)",
        (user_id, user_input, model_output)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash(f"Query saved! Model output: {model_output}", "success")
    return redirect(url_for('index'))

@app.route('/history/<int:user_id>')
def view_history(user_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_input, model_output, created_at FROM history WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('history.html', records=records)

@app.route('/')
def index():
    return render_template('index.html')

def generate_model_output(user_input):
    return f"Processed: {user_input}"

if __name__ == '__main__':
    app.run(debug=True)
