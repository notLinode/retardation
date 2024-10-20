from discord import Message, Client, TextChannel

import time
import random
import re

from bot_variables import *
import get_ai_response as ai
from shop_buttons_view import *

async def prompt(message: Message, AKASH_API_KEY: str) -> None:
    async with message.channel.typing():
        bot_msg: Message = await message.channel.send("✅\n")
        chunk_buf: str = ""
        chunk_buf_len: int = 0

        for chunk in ai.stream_response(AKASH_API_KEY, message.content[8:]):
            if chunk is None:
                break

            chunk_buf += chunk
            chunk_buf_len += len(chunk)

            if chunk_buf_len >= 200:
                bot_msg = await bot_msg.edit(content=bot_msg.content + chunk_buf)
                chunk_buf = ""
                chunk_buf_len = 0

        if chunk_buf:
            await bot_msg.edit(content=bot_msg.content + chunk_buf)

async def set_message_interval(message: Message, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        interval_str: str = message.content[22:].lower()
        
        if not interval_str.isnumeric() and interval_str != "random":
            await message.channel.send(f":prohibited: Неправильное значение интервала между сообщениями бота. Значение должно быть либо числом от `{bot_vars.SETTING_MESSAGE_INTERVAL_MIN}` до `{bot_vars.SETTING_MESSAGE_INTERVAL_MAX}`, либо `random`.")
            return

        if interval_str == "random":
            bot_vars.setting_message_interval_is_random = True
            bot_vars.message_interval_random = int(random.random() * 10) + 1

            await message.channel.send(f":white_check_mark: Интервал между сообщениями бота будет случайным для каждого сообщения.")
            return
        
        interval: int = int(interval_str)

        is_interval_less_than_min: bool = interval < bot_vars.SETTING_MESSAGE_INTERVAL_MIN
        is_interval_more_than_max: bool = interval > bot_vars.SETTING_MESSAGE_INTERVAL_MAX
        if is_interval_less_than_min or is_interval_more_than_max:
            await message.channel.send(f":prohibited: Интервал между сообщениями бота должен быть от `{bot_vars.SETTING_MESSAGE_INTERVAL_MIN}` до `{bot_vars.SETTING_MESSAGE_INTERVAL_MAX}` сообщений. Вы попытались установить: `{interval}`.")
            return

        bot_vars.setting_message_interval = interval
        bot_vars.setting_message_interval_is_random = False
        
        await message.channel.send(f":white_check_mark: Интервал между сообщениями бота установлен на `{bot_vars.setting_message_interval}` пользовательских сообщений.")

async def set_own_message_memory(message: Message, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        memory: int = int(message.content[24:])

        is_memory_less_than_min: bool = memory < bot_vars.SETTING_OWN_MESSAGE_MEMORY_MIN
        is_memory_more_than_max: bool = memory > bot_vars.SETTING_OWN_MESSAGE_MEMORY_MAX
        if is_memory_less_than_min or is_memory_more_than_max:
            await message.channel.send(f":prohibited: Память собственных сообщений бота должна быть от `{bot_vars.SETTING_OWN_MESSAGE_MEMORY_MIN}` до `{bot_vars.SETTING_OWN_MESSAGE_MEMORY_MAX}` сообщений. Вы попытались установить: `{memory}`.")
            return

        bot_vars.setting_own_message_memory = memory

        await message.channel.send(f":white_check_mark: Память собственных сообщений бота установлена на `{bot_vars.setting_own_message_memory}` сообщений.")

async def clear_memory(message: Message, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        bot_vars.recent_messages.clear()
        bot_vars.stylized_bot_messages.clear()
        await message.channel.send(f":white_check_mark: я всё заббыл нахуй")

async def feed(message: Message, AKASH_API_KEY: str, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        if bot_vars.user_interaction_tokens[message.author.id][0] <= 0:
            await message.channel.send(":prohibited: У вас нет токенов взаимодействия. Они выдаются каждые 6 сообщений.")
            return
        bot_vars.user_interaction_tokens[message.author.id][0] -= 1
        
        food_item: str = message.content[6:]
        food_satiety: int = ai.generate_food_satiety(AKASH_API_KEY, food_item)
        bot_vars.add_satiety(float(food_satiety))

        response: str = f"вау мне дали **{food_item}** и я {'получил' if food_satiety >= 0 else 'потерял'} `{abs(food_satiety)}` сытости {':drooling_face::drooling_face:' if food_satiety >= 40 else ''}\n"
        item: ShopItem = ShopItem(food_item, food_satiety, 0, 0, 0, 0, 0, 0)
        response += ai.generate_feeding_comment(AKASH_API_KEY, item)

        await message.channel.send(response)

async def heal(message: Message, AKASH_API_KEY: str, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        if bot_vars.user_interaction_tokens[message.author.id][0] <= 0:
            await message.channel.send(":prohibited: У вас нет токенов взаимодействия. Они выдаются каждые 6 сообщений.")
            return
        bot_vars.user_interaction_tokens[message.author.id][0] -= 1

        item: str = message.content[6:]
        item_health: int = ai.generate_item_health(AKASH_API_KEY, item)
        bot_vars.add_health(float(item_health))

        response: str = f"меня подлечили с помощью **{item}** и я {'получил' if item_health >= 0 else 'нахуй потерял'} `{abs(item_health)}` здоровья {':heart:' if item_health >= 0 else ':broken_heart::broken_heart::broken_heart:'}\n"
        item_obj: ShopItem = ShopItem(item, 0, item_health, 0, 0, 0, 0, 0)
        response += ai.generate_feeding_comment(AKASH_API_KEY, item_obj)
        
        await message.channel.send(response)

async def clean_litter(message: Message, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        if bot_vars.litter_box_fullness > 0:
            bonus_tokens: int = bot_vars.litter_box_fullness // 10
            bot_vars.litter_box_fullness = 0
            bot_vars.user_interaction_tokens[message.author.id][0] += bonus_tokens
            await message.channel.send(f"лоток очищен :white_check_mark:\nВы получили {bonus_tokens} 🪙")
        else:   
            await message.channel.send("лоток уже чист....")

async def shop(message: Message, AKASH_API_KEY: str, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        if not bot_vars.get_shop_items_str():
            bot_vars.shop_items = ai.generate_shop_items(AKASH_API_KEY)
            
        await message.channel.send(bot_vars.get_shop_items_str(), view=ShopView(bot_vars))

async def buy(message: Message, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        item_idx_str: str = message.content[5:]

        if not item_idx_str.isnumeric():
            await message.channel.send(":prohibited: вы даун")
            return
        
        item_idx: int = int(item_idx_str) - 1
        await buy_item(item_idx, message.channel, message.author.id, bot_vars)

# Used by ShopButton
async def buy_item(idx: int, channel: TextChannel, userid: int, bot_vars: BotVariables) -> bool:
    async with channel.typing():
        item: ShopItem = bot_vars.shop_items[idx]
        
        if item.is_bought:
            await channel.send(f":prohibited: Эта вещь уже куплена, подождите обновления магазина.")
            return item.is_bought
        
        if bot_vars.user_interaction_tokens[userid][0] < item.cost:
            await channel.send(f":prohibited: У вас недостаточно токенов взаимодействия (у вас `{bot_vars.user_interaction_tokens[userid][0]}`). Они выдаются каждые 6 сообщений.")
            return item.is_bought
        
        bot_vars.user_interaction_tokens[userid][0] -= item.cost
        item.is_name_hidden = item.is_satiety_hidden = item.is_health_hidden = False
        response: str = f"<@{userid}>, вы успешно купили {item}\n"
        item.is_bought = True

        bot_vars.add_health(item.health)
        bot_vars.add_satiety(item.satiety)

        response += ai.generate_feeding_comment(bot_vars.ai_key, item)
        await channel.send(response)

    return item.is_bought

async def status(message: Message, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        bot_status: str = f":heart: Здоровье: `{int(bot_vars.health)}`\n"
        bot_status += f":meat_on_bone: Сытость: `{int(bot_vars.satiety)}`\n"
        bot_status += f":poop: Наполненность лотка: `{bot_vars.litter_box_fullness}`\n"
        bot_status += f":hourglass: Бот прожил: `{(int(time.time()) - bot_vars.CREATED_AT) // 3600}` часов\n\n"
        bot_status += f":coin: Ваши токены взаимодействия: `{bot_vars.user_interaction_tokens[message.author.id][0]}`"

        await message.channel.send(bot_status)

async def tokens(message: Message, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        await message.channel.send(f":coin: Ваши токены взаимодействия: `{bot_vars.user_interaction_tokens[message.author.id][0]}`")

async def help(message: Message) -> None:
    async with message.channel.typing():
        help_msg: str = "```"
        help_msg += "\n;prompt [Сообщение: str] - обратиться к Llama 3.1 405B.\n"
        help_msg += "\n;set-message-interval [Интервал: int | \"random\"] - поставить количество пользовательских сообщений, после которого бот сам что-то напишет.\n"
        help_msg += "\n;set-own-message-memory [Память: int] - поставить количество собственных сообщений бота, которые он запомнит и учтёт при написании следующего своего сообщения.\n"
        help_msg += "\n;clear-memory - Очищает память бота от своих и пользовательских сообщений.\n"
        help_msg += "\n;ping - pong.\n"
        help_msg += "\n------====* КОМАНДЫ УХОДА ЗА БОТОМ *====------\n"
        help_msg += "\n;status - Показывает состояние бота и количество ваших токенов.\n"
        help_msg += "\n;tokens - Показывает количество ваших токенов.\n"
        help_msg += "\n;shop - Показывает магазин. Магазин обновляется каждый час.\n"
        help_msg += "\n;buy [Номер: int] - Покупает вещь из магазина и даёт её боту.\n"
        help_msg += "\n;feed [Еда: str] - Кормит бота тем, что вы укажете в команде. Тратит 1 токен при использовании.\n"
        help_msg += "\n;heal [Лекарство: str] - Лечит бота тем, что вы укажете в команде. Тратит 1 токен при использовании.\n"
        help_msg += "\n;clean-litter - Очищает лоток бота. Тратит 1 токен при использовании.\n"
        help_msg += "```"

        await message.channel.send(help_msg)

async def process_tokens_info(message: Message, bot_vars: BotVariables) -> None:
    userid: int = message.author.id

    if userid not in bot_vars.user_interaction_tokens:
            bot_vars.user_interaction_tokens[userid] = [3, 5, int(time.time())]

    if message.author.bot:
        return

    if bot_vars.user_interaction_tokens[userid][1] <= 0:
        bot_vars.user_interaction_tokens[userid][1] = 5
        bot_vars.user_interaction_tokens[userid][0] += 1
        await message.add_reaction("🪙")
    else:
        bot_vars.user_interaction_tokens[userid][1] -= 1

    time_since_last_message: int = int(time.time()) - bot_vars.user_interaction_tokens[userid][2]
    if time_since_last_message >= 3600:
        bot_vars.user_interaction_tokens[userid][0] += min(3, time_since_last_message // 3600) # Can't earn more than 3 tokens by idling
        await message.add_reaction("🪙")
    
    bot_vars.user_interaction_tokens[userid][2] = int(time.time())

async def automessage(
        message: Message,
        AKASH_API_KEY: str,
        bot_vars: BotVariables,
        client: Client
        ) -> None:
    bot_vars.recent_messages.append(message)

    is_mentioned: bool = client.user in message.mentions

    regex_match = re.search(r"(?:\s|^)инвалид", message.content.lower())
    is_mentioned_directly: bool = regex_match is not None
    
    is_time_to_automessage: bool

    if bot_vars.setting_message_interval_is_random:
        is_time_to_automessage = bot_vars.message_interval_random <= 0
        if is_time_to_automessage:
            bot_vars.message_interval_random = int(random.random() * 10.0) + 4
        else:
            bot_vars.message_interval_random -= 1
    else:
        recent_messages_len: int = len(bot_vars.recent_messages)
        is_time_to_automessage = recent_messages_len >= bot_vars.setting_message_interval

    automessage_condition: bool = is_mentioned or is_mentioned_directly or is_time_to_automessage
    if automessage_condition and bot_vars.recent_messages:
        async with message.channel.typing():
            automessage: str = ai.generate_automessage(AKASH_API_KEY, bot_vars)
            await message.channel.send(automessage)

            bot_vars.recent_messages.clear()

            bot_vars.stylized_bot_messages.append(automessage)
            while (len(bot_vars.stylized_bot_messages) > bot_vars.setting_own_message_memory):
                bot_vars.stylized_bot_messages.pop(0)
