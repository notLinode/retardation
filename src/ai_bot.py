import discord

import asyncio
import random
import re

from bot_variables import *
import commands
import get_ai_response as ai

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

# Create hunger routine
async def hunger_task(): # TODO: add dying on 0 health and reviving the bot with a 5️⃣ reaction
    while True:
        bot_vars.litter_box_timer -= 1

        if bot_vars.litter_box_timer == 0:
            bot_vars.litter_box_fullness += 10
            bot_vars.litter_box_timer = 60 # +10 litter box fullness every hour

        if bot_vars.litter_box_fullness >= 100:
            bot_vars.health -= 1

        if bot_vars.satiety > 100.0:
            bot_vars.satiety -= 2.0
            bot_vars.health -= 1
        elif bot_vars.satiety > 0:
            bot_vars.satiety -= 0.2 # -1 satiety every 5 minutes
            
            if bot_vars.satiety in [10.0, 20.0, 30.0]:
                await client.get_channel(1275173364574720121).send(f":bone: у меня осталось {int(bot_vars.satiety)} сытости и я голодный")
        else:
            bot_vars.health -= 1

        await asyncio.sleep(60.0)

# Print a message when the bot is up
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    client.loop.create_task(hunger_task())

# Declare commands
@client.event
async def on_message(message: discord.Message):
    global bot_vars

    if message.author == client.user:
        return
    
    if message.author.id not in bot_vars.user_interaction_tokens:
            bot_vars.user_interaction_tokens[message.author.id] = [3, 10]
    
    if bot_vars.user_interaction_tokens[message.author.id][1] <= 0:
        bot_vars.user_interaction_tokens[message.author.id][1] = 10
        bot_vars.user_interaction_tokens[message.author.id][0] += 1 if bot_vars.user_interaction_tokens[message.author.id][0] < 3 else 0
        await message.add_reaction("🪙")
    else:
        bot_vars.user_interaction_tokens[message.author.id][1] -= 1
    
                
    match message.content.split()[0]:
        case ";prompt":
            await commands.prompt(message, AKASH_API_KEY)

        case ";set-message-interval":
            await commands.set_message_interval(message, bot_vars)
        
        case ";set-own-message-memory":
            await commands.set_own_message_memory(message, bot_vars)
        
        case ";clear-memory":
           await commands.clear_memory(message, bot_vars)

        case ";feed":
            await commands.feed(message, AKASH_API_KEY, bot_vars)
        
        case ";heal":
            await commands.heal(message, AKASH_API_KEY, bot_vars)

        case ";clean-litter" | ";clean-litter-box":
            await commands.clean_litter(message, bot_vars)

        case ";status":
            await commands.status(message, bot_vars)
        
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
                bot_vars.message_interval_random = int(random.random() * 10.0) + 1 if is_time_to_automessage else bot_vars.message_interval_random - 1
            else:
                is_time_to_automessage: bool = len(bot_vars.recent_messages) >= bot_vars.setting_message_interval

            if (is_mentioned or is_mentioned_directly or is_time_to_automessage) and bot_vars.recent_messages:
                async with message.channel.typing():
                    automessage: str = ai.generate_automessage(AKASH_API_KEY, bot_vars)
                    await message.channel.send(automessage)

                    bot_vars.recent_messages.clear()

                    bot_vars.stylized_bot_messages.append(automessage)
                    while (len(bot_vars.stylized_bot_messages) > bot_vars.setting_own_message_memory):
                        bot_vars.stylized_bot_messages.pop(0)


# Run the bot
client.run(TOKEN)
