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
        name = "??" if self.is_name_hidden else self.name
        satiety = "??" if self.is_satiety_hidden or self.is_name_hidden else self.satiety
        health = "??" if self.is_health_hidden or self.is_name_hidden else self.health

        description = f"**{name}** за {self.cost} 🪙: `{satiety}🍖` `{health}🩷`"

        return f"~~{description}~~" if self.is_bought else description