from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from flask_session import Session
from flask_mail import Mail, Message

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
#from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
#from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
import io

from datetime import datetime
import mysql.connector 
import os

#import smtplib
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = 'secret_key'


conection = mysql.connector.connect(
    host='localhost', database='localdata', user='root', password='A@a12072007'
)

cursor = conection.cursor()

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '0ff074f593e6ee'
app.config['MAIL_PASSWORD'] = 'daea5fd00343b9'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@seudominio.com'
mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

@app.route("/")
def route():

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


@app.route("/teacherpage", methods=["GET", "POST"])
def teacherpage():
    
    return render_template("teacherpage.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == 'POST':
        fullname = request.form["fullname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        level = "student"
        turn = "morning"
        serie = "firt"

        if not username or not password or not fullname or not email or not confirm_password:
            return redirect("/register")
         
        cursor.execute("SELECT * FROM users WHERE username = %s AND email = %s", (username, email))
        validate = cursor.fetchone()

        if validate:
            return redirect("/register")
        
        if password != confirm_password:
            return redirect("/register")

        cursor.execute("INSERT INTO users (name, password, email, username, level, turn, serie) VALUES (%s, %s, %s, %s, %s, %s, %s)", (fullname, password, email, username, level, turn, serie))
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
            cursor.execute("SELECT level FROM users WHERE id = %s", (user[0],))
            level_result = cursor.fetchone()
            
            if level_result and level_result[0] == "teacher":
                return redirect("/teacherpage")
            else:
                return redirect("/studantpage")
        else:
            return redirect("/login")

    return render_template("login.html")

@app.route("/recover", methods=["GET", "POST"])
def recover():

    if request.method == "POST":
        email = request.form.get("email")
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            flash("Email não encontrado. Por favor, verifique seu email e tente novamente.")
            return redirect("/recover")

        token = s.dumps(email, salt="recover-salt")
        link = url_for('reset_with_token', token=token, _external=True)

        msg = Message("Recover password", recipients=[email])
        msg.body = f"Click on this link to reset your password: {link}"

        mail.send(msg)
        flash ("email enviado com sucesso!")
        return redirect("/recover")
        
    return render_template("recoverlogin.html")

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = s.loads(token, salt="recover-salt", max_age=3600)
    except:
        return redirect("/recover")

    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not new_password or not confirm_password:
            return redirect("/recover")

        if new_password != confirm_password:
            return redirect("/recover")

        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
        conection.commit()

    return render_template("reset.html")

@app.route("/reports", methods=["GET", "POST"])
def reports(): 

    if request.method == "POST":

        if request.form.get("bulletin") == "bulletin":
            cursor = conection.cursor()
            cursor.execute("SELECT id, name, course FROM users WHERE id = %s", (session["user_id"],))
            info = cursor.fetchone()

            user_info = [
                ["Id", "Name", "Course"],
                [info[0], info[1], info[2]]
            ]

            cursor.execute("SELECT subject, trimester, grade FROM grades WHERE student_id = %s", (session["user_id"],))
            user_notes = cursor.fetchall()

            notas_dict = {}
            for subject, trimester, grade in user_notes:
                if subject not in notas_dict:
                    notas_dict[subject] = {"1st": "-", "2nd": "-", "3rd": "-"}
                notas_dict[subject][trimester] = grade

            notes = [["Subject", "1st", "2nd", "3rd", "AVG"]]
            for subject, trimestres in notas_dict.items():
                notas_validas = [float(n) for n in trimestres.values() if str(n).replace('.', '', 1).isdigit()]
                media = round(sum(notas_validas) / len(notas_validas), 2) if notas_validas else "-"
                notes.append([
                    subject,
                    trimestres.get("1st", "-"),
                    trimestres.get("2nd", "-"),
                    trimestres.get("3rd", "-"),
                    media
                ])

            folder = "pdf"
            os.makedirs(folder, exist_ok=True)
            caminho_pdf = os.path.join(folder, "relatorio.pdf")

            doc = canvas.Canvas(caminho_pdf, pagesize=A4)
            width, height = A4

            doc.setFont("Helvetica-Bold", 16)
            doc.drawCentredString(width / 2, height - 60, "Student Report Card")
            doc.setFont("Helvetica", 14)
            doc.drawCentredString(width / 2, height - 80, "Lumina Institute")

            tabela = Table(user_info, colWidths=[100, 200, 150])
            tabela.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))

            second_table = Table(notes, colWidths=[122, 82, 82, 82, 82])
            second_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))

            tabela.wrapOn(doc, width, height)
            tabela.drawOn(doc, 70, height - 160)
            second_table.wrapOn(doc, width, height)
            second_table.drawOn(doc, 70, height - 230)

            doc.save()

            return send_file(
                caminho_pdf,
                as_attachment=True,
                download_name="relatorio.pdf",
                mimetype="application/pdf"
            )
        
        if request.form.get("card") == "card":
            cursor = conection.cursor()
            cursor.execute("SELECT id, name, course FROM users WHERE id = %s", (session["user_id"],))
            aluno = cursor.fetchone()

            if not aluno:
                return "Aluno não encontrado", 404

            aluno_id, nome, curso = aluno

            folder = "pdf"
            os.makedirs(folder, exist_ok=True)
            caminho_pdf = os.path.join(folder, "ID.pdf")

            largura = 85.6 * mm
            altura = 53.98 * mm

            doc = canvas.Canvas(caminho_pdf, pagesize=(largura, altura))

            doc.setStrokeColorRGB(0, 0, 0)
            doc.setFillColorRGB(0.9, 0.9, 1)
            doc.rect(0, 0, largura, altura, fill=1)

            doc.setFont("Helvetica-Bold", 10)
            doc.setFillColorRGB(0, 0, 0.5)
            doc.drawCentredString(largura / 2, altura - 10 * mm, "Lumina Institute")

            doc.setFont("Helvetica", 8)
            doc.setFillColorRGB(0, 0, 0)
            doc.drawString(10 * mm, altura - 20 * mm, f"Nome: {nome}")
            doc.drawString(10 * mm, altura - 26 * mm, f"Matrícula: {aluno_id}")
            doc.drawString(10 * mm, altura - 32 * mm, f"Curso: {curso}")

            doc.line(10 * mm, altura - 45 * mm, largura - 10 * mm, altura - 45 * mm)
            doc.drawCentredString(largura / 2, altura - 48 * mm, "Assinatura do aluno")

            doc.save()

            return send_file(
                caminho_pdf,
                as_attachment=True,
                download_name="identificacao.pdf",
                mimetype="application/pdf"
            )
        
        if request.form.get("registration") == "registration":
            cursor = conection.cursor()
            cursor.execute("SELECT id, name, course, turn FROM users WHERE id = %s", (session["user_id"],))
            aluno = cursor.fetchone()

            if not aluno:
                return "Aluno não encontrado", 404

            aluno_id, nome, curso, turno = aluno
            data_registro = datetime.now().strftime("%d/%m/%Y")

            folder = "pdf"
            os.makedirs(folder, exist_ok=True)
            caminho_pdf = os.path.join(folder, "register.pdf")

            doc = canvas.Canvas(caminho_pdf, pagesize=A4)
            largura, altura = A4

            doc.setFont("Helvetica-Bold", 16)
            doc.drawCentredString(largura / 2, altura - 50, "Lumina Institute")

            doc.setFont("Helvetica", 14)
            doc.drawCentredString(largura / 2, altura - 80, "Documento de Registro Escolar")

            doc.setFont("Helvetica", 12)
            doc.drawString(50, altura - 130, f"Nome completo: {nome}")
            doc.drawString(50, altura - 160, f"Matrícula (ID): {aluno_id}")
            doc.drawString(50, altura - 190, f"Curso: {curso}")
            doc.drawString(50, altura - 220, f"Turno: {turno}")
            doc.drawString(50, altura - 250, f"Data de registro: {data_registro}")

            doc.line(50, altura - 320, 250, altura - 320)
            doc.drawString(50, altura - 335, "Assinatura do responsável")

            doc.setFont("Helvetica-Oblique", 10)
            doc.drawCentredString(largura / 2, 30, "Este documento foi gerado automaticamente pelo sistema Lumina.")

            doc.save()

            return send_file(
                caminho_pdf,
                as_attachment=True,
                download_name="registro.pdf",
                mimetype="application/pdf"
            )
            
    return render_template("reports.html")


@app.route("/grid")
def grid():

    return render_template("grid.html")


@app.route("/editgrades")
def editgrades():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="A@a12072007",
        database="localdata"
    )
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, name, course, turn FROM users WHERE level = 'student'")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM grades")
    grades = cursor.fetchall()

    db.close() 
    return render_template("editgrades.html", students=students, grades=grades)


@app.route("/updategrades", methods=["POST"])
def updategrades():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="A@a12072007",
        database="localdata"
    )
    cursor = db.cursor()
    form = request.form

    for key in form:
        if key.startswith("grade_"):
            grade_id = key.split("_")[1]
            nova_nota = form[key]
            cursor.execute("UPDATE grades SET grade = %s WHERE id = %s", (nova_nota, grade_id))

    for key in form:
        if key.startswith("new_student_id"):
            student_ids = form.getlist(key)
            for student_id in student_ids:
                subject_list = form.getlist(f"new_subject_{student_id}[]")
                trimester_list = form.getlist(f"new_trimester_{student_id}[]")
                grade_list = form.getlist(f"new_grade_{student_id}[]")

                for subject, trimester, grade in zip(subject_list, trimester_list, grade_list):
                    if subject.strip() and grade.strip():
                        cursor.execute(
                            "INSERT INTO grades (student_id, subject, trimester, grade) VALUES (%s, %s, %s, %s)",
                            (student_id, subject, trimester, grade)
                        )

    db.commit()
    cursor.close()
    db.close()

    return redirect("/editgrades")

