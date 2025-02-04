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
            sorted_reels: list["_Reel"] = sorted(self.reels, key=lambda x: x.value)

            for elem in sorted_reels:
                match elem:
                    case _Reel.SKULL:
                        self.winnings -= self.bet / 3
                    case _Reel.PROVERKA:
                        self.winnings += self.bet / 3

            match sorted_reels:
                case [_Reel.CHERRIES, _Reel.CHERRIES, _Reel.CHERRIES]:
                    self.winnings += self.bet
                case [_Reel.CHERRIES, _Reel.CHERRIES, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 3.5
                case [_Reel.CHERRIES, _Reel.CHERRIES, _Reel.BULBORB] | [_Reel.CHERRIES, _Reel.CHERRIES, _Reel.ESQ_GRAGAS]:
                    self.winnings += self.bet * 1.5
                case [_Reel.CHERRIES, _Reel.CHERRIES, x] | [x, _Reel.CHERRIES, _Reel.CHERRIES]:
                    self.winnings += self.bet * 0.5

                case [_Reel.FUNGUS, _Reel.FUNGUS, _Reel.FUNGUS]:
                    self.winnings += self.bet * 3
                case [_Reel.CHERRIES, _Reel.FUNGUS, _Reel.FUNGUS]:
                    self.winnings += self.bet * 2
                case [_Reel.FUNGUS, _Reel.FUNGUS, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 3.5
                case [_Reel.FUNGUS, _Reel.FUNGUS, _Reel.BULBORB] | [_Reel.FUNGUS, _Reel.FUNGUS, _Reel.ESQ_GRAGAS]:
                    self.winnings += self.bet * 1.5
                case [_Reel.FUNGUS, _Reel.FUNGUS, x] | [x, _Reel.FUNGUS, _Reel.FUNGUS]:
                    self.winnings += self.bet * 0.5

                case [_Reel.GRAGAS, _Reel.GRAGAS, _Reel.GRAGAS]:
                    self.winnings += self.bet * 1.5
                case [_Reel.CHERRIES, _Reel.GRAGAS, _Reel.GRAGAS] | [_Reel.FUNGUS, _Reel.GRAGAS, _Reel.GRAGAS]:
                    self.winnings += self.bet
                case [_Reel.GRAGAS, _Reel.GRAGAS, x] | [x, _Reel.GRAGAS, _Reel.GRAGAS]:
                    self.winnings += self.bet * 0.5

                case [_Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS]:
                    self.winnings += self.bet * 10
                case [_Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 6
                case [_Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS, _Reel.BULBORB]:
                    self.winnings += self.bet * 4
                case [_Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS, x] | [x, _Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS]:
                    self.winnings += self.bet * 3
                case [x, y, _Reel.ESQ_GRAGAS] | [x, _Reel.ESQ_GRAGAS, y] | [_Reel.ESQ_GRAGAS, x, y]:
                    self.winnings += self.bet

                case [_Reel.BULBORB, _Reel.BULBORB, _Reel.BULBORB]:
                    self.winnings += self.bet * 10
                case [_Reel.BULBORB, _Reel.BULBORB, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 5
                case [_Reel.ESQ_GRAGAS, _Reel.BULBORB, _Reel.BULBORB]:
                    self.winnings += self.bet * 3
                case [_Reel.BULBORB, _Reel.BULBORB, x] | [x, _Reel.BULBORB, _Reel.BULBORB]:
                    self.winnings += self.bet * 2
                case [x, y, _Reel.BULBORB] | [x, _Reel.BULBORB, y] | [_Reel.BULBORB, x, y]:
                    self.winnings += self.bet
                
                case [_Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 1000
                case [_Reel.BULBORB, _Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB] | [_Reel.ESQ_GRAGAS, _Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 11
                case [x, _Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 10
                case [x, y, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 3

            self.winnings = max(round(self.winnings), 0)
            self.player_token_info[0] += int(self.winnings)

            await self.msg.edit(content=str(self), view=self)
            return
        
        await asyncio.sleep(0.5)

        self.reels[cnt] = _Reel.get_random()

        await self.msg.edit(content=str(self), view=self)

        await self.spin(cnt + 1)

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

    class View_Test():
        def __init__(self, bet):
            self.bet = bet
            self.winnings = 0.0
            self.reels = [_Reel.get_random(), _Reel.get_random(), _Reel.get_random()]

            sorted_reels: list["_Reel"] = sorted(self.reels, key=lambda x: x.value)

            for elem in sorted_reels:
                match elem:
                    case _Reel.SKULL:
                        self.winnings -= self.bet / 3
                    case _Reel.PROVERKA:
                        self.winnings += self.bet / 3

            match sorted_reels:
                case [_Reel.CHERRIES, _Reel.CHERRIES, _Reel.CHERRIES]:
                    self.winnings += self.bet
                case [_Reel.CHERRIES, _Reel.CHERRIES, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 3.5
                case [_Reel.CHERRIES, _Reel.CHERRIES, _Reel.BULBORB] | [_Reel.CHERRIES, _Reel.CHERRIES, _Reel.ESQ_GRAGAS]:
                    self.winnings += self.bet * 1.5
                case [_Reel.CHERRIES, _Reel.CHERRIES, x] | [x, _Reel.CHERRIES, _Reel.CHERRIES]:
                    self.winnings += self.bet * 0.5

                case [_Reel.FUNGUS, _Reel.FUNGUS, _Reel.FUNGUS]:
                    self.winnings += self.bet * 3
                case [_Reel.CHERRIES, _Reel.FUNGUS, _Reel.FUNGUS]:
                    self.winnings += self.bet * 2
                case [_Reel.FUNGUS, _Reel.FUNGUS, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 3.5
                case [_Reel.FUNGUS, _Reel.FUNGUS, _Reel.BULBORB] | [_Reel.FUNGUS, _Reel.FUNGUS, _Reel.ESQ_GRAGAS]:
                    self.winnings += self.bet * 1.5
                case [_Reel.FUNGUS, _Reel.FUNGUS, x] | [x, _Reel.FUNGUS, _Reel.FUNGUS]:
                    self.winnings += self.bet * 0.5

                case [_Reel.GRAGAS, _Reel.GRAGAS, _Reel.GRAGAS]:
                    self.winnings += self.bet * 1.5
                case [_Reel.CHERRIES, _Reel.GRAGAS, _Reel.GRAGAS] | [_Reel.FUNGUS, _Reel.GRAGAS, _Reel.GRAGAS]:
                    self.winnings += self.bet
                case [_Reel.GRAGAS, _Reel.GRAGAS, x] | [x, _Reel.GRAGAS, _Reel.GRAGAS]:
                    self.winnings += self.bet * 0.5

                case [_Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS]:
                    self.winnings += self.bet * 10
                case [_Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 6
                case [_Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS, _Reel.BULBORB]:
                    self.winnings += self.bet * 4
                case [_Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS, x] | [x, _Reel.ESQ_GRAGAS, _Reel.ESQ_GRAGAS]:
                    self.winnings += self.bet * 3
                case [x, y, _Reel.ESQ_GRAGAS] | [x, _Reel.ESQ_GRAGAS, y] | [_Reel.ESQ_GRAGAS, x, y]:
                    self.winnings += self.bet

                case [_Reel.BULBORB, _Reel.BULBORB, _Reel.BULBORB]:
                    self.winnings += self.bet * 10
                case [_Reel.BULBORB, _Reel.BULBORB, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 5
                case [_Reel.ESQ_GRAGAS, _Reel.BULBORB, _Reel.BULBORB]:
                    self.winnings += self.bet * 3
                case [_Reel.BULBORB, _Reel.BULBORB, x] | [x, _Reel.BULBORB, _Reel.BULBORB]:
                    self.winnings += self.bet * 2
                case [x, y, _Reel.BULBORB] | [x, _Reel.BULBORB, y] | [_Reel.BULBORB, x, y]:
                    self.winnings += self.bet
                
                case [_Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 1000
                case [_Reel.BULBORB, _Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB] | [_Reel.ESQ_GRAGAS, _Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 101
                case [x, _Reel.NUCLEAR_BULBORB, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 100
                case [x, y, _Reel.NUCLEAR_BULBORB]:
                    self.winnings += self.bet * 3

            self.winnings = max(round(self.winnings), 0)
    
    n = 100000
    bet = 10000
    winnings = []
    total = 0
    for _ in range(n):
        view = View_Test(bet)
        winnings.append(view.winnings)
        total += view.winnings
    winnings.sort()
    total
    print(f"for {n} games with a bet of {bet}:\naverage:{total/n}\nmedian:{winnings[n//2]}")
