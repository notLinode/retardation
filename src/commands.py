from discord import Message

import random

import get_ai_response as ai
from bot_variables import *

async def prompt(message: Message, AKASH_API_KEY: str) -> None:
    async with message.channel.typing():
        ai_response: str = ai.get_response(AKASH_API_KEY, message.content[8:])

        while len(ai_response) > 2000:
            await message.channel.send(ai_response[:2000])
            ai_response = ai_response[2000:]

        await message.channel.send(ai_response)

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

        if interval < bot_vars.SETTING_MESSAGE_INTERVAL_MIN or interval > bot_vars.SETTING_MESSAGE_INTERVAL_MAX:
            await message.channel.send(f":prohibited: Интервал между сообщениями бота должен быть от `{bot_vars.SETTING_MESSAGE_INTERVAL_MIN}` до `{bot_vars.SETTING_MESSAGE_INTERVAL_MAX}` сообщений. Вы попытались установить: `{interval}`.")
            return

        bot_vars.setting_message_interval = interval
        bot_vars.setting_message_interval_is_random = False
        
        await message.channel.send(f":white_check_mark: Интервал между сообщениями бота установлен на `{bot_vars.setting_message_interval}` пользовательских сообщений.")

async def set_own_message_memory(message: Message, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        memory: int = int(message.content[24:])

        if memory < bot_vars.SETTING_OWN_MESSAGE_MEMORY_MIN or memory > bot_vars.SETTING_OWN_MESSAGE_MEMORY_MAX:
            await message.channel.send(f":prohibited: Память собственных сообщений бота должна быть от `{bot_vars.SETTING_OWN_MESSAGE_MEMORY_MIN}` до `{bot_vars.SETTING_OWN_MESSAGE_MEMORY_MAX}` сообщений. Вы попытались установить: `{memory}`.")
            return

        bot_vars.setting_own_message_memory = memory

        await message.channel.send(f":white_check_mark: Память собственных сообщений бота установлена на `{bot_vars.setting_own_message_memory}` сообщений.")

async def clear_memory(message: Message, bot_vars: BotVariables) -> None:
    async with message.channel.typing():
        bot_vars.recent_messages.clear()
        bot_vars.stylized_bot_messages.clear()
        await message.channel.send(f":white_check_mark: я всё заббыл нахуй")

async def help(message: Message) -> None:
    async with message.channel.typing():
        help_msg: str = "```"
        help_msg += "\n;prompt [Сообщение: str] - обратиться к Llama 3.1 405B.\n"
        help_msg += "\n;set-message-interval [Интервал: int | \"random\"] - поставить количество пользовательских сообщений, после которого бот сам что-то напишет.\n"
        help_msg += "\n;set-own-message-memory [Память: int] - поставить количество собственных сообщений бота, которые он запомнит и учтёт при написании следующего своего сообщения.\n"
        help_msg += "\n;clear-memory - Очищает память бота от своих и пользовательских сообщений.\n"
        help_msg += "\n;ping - pong.\n"
        help_msg += "```"

        await message.channel.send(help_msg)