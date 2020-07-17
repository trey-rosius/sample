from ma import ma
from models.cart import CartModel


class CartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CartModel
        include_Fk = True
        load_instance = True
