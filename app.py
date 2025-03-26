from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import mysql.connector 
#from flask_sqlalchemy import SQLAlchemy
#from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
#from flask_wtf import FlaskForm
#from wtforms import StringField, PasswordField, SubmitField
#from wtforms.validators import InputRequired, Length, ValidationError
#from flask_bcrypt import Bcrypt


app = Flask(__name__)

conection = mysql.connector.connect(host='localhost', database='localdata', user='root', password='A@a12072007') #Mysql conection
cursor = conection.cursor() #To using SQL commands

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def root():
    return redirect("/login")  


@app.route("/register")
def register():
    
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (username, password))
        conection.commit()
        return redirect("/login")  #render the homepage.html template
    
    return render_template("register.html") 
 

@app.route("/login",  methods=['GET', 'POST']) #Initial route
def login():

    session.clear() #Clear the session
    
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        
        #cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (username, password))
        search = cursor.execute("SELECT * FROM users WHERE name = %s AND password = %s", (username, password))
        conection.commit()

        return redirect("/homepage") #redirect to order rote, int his case is the homepage rote

    return render_template("login.html")  



@app.route("/homepage") #Main route 
def homepage():
    
    return render_template("homepage.html")

