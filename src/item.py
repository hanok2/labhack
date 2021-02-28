from components.item_comp import ItemComponent
from src import entity
from src.renderorder import RenderOrder


class Item(entity.Entity):
    def __init__(
        self, *,
        x=0, y=0,
        char="?",
        color=(255, 255, 255),
        name="<Unnamed>",
        consumable=None,
        equippable=None,
        item=ItemComponent(),
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
            item=item
        )

        self.consumable = consumable
        self.equippable = equippable
