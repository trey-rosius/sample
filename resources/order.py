from collections import Counter
from flask import request
from flask_restful import Resource
from stripe import error

from models.order import OrderModel, ItemsInOrder
from resources.item import item_schema
from schemas.items_in_order_schema import ItemsInOrderSchema

from schemas.order import OrderSchema
from models.item import ItemModel

order_schema = OrderSchema()
items_in_order_schema = ItemsInOrderSchema()

'''
class ItemsForOrder(Resource):
    @classmethod
    def get(cls,order_id:int):
        return item_schema.dump(OrderModel.find_all_items_for_specific_order(order_id),many=True),200


'''

class OrderItemsList(Resource):
    @classmethod
    def get(cls, order_id: int):
        return {"items_in_order":items_in_order_schema.dump(ItemsInOrder.get_items_for_order(order_id), many=True)}, 200





class MakePaymentForOrder(Resource):
    @classmethod
    def post(cls,order_id:int):
        # first check if order exists
        # then check if
        data = request.get_json()
        order = OrderModel.find_pending_id(order_id)
        if not order:
            return {"message": "No active order for this user"}, 200

        try:
            order.set_status("failed")  # assume the order would fail until it's completed
            order.charge_with_stripe(data["token"])
            order.set_status("complete-after")  # charge succeeded
            return order_schema.dump(order), 200
            # the following error handling is advised by Stripe, although the handling implementations are identical,
            # we choose to specify them separately just to give the students a better idea what we can expect
        except error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            return e.json_body, e.http_status
        except error.RateLimitError as e:
            # Too many requests made to the API too quickly
            return e.json_body, e.http_status
        except error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            return e.json_body, e.http_status
        except error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return e.json_body, e.http_status
        except error.APIConnectionError as e:
            # Network communication with Stripe failed
            return e.json_body, e.http_status
        except error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return e.json_body, e.http_status
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            print(e)
            return {"message": "order error"}, 500



class OrderListForUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        # first check if user exists
        # then check if
        order = OrderModel.find_all_orders_for_user(user_id)
        if not order:
            return {"message": "No active order for this user"}, 200

        return order_schema.dump(order, many=True), 200


class Order(Resource):
    @classmethod
    def get(cls,order_id):

        return order_schema.dump(OrderModel.find_by_id(order_id)), 200

    @classmethod
    def post(cls):
        """
        Expect a token and a list of items from the request body
        Construct an order and talk to the Stripe API to make charge
        """
        data = request.get_json()
        order = OrderModel.find_pending_order_by_user_id(data["user_id"])
        if order:
            items = []
            item_id_quantities = Counter(data["item_ids"])
            # [3,3,4,1,6,6,6]
            for _id, count in item_id_quantities.most_common():  # [6,3],[1,1],[4,1],3,2] most common
                item = ItemModel.find_by_id(_id)
                if not item:
                    return {"message": "Order Item by id not found"}, 404
                itemsInOrder = ItemsInOrder.is_item_available(_id, order.id)
                if itemsInOrder:
                    itemsInOrder.set_quantity(count)
                else:

                    orderItems = ItemsInOrder(item_id=_id, quantity=count, order_id=order.id)
                    orderItems.save_to_db()

            return {"message": "Order saved to Items in Order"}, 200

        items = []
        item_id_quantities = Counter(data["item_ids"])
        # [3,3,4,1,6,6,6]
        for _id, count in item_id_quantities.most_common():  # [6,3],[1,1],[4,1],3,2] most common
            item = ItemModel.find_by_id(_id)
            if not item:
                return {"message": "Order Item by id not found"}, 404
            items.append(ItemsInOrder(item_id=_id, quantity=count))

        order = OrderModel(items=items, status="pending", user_id=data["user_id"])
        order.save_to_db()
        return order_schema.dump(order), 200

class OrderList(Resource):
    @classmethod
    def get(cls):
        return order_schema.dump(OrderModel.find_all(), many=True), 200

