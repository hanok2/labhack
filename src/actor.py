from src import entity
from src.renderorder import RenderOrder


class Actor(entity.Entity):
    def __init__(
        self, *,
        x=0, y=0,
        char="?",
        color=(255, 255, 255),
        name="<Unnamed>",
        ai_cls,
        equipment,
        fighter,
        attacks,
        attributes,
        inventory,
        level,
        energymeter,
    ):

        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )

        self.ai = ai_cls(self)
        self.equipment = equipment
        self.equipment.parent = self
        self.fighter = fighter
        self.fighter.parent = self
        self.attacks = attacks
        self.attacks.parent = self
        self.attributes = attributes
        self.attributes.parent = self
        self.inventory = inventory
        self.inventory.parent = self
        self.level = level
        self.level.parent = self
        self.energymeter = energymeter
        self.energymeter.parent = self

    @property
    def is_alive(self):
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)
