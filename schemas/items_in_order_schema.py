from ma import ma
from models.order import ItemsInOrder
from schemas.item import ItemSchema
from schemas.order import OrderSchema


class ItemsInOrderSchema(ma.SQLAlchemyAutoSchema):
    item = ma.Nested(ItemSchema)

    class Meta:

        model = ItemsInOrder
        include_fk =True
        load_instance=True
