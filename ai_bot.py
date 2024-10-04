import discord
import get_ai_response as ai

intents = discord.Intents.default()
intents.guild_typing = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(';prompt'):
        await message.channel.send(ai.get_response(message.content))

    if message.content.startswith(';ping'):
        await message.channel.send('pong')


client.run('token')