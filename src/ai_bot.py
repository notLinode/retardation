import discord

import random
import re

import get_ai_response as ai
from bot_variables import *
import commands

# Retrieve sensitive information from an unlisted file
TOKEN: str
AKASH_API_KEY: str

with open("tokens.txt", "r") as file:
    temp = file.read().splitlines()
    TOKEN = temp[0]
    AKASH_API_KEY = temp[1]

# Declare the bot
intents = discord.Intents.default()
intents.guild_typing = True
intents.message_content = True
intents.guild_reactions = True

client = discord.Client(intents=intents)

# Declare global variables and constants
bot_vars = BotVariables()

# Print a message when the bot is up
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Declare commands
@client.event
async def on_message(message: discord.Message):
    global bot_vars

    if message.author == client.user:
        return
    
    match message.content.split()[0]:
        case ";prompt":
            await commands.prompt(message, AKASH_API_KEY)

        case ";set-message-interval":
            await commands.set_message_interval(message, bot_vars)
        
        case ";set-own-message-memory":
            await commands.set_own_message_memory(message, bot_vars)
        
        case ";clear-memory":
           await commands.clear_memory(message, bot_vars)
        
        case ";ping":
            await message.channel.send('pong')
        
        case ";help":
            await commands.help(message)
        
        # If the message is not a commmand, we initiate automessaging
        case _:
            bot_vars.recent_messages.append(message)

            is_mentioned: bool = client.user in message.mentions
            is_mentioned_directly: bool =  re.search(r"(?:\s|^)инвалид", message.content.lower()) is not None

            if bot_vars.setting_message_interval_is_random:
                is_time_to_automessage: bool = bot_vars.message_interval_random <= 0
                bot_vars.message_interval_random = int(random.random() * 10) + 1 if is_time_to_automessage else bot_vars.message_interval_random - 1
            else:
                is_time_to_automessage: bool = len(bot_vars.recent_messages) >= bot_vars.setting_message_interval

            if (is_mentioned or is_mentioned_directly or is_time_to_automessage) and bot_vars.recent_messages:
                async with message.channel.typing():
                    automessage: str = ai.generate_automessage(AKASH_API_KEY, bot_vars.recent_messages, bot_vars.stylized_bot_messages)
                    await message.channel.send(automessage)

                    bot_vars.recent_messages.clear()

                    bot_vars.stylized_bot_messages.append(automessage)
                    while (len(bot_vars.stylized_bot_messages) > bot_vars.setting_own_message_memory):
                        bot_vars.stylized_bot_messages.pop(0)


# Run the bot
client.run(TOKEN)
