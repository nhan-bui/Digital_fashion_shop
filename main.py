from flask import render_template, request, redirect, url_for, jsonify, session
from models import *
import utils
import cloudinary.uploader
from flask_login import login_user, logout_user, current_user
from init import login_manager
import replicate
from dotenv import load_dotenv

load_dotenv()

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


@app.route("/api/add_item", methods=["post"])
def add_item_api():
    data = request.json

    pr_id = data['pr_id']
    quantity = int(data['quantity'])
    size = data['size']
    if current_user.is_authenticated:
        try:
            utils.add_to_cart(product_id=pr_id, user_id=current_user.id, size=size, quantity=quantity)
            return jsonify({'status': "oke"})
        except Exception as e:
            print(e)
            return jsonify({'status': "not oke"})
    else:
        carts = session.get('carts', [])
        pr = Products.query.get(pr_id)
        carts.append({'product_id': pr_id, 'quantity': quantity, 'name': pr.name,
                      'size': size, 'price': pr.price, 'image': pr.image, 'category' : pr.category})
        session['carts'] = carts

    return jsonify({'status': 'oke'})


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
            if 'carts' in session:
                for ct in session['carts']:
                    utils.add_to_cart(product_id=ct['product_id'], user_id=current_user.id, size=ct['size'], quantity=ct['quantity'])
                session.pop('carts', None)
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
        cpass = request.form.get("confirm_password").strip()
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
            address = request.form.get('address')
            phone_num = request.form.get('phone_num')
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']

            try:
                current_user.name = name
                current_user.avatar_path = avatar_path
                current_user.address = address
                current_user.phone_num = phone_num
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
        item_cart = []
        if 'carts' in session:
            for ct in session['carts']:
                item_cart.append(ct)

        if request.method.__eq__("POST"):
            if 'bt3' or 'bt4' in request.form:
                return redirect(url_for('login'))
        return render_template("cart.html", item_cart=item_cart)
    else:
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
                return redirect(url_for('cart'))
            except Exception as e:
                return redirect(url_for('cart'))
        elif "bt2" in request.form:
            try:
                cart_id = request.form.get("cart_id")
                delete_cart = Cart.query.get(cart_id)
                db.session.delete(delete_cart)
                db.session.commit()
                return redirect(url_for('cart'))
            except Exception as e:
                return redirect(url_for('cart'))

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
    elif num_page == "4":
        num_page = int(num_page)
        products = Products.query
        return render_template("admin.html", num_page=num_page, products=products)

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


@app.route("/api/change_active", methods=["POST"])
def change_active():
    data = request.json
    product_id = int(data['product_id'])
    if current_user.user_role != UserRole.ADMIN:
        return jsonify({"status": "no admin"})

    result = utils.change_active(product_id=product_id)
    if result != 3:
        return jsonify({"status": "oke", "active": result})
    return jsonify({"status": "not_oke", "active": result})


@app.route("/product", methods=["POST", "GET"])
def product():
    err = None
    products = Products.query

    product_id = int(request.args.get("product_id"))
    comments = Comment.query.filter(Comment.product_id == product_id)
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


@app.route("/try_on", methods=["GET", "POST"])
def try_on():
    garms = Products.query.filter(Products.category.in_([1, 3]))
    return render_template("try_on.html", garms=garms)


@app.route("/api/load_image", methods=["POST", "GET"])
def get_image():
    data = request.json
    model = data[0]['base64']
    garm = data[1]['image_link']
    human = f"data:application/octet-stream;base64,{model}"
    inp = {
        "garm_img": garm,
        "human_img": human,
        "garment_des": "cute pink top"
    }
    output = replicate.run(
            "cuuupid/idm-vton:906425dbca90663ff5427624839572cc56ea7d380343d13e2a4c4b09d3f0c30f",
            input=inp
        )
    # print(output)
    # => "https://replicate.delivery/pbxt/Tfs5JETdzlURKyKeUOltKwch...
    try:

        return jsonify({"status": "oke",
                        "image": output})
    except Exception:
        return jsonify({"status": "not oke"})


if __name__ == "__main__":
    app.run(debug=True)