import discord
import asyncio

from enum import Enum
import random


_REEL_EMOJIS: tuple = (
    ":skull:", "<:proverka:1307010119824965723>", ":cherries:", ":mushroom:",
    "<:gragas:1336062411970580511>", "<:esq_gragas:1336062410041196646>",
    "<:bulborb:1336061550498287616>", "<:nuclear_bulborb:1336061387847372830>",
    ":star:", ":egg:", "<a:slots:1336120636635873390>"
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
    STAR = 9
    EGG = 10
    SPINNING = 11

    def to_emoji(self) -> str:
        return _REEL_EMOJIS[self.value - 1]

    @classmethod
    def get_random(cls) -> "_Reel":
        return cls(random.sample(
            population=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            k=1,
            counts=[20, 33, 10, 10, 15, 9, 5, 1, 30, 25]
        )[0])


_PIROTS_EMOJIS: tuple = (
    ":bird:", ":black_bird:", ":baby_chick:",
    ":red_square:", ":white_square_button:", ":yellow_square:", ":star2:", ":wing:",
    ":red_square:", ":white_square_button:", ":yellow_square:", ":star2:", ":wing:",
    ":black_large_square:", ":rock:"
)


_PIROTS_WEIGHTS: tuple = (27, 30, 33, 9, 2, 7)


class _Pirots(Enum):
    RED_BIRD = 1
    BLACK_BIRD = 2
    YELLOW_BIRD = 3
    RED_GEM = 4
    BLACK_GEM = 5
    YELLOW_GEM = 6
    STAR = 7
    WING = 8
    RED_GEM_CLAIMED = 9
    BLACK_GEM_CLAIMED = 10
    YELLOW_GEM_CLAIMED = 11
    STAR_CLAIMED = 12
    WING_CLAIMED = 13
    EMPTY = 14
    ROCK = 15

    def to_emoji(self) -> str:
        return _PIROTS_EMOJIS[self.value - 1]

    @classmethod
    def get_random_gem(cls) -> "_Pirots":
        return random.choices(
            population=[cls.RED_GEM, cls.BLACK_GEM, cls.YELLOW_GEM, cls.STAR, cls.WING, cls.ROCK],
            weights=_PIROTS_WEIGHTS,
            k=1
        )[0]
    
    @classmethod
    def get_random_board(cls) -> list[list["_Pirots"]]:
        random_gems = random.choices(
            population=[cls.RED_GEM, cls.BLACK_GEM, cls.YELLOW_GEM, cls.STAR, cls.WING, cls.ROCK],
            weights=_PIROTS_WEIGHTS,
            k=25
        )

        random_board = [[random_gems[x*5+y] for x in range(5)] for y in range(5)]

        birds_pos = [(x, y) for x in range(5) for y in range(5)]
        random.shuffle(birds_pos)

        random_board[birds_pos[0][0]][birds_pos[0][1]] = _Pirots.RED_BIRD
        random_board[birds_pos[1][0]][birds_pos[1][1]] = _Pirots.BLACK_BIRD
        random_board[birds_pos[2][0]][birds_pos[2][1]] = _Pirots.YELLOW_BIRD

        return random_board


class View(discord.ui.View):
    bet: int
    player_userid: int
    player_token_info: list[int]
    msg: discord.Message

    reels: list[_Reel]  # 3x1
    pirots_reels: list[list[_Pirots]]  # 5x5

    bonus_spins: int
    pirots_spins: int

    winnings: float
    pirots_winnings: float
    total_winnings: float

    is_bonus: bool
    is_pirots: bool

    pirots_notification_msg: str
    pirots_notification_row: int

    saved_bonus_spins: int
    saved_bonus_winnings: float

    def __init__(self, bet: int, userid: int, token_info: list[int]):
        super().__init__(timeout=30)
        self.bet = bet
        self.player_userid: int = userid
        self.player_token_info = token_info

        self.reels = [_Reel.SPINNING, _Reel.SPINNING, _Reel.SPINNING]
        self.pirots_reels = [[_Reel.SPINNING for _ in range(5)] for _ in range(5)]

        self.bonus_spins = 0
        self.pirots_spins = 0

        self.winnings = 0.0
        self.pirots_winnings = 0.0
        self.total_winnings = 0.0

        self.is_bonus = False
        self.is_pirots = False

        self.pirots_notification_msg = ""
        self.pirots_notification_row = 0

        self.saved_bonus_spins = 0
        self.saved_bonus_winnings = 0.0

        self.player_token_info[0] -= self.bet

    def __str__(self) -> str:
        s: str = f"<@{self.player_userid}> | :coin: Ставка: `{self.bet}`\n"

        if self.is_pirots:
            # 5x5
            for i, row in enumerate(self.pirots_reels):
                s += "> " + "".join(reel.to_emoji() for reel in row)
                if i == self.pirots_notification_row:
                    s += f"  {self.pirots_notification_msg}"
                s += "\n"

            s += "\n**:pirate_flag: Бонусная игра с птичками!**\n"

            if self.pirots_spins > 0:
                s += f"Птички улетят через `{self.pirots_spins}` спинов :wing:"
            else:
                s += "Птички улетели :wing:"
        else:
            # 3x1
            s += "> " + " ".join(reel.to_emoji() for reel in self.reels)

        if self.is_bonus:
            s += f"  +{int(self.winnings)} :coin:"
            s += f"\n\n<:Screenshot:1278850856711880787> Бонусная игра!\n"
            s += f"Слот закончится через `{self.bonus_spins}` спинов"

        winnings = max(self.winnings, self.total_winnings)
        s += f"\n\n**Навар: +{int(winnings)} :coin:**"

        return s

    async def pirots_reset_board(self) -> None:
        new_board = _Pirots.get_random_board()

        # Reveal the board
        self.pirots_reels = [[_Reel.SPINNING for _ in range(5)] for _ in range(5)]
        for x in range(5):
            await self.msg.edit(content=str(self), view=self)
            await asyncio.sleep(0.5)

            for y in range(5):
                self.pirots_reels[y][x] = new_board[y][x]

    async def pirots_move_birds(self) -> None:
        moved: bool = False

        for x in range(5):
            for y in range(5):
                cell: _Pirots = self.pirots_reels[x][y]
                if cell in [_Pirots.RED_BIRD, _Pirots.BLACK_BIRD, _Pirots.YELLOW_BIRD]:
                    cluster: list[tuple[int, int]] = self.pirots_map_gem_cluster(
                        target_gem=_Pirots(cell.value + 3),
                        bird_position=(x, y),
                        cluster=list()
                    )
                    
                    for i in range(1, len(cluster)):
                        gem = cluster[i]
                        claimed_cell = self.pirots_reels[gem[0]][gem[1]]
                        self.pirots_reels[gem[0]][gem[1]] = cell

                        prev_position = cluster[i-1]
                        self.pirots_reels[prev_position[0]][prev_position[1]] = _Pirots.EMPTY

                        match claimed_cell:
                            case _Pirots.STAR_CLAIMED:
                                self.total_winnings += self.bet * 1/3
                                self.pirots_winnings += self.bet * 1/3
                                self.pirots_notification_msg = f"**+{int(self.bet * 1/3)} :coin:**"
                                self.pirots_notification_row = gem[0]
                            
                            case _Pirots.WING_CLAIMED:
                                self.total_winnings += self.bet
                                self.pirots_winnings += self.bet
                                self.pirots_spins += 1
                                self.pirots_notification_msg = "**+ФРИСПИН**"
                                self.pirots_notification_row = gem[0]

                            case _:
                                self.total_winnings += self.bet * 0.125
                                self.pirots_winnings += self.bet * 0.125
                        
                        moved = True

                        await self.msg.edit(content=str(self), view=self)
                        self.pirots_notification_msg = ""
                        self.pirots_notification_row = 0
                        await asyncio.sleep(0.5)

        if moved:
            self.pirots_move_empty_cells_up()
            await self.msg.edit(content=str(self), view=self)
            await asyncio.sleep(0.5)

            self.pirots_fill_empty_cells()
            await self.msg.edit(content=str(self), view=self)
            await asyncio.sleep(0.5)

            await self.pirots_move_birds()

    def pirots_map_gem_cluster(
            self,
            target_gem: _Pirots,
            bird_position: tuple[int, int],
            cluster: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        if len(cluster) == 0:
            cluster.append(bird_position)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            nx = bird_position[0] + dx
            ny = bird_position[1] + dy

            if (0 <= nx < 5) and (0 <= ny < 5) and (self.pirots_reels[nx][ny] in [target_gem, _Pirots.STAR, _Pirots.WING]):
                cluster.append((nx, ny))
                self.pirots_reels[nx][ny] = _Pirots(self.pirots_reels[nx][ny].value + 5)
                self.pirots_map_gem_cluster(target_gem, (nx, ny), cluster)

        return cluster

    def pirots_move_empty_cells_up(self) -> None:
        for x in range(5):
            free_cells = []
            for y in range(4, -1, -1):
                if self.pirots_reels[y][x] == _Pirots.EMPTY:
                    free_cells.append(y)
                elif len(free_cells) > 0:
                    self.pirots_reels[free_cells[0]][x] = self.pirots_reels[y][x]
                    free_cells.pop(0)
                    self.pirots_reels[y][x] = _Pirots.EMPTY
                    free_cells.append(y)
    
    def pirots_fill_empty_cells(self) -> None:
        for y in range(5):
            for x in range (5):
                if self.pirots_reels[y][x] == _Pirots.EMPTY:
                    self.pirots_reels[y][x] = _Pirots.get_random_gem()

    async def set_msg_and_spin(self, msg: discord.Message) -> None:
        self.msg = msg
        await self.spin()

    async def spin(self, cnt: int = 0) -> None:
        if self.is_pirots:
            return await self.spin_pirots()

        elif self.is_bonus:
            return await self.spin_bonus(cnt)

        if cnt == 3:
            self.player_token_info[0] += int(self.winnings)

            if self.reels == [_Reel.STAR, _Reel.STAR, _Reel.STAR]:
                self.is_bonus = True
                self.bonus_spins = 4
            elif self.reels == [_Reel.EGG, _Reel.EGG, _Reel.EGG]:
                self.is_pirots = True
                self.pirots_winnings = 0.0
                self.pirots_spins = 3

            await self.msg.edit(content=str(self), view=self)

            if self.is_bonus or self.is_pirots:
                self.reels = [_Reel.SPINNING, _Reel.SPINNING, _Reel.SPINNING]
                await asyncio.sleep(0.5)
                return await self.spin(0)

            return

        await asyncio.sleep(0.5)

        is_two_stars: bool = self.reels[0] == self.reels[1] == _Reel.STAR
        is_two_eggs: bool = self.reels[0] == self.reels[1] == _Reel.EGG

        if (is_two_stars or is_two_eggs) and random.random() < 0.4:
            self.reels[2] = self.reels[1]
        else:
            self.reels[cnt] = _Reel.get_random()

        self.winnings = max(round(self.bet * self.calc_multiplier()), 0)

        await self.msg.edit(content=str(self), view=self)
        await self.spin(cnt + 1)
    
    async def spin_pirots(self) -> None:
        if self.pirots_spins <= 0:
            self.is_pirots = False
            self.player_token_info[0] += int(self.pirots_winnings)

            if self.saved_bonus_spins > 0:
                self.is_bonus = True
                self.bonus_spins = self.saved_bonus_spins
                self.total_winnings += self.saved_bonus_winnings
                self.saved_bonus_spins = 0
                self.saved_bonus_winnings = 0.0

                self.reels = [_Reel.SPINNING, _Reel.SPINNING, _Reel.SPINNING]
                await self.msg.edit(content=str(self), view=self)
                await asyncio.sleep(1)
                await self.spin(0)

            return

        await self.pirots_reset_board()
        await asyncio.sleep(0.5)
        await self.pirots_move_birds()

        self.pirots_spins -= 1
        await self.msg.edit(content=str(self), view=self)
        return await self.spin()
    
    async def spin_bonus(self, cnt: int) -> None:
        if cnt == 3:
            self.total_winnings += self.winnings

            if self.reels == [_Reel.EGG, _Reel.EGG, _Reel.EGG]:
                self.saved_bonus_spins = self.bonus_spins
                self.saved_bonus_winnings = self.total_winnings
                self.is_bonus = False

                self.is_pirots = True
                self.pirots_winnings = 0.0
                self.pirots_spins = 3

                return await self.spin(0)

            if self.reels == [_Reel.STAR, _Reel.STAR, _Reel.STAR]:
                self.bonus_spins += 4
            self.bonus_spins -= 1

            if self.bonus_spins < 0:
                self.is_bonus = False
                self.player_token_info[0] += int(self.total_winnings)
                await self.msg.edit(content=str(self), view=self)
                return

            self.reels = [_Reel.SPINNING, _Reel.SPINNING, _Reel.SPINNING]
            await asyncio.sleep(0.5)
            return await self.spin(0)

        await asyncio.sleep(0.5)

        is_two_stars: bool = self.reels[0] == self.reels[1] == _Reel.STAR
        is_two_eggs: bool = self.reels[0] == self.reels[1] == _Reel.EGG

        if (is_two_stars or is_two_eggs) and random.random() < 0.4:
            self.reels[2] = self.reels[1]
        else:
            self.reels[cnt] = _Reel.get_random()

        self.winnings = max(round(self.bet * self.calc_multiplier()), 0)

        await self.msg.edit(content=str(self), view=self)
        return await self.spin(cnt + 1)

    def calc_multiplier(self) -> float:
        cnts: list[int] = [0] * 11  # Emoji counts
        for reel in self.reels:
            cnts[reel.value - 1] += 1

        if cnts[3] == 2 and cnts[2] == 1:  # 2 fungi 1 cherry
            return 2
        if cnts[4] == 2 and (cnts[2] == 1 or cnts[3] == 1):  # 2 graga, 1 cherry/fungus
            return 1

        mult: float = 0.0

        mult += cnts[1] * 1/3 - cnts[0] * 1/3 + cnts[8] * 1/4 + cnts[9] * 1/4  # Proverka, skulls, stars, and eggs
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
        elif (not self.is_bonus and not self.is_pirots and any(reel == _Reel.SPINNING for reel in self.reels)) or \
                (self.is_pirots and any(reel == _Reel.SPINNING for row in self.pirots_reels for reel in row)):
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
