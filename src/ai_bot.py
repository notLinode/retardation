import discord

import asyncio

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

# Read saved info from a file if it exists
bot_vars: BotVariables

try:
    bot_vars = BotVariables.from_file("data/bot_vars.csv")
except Exception as e:
    print(f"Exception while reading bot vars: {e}")
    bot_vars = BotVariables()

# Create custom routines
async def save_on_disk_task():
    while True:
        await asyncio.sleep(60.0)

        async with asyncio.Lock():
            try:
                bot_vars.write_to_file("data/bot_vars.csv")
            except Exception as e:
                print(f"Error while writing to a file: {e}")

async def hunger_task(): # TODO: add dying on 0 health and reviving the bot with a 5️⃣ reaction
    while True:
        bot_vars.litter_box_timer -= 1

        if bot_vars.litter_box_timer == 0:
            bot_vars.add_litter(10)
            bot_vars.litter_box_timer = 60 # +10 litter box fullness every hour

        if bot_vars.litter_box_fullness >= 100:
            bot_vars.add_health(-1.0)

        if bot_vars.satiety > 100.0:
            bot_vars.satiety -= 2.0
            bot_vars.health -= 1
        elif bot_vars.satiety > 0:
            bot_vars.satiety -= 0.2 # -1 satiety every 5 minutes
        else:
            bot_vars.add_health(-1.0)

        await asyncio.sleep(60.0)

async def presence_task():
    while True:
        try:
            presence: str = f"{'❤️' if int(bot_vars.health) > 10 else '💔'} {int(bot_vars.health)} "
            presence += f"{'🍖' if int(bot_vars.satiety) > 50 else '🦴'} {int(bot_vars.satiety)} "
            presence += f"💩 {bot_vars.litter_box_fullness}"

            activity = discord.Activity(type=discord.ActivityType.playing, name=presence)
            await client.change_presence(activity=activity)
        except Exception as e:
            print(f"Error while changing presence: {e}")

        await asyncio.sleep(10.0)

async def update_shop_task():
    while True:
        try:
            bot_vars.shop_items = ai.generate_shop_items(AKASH_API_KEY)
            bot_vars.shop_items_next_update_time = int(time.time()) + 3600
            await asyncio.sleep(3600.0)
        except Exception as e:
            print(f"Error while updating shop: {e}")
            bot_vars.set_default_shop_items()
            bot_vars.shop_items_next_update_time = int(time.time()) + 60
            await asyncio.sleep(60.0)

# Print a message when the bot is up
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    client.loop.create_task(hunger_task())
    client.loop.create_task(presence_task())
    client.loop.create_task(update_shop_task())
    client.loop.create_task(save_on_disk_task())

# Declare commands
@client.event
async def on_message(message: discord.Message):
    global bot_vars

    if message.author == client.user:
        return
    
    await commands.process_tokens_info(message, bot_vars)
                
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
        
        case ";shop":
            await commands.shop(message, AKASH_API_KEY, bot_vars)
        
        case ";buy":
            await commands.buy(message, AKASH_API_KEY, bot_vars)

        case ";clean-litter" | ";clean-litter-box":
            await commands.clean_litter(message, bot_vars)

        case ";status":
            await commands.status(message, bot_vars)

        case ";tokens" | ";tok":
            await commands.tokens(message, bot_vars)
        
        case ";ping":
            await message.channel.send('pong')
        
        case ";help":
            await commands.help(message)
        
        case _:
            await commands.automessage(message, AKASH_API_KEY, bot_vars, client)


# Run the bot
client.run(TOKEN)
