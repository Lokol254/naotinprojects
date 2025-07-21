from flask import Flask, request, jsonify, send_file, render_template_string, session, redirect, url_for
import pandas as pd
from io import BytesIO
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'naotin_secret_key'
CORS(app)

# Simulated database
students = []
users = {}  # username -> hashed_password

@app.route('/')
def home():
    if not os.path.exists("index.html"):
        return "Error: index.html file not found", 404
    with open("index.html", "r", encoding="utf-8") as f:
        return render_template_string(f.read())

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    if not username or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    if username in users:
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = generate_password_hash(data.get('password'))
    users[username] = hashed_password

    student_data = {
        'name': data.get('name'),
        'school': data.get('school'),
        'course': data.get('course'),
        'designation': data.get('designation'),
        'village': data.get('village'),
        'year': data.get('year'),
        'phone': data.get('phone'),
        'parentPhone': data.get('parentPhone'),
        'fees': data.get('fees'),
        'username': username
    }
    students.append(student_data)
    return jsonify({'message': 'Registered successfully'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and check_password_hash(users[username], password):
        session['user'] = username
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/download', methods=['GET'])
def download():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized access'}), 403
    df = pd.DataFrame(students)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="students_report.xlsx", as_attachment=True)

@app.route('/students', methods=['GET'])
def get_students():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(students), 200

if __name__ == '__main__':
    app.run(debug=True)

