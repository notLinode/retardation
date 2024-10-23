import discord

import asyncio
from enum import Enum
import random

CARD_EMOJIS: tuple[str] = (
    "<:Ace:1297849594398642256>",   "<:Two:1297849617165320245>",   "<:Three:1297849668411199560>",
    "<:Four:1297849599876137011>",  "<:Five:1297849598249009214>",  "<:Six:1297849611041509466>",
    "<:Seven:1297849609216987136>", "<:Eight:1297849596130627655>", "<:Nine:1297849605379325982>",
    "<:Ten:1297849612962496512>",   "<:Jack:1297849601663041579>",  "<:Queen:1297849607212236830>",
    "<:King:1297849603563196417>"
)
 
class Card(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

    def to_emoji(self) -> str:
        return CARD_EMOJIS[self.value-1]

def get_random_card() -> Card:
    return Card(int(random.random() * 13) + 1)

class Game():
    class State(Enum):
        PLAYER_DRAWING = 1
        CAN_DOUBLE_DOWN = 2
        CAN_SPLIT = 3
        DEALER_DRAWING = 4
        LOSE = 5
        WIN = 6
        TIE = 7

    state: State
    move_num: int

    bet: int
    token_info: list[int]
    
    player_hand: list[Card]
    dealer_hand: list[Card]

    def __init__(self, bet: int, token_info: list[int]) -> None:
        token_info[0] -= bet

        self.player_hand = []
        self.dealer_hand = []

        for _ in range(2):
            self.player_hand.append(get_random_card())
        
        self.dealer_hand.append(get_random_card())
        
        self.move_num = 1
        self.bet = bet
        self.token_info = token_info

        self.state = self.State.WIN if self.get_hand_score(self.player_hand) == 21 else self.State.PLAYER_DRAWING
        self.determine_state()
    
    def determine_state(self) -> State:
        player_score = self.get_hand_score(self.player_hand)
        dealer_score = self.get_hand_score(self.dealer_hand)

        if player_score > 21:
            self.state = self.State.LOSE
            return self.state
        
        if dealer_score > 21:
            self.state = self.State.WIN
            return self.state
        
        if self.state == self.State.DEALER_DRAWING:
            self.state = self.State.WIN if player_score > dealer_score else (
            self.State.LOSE if player_score < dealer_score else self.State.TIE
            )
            return self.state
        
        has_enough_money: bool = self.bet <= self.token_info[0]
        is_first_move: bool = self.move_num == 1

        if len(self.player_hand) == 2 and is_first_move:
            has_two_of_same: bool = min(self.player_hand[0].value, 10) == min(self.player_hand[1].value, 10)
            if has_two_of_same and has_enough_money:
                self.state = self.State.CAN_SPLIT
                return self.state
        
        if is_first_move and has_enough_money:
            self.state = self.State.CAN_DOUBLE_DOWN
            return self.state
        
        if self.state != self.State.DEALER_DRAWING:
            self.state = self.State.PLAYER_DRAWING
            return self.state
    
    def get_hand_score(self, hand: list[Card]) -> int:
        score: int = 0
        aces: int = 0
        
        for card in hand:
            match card:
                case Card.ACE:
                    score += 11
                    aces = -~aces
                case _:
                    score += min(card.value, 10)
        
        while aces:
            if score > 21:
                score -= 10
            aces = ~-aces

        return score
    
    async def hit(self) -> None:
        if self.determine_state() not in [self.State.PLAYER_DRAWING, self.State.CAN_DOUBLE_DOWN, self.State.CAN_SPLIT]:
            return
        
        self.player_hand.append(get_random_card())
        self.move_num += 1

        self.determine_state()
    
    async def double(self) -> None:
        if self.determine_state() not in [self.State.CAN_DOUBLE_DOWN, self.State.CAN_SPLIT]:
            return
        
        self.player_hand.append(get_random_card())
        self.move_num += 1
        self.token_info[0] -= self.bet
        self.bet *= 2

    async def stand(self) -> None:
        if self.determine_state() not in [self.State.PLAYER_DRAWING, self.State.CAN_DOUBLE_DOWN, self.State.CAN_SPLIT]:
            return

    async def dealer_draw(self) -> None:
        self.state = self.State.DEALER_DRAWING

        while self.get_hand_score(self.dealer_hand) < 17:
            self.dealer_hand.append(get_random_card())
        
        await self.give_winnings()
    
    async def give_winnings(self) -> None:
        match self.determine_state():
            case self.State.WIN:
                self.token_info[0] += self.bet * 2
            case self.State.LOSE:
                pass
            case self.State.TIE:
                self.token_info[0] += self.bet

class GameManager():
    player_userid: int
    player_name: str
    state: Game.State
    cur_game: Game
    split_game: Game | None
    is_split: bool
    
    def __init__(self, bet: int, token_info: list[str], user: discord.User) -> None:
        self.cur_game = Game(bet, token_info)
        self.player_userid = user.id
        self.player_name = user.name
        self.state = self.cur_game.state
        self.split_game = None
        self.is_split = False

    def get_hand_score(self, hand: list[Card]) -> int:
        return self.cur_game.get_hand_score(hand)

    async def hit(self) -> None:
        await self.cur_game.hit()
        self.state = self.cur_game.state

        is_game_end: bool = self.state in [Game.State.WIN, Game.State.LOSE, Game.State.TIE]
        if self.is_split and is_game_end:
            self.cur_game, self.split_game = self.split_game, self.cur_game
            self.split_game.state = Game.State.DEALER_DRAWING
            self.is_split = False
            self.state = self.cur_game.state
            return
        
        if self.split_game is not None and is_game_end:
            self.state = self.cur_game.state = Game.State.DEALER_DRAWING
            await self.cur_game.dealer_draw()
            await self.split_game.give_winnings()

    async def stand(self) -> None:
        await self.cur_game.stand()
        self.state = self.cur_game.state

        if self.is_split:
            self.cur_game, self.split_game = self.split_game, self.cur_game
            self.split_game.state = Game.State.DEALER_DRAWING
            self.is_split = False
            return
        
        await self.cur_game.dealer_draw()
        self.state = self.cur_game.state

        if self.split_game != None:
            await self.split_game.give_winnings()
    
    async def double(self) -> None:
        await self.cur_game.double()
        self.state = self.cur_game.state

        if self.is_split:
            self.cur_game, self.split_game = self.split_game, self.cur_game
            self.split_game.state = Game.State.DEALER_DRAWING
            self.is_split = False
            return
        
        await self.cur_game.dealer_draw()
        self.state = self.cur_game.state

        if self.split_game != None:
            await self.split_game.give_winnings()
    
    async def split(self) -> None:
        if self.cur_game.determine_state() != Game.State.CAN_SPLIT:
            return

        self.split_game = Game(self.cur_game.bet, self.cur_game.token_info)
        self.split_game.player_hand = [self.cur_game.player_hand.pop()]
        self.split_game.dealer_hand = self.cur_game.dealer_hand
        self.is_split = True
        self.state = self.cur_game.determine_state()
        self.split_game.determine_state()
    
    def hand_to_emojis(self, hand: list[Card]) -> str:
        return ''.join([card.to_emoji() for card in hand])
    
    def get_game_ending_str(self, state: Game.State, bet: int) -> str:
        match state:
            case Game.State.WIN:
                return f"**Победа!!! +{bet * 2} :coin:**\n\n"
            case Game.State.LOSE:
                return "**Проигрыш...**\n\n"
            case Game.State.TIE:
                return f"**Ничья?? +{bet} :coin:**\n\n"
            case _:
                return "\n"

    def __str__(self) -> str:
        s: str = f":coin: Ваши токены: `{self.cur_game.token_info[0]}`{'. Ставка: `'+str(self.cur_game.bet)+'`' if self.split_game == None else ''}\n\n"

        dealer_hand_emojis: str = self.hand_to_emojis(self.cur_game.dealer_hand)
        s += f"Дилер:\n`{self.get_hand_score(self.cur_game.dealer_hand)}` | {dealer_hand_emojis}\n\n"

        player_hand_emojis: str = self.hand_to_emojis(self.cur_game.player_hand)
        if self.split_game == None:
            s += f"{self.player_name}:\n`{self.get_hand_score(self.cur_game.player_hand)}` | {player_hand_emojis}\n\n"
            s += self.get_game_ending_str(self.state, self.cur_game.bet)
        else:
            split_hand_emojis: str = self.hand_to_emojis(self.split_game.player_hand)
            if self.is_split:
                first_game: Game = self.cur_game
                first_hand_emojis: str = player_hand_emojis
                second_game: Game = self.split_game
                second_hand_emojis: str = split_hand_emojis
            else:
                first_game: Game = self.split_game
                first_hand_emojis: str = split_hand_emojis
                second_game: Game = self.cur_game
                second_hand_emojis: str = player_hand_emojis
            s += f"{'▶️ ' if self.is_split else ''}{self.player_name} (Рука 1, ставка: `{first_game.bet}`):\n`{self.get_hand_score(first_game.player_hand)}` | {first_hand_emojis}\n"
            s += f"State: `{first_game.state}`\n"
            s += self.get_game_ending_str(first_game.state, first_game.bet)
            s += f"{'▶️ ' if not self.is_split else ''}{self.player_name} (Рука 2, ставка: `{second_game.bet}`):\n`{self.get_hand_score(second_game.player_hand)}` | {second_hand_emojis}\n"
            s += f"State: `{second_game.state}`\n"
            s += self.get_game_ending_str(second_game.state, second_game.bet)
            s += f"\nManager state: `{self.state}`"

        return s
    
class Button(discord.ui.Button["View"]):
    def __init__(self, label: str, style: discord.ButtonStyle) -> None:
        super().__init__(label=label, style=style)

    async def interaction_check(self, interaction: discord.Interaction["View"]) -> bool:
        is_wrong_user: bool = interaction.user.id != self.view.manager.player_userid
        if is_wrong_user:
            await interaction.response.send_message("Это не твоя игра.", ephemeral=True)

        return not is_wrong_user
    
    async def callback(self, interaction: discord.Interaction["View"]) -> None:
        manager: GameManager = self.view.manager

        for button in self.view.children:
            if isinstance(button, DoubleButton):
                button.disabled = manager.state not in [Game.State.CAN_DOUBLE_DOWN, Game.State.CAN_SPLIT]
            elif isinstance(button, SplitButton):
                button.disabled = manager.state != Game.State.CAN_SPLIT

        if manager.state in [Game.State.WIN, Game.State.LOSE, Game.State.TIE]:
            self.view.stop()
        
        await interaction.response.edit_message(content=str(manager), view=self.view)

class HitButton(Button):
    async def callback(self, interaction: discord.Interaction["View"]) -> None:
        await self.view.manager.hit()
        await super().callback(interaction)

class DoubleButton(Button):
    def __init__(self, label: str, style: discord.ButtonStyle, can_double: bool) -> None:
        super().__init__(label, style)
        self.disabled = not can_double

    async def callback(self, interaction: discord.Interaction["View"]) -> None:
        await self.view.manager.double()
        await super().callback(interaction)

class SplitButton(Button):
    def __init__(self, label: str, style: discord.ButtonStyle, can_split: bool) -> None:
        super().__init__(label, style)
        self.disabled = not can_split

    async def callback(self, interaction: discord.Interaction["View"]) -> None:
        await self.view.manager.split()
        await super().callback(interaction)

class StandButton(Button):
    async def callback(self, interaction: discord.Interaction["View"]) -> None:
        await self.view.manager.stand()
        await super().callback(interaction)

class View(discord.ui.View):
    children: list[Button]
    manager: GameManager

    def __init__(self, manager: GameManager):
        super().__init__()

        self.manager = manager

        self.add_item(HitButton("Hit", discord.ButtonStyle.primary))

        can_double: bool = self.manager.state in [Game.State.CAN_DOUBLE_DOWN, Game.State.CAN_SPLIT]
        self.add_item(DoubleButton("Double", discord.ButtonStyle.danger, can_double))

        can_split: bool = self.manager.state == Game.State.CAN_SPLIT
        self.add_item(SplitButton("Split", discord.ButtonStyle.success, can_split))

        self.add_item(StandButton("Stand", discord.ButtonStyle.secondary))
    
    def stop(self) -> None:
        for button in self.children:
            button.disabled = True
        super().stop()
