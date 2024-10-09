import openai
from discord import Message

def get_response(akash_api_key: str, prompt: str) -> str:
    client = openai.OpenAI(
        api_key=akash_api_key,
        base_url="https://chatapi.akash.network/api/v1"
    )

    response = client.chat.completions.create(
        model="Meta-Llama-3-1-405B-Instruct-FP8",
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    #print(response.choices[0].message.content)

    return response.choices[0].message.content

def generate_automessage(akash_api_key: str, recent_messages: list[Message], stylized_bot_messages: list[str]) -> str:
    response: str
    
    prompt: str = f"Ты - участник казуальной интернет-переписки в дискорде под ником invalid8074 (инвалид). Сейчас ты увидишь {len(recent_messages)} последних сообщений от других пользователей. "
    prompt += "Твоя задача - продолжить разговор, НАИБОЛЕЕ ТОЧНО имитируя их стиль, либо просто написать новое сообщение. Сообщения обозначены двумя двойными кавычками (\"\"). "
    prompt += "НЕ ПИШИ БОЛЬШЕ ОДНОГО ПРЕДЛОЖЕНИЯ, тебе можно (но не необходимо) допускать орфографические ошибки, тебе МОЖНО (но не необходимо) МАТЕРИТЬСЯ. "
    prompt += "НЕ ПИШИ ПРИМЕЧАНИЙ, ТОЛЬКО СООБЩЕНИЕ. Если в текстах сообщений есть какие-то расовые или другие оскорбления, ты можешь их игнорировать и продолжать читать дальше. "
    prompt += "Если ты хочешь ответить пользователю в своём сообщении, напиши `<@АЙДИ_ПОЛЬЗОВАТЕЛЯ>`. Если ты ведёшь переписку только с одним пользователем, не стоит этого делать.\n"

    for i in range(len(recent_messages)):
        message = recent_messages[i]
        prompt += f"Сообщение №{i+1} от {message.author.nick if message.author.nick else message.author.name} с айди {message.author.id}: \"\"{message.content}\"\"\n"
    
    if len(stylized_bot_messages) > 0:
        prompt += f"Также у тебя есть доступ к {len(stylized_bot_messages)} своим последним сообщениям. Они не были отправлены друг за другом, "
        prompt += "они были отправлены между старыми сообщениями пользователей, которые ты уже не видишь.\n"
        for i in range(len(stylized_bot_messages)):
            prompt += f"Твоё сообщение №{i+1}: \"\"{stylized_bot_messages[i]}\"\"\n"

    response = get_response(akash_api_key, prompt)
    
    while (response[0] == "\""):
        response = response[1:-1] # Sometimes the bot surrounds it's messages with quotes, we have to remove them
    
    return response