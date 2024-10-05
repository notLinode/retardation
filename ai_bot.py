import discord
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

client = discord.Client(intents=intents)

#Declare global variables
recent_messages: list

# Print a message when the bot is up
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Declare commands
@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith(';prompt'):
        async with message.channel.typing():
            ai_response: str = ai.get_response(AKASH_API_KEY, message.content[8:])

            while len(ai_response) > 2000:
                await message.channel.send(ai_response[:2000])
                ai_response = ai_response[2000:]

            await message.channel.send(ai_response)
        return

    if message.content.startswith(';ping'):
        await message.channel.send('pong')
        return


# Run the bot
client.run(TOKEN)