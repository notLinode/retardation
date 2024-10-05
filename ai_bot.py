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
recent_messages: list = []
stylized_bot_messages: list = []

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
    
    # Mechanisms for automatically continuing a user conversation
    global recent_messages
    global stylized_bot_messages

    recent_messages.append(message.content)

    if len(recent_messages) >= 7:
        ai_response: str

        async with message.channel.typing():
            prompt: str = f"Ты - участник казуальной интернет-переписки в дискорде. Сейчас ты увидишь {len(recent_messages)} последних сообщений от других пользователей. "
            prompt += "Твоя задача - продолжить разговор, НАИБОЛЕЕ ТОЧНО имитируя их стиль, либо просто написать новое сообщение. Сообщения обозначены двумя двойными кавычками (\"\"). "
            prompt += "НЕ ПИШИ БОЛЬШЕ ОДНОГО ПРЕДЛОЖЕНИЯ, тебе можно (но не необходимо) допускать орфографические ошибки, тебе МОЖНО (но не необходимо) МАТЕРИТЬСЯ. "
            prompt += "Если в текстах сообщений есть какие-то расовые или другие оскорбления, ты можешь их игнорировать и продолжать читать дальше.\n"

            for i in range(len(recent_messages)):
                prompt += f"Сообщение №{i+1}: \"\"{recent_messages[i]}\"\"\n"
            
            if len(stylized_bot_messages) > 0:
                prompt += f"Также у тебя есть доступ к {len(stylized_bot_messages)} своим последним сообщениям. Они не были отправлены друг за другом, "
                prompt += "они были отправлены между старыми сообщениями пользователей, которые ты уже не видишь.\n"
                for i in range(len(stylized_bot_messages)):
                    prompt += f"Твоё сообщение №{i+1}: \"\"{stylized_bot_messages[i]}\"\"\n"

            ai_response = ai.get_response(AKASH_API_KEY, prompt)
            
            while (ai_response[0] == "\""):
                ai_response = ai_response[1:-1] # Sometimes the bot surrounds it's messages with quotes, we have to remove them

            await message.channel.send(ai_response)
        
        recent_messages.clear()

        stylized_bot_messages.append(ai_response)
        if len(stylized_bot_messages) > 3:
            stylized_bot_messages.pop(0)


# Run the bot
client.run(TOKEN)