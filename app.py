from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from dotenv import load_dotenv

from db import db
from ma import ma
from blacklist import BLACKLIST

from resources.order import Order,OrderListForUser,OrderItemsList,MakePaymentForOrder,OrderList

from resources.user import UserRegister, UserLogin, User, TokenRefresh, UserLogout
from resources.cart import Cart,CartList

from resources.item import Item, ItemList
from resources.store import Store, StoreList



app = Flask(__name__)
load_dotenv(".env")
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")
api.add_resource(Order, '/order')
api.add_resource(OrderList, '/orders')
api.add_resource(OrderListForUser, '/order/user/<int:user_id>')

api.add_resource(Cart,'/cart/<int:user_id>','/cart/add')
api.add_resource(CartList,'/carts')
api.add_resource(OrderItemsList,'/order/items/<int:order_id>')
api.add_resource(MakePaymentForOrder,'/makePayment/<int:order_id>')


if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)
