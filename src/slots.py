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
            counts=[15, 35, 10, 10, 15, 9, 5, 1]
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
        reels_sorted_vals: list[int] = sorted(list(map(lambda x: x.value, self.reels)))
        mult: float = 0.0

        for elem in reels_sorted_vals:
            match elem:
                case 1:
                    mult -= 1/3
                case 2:
                    mult += 1/3

        match reels_sorted_vals:
            case [3, 3, 3]:
                mult += 1
            case [3, 3, 8]:
                mult += 4
            case [3, 3, 7] | [3, 3, 6]:
                mult += 2
            case [3, 3, x] | [x, 3, 3]:
                mult += 1

            case [4, 4, 4]:
                mult += 3
            case [3, 4, 4]:
                mult += 2
            case [4, 4, 8]:
                mult += 4
            case [4, 4, 7] | [4, 4, 6]:
                mult += 2
            case [4, 4, x] | [x, 4, 4]:
                mult += 1

            case [5, 5, 5]:
                mult += 1.5
            case [3, 5, 5] | [4, 5, 5]:
                mult += 1
            case [5, 5, 7] | [5, 5, 6]:
                mult += 1.5
            case [5, 5, 9]:
                mult += 4
            case [5, 5, x] | [x, 5, 5]:
                mult += 0.5

            case [6, 6, 6]:
                mult += 10
            case [6, 6, 8]:
                mult += 6
            case [6, 7, 8]:
                mult += 5
            case [6, 6, 7]:
                mult += 4
            case [6, 6, x] | [x, 6, 6]:
                mult += 3
            case [x, 6, 7] | [6, 7, x]:
                mult += 2
            case [x, y, 6] | [x, 6, y] | [6, x, y]:
                mult += 1

            case [7, 7, 7]:
                mult += 10
            case [7, 7, 8]:
                mult += 5
            case [6, 7, 7]:
                mult += 3
            case [7, 7, x] | [x, 7, 7]:
                mult += 2
            case [x, y, 7] | [x, 7, y] | [7, x, y]:
                mult += 1
            
            case [8, 8, 8]:
                mult += 1000
            case [7, 8, 8] | [6, 8, 8]:
                mult += 11
            case [x, 8, 8]:
                mult += 10
            case [x, y, 8]:
                mult += 3
        
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
    for _ in range(n):
        view = View_Test(bet)
        winnings.append(view.winnings)
        total += view.winnings
        if view.winnings >= bet:
            wins_cnt += 1
    winnings.sort()
    total
    print(f"for {n} games with a bet of {bet}:\naverage: {total/n}\nmedian: {winnings[n//2]}\nchance to win: {wins_cnt/n*100}%")
