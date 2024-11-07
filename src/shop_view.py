from discord import Interaction
from discord.ui import View, Button

import commands
from shop_item import ShopItem


_NUM_EMOJIS: tuple = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣",
                      "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟",
                      "1️⃣1️⃣", "1️⃣2️⃣", "1️⃣3️⃣", "1️⃣4️⃣", "1️⃣5️⃣",
                      "1️⃣6️⃣", "1️⃣7️⃣", "1️⃣8️⃣", "1️⃣9️⃣", "2️⃣0️⃣",
                      "2️⃣1️⃣", "2️⃣2️⃣", "2️⃣3️⃣", "2️⃣4️⃣", "2️⃣5️⃣")


class _ShopButton(Button["ShopView"]):
    view: "ShopView"
    idx: int
    item: ShopItem

    def __init__(self, idx: int, item: ShopItem):
        if idx > 24 or idx < 0:
            raise ValueError("Button index must be between 0 and 24")
        
        super().__init__(label=f"{_NUM_EMOJIS[idx]}")

        self.idx = idx
        self.item = item
        self.disabled = item.is_bought

    async def callback(self, interaction: Interaction["ShopView"]):
        await interaction.response.defer()
        self.disabled = await commands.buy_item(
            idx=self.idx,
            channel=interaction.message.channel,
            userid=interaction.user.id,
            orig_shop_msg=interaction.message,
            shop_view=self.view
        )


class ShopView(View):
    children: list[_ShopButton]

    def __init__(self, shop_items: list[ShopItem]):
        super().__init__()
        for i in range(len(shop_items)):
            self.add_item(_ShopButton(i, shop_items[i]))
