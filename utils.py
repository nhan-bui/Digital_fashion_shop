from init import db, app
from models import Products, User, Cart
import hashlib


def add_items(x: Products):
    db.session.add(x)
    db.session.commit()


def add_user(name, email, password, avatar_path):
    password = str(hashlib.sha256(password.encode('utf-8')).hexdigest())
    user = User(name=name, email=email, password=password, avatar_path=avatar_path)
    db.session.add(user)
    db.session.commit()


def get_product(cate_id=None, keyword=None):
    products = Products.query
    if cate_id:
        products = products.filter(Products.category.__eq__(cate_id))
    if keyword:
        products = products.filter(Products.name.contains(keyword))
    return products


def check_login(email, password):
    if email and password:
        password = str(hashlib.sha256(password.encode('utf-8')).hexdigest())
        user = User.query.filter(User.email.__eq__(email.strip()), User.password.__eq__(password)).first()
        return user


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_cart(product_id, user_id):
    return Cart.query.filter(Cart.product_id.__eq__(product_id), Cart.user_id.__eq__(user_id)).first()


def add_to_cart(product_id, user_id, quantity):
    cart = get_cart(product_id=product_id, user_id=user_id)
    if cart and cart.is_bill.__eq__(False):
        cart.quantity += quantity
    else:
        cart = Cart(product_id=product_id, user_id=user_id, quantity=quantity)
        db.session.add(cart)
    try:
        db.session.commit()
    except Exception as e:
        print(f"Error committing transaction: {str(e)}")
        db.session.rollback()


def make_bill(product_id, user_id, quantity):
    cart = Cart.query.filter(Cart.user_id.__eq__(user_id), Cart.product_id.__eq__(product_id),
                             Cart.is_bill.__eq__(False)).first()
    cart.quantity = quantity
    cart.is_bill = True
    db.session.commit()
