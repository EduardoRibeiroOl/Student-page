from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_session import Session


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle 
from reportlab.lib import colors

from datetime import datetime

import mysql.connector 
import os

app = Flask(__name__)


conection = mysql.connector.connect(
    host='localhost', database='localdata', user='root', password='A@a12072007'
)

cursor = conection.cursor()

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/")
def route():

    return redirect("/login")


@app.route("/studantpage")
def studantpage():

    if "user_id" in session:
        return render_template("studantpage.html")
    
    return render_template("homepage.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            return redirect("/register")

       
        cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
        validate_name = cursor.fetchone()

        if validate_name:
            return redirect("/register")

        cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (username, password))
        conection.commit()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():

    session.clear() 

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return redirect("/login")

        cursor.execute("SELECT * FROM users WHERE name = %s AND password = %s", (username, password))
        user = cursor.fetchone()  

        if user:
            session["user_id"] = user[0] 
            return redirect("/studantpage")
        else:
            return redirect("/login")

    return render_template("login.html")


@app.route("/reports", methods=["GET", "POST"])
def reports(): 

    if request.method == "POST":

        if request.form.get("bulletin") == "bulletin":
            filename = "bulletin.pdf"

            def registration(filename):
                styles = getSampleStyleSheet()
                doc = SimpleDocTemplate(filename, pagesize=A4)

                elements = []
                title = Paragraph("Relatório de Teste", styles["Title"])
                paragraph = Paragraph("Exemplo para ver se tá tudo certo", styles["BodyText"])

                elements.append(title)
                elements.append(Spacer(1, 20))
                elements.append(paragraph)

                doc.build(elements)

            registration(filename)

            return send_file(filename, as_attachment=True)

        
        if request.form.get("registration") == "registration":
            
            return redirect("/studantpage")
        
        if request.form.get("card") == "card":

            return redirect("/studantpage")

    return render_template("reports.html")


@app.route("/notes")
def notes():

    cursor.execute("SELECT matter_name FROM matters")
    notes = cursor.fetchall()
    return render_template("notes.html", notes=notes)

@app.route("/grid")
def grid():
    
    return render_template("grid.html")
