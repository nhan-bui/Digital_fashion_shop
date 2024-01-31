import os
from sqlalchemy import Integer, Column, String, Boolean, DateTime, Enum
from flask_login import UserMixin
from init import db, app
from datetime import datetime
from enum import Enum as UserEnum


class Products(db.Model):
    __tablename__ = "product"
    __table_args__ = {'extend_existing': True}  # Thêm option extend_existing=True

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    category = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(String(200))

    def __str__(self):
        return f"{self.id} {self.name}"


class UserRole(UserEnum):
    ADMIN = 1
    USER = 2


class User(db.Model, UserMixin):
    __table__name = "user"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    email = Column(String(30), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    avatar_path = Column(String(300))
    active = Column(Boolean, default=True)
    joined_dated = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)

    def __str__(self):
        return self.name


if __name__ == "__main__":
    filenames = os.listdir("static/image")
    print(filenames)
    with app.app_context():
        # db.create_all()
        # utils.add_user(name="Nhân", email="nhan1901@gmail.com", password="123456", avatar_path="static/image/deafaut_avatar.jpg")
        print("TEST oke")

