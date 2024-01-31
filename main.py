from flask import Flask, render_template, request, redirect, url_for
from models import *
import utils
import cloudinary.uploader
from flask_login import login_user, logout_user
from init import login_manager


@app.route("/", methods=['get', 'post'])
def home():
    products = Products.query
    cate_id = request.args.get('category')
    keyword = request.args.get('keyword')
    products = utils.get_product(cate_id=cate_id, keyword=keyword)
    # if cate_id is not None:
    #     products = utils.get_product(cate_id=cate_id)

    return render_template("index.html", products=products)


@app.route("/login", methods=['get', 'post'])
def login():
    err = None
    if request.method.__eq__("POST"):
        email = request.form.get("email")
        password = request.form.get("password")
        user = utils.check_login(email=email, password=password)

        if user:
            login_user(user=user)
            return redirect(url_for('home'))

        err = 1

    return render_template("login.html", err=err)


@app.route("/register", methods=['get', 'post'])
def register():
    err = None
    if request.method.__eq__("POST"):
        name = request.form.get("name")
        email = request.form.get('email')
        password = request.form.get("password").strip()
        cpass = request.form.get("confirmpassword").strip()
        avatar_path = "static/image/deafaut_avatar.jpg"
        avatar = request.files.get('avatar')
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']

        if password != cpass:
            err = 1
            return render_template("register.html", err=err)

        try:
            utils.add_user(name=name, email=email, password=password, avatar_path=avatar_path)
            err = 0
        except Exception:
            err = 2
    return render_template("register.html", err=err)


@login_manager.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route("/log-out")
def log_out():
    logout_user()
    return redirect(url_for('home'))


@app.route("/user")
def user_page():
    return render_template("user.html")

if __name__ == "__main__":
    app.run(debug=True)