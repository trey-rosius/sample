from db import db
from typing import List

'''
class CartItems(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False)

    item = db.relationship("ItemModel")
    cart = db.relationship("CartModel", back_populates="items")
'''


class CartModel(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    users = db.relationship("UserModel", back_populates="carts")

    # items = db.relationship("CartItems", back_populates="cart")

    @classmethod
    def find_all_cart_items(cls) -> List["CartModel"]:
        return cls.query.all()

    @classmethod
    def check_if_user_cart_already_exist(cls, _user_id: int):
        return cls.query.filter_by(user_id=_user_id).first()

    @classmethod
    def find_all_items_for_user(cls, _user_id: int) -> "CartModel":
        return cls.query.filter_by(user_id=_user_id).all()

    def add_to_cart(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_cart(self) -> None:
        db.session.delete(self)
        db.session.commit()
