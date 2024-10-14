from dataclasses import dataclass, field
from discord import Message
from shop_item import *

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

    user_interaction_tokens: dict[int, list[int]] = field(default_factory=dict[int, list[int]]) # key - userid;
                                                                                                # list[0] - tokens (max 3);
                                                                                                # list[1] - messages until next token;
                                                                                                # list[2] - time of last message

    shop_items: list[ShopItem] = field(default_factory=list[ShopItem])

    def get_shop_items_str(self) -> str:
        s = ""

        for i in range(len(self.shop_items)):
            s += f"{i}. {self.shop_items[i]}\n"

        return s