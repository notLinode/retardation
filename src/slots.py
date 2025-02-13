import discord

import asyncio
from enum import Enum
import random


_REEL_EMOJIS: tuple = (
    ":skull:", "<:proverka:1307010119824965723>", ":cherries:", ":mushroom:",
    "<:gragas:1336062411970580511>", "<:esq_gragas:1336062410041196646>",
    "<:bulborb:1336061550498287616>", "<:nuclear_bulborb:1336061387847372830>",
    "<a:slots:1336120636635873390>"
)


class _Reel(Enum):
    SKULL = 1
    PROVERKA = 2
    CHERRIES = 3
    FUNGUS = 4
    GRAGAS = 5
    ESQ_GRAGAS = 6
    BULBORB = 7
    NUCLEAR_BULBORB = 8
    SPINNING = 9

    def to_emoji(self) -> str:
        return _REEL_EMOJIS[self.value-1]
    
    @classmethod
    def get_random(cls) -> "_Reel":
        return cls(random.sample(
            population=[1, 2, 3, 4, 5, 6, 7, 8],
            k=1,
            counts=[17, 33, 10, 10, 15, 9, 5, 1]
        )[0])


class View(discord.ui.View):
    bet: int
    player_userid: int
    player_token_info: list[int]
    msg: discord.Message
    reels: list[_Reel]
    winnings: float

    def __init__(self, bet: int, userid: int, token_info: list[int]):
        super().__init__(timeout=30)
        self.bet = bet
        self.player_userid: int = userid
        self.player_token_info = token_info
        self.reels = [_Reel.SPINNING, _Reel.SPINNING, _Reel.SPINNING]
        self.winnings = 0.0

        self.player_token_info[0] -= self.bet

    def __str__(self) -> str:
        s: str = f"<@{self.player_userid}> | :coin: Ставка: `{self.bet}`\n"
        s += f"> {self.reels[0].to_emoji()} {self.reels[1].to_emoji()} {self.reels[2].to_emoji()}\n\n"
        s += f"**Навар: {('+' if self.winnings >= 0 else '') + str(int(self.winnings))} :coin:**"

        return s

    async def set_msg_and_spin(self, msg: discord.Message) -> None:
        self.msg = msg
        await self.spin()

    async def spin(self, cnt: int = 0) -> None:
        if cnt == 3:
            self.player_token_info[0] += int(self.winnings)
            await self.msg.edit(content=str(self), view=self)
            return
        
        await asyncio.sleep(0.5)

        self.reels[cnt] = _Reel.get_random()
        self.winnings = max(round(self.bet * self.calc_multiplier()), 0)

        await self.msg.edit(content=str(self), view=self)

        await self.spin(cnt + 1)

    def calc_multiplier(self) -> float:
        cnts: list[int] = [0] * 9  # Emoji counts
        for reel in self.reels:
            cnts[reel.value-1] += 1

        if cnts[3] == 2 and cnts[2] == 1:  # 2 fungi 1 cherry
            return 2
        if cnts[4] == 2 and (cnts[2] == 1 or cnts[3] == 1):  # 2 graga, 1 cherry/fungus
            return 1

        mult: float = 0.0

        mult += cnts[1] * 4/9 - cnts[0] * 1/3  # Proverka and skulls
        mult += 1 if (cnts[2] == 2) else 2.5 if (cnts[2] == 3) else 0  # Cherries
        mult += 1.5 if (cnts[3] == 2) else 3 if (cnts[3] == 3) else 0  # Fungi
        mult += 0.5 if (cnts[4] == 2) else 2.5 if (cnts[4] == 3) else 0  # Graga
        mult += 1 if (cnts[5] == 1) else 3 if (cnts[5] == 2) else 10 if (cnts[5] == 3) else 0  # Esq. Grugans
        mult += 1 if (cnts[6] == 1) else 2 if (cnts[6] == 2) else 10 if (cnts[6] == 3) else 0  # Bulborbs
        mult += 3 if (cnts[7] == 1) else 10 if (cnts[7] == 2) else 1000 if (cnts[7] == 3) else 0  # Nuclear bulborbs

        return mult

    @discord.ui.button(label="Сыграть снова")
    async def play_again_btn(self, interaction: discord.Interaction, btn: discord.ui.Button) -> None:
        if interaction.user.id != self.player_userid:
            await interaction.response.send_message("Не твоя игра сучк", ephemeral=True)
        elif self.reels[2] == _Reel.SPINNING:
            await interaction.response.send_message("Подожди, пока слоты докрутятся", ephemeral=True)
        elif self.player_token_info[0] >= self.bet:
            btn.disabled = True
            await interaction.response.defer()
            self.stop()

            new_view: View = View(self.bet, self.player_userid, self.player_token_info)
            msg: discord.Message = await self.msg.channel.send(str(new_view), view=new_view)
            await new_view.set_msg_and_spin(msg)
        else:
            btn.disabled = True
            await interaction.response.send_message(":prohibited: Недостаточно токенов!", ephemeral=True)
            self.stop()


if __name__ == "__main__":
    print("George Droid Slots Testing Mode Activated")

    class View_Test(View):
        def __init__(self, bet):
            self.bet = bet
            self.reels = [_Reel.get_random(), _Reel.get_random(), _Reel.get_random()]
            self.winnings = max(round(self.bet * self.calc_multiplier()), 0)
    
    n = 100000
    bet = 10000
    winnings = []
    total = 0
    wins_cnt = 0
    ties_cnt = 0
    for _ in range(n):
        view = View_Test(bet)
        winnings.append(view.winnings)
        total += view.winnings
        if view.winnings > bet:
            wins_cnt += 1
        elif view.winnings == bet:
            ties_cnt += 1
    winnings.sort()
    total
    print(f"for {n} games with a bet of {bet}:\naverage: {total/n}\nmedian: {winnings[n//2]}\nchance to win: {wins_cnt/n*100}%\nchance of a tie: {ties_cnt/n*100}%")
