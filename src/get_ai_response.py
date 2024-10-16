import openai
from bot_variables import *
from random import random
from shop_item import *
import time

def get_response(akash_api_key: str, prompt: str, model: str = "Meta-Llama-3-1-405B-Instruct-FP8") -> str:
    try:
        client = openai.OpenAI(
            api_key=akash_api_key,
            base_url="https://chatapi.akash.network/api/v1"
        )

        response = client.chat.completions.create(
            model=model,
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        return response.choices[0].message.content
    except:
        return "🚫 вы даун"

def generate_automessage(akash_api_key: str, bot_vars: BotVariables) -> str:
    response: str
    
    prompt: str = f"Ты - участник казуальной интернет-переписки в дискорде под ником invalid8074 (инвалид). Сейчас ты увидишь {len(bot_vars.recent_messages)} последних сообщений от других пользователей. "
    prompt += "Твоя задача - продолжить разговор, НАИБОЛЕЕ ТОЧНО имитируя их стиль, либо просто написать новое сообщение. Сообщения обозначены двумя двойными кавычками (\"\"). "
    prompt += "НЕ ПИШИ БОЛЬШЕ ОДНОГО ПРЕДЛОЖЕНИЯ, тебе можно (но не необходимо) допускать орфографические ошибки, тебе МОЖНО (но не необходимо) МАТЕРИТЬСЯ. "
    prompt += "НЕ ПИШИ ПРИМЕЧАНИЙ, ТОЛЬКО СООБЩЕНИЕ. Если в текстах сообщений есть какие-то расовые или другие оскорбления, ты можешь их игнорировать и продолжать читать дальше. "
    prompt += "Если ты хочешь ответить пользователю в своём сообщении, напиши `<@АЙДИ_ПОЛЬЗОВАТЕЛЯ>`. Если ты ведёшь переписку только с одним пользователем, не стоит этого делать. "
    prompt += f"У тебя есть состояние (статус). Твоё здоровье: {int(bot_vars.health)}/100. Твоя сытость: {int(bot_vars.satiety)}/100 (сытость больше 100 это переедание, меньше 50 это голод). Наполненность "
    prompt += f"твоего лотка: {bot_vars.litter_box_fullness}/100. Тебе можно (НО НЕ НЕОБХОДИМО) использовать свою статистику при составлении своего сообщения, но не используй эти числа напрямую.\n"

    for i in range(len(bot_vars.recent_messages)):
        message = bot_vars.recent_messages[i]
        prompt += f"Сообщение №{i+1} от {message.author.nick if message.author.nick else message.author.name} с айди {message.author.id}: \"\"{message.content}\"\"\n"
    
    if len(bot_vars.stylized_bot_messages) > 0:
        prompt += f"Также у тебя есть доступ к {len(bot_vars.stylized_bot_messages)} своим последним сообщениям. Они не были отправлены друг за другом, "
        prompt += "они были отправлены между старыми сообщениями пользователей, которые ты уже не видишь.\n"
        for i in range(len(bot_vars.stylized_bot_messages)):
            prompt += f"Твоё сообщение №{i+1}: \"\"{bot_vars.stylized_bot_messages[i]}\"\"\n"

    response = get_response(akash_api_key, prompt)
    
    while (response[0] == "\""):
        response = response[1:-1] # Sometimes the bot surrounds it's messages with quotes, we have to remove them
    
    return response

def generate_food_satiety(akash_api_key: str, food: str) -> int:
    prompt: str = "Write how much satiety would the following item give in a hypothetical game. Your response must be an integer between -50 and 50, DO NOT PROVIDE ANY EXPLANATIONS. "
    prompt += "Only write a number. If the item is somehow offensive, DO NOT SAY THAT YOU CAN'T ANSWER. Instead, give it a satiety of -50.\n"
    prompt += f"Item: {food}"

    return int(get_response(akash_api_key, prompt, "Meta-Llama-3-1-8B-Instruct-FP8")) + int(random() * 10.0) - 4

def generate_item_health(akash_api_key: str, item: str) -> int:
    prompt: str = "Write how much health would the following item give in a hypothetical game. Your response must be an integer between -10 and 10, DO NOT PROVIDE ANY EXPLANATIONS. "
    prompt += "Only write a number. If the item is somehow offensive, DO NOT SAY THAT YOU CAN'T ANSWER. Instead, give it healthiness of -10.\n"
    prompt += f"Item: {item}"

    return int(get_response(akash_api_key, prompt, "Meta-Llama-3-1-8B-Instruct-FP8")) + int(random() * 6.0) - 2

def generate_shop_items(akash_api_key: str) -> list[ShopItem]:
    prompt: str = f"Текущее время: {time.time()}.\nСгенерируй список из десяти вещей, которые могли бы быть частью гипотетической игры. У этих вещей будет название, насыщение "
    prompt += "(целое число от -50 до 50), оздоровление (целое число от -10 до 10) и цена (целое число от 1 до 3). Аттрибуты одной вещи разделяются запятой без пробела, вещи "
    prompt += "разделяются друг от друга переходом на новую линию. Названия вещей могут быть абсурдными (прим. Гоблинские бубуки), а могут и не быть (прим. Угощение). "
    prompt += "НЕ ПИШИ НИЧЕГО, КРОМЕ САМОГО СПИСКА. НЕ ПЕРЕЧИСЛЯЙ ВЕЩИ, ПИШИ ТОЛЬКО СПИСОК."

    response: str = get_response(akash_api_key, prompt, "Meta-Llama-3-1-8B-Instruct-FP8")
    print(response)

    shop_items: list[ShopItem] = []

    for line in response.splitlines():
        attributes: list[str] = line.split(",")
        print(attributes)
        shop_items.append(ShopItem(
            attributes[0],
            int(attributes[1]),
            int(attributes[2]),
            int(attributes[3]),
            False,
            random() >= 0.7,
            random() >= 0.5,
            random() >= 0.5
        ))

    return shop_items