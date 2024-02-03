from init import db, app
from models import Products, User, Cart, UserRole
import hashlib


def add_items(x: Products):
    db.session.add(x)
    db.session.commit()


def add_user(name, email, password, avatar_path, user_role=UserRole.USER):
    password = str(hashlib.sha256(password.encode('utf-8')).hexdigest())
    user = User(name=name, email=email, password=password, avatar_path=avatar_path, user_role=user_role)
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


def get_cart(product_id, user_id, size):
    return Cart.query.filter(Cart.product_id.__eq__(product_id), Cart.user_id.__eq__(user_id),
                             Cart.size.__eq__(size)).first()


def add_to_cart(product_id, user_id, size, quantity):
    cart = get_cart(product_id=product_id, user_id=user_id, size=size)
    if cart and cart.is_bill.__eq__(False):
        cart.quantity += quantity
    else:
        cart = Cart(product_id=product_id, user_id=user_id, quantity=quantity, size=size)
        db.session.add(cart)
    try:
        db.session.commit()
    except Exception as e:
        print(f"Error committing transaction: {str(e)}")
        db.session.rollback()


def make_bill(product_id, user_id, quantity, size):
    cart = Cart.query.filter(Cart.user_id.__eq__(user_id), Cart.product_id.__eq__(product_id),
                             Cart.is_bill.__eq__(False), Cart.size.__eq__(size)).first()
    cart.quantity = quantity
    cart.size = size
    cart.is_bill = True
    db.session.commit()


def admin_confirm(bill_id):
    bill = Cart.query.get(bill_id)
    bill.admin_confirm = True
    db.session.commit()


if __name__ == "__main__":
    name = "Nhân admin"
    email = "admin1@gmail.com"
    password = "123456"
    avatar_path = "static/image/deafaut_avatar.jpg"
    user_role = UserRole.ADMIN
    with app.app_context():
        add_user(name=name, email=email, password=password, avatar_path=avatar_path, user_role=user_role)

