import stripe

from db import db
from typing import List, Dict
import os

from models.item import ItemModel

CURRENCY = "usd"


class ItemsInOrder(db.Model):
    __tablename__ = "items_in_order"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    quantity = db.Column(db.Integer)

    item = db.relationship("ItemModel")
    order = db.relationship("OrderModel", back_populates="items")

    @classmethod
    def get_items_for_order(cls, _order_id) -> List["ItemsInOrder"]:
        items = []

        for i in ItemsInOrder.query.filter(ItemsInOrder.order.has(id=_order_id)).all():
            items.append(i)
        return items

    @classmethod
    def is_item_available(cls, _item_id: int, order_id: int) -> "ItemsInOrder":
        return cls.query.filter_by(item_id=_item_id, order_id=order_id).first()

    def set_quantity(self, _quantity: int) -> None:
        self.quantity = self.quantity + _quantity
        db.session.commit()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()


class OrderModel(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    items = db.relationship("ItemsInOrder", back_populates='order')

    @property
    def description(self):
        '''
        Generating a simple string representing this order
        '''
        item_counts = [f"{i.quantity}x {i.item.name}" for i in self.items]
        return ",".join(item_counts)

    @property
    def amount(self):
        return int(sum([item_data.item.price * item_data.quantity for item_data in self.items]) * 100)

    @classmethod
    def amount_per_order(cls, order_id: int):
        return int(sum([item_data.item.price * item_data.quantity for item_data in
                        ItemsInOrder.query.filter(ItemsInOrder.order.has(id=order_id)).all()]) * 100)

    @classmethod
    def description_per_order(cls, order_id: int):
        '''
        Generating a simple string representing this order
        '''
        item_counts = [f"{i.quantity}x {i.item.name}" for i in
                       ItemsInOrder.query.filter(ItemsInOrder.order.has(id=order_id)).all()]
        return ",".join(item_counts)

    '''

        def find_all_items_for_specific_order(self, order_id: int) -> List["ItemModel"]:
            return ItemModel.query.filter(self.items.any(order_id=order_id)).all()
        '''

    @classmethod
    def find_pending_order_by_user_id(cls, _user_id: int) -> "OrderModel":
        return cls.query.filter_by(user_id=_user_id, status="pending").first()

    @classmethod
    def find_all_orders_for_user(cls, _user_id: int) -> List['OrderModel']:
        return cls.query.filter_by(user_id=_user_id).all()

    @classmethod
    def find_all_items_for_specific_order(cls, _order_id: int) -> List['ItemModel']:
        items = []

        for i in ItemsInOrder.query.filter(ItemsInOrder.order.has(id=_order_id)).all():
            items.append(i.item)

        return items


    @classmethod
    def find_all(cls) -> List['OrderModel']:
        return cls.query.all()

    @classmethod
    def find_by_id(cls, _id: int) -> "OrderModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_pending_id(cls, _id: int) -> "OrderModel":
        return cls.query.filter_by(id=_id, status="pending").first()

    def set_status(self, new_status: str) -> None:
        self.status = new_status
        self.save_to_db()

    def charge_with_stripe(self, token: str) -> stripe.Charge:
        stripe.api_key = os.getenv("STRIPE_API_KEY")
        return stripe.Charge.create(
            amount=self.amount,  # amount of cents(100 means USD1.00)
            currency=CURRENCY,
            description=self.description,
            source=token

        )

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
