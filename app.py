
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file from flask_cors import CORS from werkzeug.security import generate_password_hash, check_password_hash from io import BytesIO import pandas as pd import os

app = Flask(name) app.secret_key = 'naotin_secret_key' CORS(app)

Simulated databases

users = {}  # username -> {'password': hashed, 'role': 'admin' or 'student'} students = []

AI Feature: Simple prediction based on designation and year

def predict_status(designation, year): if 'chair' in designation.lower() or year == '4th': return "Likely Leader" elif year in ['1st', '2nd']: return "Likely Active Member" else: return "Participant"

@app.route('/') def index(): if 'username' in session: is_admin = users[session['username']]['role'] == 'admin' return render_template("main.html", students=students, is_admin=is_admin) return render_template("main.html")

@app.route('/register', methods=['POST']) def register(): username = request.form.get('username') password = request.form.get('password') role = request.form.get('role')  # 'admin' or 'student'

if username in users:
    return "Username already exists", 400

users[username] = {
    'password': generate_password_hash(password),
    'role': role
}
return redirect(url_for('index'))

@app.route('/login', methods=['POST']) def login(): username = request.form.get('username') password = request.form.get('password')

user = users.get(username)
if user and check_password_hash(user['password'], password):
    session['username'] = username
    return redirect(url_for('index'))
return "Invalid credentials", 401

@app.route('/logout') def logout(): session.pop('username', None) return redirect(url_for('index'))

@app.route('/submit', methods=['POST']) def submit(): if 'username' not in session: return "Unauthorized", 403

data = {
    'name': request.form.get('name'),
    'village': request.form.get('village'),
    'phone': request.form.get('phone'),
    'parent_phone': request.form.get('parent_phone'),
    'designation': request.form.get('designation'),
    'year': request.form.get('year'),
    'username': session['username']
}
data['ai_prediction'] = predict_status(data['designation'], data['year'])
students.append(data)
return redirect(url_for('index'))

@app.route('/export') def export(): if 'username' not in session or users[session['username']]['role'] != 'admin': return "Unauthorized", 403 df = pd.DataFrame(students) output = BytesIO() df.to_excel(output, index=False) output.seek(0) return send_file(output, download_name="students_report.xlsx", as_attachment=True)

if name == 'main': port = int(os.environ.get("PORT", 5000)) app.run(host="0.0.0.0", port=port)

