from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import mysql.connector 

app = Flask(__name__)


conection = mysql.connector.connect(
    host='localhost', database='localdata', user='root', password='A@a12072007'
)
cursor = conection.cursor()

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def root():
    return redirect("/login")

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
        user = cursor.fetchone()  # Busca um usuário na base de dados

        if user:
            session["user_id"] = user[0] 
            return redirect("/homepage")
        else:
            return redirect("/login")

    return render_template("login.html")

@app.route("/homepage")
def homepage():
    if "user_id" in session:
        return render_template("homepage.html")

    return redirect("/login")  
