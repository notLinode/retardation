from dataclasses import dataclass, field
from discord import Message
from shop_item import *
import time

@dataclass
class BotVariables:
    SETTING_MESSAGE_INTERVAL_MIN: int = 1
    SETTING_MESSAGE_INTERVAL_MAX: int = 25
    setting_message_interval: int = 7
    setting_message_interval_is_random: bool = True
    message_interval_random: int = 4

    SETTING_OWN_MESSAGE_MEMORY_MIN: int = 1
    SETTING_OWN_MESSAGE_MEMORY_MAX: int = 10
    setting_own_message_memory: int = 3

    recent_messages: list[Message] = field(default_factory=list[Message])
    stylized_bot_messages: list[str] = field(default_factory=list[str])

    satiety: float = 100.0
    health: float = 100.0
    litter_box_fullness: int = 0
    litter_box_timer: int = 60

    def add_health(self, health: float) -> None:
        self.health += health
        if self.health > 100.0:
            self.health = 100.0
        elif self.health < 0:
            self.health = 0
    
    def add_satiety(self, satiety: float) -> None:
        self.satiety += satiety
        if self.satiety > 200.0:
            self.satiety = 200.0
        elif self.satiety < 0:
            self.satiety = 0
    
    def add_litter(self, litter: int) -> None:
        self.litter_box_fullness += litter
        if self.litter_box_fullness > 100:
            self.litter_box_fullness = 100
        elif self.litter_box_fullness < 0:
            self.litter_box_fullness = 0

    user_interaction_tokens: dict[int, list[int]] = field(default_factory=dict[int, list[int]]) # key - userid;
                                                                                                # list[0] - tokens (max 3);
                                                                                                # list[1] - messages until next token;
                                                                                                # list[2] - time of last message

    shop_items: list[ShopItem] = field(default_factory=list[ShopItem])
    shop_items_next_update_time: int = 0

    def get_shop_items_str(self) -> str:
        s = ""

        for i in range(len(self.shop_items)):
            s += f"{i}. {self.shop_items[i]}\n"

        s += f"\n⏳ До обновления магазина `{(self.shop_items_next_update_time - int(time.time())) // 60}` минут."

        return s
    
    def set_default_shop_items(self) -> None:
        item_1: ShopItem = ShopItem("Гоблинские бубуки", -30, 9, 1, 0, 0, 0, 0)
        item_2: ShopItem = ShopItem("Угощение", 50, 0, 2, 0, 0, 0, 0)
        self.shop_items = [item_1, item_2]
    
    @staticmethod
    def deserialize_user_interaction_tokens(tokens_str: str) -> dict[int, list[int]]:
        for pair in tokens_str.split(', '):
            userid, tokens_info = pair.split(': ')
            user_interaction_tokens: dict[int, list[int]] = {}
            user_interaction_tokens[int(userid)] = eval(tokens_info)
        return user_interaction_tokens
