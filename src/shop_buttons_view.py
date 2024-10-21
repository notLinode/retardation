from typing import Any
from discord import Interaction
from discord.ui import View, Button
from bot_variables import *
from shop_item import *
import commands

NUM_EMOJIS: tuple[str] = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣",
                          "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟",
                          "1️⃣1️⃣", "1️⃣2️⃣", "1️⃣3️⃣", "1️⃣4️⃣", "1️⃣5️⃣",
                          "1️⃣6️⃣", "1️⃣7️⃣", "1️⃣8️⃣", "1️⃣9️⃣", "2️⃣0️⃣",
                          "2️⃣1️⃣", "2️⃣2️⃣", "2️⃣3️⃣", "2️⃣4️⃣", "2️⃣5️⃣",)

class ShopButton(Button["ShopView"]):
    idx: int
    item: ShopItem

    def __init__(self, idx: int, item: ShopItem):
        if idx > 24 or idx < 0:
            raise Exception("Button index must be between 0 and 24")
        super().__init__(label=f"{NUM_EMOJIS[idx]}")

        self.idx = idx
        self.item = item

        if item.is_bought:
            self.disabled = True

    async def callback(self, interaction: Interaction["ShopView"]) -> Any:
        await interaction.response.defer()
        self.disabled = await commands.buy_item(
            idx=self.idx,
            channel=interaction.message.channel,
            userid=interaction.user.id,
            bot_vars=self.view.bot_vars
            )
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            content=self.view.bot_vars.get_shop_items_str(),
            view=self.view
            )

class ShopView(View):
    children: list[ShopButton]
    bot_vars: BotVariables

    def __init__(self, bot_vars: BotVariables):
        super().__init__()
        self.bot_vars = bot_vars
        for i in range(len(bot_vars.shop_items)):
            self.add_item(ShopButton(i, bot_vars.shop_items[i]))