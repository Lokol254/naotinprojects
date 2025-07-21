
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")  # For session management
CORS(app)

# Dummy "database"
students = []
admin_credentials = {"username": "admin", "password": generate_password_hash("admin123")}

# === Routes ===

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        if user == admin_credentials["username"] and check_password_hash(admin_credentials["password"], pwd):
            session["admin"] = True
            return redirect("/admin")
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html", students=students)

@app.route("/register", methods=["POST"])
def register_student():
    data = request.form
    student = {
        "name": data["name"],
        "email": data["email"],
        "year": data["year"],
        "course": data["course"]
    }
    students.append(student)
    return redirect(url_for("admin_dashboard"))

@app.route("/export")
def export_excel():
    df = pd.DataFrame(students)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="students.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# === AI Feature (Basic) ===
@app.route("/ai/summary")
def ai_summary():
    if not students:
        return "No data available"
    summary = f"Total students: {len(students)}"
    return summary

# === Run App ===
if __name__ == "__main__":
    app.run(debug=True)