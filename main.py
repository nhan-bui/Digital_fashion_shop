from flask import render_template, request, redirect, url_for
from models import *
import utils
import cloudinary.uploader
from flask_login import login_user, logout_user, current_user
from init import login_manager


@app.context_processor
def inject_user_role():
    return dict(UserRole=UserRole)


@app.route("/", methods=['get', 'post'])
def home():
    # products = Products.query
    cate_id = request.args.get('category')
    keyword = request.args.get('keyword')
    products = utils.get_product(cate_id=cate_id, keyword=keyword)

    if request.method.__eq__("POST"):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        pr_id = request.form.get("product_id")
        user_id = current_user.id
        quantity = int(request.form.get("quantity"))
        size_clothes = request.form.get("size_clothes")
        size_shoe = request.form.get("size_shoe")
        size = size_shoe or size_clothes
        utils.add_to_cart(product_id=pr_id, user_id=user_id, quantity=quantity, size=size)

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
            if current_user.user_role == UserRole.ADMIN:
                return redirect(url_for('admin'))
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
        address = request.form.get("address").strip()
        phonenum = request.form.get("phonenum")
        avatar_path = "https://res.cloudinary.com/dscod7nw4/image/upload/v1708148084/qi3ttkumhoogbhew8ae6.jpg"
        avatar = request.files.get('avatar')
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']

        if password != cpass:
            err = 1
            return render_template("register.html", err=err)

        try:
            utils.add_user(name=name, email=email, password=password, avatar_path=avatar_path,
                           address=address, phonenum=phonenum)
            err = 0
        except Exception as e:
            err = 2
    return render_template("register.html", err=err)


@login_manager.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route("/log-out")
def log_out():
    logout_user()
    return redirect(url_for('home'))


@app.route("/user", methods=['post', "get"])
def user_page():
    err = None
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    bills = Cart.query.filter(Cart.user_id.__eq__(current_user.id), Cart.is_bill.__eq__(True))

    if request.method.__eq__("POST"):
        try:
            name = request.form.get("name")
            avatar = request.files.get('avatar')
            avatar_path = current_user.avatar_path
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']

            try:
                current_user.name = name
                current_user.avatar_path = avatar_path
                db.session.commit()
                err = 0
                return redirect(url_for("user_page"))
            except Exception:
                err = 1
        except Exception:
            err = 1

    return render_template("user.html", err=err, bills=bills)


@app.route("/cart", methods=["get", "post"])
def cart():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    item_cart = Cart.query.filter(Cart.user_id.__eq__(current_user.id), Cart.is_bill.__eq__(False))

    if request.method.__eq__("POST"):
        if 'bt1' in request.form:
            product_id = request.form.get("product_id")
            user_id = current_user.id
            quantity = int(request.form.get("quantity"))
            size_shoe = request.form.get("size_shoe")
            size_clothes = request.form.get("size_clothes")
            size = size_shoe or size_clothes
            try:
                utils.make_bill(product_id=product_id, user_id=user_id, quantity=quantity, size=size)
            except Exception as e:
                return "Đã có lỗi xảy ra"
        elif "bt2" in request.form:
            cart_id = request.form.get("cart_id")
            delete_cart = Cart.query.get(cart_id)
            db.session.delete(delete_cart)
            db.session.commit()

    return render_template("cart.html", item_cart=item_cart)


@app.route("/admin", methods=["get", "post"])
def admin():
    err = None
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    if current_user.user_role == UserRole.USER:
        return redirect(url_for('user_page'))

    num_page = request.args.get('page_id')
    items = Cart.query.filter(Cart.is_bill.__eq__(True))
    if num_page == "1":
        items = items.filter(Cart.admin_confirm.__eq__(True))
    elif num_page == "2":
        items = items.filter(Cart.admin_confirm.__eq__(False))
    elif num_page == "3":
        num_page = int(num_page)
        return render_template("admin.html", num_page=num_page)

    if request.method == "POST":
        if "sm1" in request.form:
            bill_id = request.form.get("bill_id")
            utils.admin_confirm(bill_id=bill_id)
        elif "sm2" in request.form:
            name_product = request.form.get("name")
            avatar = request.files.get("avatar")
            price = int(request.form.get("price"))
            image_path = None
            category = int(request.form.get("category"))
            description = request.form.get("description")
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                image_path = res['secure_url']
            new_product = Products(name=name_product, image=image_path, price=price,
                                   category=category, description=description)
            try:
                utils.add_items(new_product)
                err = 1
            except Exception as e:
                err = 0
            return render_template("admin.html", err=err)

    return render_template("admin.html", items=items)


@app.route("/product", methods=["POST", "GET"])
def product():
    err = None
    products = Products.query

    product_id = int(request.args.get("product_id"))
    comments = Comment.query.filter(Comment.product_id)
    item = products.get(product_id)
    if request.method == "POST":
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        content = request.form.get('box')
        try:
            utils.add_comment(user_id=current_user.id, product_id=product_id, content=content)
            err = 0

        except Exception as e:
            err = 1
        return redirect(url_for('product', product_id=product_id))

    return render_template("product.html", item=item, comments=comments, err=err)


if __name__ == "__main__":
    app.run(debug=True)