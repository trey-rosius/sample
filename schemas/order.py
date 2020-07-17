from ma import ma
from models.order import OrderModel


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderModel
        load_only=("token",) #never dump token. Only accept(load) it.
        dump_only=("id","status",) #never load Id and status. only dump them
        include_fk=True
        load_instance = True