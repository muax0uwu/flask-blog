import math
import os.path
import flask
from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
from datetime import datetime
import time
from werkzeug.utils import secure_filename

local_server = True

with open("config.json","r") as j:
    params = json.load(j)["params"]

with open("config.json","r") as j:
    dash = json.load(j)["dashboard"]


fb_url=params["fb_url"]

app = Flask(__name__)
app.secret_key="super-sec-key"
app.config["file-path"] = dash["upload_folder"]
app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_DEBUG = True,
    MAIL_SUPPRESS_SEND = False,
    TESTING=False,
    MAIL_USERNAME = params['gmail'],
    MAIL_PASSWORD = params['gmail_pass']
)
mail = Mail(app)
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12))


class Posts(db.Model):
    sno = db.Column(db.Integer(), primary_key=True)
    slug = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(80), nullable=True)
    content = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(12))



@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    if 'user' in session and session['user'] == dash["user_name"]:
        posts = Posts.query.all()
        return render_template("dashboard.html",posts=posts)
    else:
        if request.method == 'POST':
            username = request.form.get("username")
            password = request.form.get("pass")
            if username == dash["user_name"] and password == dash["user_pass"]:
                posts = Posts.query.all()
                session['user'] = username
                return render_template("dashboard.html",posts=posts)
            else:
                flash("Invalid Email or Password, Please Try Again.","invalid")
                return render_template("login.html")
        else:
            return render_template("login.html")


no_of_posts = 3
postss = Posts.query.filter_by().all()
@app.route("/")
def index():
    postse = []
    last = math.ceil(len(postss) / no_of_posts)
    page = request.args.get("page")

    if not str(page).isnumeric():
        page = 0

    postse = postss[int(page)*int(no_of_posts) : int(page)*int(no_of_posts)+int(no_of_posts)]
    print(page)
    print(type(page))
    print(last)
    print(type(last))
    if page == 0 or page == "0":
        print("asas")
        prev = "#"
        next = "/?page="+str(int(page)+1)
    elif int(page) == int(last)-1:
        print("asas")
        next = "#"
        prev = "/?page="+str(int(page)-1)
    else:
        prev = "/?page="+str(int(page)-1)
        next = "/?page="+str(int(page)+1)
    return render_template("index.html",fb=fb_url, posts=postse, prev=prev,next=next)



@app.route("/index")
def home():
    postse = []
    last = math.ceil(len(postss) / no_of_posts)
    page = request.args.get("page")

    if not str(page).isnumeric():
        page = 0

    postse = postss[int(page) * int(no_of_posts): int(page) * int(no_of_posts) + int(no_of_posts)]
    print(page)
    print(type(page))
    print(last)
    print(type(last))
    if page == 0 or page == "0":
        print("asas")
        prev = "#"
        next = "/?page=" + str(int(page) + 1)
    elif int(page) == int(last) - 1:
        print("asas")
        next = "#"
        prev = "/?page=" + str(int(page) - 1)
    else:
        prev = "/?page=" + str(int(page) - 1)
        next = "/?page=" + str(int(page) + 1)
    return render_template("index.html", fb=fb_url, posts=postse, prev=prev, next=next, page=page)

@app.route("/about")
def about():
    return render_template("about.html",fb=fb_url)

@app.route("/contact", methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        return render_template("contact.html",fb=fb_url)

    return render_template("contact.html",fb=fb_url)



@app.route("/post/<string:post_slug>",methods=['GET'])
def posts(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",fb=fb_url,post=post)


@app.route("/edit/post-<string:sno>",methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user'] == dash["user_name"]:
        aaa = Posts.query.filter_by(sno=sno).first()

        if request.method == 'POST':
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            slug = request.form.get('slug')
            content = request.form.get('content')
            image = request.form.get('img_file')
            date = datetime.now()


            if sno == "add-post":
                new_post = Posts(title = title, subtitle=subtitle, slug=slug,content=content,image=image, date=date)
                db.session.add(new_post)
                db.session.commit()
            elif aaa != None:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.subtitle = subtitle
                post.slug = slug
                post.content = content
                post.image = image
                post.date=date
                db.session.commit()
                return redirect("/dashboard")
            else:
                return render_template("404.html")
        if aaa != None or sno == "add-post":
            post = Posts.query.filter_by(sno=sno).first()
            return render_template("edit.html",sno=sno, post=post)
        elif aaa == None:
            return render_template("404.html")
    else:
        return redirect("/dashboard")

ALLOWED_EXTENSIONS =('.png', '.jpg', '.jpeg', '.gif')

@app.route("/uploader", methods=['GET','POST'])
def uploader():
    if 'user' in session and session['user'] == dash["user_name"]:
        if request.method == 'POST':
            file = request.files['file']
            if (file.filename).endswith(ALLOWED_EXTENSIONS):
                file.save(os.path.join(app.config["file-path"],secure_filename(file.filename)))
                return redirect("/file-uploaded-successfully")
            else:
                return redirect("/file-uploaded-successfully")
    else:
        return redirect("/dashboard")



@app.route("/file-uploaded-successfully")
def success():
    if 'user' in session and session['user'] == dash["user_name"]:
        return render_template("upload-success.html")
    else:
        return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.pop("user")
    flask.flash("Logout Successfully")
    return redirect("/dashboard")


@app.route("/post/delete-post-<string:sno>")
def delete_post(sno):
    if 'user' in session and session['user'] == dash["user_name"]:
        delete_post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(delete_post)
        db.session.commit()
        return redirect("/dashboard")

@app.errorhandler(404)
def error_handle(e):
    return render_template("404.html")

app.run(debug=True)