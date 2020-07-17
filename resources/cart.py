import sys

from flask import request
from flask_restful import Resource

from models.cart import CartModel


from schemas.cart import CartSchema
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)

cart_schema = CartSchema()


class CartList(Resource):
    @classmethod
    def get(cls):
        return cart_schema.dump(CartModel.find_all_cart_items(), many=True), 200


class Cart(Resource):
    @classmethod
    def get(cls, user_id: int):
        cart = CartModel.find_all_items_for_user(user_id)
        if not cart:
            return {"message": "user cart is empty"}, 200
        return cart_schema.dump(cart, many=True), 200

    @classmethod
    @jwt_required
    def post(cls):
        '''
        Expect an item, with it's quantity,
        '''
        cart_json = request.get_json()
       # user = UserModel.find_by_id(cart_json["user_id"])
        #cart = CartModel(status="pending",user=user)
        cart = cart_schema.load(cart_json)

        try:
            cart.save_to_db()
            return cart_schema.dump(cart),200
        except:
            return{"message":"an error occured when saving to db"}
