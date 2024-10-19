from discord import Message

import csv
from dataclasses import asdict, dataclass, field, fields
import os
import time

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
    
    def generate_dto(self) -> "BotVariablesDto":
        return BotVariablesDto(
            self.SETTING_MESSAGE_INTERVAL_MIN,
            self.SETTING_MESSAGE_INTERVAL_MAX,
            self.setting_message_interval,
            self.setting_message_interval_is_random,
            self.message_interval_random,
            self.SETTING_OWN_MESSAGE_MEMORY_MIN,
            self.SETTING_OWN_MESSAGE_MEMORY_MAX,
            self.setting_own_message_memory,
            self.satiety,
            self.health,
            self.litter_box_fullness,
            self.litter_box_timer,
            self.user_interaction_tokens.copy()
        )
    
    @classmethod
    def from_file(cls, readpath: str) -> "BotVariables":
        try:
            with open(readpath, "r") as file:
                reader = csv.DictReader(file)
                reader.line_num
                for row in reader:
                    bot_vars = cls(
                        SETTING_MESSAGE_INTERVAL_MIN   = int(row["SETTING_MESSAGE_INTERVAL_MIN"]),
                        SETTING_MESSAGE_INTERVAL_MAX   = int(row["SETTING_MESSAGE_INTERVAL_MAX"]),
                        setting_message_interval       = int(row["setting_message_interval"]),
                        setting_message_interval_is_random = (
                            row["setting_message_interval_is_random"] == "True"
                        ),
                        message_interval_random        = int(row["message_interval_random"]),
                        SETTING_OWN_MESSAGE_MEMORY_MIN = int(row["SETTING_OWN_MESSAGE_MEMORY_MIN"]),
                        SETTING_OWN_MESSAGE_MEMORY_MAX = int(row["SETTING_OWN_MESSAGE_MEMORY_MAX"]),
                        setting_own_message_memory     = int(row["setting_own_message_memory"]),
                        satiety                        = float(row["satiety"]),
                        health                         = float(row["health"]),
                        litter_box_fullness            = int(row["litter_box_fullness"]),
                        litter_box_timer               = int(row["litter_box_timer"]),
                        user_interaction_tokens        = eval(row["user_interaction_tokens"])
                    )
            return bot_vars
        except Exception as e:
            raise e
    
    def write_to_file(self, writepath: str) -> None:
        dir_path = os.path.dirname(writepath)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        bot_vars_dto: BotVariablesDto = self.generate_dto()
        
        try:
            with open(writepath, "w+") as file:
                flds = [fld.name for fld in fields(BotVariablesDto)]
                writer = csv.DictWriter(file, flds)

                writer.writeheader()
                writer.writerow(asdict(bot_vars_dto))
        except Exception as e:
            raise e

@dataclass
class BotVariablesDto:
    SETTING_MESSAGE_INTERVAL_MIN: int
    SETTING_MESSAGE_INTERVAL_MAX: int
    setting_message_interval: int
    setting_message_interval_is_random: bool
    message_interval_random: int

    SETTING_OWN_MESSAGE_MEMORY_MIN: int
    SETTING_OWN_MESSAGE_MEMORY_MAX: int
    setting_own_message_memory: int

    satiety: float
    health: float
    litter_box_fullness: int
    litter_box_timer: int

    user_interaction_tokens: dict[int, list[int]] = field(default_factory=dict[int, list[int]])
