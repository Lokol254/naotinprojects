
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file from flask_sqlalchemy import SQLAlchemy from flask_cors import CORS from werkzeug.security import generate_password_hash, check_password_hash import pandas as pd from io import BytesIO import os

app = Flask(name) app.secret_key = 'naotin_secret_key' app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///naotin.db' app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app) db = SQLAlchemy(app)

--- Models ---

class User(db.Model): id = db.Column(db.Integer, primary_key=True) username = db.Column(db.String(80), unique=True, nullable=False) password = db.Column(db.String(120), nullable=False) role = db.Column(db.String(10), default='student')  # 'admin' or 'student'

class Student(db.Model): id = db.Column(db.Integer, primary_key=True) name = db.Column(db.String(100)) school = db.Column(db.String(100)) course = db.Column(db.String(100)) designation = db.Column(db.String(100)) village = db.Column(db.String(100)) year = db.Column(db.String(20)) phone = db.Column(db.String(20)) parentPhone = db.Column(db.String(20)) fees = db.Column(db.String(20)) username = db.Column(db.String(80))

--- Routes ---

@app.route('/') def index(): return render_template("index.html")

@app.route('/register', methods=['POST']) def register(): data = request.form username = data.get('username') password = data.get('password')

if User.query.filter_by(username=username).first():
    return "Username already exists", 400

hashed_password = generate_password_hash(password)
new_user = User(username=username, password=hashed_password, role='student')
db.session.add(new_user)

student = Student(
    name=data.get('name'),
    school=data.get('school'),
    course=data.get('course'),
    designation=data.get('designation'),
    village=data.get('village'),
    year=data.get('year'),
    phone=data.get('phone'),
    parentPhone=data.get('parentPhone'),
    fees=data.get('fees'),
    username=username
)
db.session.add(student)
db.session.commit()

return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST']) def login(): if request.method == 'POST': data = request.form user = User.query.filter_by(username=data.get('username')).first() if user and check_password_hash(user.password, data.get('password')): session['user'] = user.username session['role'] = user.role return redirect(url_for('dashboard')) return "Invalid credentials", 401 return render_template("login.html")

@app.route('/dashboard') def dashboard(): if 'user' not in session: return redirect(url_for('login'))

user_role = session.get('role')
if user_role == 'admin':
    students = Student.query.all()
    return render_template("admin_dashboard.html", students=students)
else:
    students = Student.query.all()
    return render_template("dashboard.html", students=students)

@app.route('/download') def download(): if 'user' not in session or session.get('role') != 'admin': return "Unauthorized", 403

students = Student.query.all()
df = pd.DataFrame([{
    'Name': s.name,
    'School': s.school,
    'Course': s.course,
    'Designation': s.designation,
    'Village': s.village,
    'Year': s.year,
    'Phone': s.phone,
    'Parent Phone': s.parentPhone,
    'Fees Arrears': s.fees
} for s in students])

output = BytesIO()
df.to_excel(output, index=False)
output.seek(0)
return send_file(output, download_name="students_report.xlsx", as_attachment=True)

@app.route('/logout') def logout(): session.clear() return redirect(url_for('index'))

--- AI Logic Placeholder (Future Add-on) ---

e.g., smart student recommendations, AI-assisted profile updates, etc.

from openai import OpenAI or HuggingFace pipelines in future

if name == 'main': with app.app_context(): db.create_all() port = int(os.environ.get("PORT", 5000)) app.run(host="0.0.0.0", port=port)

