import discord

from dataclasses import dataclass, field
from enum import Enum
import time

class _UpgradeType(Enum):
    PERSONAL = 0
    GLOBAL = 1


@dataclass
class _Upgrade:
    u_id: int
    cost: int
    name: str
    desc: str
    TYPE: _UpgradeType
    is_owned: bool = False

    def __str__(self) -> str:
        s: str = f"**{self.name}** за {self.cost} 🪙: {self.desc}"
        return f"~~{s}~~" if self.is_owned else s
    
    def get_cost(self, userid: int) -> int:
        return self.cost

    def get_label(self, userid: int) -> str:
        return f"{self.name} | {self.get_cost(userid)} 🪙"
    
    def buy(self, token_info: list[int], userid: int) -> None:
        can_buy: bool = (self.cost <= token_info[0]) and not self.is_owned
        if can_buy:
            token_info[0] -= self.cost
            self.is_owned = True


@dataclass
class _U_AfkTokens(_Upgrade):
    DEFAULT_VAL: int = 3  # The default amount of AFK hours with token gain
    MAX_LEVEL: int = 9
    COST_PER_LEVEL: int = 10
    levels: dict[int, int] = field(default_factory=dict[int, int])  # Key - userid, value - level

    def get_label(self, userid: int) -> str:
        self.is_owned = self.get_level(userid) >= self.MAX_LEVEL
        return super().get_label(userid)

    def get_level(self, userid: int) -> int:
        if userid not in self.levels.keys():
            self.levels[userid] = 0
        return self.levels[userid]
    
    def get_cost(self, userid: int) -> int:
        level: int = self.get_level(userid)
        return self.cost + level * self.COST_PER_LEVEL

    def to_str(self, userid: int) -> str:
        level: int = self.get_level(userid)
        cost: int = self.get_cost(userid)

        s: str = f"**{self.name}** за {cost} 🪙 (__{level+1}/{self.MAX_LEVEL+1}__): {self.desc}"
        return f"~~{s}~~" if self.is_owned else s
    
    def buy(self, token_info: list[int], userid: int) -> None:
        can_buy: bool = (self.cost <= token_info[0]) and not self.is_owned
        if can_buy:
            token_info[0] -= self.cost
            self.levels[userid] += 1
            self.is_owned = self.levels[userid] == self.MAX_LEVEL

@dataclass
class _U_Fubar(_Upgrade):
    expiration_time: int = 0
    
    def check_expiration(self) -> bool:
        """Updates `is_owned` according to `expiration_time`, returns if the upgrade is still active."""
        self.is_owned = int(time.time()) < self.expiration_time
        return self.is_owned

    def __str__(self) -> str:
        self.check_expiration()
        return super().__str__()

    def get_label(self, userid: int) -> str:
        self.check_expiration()
        return super().get_label(userid)

    def buy(self, token_info: list[int], userid: int) -> None:
        can_buy: bool = (self.cost <= token_info[0]) and not self.is_owned
        if can_buy:
            token_info[0] -= self.cost
            self.is_owned = True
            self.expiration_time = int(time.time()) + 3600

_ALL_UPGRADES: list[_Upgrade] = [
    _Upgrade(
        u_id=0,
        name="🍗 ;feed",
        desc="Разблокирует команду `;feed` для всего сервера, с помощью которой можно кормить бота пользовательской едой.",
        cost=50,
        TYPE=_UpgradeType.GLOBAL
    ),
    _Upgrade(
        u_id=1,
        name="🩷 ;heal",
        desc="Разблокирует команду `;heal` для всего сервера, с помощью которой можно лечить бота пользовательскими лекарствами.",
        cost=50,
        TYPE=_UpgradeType.GLOBAL
    ),
    _U_AfkTokens(
        u_id=2,
        name="⌛ +1 час АФК токенов",
        desc="Прибавляет один час к максимальному количеству проведённых в АФК часов, за которые вы получаете токены. (По умолчанию - 3)",
        cost=10,
        TYPE=_UpgradeType.PERSONAL
    ),
    _U_Fubar(
        u_id=3,
        name="👹 Ты ебанутый",
        desc="Добавляет \"ТЫ ЕБАНУТЫЙ\" к запросу сообщений инвалида и команде `;prompt` на час.",
        cost=15,
        TYPE=_UpgradeType.GLOBAL
    )
    ]


class Upgrades:
    upgrades: list[_Upgrade]

    def __init__(self) -> None:
        self.upgrades = list()
        self.upgrades.extend(_ALL_UPGRADES)

    @classmethod
    def reinstantiate(
            cls,
            is_feed_bought: bool,
            is_heal_bought: bool,
            afk_token_levels: dict[int, int]
        ) -> "Upgrades":
        upgrades: Upgrades = cls()
        upgrades.upgrades[0].is_owned = is_feed_bought
        upgrades.upgrades[1].is_owned = is_heal_bought
        upgrades.upgrades[2].levels = afk_token_levels
        return upgrades
    
    def to_str(self, userid: int) -> str:
        s: str = ""

        for upgrade in self.upgrades:
            s += "- "

            match upgrade.TYPE:
                case _UpgradeType.GLOBAL:
                    s += upgrade.__str__()
                case _UpgradeType.PERSONAL:
                    s += upgrade.to_str(userid)

            s += "\n"
        
        return s

    def can_feed(self) -> bool:
        return self.upgrades[0].is_owned
    
    def can_heal(self) -> bool:
        return self.upgrades[1].is_owned
    
    def get_max_afk_hours(self, userid: int) -> int:
        afk_tok_upgrade: _U_AfkTokens = self.upgrades[2]
        return afk_tok_upgrade.get_level(userid) + afk_tok_upgrade.DEFAULT_VAL
    
    def is_fubar(self) -> bool:
        fubar_upgrade: _U_Fubar = self.upgrades[3]
        return fubar_upgrade.check_expiration()


class _UpgradeButton(discord.ui.Button):
    view: "UpgradesView"
    upgrade: _Upgrade

    def __init__(self, upgrade: _Upgrade, label: str, disabled: bool) -> None:
        super().__init__(label=label, disabled=disabled)
        self.upgrade = upgrade
    
    async def interaction_check(self, interaction: discord.Interaction["UpgradesView"]) -> bool:
        is_wrong_user: bool = interaction.user.id != self.view.userid
        if is_wrong_user:
            await interaction.response.send_message("Это не ваше меню.", ephemeral=True)

        return not is_wrong_user

    async def callback(self, interaction: discord.Interaction["UpgradesView"]):
        self.upgrade.buy(self.view.user_token_info, self.view.userid)
        self.disabled = self.upgrade.is_owned
        self.label = self.upgrade.get_label(self.view.userid)

        await interaction.response.edit_message(
            content=self.view.upgrades.to_str(self.view.userid),
            view=self.view
            )


class UpgradesView(discord.ui.View):
    children: list[_UpgradeButton]
    upgrades: Upgrades
    userid: int
    user_token_info: list[int]

    def __init__(self, upgrades: Upgrades, userid: int, user_token_info: list[int]):
        super().__init__()
        self.upgrades = upgrades
        self.userid = userid
        self.user_token_info = user_token_info

        for upgrade in upgrades.upgrades:
            self.add_item(_UpgradeButton(
                upgrade=upgrade,
                label=upgrade.get_label(userid),
                disabled=(upgrade.cost > user_token_info[0]) or upgrade.is_owned
            ))
    
    def to_str(self) -> str:
        return self.upgrades.to_str(self.userid)
