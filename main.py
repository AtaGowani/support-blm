import hashlib
import os

from flask import Flask, session, url_for, redirect, render_template, request, abort, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = os.getenv("APP_SECRET")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text())
    petition_link = db.Column(db.String(500))
    other_link = db.Column(db.String(500))
    approved = db.Column(db.Boolean)

    def __init__(self, title, description, petition_link, other_link, approved):
        self.title = title
        self.description = description
        self.petition_link = petition_link
        self.other_link = other_link
        self.approved = approved

class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    password = db.Column(db.Text())

    def __init__(self, username, password):
        self.username = username
        self.password = password


def create_user(username, pw):
    user = Account.query.filter(Account.username == username).first()

    if user:
        user = user.__dict__
        if (user["username"] == username):
            return
    
    password = hashlib.sha256(pw.encode()).hexdigest()
    username = username.upper()
    data = Account(username, password)
    db.session.add(data)
    db.session.commit()

def verify_pass(username, pw):
    user = Account.query.filter(Account.username == username).first().__dict__
    if (user["password"] == hashlib.sha256(pw.encode()).hexdigest()):
        return True
    return False


@app.errorhandler(401)
def FUN_401(error):
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    return render_template("page_413.html"), 413


@app.route("/")
def index():
    posts = Post.query.filter(Post.approved == True).all()
    data = []
    
    for post in posts:
        data.append(post.__dict__)
    
    return render_template("index.html", data=data)

@app.route("/admin/posts")
def admin():
    if session.get("current_user", None) == "ADMIN":
        posts = Post.query.filter(Post.approved == False).all()
        data = []

        for post in posts:
            data.append(post.__dict__)
        
        return render_template("admin.html", data=data)
    else:
        return abort(401)

@app.route("/add_post", methods = ["POST"])
def add_post():
    title = request.form.get("petition_title")
    description = request.form.get("description")
    petition_link = request.form.get("petition_link")
    other_1 = request.form.get("other_1")
    
    data = Post(title, description, petition_link, other_1, False)
    db.session.add(data)
    db.session.commit()

    return(redirect(url_for("index")))

@app.route("/delete_post/<post_id>", methods = ["GET"])
def delete_post(post_id):
    if session.get("current_user", None):
        post = Post.query.filter(Post.id == post_id).first()
        db.session.delete(post)
        db.session.commit()
    else:
        return abort(401)
    return(redirect(url_for("admin")))

@app.route("/approve_post/<post_id>", methods = ["GET"])
def approve_post(post_id):
    if session.get("current_user", None):
        post = Post.query.filter(Post.id == post_id).first()
        post.approved = True
        db.session.commit()
    else:
        return abort(401)
    return(redirect(url_for("admin")))

@app.route("/login", methods = ["POST"])
def login():
    username = request.form.get("id").upper()
    user = Account.query.filter(Account.username == username).first()
    
    if user:
        user = user.__dict__
        if verify_pass(username, request.form.get("pw")):
            session['current_user'] = username
    
    return(redirect(url_for("index")))

@app.route("/logout/")
def logout():
    session.pop("current_user", None)
    return(redirect(url_for("index")))


if __name__ == "__main__":
    app.run(debug=True, host="localhost")
