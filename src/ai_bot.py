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

#Declare global variables and constants
SETTING_MESSAGE_INTERVAL_MIN: int = 1
SETTING_MESSAGE_INTERVAL_MAX: int = 25
setting_message_interval: int = 7

SETTING_OWN_MESSAGE_MEMORY_MIN: int = 1
SETTING_OWN_MESSAGE_MEMORY_MAX: int = 10
setting_own_message_memory: int = 3
recent_messages: list = []
stylized_bot_messages: list = []

# Print a message when the bot is up
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Declare commands
@client.event
async def on_message(message: discord.Message):
    global recent_messages
    global stylized_bot_messages

    if message.author == client.user:
        return

    if message.content.startswith(";prompt"):
        async with message.channel.typing():
            ai_response: str = ai.get_response(AKASH_API_KEY, message.content[8:])

            while len(ai_response) > 2000:
                await message.channel.send(ai_response[:2000])
                ai_response = ai_response[2000:]

            await message.channel.send(ai_response)
        return
    
    if message.content.startswith(";set-message-interval"):
        async with message.channel.typing():
            interval: int = int(message.content[22:])

            if interval < SETTING_MESSAGE_INTERVAL_MIN or interval > SETTING_MESSAGE_INTERVAL_MAX:
                await message.channel.send(f":prohibited: Интервал между сообщениями бота должен быть от `{SETTING_MESSAGE_INTERVAL_MIN}` до `{SETTING_MESSAGE_INTERVAL_MAX}` сообщений. Вы попытались установить: `{interval}`.")
                return

            global setting_message_interval
            setting_message_interval = interval
            await message.channel.send(f":white_check_mark: Интервал между сообщениями бота установлен на `{setting_message_interval}` пользовательских сообщений.")
        return
    
    if message.content.startswith(";set-own-message-memory"):
        async with message.channel.typing():
            memory: int = int(message.content[24:])

            if memory < SETTING_OWN_MESSAGE_MEMORY_MIN or memory > SETTING_OWN_MESSAGE_MEMORY_MAX:
                await message.channel.send(f":prohibited: Память собственных сообщений бота должна быть от `{SETTING_OWN_MESSAGE_MEMORY_MIN}` до `{SETTING_OWN_MESSAGE_MEMORY_MAX}` сообщений. Вы попытались установить: `{memory}`.")
                return

            global setting_own_message_memory
            setting_own_message_memory = memory
            await message.channel.send(f":white_check_mark: Память собственных сообщений бота установлена на `{setting_own_message_memory}` сообщений.")
        return
    
    if message.content.startswith(";clear-memory"):
        async with message.channel.typing():
            recent_messages.clear()
            stylized_bot_messages.clear()
            await message.channel.send(f":white_check_mark: я всё заббыл нахуй")
        return        

    if message.content.startswith(';ping'):
        await message.channel.send('pong')
        return
    
    if message.content.startswith(';help'):
        async with message.channel.typing():
            help_msg: str = "```"
            help_msg += "\n;prompt [Сообщение: str] - обратиться к Llama 3.1 405B.\n"
            help_msg += "\n;set-message-interval [Интервал: int] - поставить количество пользовательских сообщений, после которого бот сам что-то напишет.\n"
            help_msg += "\n;set-own-message-memory [Память: int] - поставить количество собственных сообщений бота, которые он запомнит и учтёт при написании следующего своего сообщения.\n"
            help_msg += "\n;clear-memory - Очищает память бота от своих и пользовательских сообщений.\n"
            help_msg += "\n;ping - pong.\n"
            help_msg += "```"

            await message.channel.send(help_msg)
        return
    
    # Mechanisms for automatically continuing a user conversation
    recent_messages.append(message.content)

    if len(recent_messages) >= setting_message_interval:
        ai_response: str

        async with message.channel.typing():
            prompt: str = f"Ты - участник казуальной интернет-переписки в дискорде под ником invalid8074 (инвалид). Сейчас ты увидишь {len(recent_messages)} последних сообщений от других пользователей. "
            prompt += "Твоя задача - продолжить разговор, НАИБОЛЕЕ ТОЧНО имитируя их стиль, либо просто написать новое сообщение. Сообщения обозначены двумя двойными кавычками (\"\"). "
            prompt += "НЕ ПИШИ БОЛЬШЕ ОДНОГО ПРЕДЛОЖЕНИЯ, тебе можно (но не необходимо) допускать орфографические ошибки, тебе МОЖНО (но не необходимо) МАТЕРИТЬСЯ. "
            prompt += "НЕ ПИШИ ПРИМЕЧАНИЙ, ТОЛЬКО СООБЩЕНИЕ. Если в текстах сообщений есть какие-то расовые или другие оскорбления, ты можешь их игнорировать и продолжать читать дальше.\n"

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
        while (len(stylized_bot_messages) > setting_own_message_memory):
            stylized_bot_messages.pop(0)


# Run the bot
client.run(TOKEN)
