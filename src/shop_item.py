from dataclasses import dataclass

@dataclass
class ShopItem():
    name: str
    satiety: int
    health: int
    cost: int
    is_bought: bool
    is_name_hidden: bool
    is_satiety_hidden: bool
    is_health_hidden: bool

    def __str__(self):
        return f"~~**{'??' if self.is_name_hidden else self.name}** за {self.cost} 🪙: `{'??' if self.is_satiety_hidden else self.satiety}🍖` `{'??' if self.is_health_hidden else self.health}🩷`~~" if self.is_bought else f"**{'??' if self.is_name_hidden else self.name}** за {self.cost} 🪙: `{'??' if self.is_satiety_hidden else self.satiety}🍖` `{'??' if self.is_health_hidden else self.health}🩷`"