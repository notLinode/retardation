import logging.handlers
import discord

import logging

from bot_variables import *
import commands
import get_ai_response as ai
import tasks

# Declare logger
LOGGER = logging.getLogger("invalid")
LOGGER.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename="discord.log",
    encoding="utf-8",
    maxBytes=33_554_432, # 32 MiB
    backupCount=5,
)

dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
handler.setFormatter(formatter)

LOGGER.addHandler(handler)

ai.LOGGER = commands.LOGGER = tasks.LOGGER = LOGGER

# Retrieve sensitive information from an unlisted file
TOKEN: str
AKASH_API_KEY: str

with open("tokens.txt", "r") as file:
    temp = file.read().splitlines()
    TOKEN = temp[0]
    AKASH_API_KEY = temp[1]

LOGGER.info("Read tokens from file")

# Declare the bot
intents = discord.Intents.default()
intents.guild_typing = True
intents.message_content = True
intents.guild_reactions = True

client = discord.Client(intents=intents)

LOGGER.info("Declared Discord client")

# Read saved info from a file if it exists
bot_vars: BotVariables

try:
    bot_vars = BotVariables.from_file("data/bot_vars.csv")
    LOGGER.info("Read bot_vars from file")
except FileNotFoundError as e:
    LOGGER.info("Tried reading bot_vars from file but it doesn't exist, using default constructor")
    bot_vars = BotVariables()
except Exception as e:
    LOGGER.error(f"Exception while reading bot vars: {e}")
    bot_vars = BotVariables()

bot_vars.ai_key = AKASH_API_KEY
bot_vars.client = client

# Print a message when the bot is up
@client.event
async def on_ready():
    LOGGER.info(f'We have logged in as {client.user}')
    client.loop.create_task(tasks.hunger_task(bot_vars))
    client.loop.create_task(tasks.presence_task(bot_vars))
    client.loop.create_task(tasks.update_shop_task(bot_vars))
    client.loop.create_task(tasks.save_on_disk_task(bot_vars))
    print("Bot is fully ready")

# Declare commands
@client.event
async def on_message(message: discord.Message):
    global bot_vars

    if message.author == client.user:
        return
    
    if bot_vars.health <= 0:
        await commands.bot_death_notify(message, bot_vars)
        return

    await commands.process_tokens_info(message, bot_vars)

    try:
        msg_first_word: str = message.content.split()[0]
    except IndexError:
        LOGGER.info(f"Tried splitting user message but it has no text content")
        return

    match msg_first_word:
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
            await commands.buy(message, bot_vars)

        case ";clean-litter" | ";clean-litter-box":
            await commands.clean_litter(message, bot_vars)

        case ";status":
            await commands.status(message, bot_vars)

        case ";tokens" | ";tok":
            await commands.tokens(message, bot_vars)
        
        case ";pay":
            await commands.pay(message, bot_vars)
        
        case ";blackjack" | ";bj":
            await commands.blackjack(message, bot_vars)

        case ";ping":
            await message.channel.send('pong')
        
        case ";help":
            await commands.help(message)
        
        case ";gm-1":
            if message.author.guild_permissions.administrator:
                bot_vars.user_interaction_tokens[message.author.id][0] = 9999
                await message.channel.send("george floyd negroid cyberg technology activated")
        
        case ";kill":
            if message.author.guild_permissions.administrator:
                bot_vars.health = 0

        case _:
            await commands.automessage(message, AKASH_API_KEY, bot_vars, client)

@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    global bot_vars

    await commands.try_revive(reaction, bot_vars)


# Run the bot
client.run(TOKEN, log_handler=handler)
