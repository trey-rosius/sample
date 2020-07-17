from ma import ma
from models.user import UserModel

from schemas.order import OrderSchema


class UserSchema(ma.SQLAlchemyAutoSchema):
    orders = ma.Nested(OrderSchema, many=True)

    class Meta:
        model = UserModel
        load_only = ("password","orders.user_id",)
        dump_only = ("id",)
        load_instance = True
