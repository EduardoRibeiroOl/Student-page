from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_session import Session


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle 
from reportlab.lib import colors
import io

import datetime
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
    return redirect("/reports") 
   # return render_template("homepage.html")
    

@app.route("/home")
def homepage():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")



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
        
        if request.form.get("registration") == "registration":
            
            folder = "pdf" 
            caminho_pdf = os.path.join(folder, "relatorio.pdf")

           
            doc = canvas.Canvas(caminho_pdf)
            doc.drawCentredString(250, 750, "Relatório de Estudos")
            doc.setFont("Helvetica-Bold", 14)
            doc.drawString(100, 700, "Este PDF foi gerado e salvo diretamente no servidor.")
            doc.save()

            return send_file(
                caminho_pdf,
                as_attachment=True,
                download_name="relatorio.pdf", 
                mimetype="application/pdf"
            )

        return redirect("/reports")
        
        if request.form.get("card") == "card":

            return redirect("/studantpage")


    return render_template("reports.html")


@app.route("/notes")
def notes():

    cursor.execute("SELECT matter_name, trimestre1, trimestre2, trimestre3 FROM matters")
    notes = cursor.fetchall()   

    return render_template("notes.html", notes=notes)

@app.route("/grid")
def grid():
    
    return render_template("grid.html")

