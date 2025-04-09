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
    #return redirect("/reports") 
    return render_template("homepage.html")
    

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
        fullname = request.form["fullname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not username or not password or not fullname or not email or not confirm_password:
            return redirect("/register")
         
        cursor.execute("SELECT * FROM users WHERE username = %s AND email = %s", (username, email))
        validate = cursor.fetchone()

        if validate:
            return redirect("/register")
        
        if password != confirm_password:
            return redirect("/register")

        cursor.execute("INSERT INTO users (name, password, email, username) VALUES (%s, %s, %s, %s)", (fullname, password, email, username))
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

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
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

        cursor.execute("SELECT id, name, password FROM users WHERE id = %s", (session["user_id"],))
        info = cursor.fetchone() 

        user_info = [
            [ "Id", "name","Course"],
            [ info[0], info[1], info[2]]    
            ]                              
        
        cursor.execute("SELECT matter_name, trimestre1, trimestre2, trimestre3, ROUND((trimestre1 + trimestre2 + trimestre3) / 3, 2) AS MED FROM matters")

        user_notes = cursor.fetchall()

        notes = [
            ["matter", "1","2", "3", "MED"]
            ]
        
        for note in user_notes:
            notes.append(list(note))



        if request.form.get("registration") == "registration":
            
            folder = "pdf" 
            caminho_pdf = os.path.join(folder, "relatorio.pdf")
            doc = canvas.Canvas(caminho_pdf, pagesize=A4)
            width, height = A4


            doc.setFont("Helvetica-Bold", 16)
            doc.setFillColorRGB(0.0, 0.0, 0.0) 
            doc.drawCentredString(width / 2, height - 60, "Student report card")
            
            doc.setFont("Helvetica", 14)
            doc.drawCentredString(width / 2, height - 80, "Lumina Institute")

            tabela = Table(user_info, colWidths=[150, 100, 150])
            tabela.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))

            second_table = Table(notes, colWidths=[100, 100, 100, 100])
            second_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))


            # Table
            tabela.wrapOn(doc, width, height)
            tabela.drawOn(doc, 100, height - 150) 
            # Second table
            second_table.wrapOn(doc, width, height)
            second_table.drawOn(doc, 50, height - 600)

            doc.save()

            return send_file(
                caminho_pdf,
                as_attachment=True,
                download_name="relatorio.pdf", 
                mimetype="application/pdf"
            )
        
        if request.form.get("card") == "card":

            return redirect("/studantpage")


    return render_template("reports.html")

@app.route("/grid")
def grid():
    
    return render_template("grid.html")

