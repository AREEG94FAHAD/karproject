import os
import datetime
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy import asc,desc

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, abort
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_caching import Cache
from helpers import login_required

# Configure application
#jjjjjjjjjjjjjjjjjj



app = Flask(__name__)
app.secret_key= "sahhskskks"


# os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:areeg@localhost:5432/gheed'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 100
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter


# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///finance.db")


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    hash = db.Column(db.String(220))
    # email = db.Column(db.String(220))
    # fullname = db.Column(db.String(220))
    db.session.commit()


class Items(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    sheet = db.Column(db.String)
    image = db.Column(db.String)
    location = db.Column(db.String(220))
    nameOfDevice = db.Column(db.String(220))
    username = db.Column(db.String(120))
    relationship("History", backref="history", lazy='dynamic')
    date = db.Column(db.String(120))
    db.session.commit()


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(220))
    nameOfDevice = db.Column(db.String(220))
    username = db.Column(db.String(120))
    device_id = db.Column(Integer, ForeignKey('items.id'))
    date = db.Column(db.String(120))
    db.session.commit()



db.create_all()

@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template('login.html')

    items = db.session.query(Items).order_by(desc(Items.date))
    
    return render_template("data.html", data=items)

@app.route("/history/<id>")
def history(id):
    if not session.get('logged_in'):
        return render_template('login.html')

    history = db.session.query(History).filter(History.device_id==id).order_by(asc(History.date))
    
    return render_template("history.html", data=history)


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        username = request.form.get('username').lower()
        # email = request.form.get('email').lower()
        companycode = request.form.get('companycode').lower()

        if companycode != '10':
            return abort(422," Wrong company code")
            
        username_ck = db.session.query(Users).filter((Users.username == username)).one_or_none()

        if(username_ck):
            return abort(404, "Existing username or email")
        else:
            new_user = Users(
                hash=generate_password_hash(request.form.get('password')),
                # fullname=request.form.get('fullname'),
                username=username,
                # email=email
                )
            db.session.add(new_user)
            db.session.commit()
            db.session.close()


        userid= db.session.query(Users.id, Users.username).filter(Users.username == username).one_or_none()
        session['logged_in'] = True
        session["user_id"] = userid.id
        session["username"] = userid.username
        # session["fullname"] = userid.fullname
        return redirect(url_for("index"))

    else:
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username=request.form.get("username").lower()
        password=request.form.get("password").lower()
        if(username == 'ggggaaaa'):
            return  abort(422, "try with another account")

        user = db.session.query(Users).filter(Users.username == username).one_or_none()

        # Ensure username exists and password is correct
        if user == None or not check_password_hash(
                user.hash, request.form.get("password")):
            return abort(404, "Invalid Username or Password")
        session['logged_in'] = True

        session["user_id"] = user.id
        session["username"] = user.username
        # session["fullname"] = user.fullname

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")







@app.route("/edit/<id>", methods=["post"])
@login_required
def check_edit(id):

    adminname = request.form.get("adminusername").lower()
    adminpassword = request.form.get("adminpasword").lower()
    user = db.session.query(Users).filter((Users.username == 'ggggaaaa')).one_or_none()

    if (user is None) or not (check_password_hash(user.hash,adminpassword)):

        return abort(422," Wrong Admin name or Admin password")

    else:
        item = db.session.query(Items).filter(Items.id==id).one_or_none()
        # print("----------------------------"+str(item.location))
        return render_template("ed.html", data=item)

        

@app.route("/update", methods=["post"])
@login_required
def edititem():
    

    id = request.form.get("id")
    name = db.session.query(Items.nameOfDevice).filter((Items.id == id)).one_or_none()
    # date = request.form.get("date")
    location = request.form.get("location")
    # nameOfDevice = request.form.get("nameOfDevice")
    # nameOfDevice = request.form.get("nameOfDevice")

    # sheet = request.form.get("sheet")
    now = datetime.datetime.now()
    date1=now.strftime("%Y-%m-%d %H:%M:%S")
    print("  ",name,"   ")

    histor =History(
 
        nameOfDevice=name[0][0],
        location=location,
        date=date1,
        username=session["username"],
        device_id=id
        )

    db.session.add(histor)

    updatee = {
    'date':date1,
    'location' :request.form.get('location'),
    # 'sheet' :request.form.get('sheet'),
    'username':session["username"], 
  }


    db.session.query(Items).filter(Items.id == id).update(updatee)
    
    db.session.commit()
    db.session.close()

    return redirect(url_for("index"))


@app.route("/delete/<id>", methods=['post'])
@login_required
def delete_item(id):

    # if not session.get('logged_in'):
    #     return render_template('login.html')

    adminname = request.form.get("adminusername").lower()
    adminpassword = request.form.get("adminpasword").lower()
    user = db.session.query(Users).filter((Users.username == 'ggggaaaa')).one_or_none()

    if (user is None) or not (check_password_hash(user.hash,adminpassword)):

        return abort(422," Wrong Admin name or Admin password")

    else:

        history_items =db.session.query(History).filter(History.device_id == id).all()
        if history_items:
            for item in history_items:
                db.session.delete(item)
                db.session.commit()
            
        item = db.session.query(Items).filter(Items.id == id).one_or_none()

        if item:
            db.session.delete(item)
            db.session.commit()
        
   
    
    return redirect("/")
    
@app.route("/checknew", methods=["post"])
@login_required
def newitem():
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    
    adminname = request.form.get("adminusername").lower()
    adminpassword = request.form.get("adminpasword").lower()
    user = db.session.query(Users).filter((Users.username == 'ggggaaaa')).one_or_none()

    if (user is None) or not (check_password_hash(user.hash,adminpassword)):

        return abort(422," Wrong Admin name or Admin password")

    else:
        return render_template("addnew.html")




@app.route("/editadmin", methods=["GET", "POST"])
@login_required
def editadmin():
    if request.method == "POST":
            username=request.form.get("username").lower()
            password=request.form.get("password").lower()
            user = db.session.query(Users).filter(Users.username == username).one_or_none()

            if user == None :
                return abort(404, "wrong admin username")
            updateadminpass = {
                'hash':generate_password_hash(password)
                }
            db.session.query(Users).filter(Users.username== username).update(updateadminpass)
            db.session.commit()
            db.session.close()

            return redirect("/")
    else:
        return render_template("edit.html")



@app.route("/addnew", methods=["post"])
@login_required
def addnew():
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    
    nameOfDevice = request.form.get("nameOfDevice")
    location = request.form.get("location")
    datasheet = request.form.get("datasheet")
    image = request.form.get("image")
    now = datetime.datetime.now()
    da = now.strftime("%Y-%m-%d %H:%M:%S")

    addnew = Items(
    nameOfDevice=nameOfDevice,
    location=location,
    sheet=datasheet,
    date=da,
    image=image,
    username=session["username"])
    db.session.add(addnew)
    db.session.commit()

    item_id = db.session.query(Items.id).order_by(Items.id.desc()).limit(1)
    # print(";;;;;;;;;;;;",item_id[0][0])

    histor =History(
 
        nameOfDevice=nameOfDevice,
        location=location,
        date=da,
        username=session["username"],
        device_id =item_id[0][0]
    )

    db.session.add(histor)
    db.session.commit()
    

    try:
        db.session.close()
    except:
        abort(422)

    return redirect("/")

@app.errorhandler(422)
def not_processable(e):
    # note that we set the 404 status explicitly
    return render_template('error.html',e=e)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html',e=e)