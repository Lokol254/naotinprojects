
from flask import Flask, render_template, request, redirect, url_for, session, send_file from werkzeug.security import generate_password_hash, check_password_hash import pandas as pd import os from io import BytesIO from flask_cors import CORS

app = Flask(name) CORS(app) app.secret_key = 'naotin_secret_key'

data_store = []  # Simulate a DB (use SQLite/MySQL in production)

Dummy admin user

admin_user = {'username': 'admin', 'password': generate_password_hash('admin123')}

@app.route('/') def index(): return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST']) def login(): if request.method == 'POST': username = request.form['username'] password = request.form['password']

if username == admin_user['username'] and check_password_hash(admin_user['password'], password):
        session['user'] = 'admin'
        return redirect(url_for('admin_dashboard'))

    for student in data_store:
        if student['username'] == username and check_password_hash(student['password'], password):
            session['user'] = username
            return redirect(url_for('student_dashboard'))

    return 'Invalid credentials'
return render_template('login.html')

@app.route('/register', methods=['GET', 'POST']) def register(): if request.method == 'POST': new_user = { 'username': request.form['username'], 'fullname': request.form['fullname'], 'email': request.form['email'], 'course': request.form['course'], 'password': generate_password_hash(request.form['password']) } data_store.append(new_user) return redirect(url_for('login')) return render_template('register.html')

@app.route('/admin') def admin_dashboard(): if 'user' in session and session['user'] == 'admin': return render_template('admin.html', students=data_store) return redirect(url_for('login'))

@app.route('/student') def student_dashboard(): if 'user' in session and session['user'] != 'admin': student = next((s for s in data_store if s['username'] == session['user']), None) return render_template('student.html', student=student) return redirect(url_for('login'))

@app.route('/logout') def logout(): session.pop('user', None) return redirect(url_for('login'))

@app.route('/download') def download(): if 'user' in session and session['user'] == 'admin': df = pd.DataFrame(data_store) output = BytesIO() with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df.to_excel(writer, index=False, sheet_name='Students') writer.sheets['Students'].write(0, 0, 'Naotin Unit Students Database') output.seek(0) return send_file(output, download_name='naotin_students.xlsx', as_attachment=True) return redirect(url_for('login'))

if name == 'main': port = int(os.environ.get("PORT", 5000)) app.run(host='0.0.0.0', port=port)

