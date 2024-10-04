import discord
import get_ai_response as ai

# Retrieve sensitive information from an unlisted file
TOKEN = ""
AKASH_API_KEY = ""

with open("tokens.txt", "r") as file:
    temp = file.read().splitlines()
    TOKEN = temp[0]
    AKASH_API_KEY = temp[1]

# Declare the bot
intents = discord.Intents.default()
intents.guild_typing = True
intents.message_content = True

client = discord.Client(intents=intents)

# Print a message when the bot is up
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Declare commands
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(';prompt'):
        await message.channel.send(ai.get_response(AKASH_API_KEY, message.content[8:]))

    if message.content.startswith(';ping'):
        await message.channel.send('pong')


# Run the bot
client.run(TOKEN)