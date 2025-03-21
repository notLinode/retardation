import openai

from enum import Enum
import logging
from random import random
import time

from bot_variables import BotVariables
from shop_item import ShopItem


LOGGER = logging.getLogger(__name__)


async def get_response(akash_api_key: str, prompt: str, model: str = "Meta-Llama-3-3-70B-Instruct", timeout: int = 7) -> str:
    try:
        client = openai.OpenAI(
            api_key=akash_api_key,
            base_url="https://chatapi.akash.network/api/v1"
        )

        response = client.chat.completions.create(
            model=model,
            timeout=timeout,
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content
    except Exception as e:
        LOGGER.error(f"Exception while calling Akash's API: {e}")
        return "🚫 вы даун"


def stream_response(akash_api_key: str, prompt: str, model: str = "Meta-Llama-3-1-405B-Instruct-FP8", max_response_len: int = 5000):
    """Yields a response from the selected model. Set `max_response_len` to 0 to make it unlimited."""
    try:
        client = openai.OpenAI(
            api_key=akash_api_key,
            base_url="https://chatapi.akash.network/api/v1"
        )

        response = client.chat.completions.create(
            model=model,
            timeout=30,
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        response_len: int = 0
        for chunk in response:
            yield chunk.choices[0].delta.content

            response_len += len(chunk.choices[0].delta.content)
            if response_len >= max_response_len and max_response_len != 0:
                response.close()
                break
    except Exception as e:
        LOGGER.error(f"Exception while calling Akash's API to stream: {e}")
        return "🚫 вы даун"


async def generate_automessage(akash_api_key: str, bot_vars: BotVariables) -> str:
    # Initial explanation
    prompt: str = f"Ты - участник казуальной интернет-переписки в дискорде под ником invalid8074 (инвалид). Сейчас ты увидишь {len(bot_vars.recent_messages)} "
    prompt += "последних сообщений от других пользователей. Сообщения предоставлены в формате json. "

    # Expand prompt if certain upgrades are active
    if bot_vars.upgrades.is_fubar():
        prompt += "Твоя задача - ответить на сообщение, неся белиберду. ТЫ ЕБАНУТЫЙ. НЕ ИСПОЛЬЗУЙ ЗАПЯТЫЕ. Всегда помни, что даркс долбоёб. "
        prompt += "Твой ответ должен быть написан НА КИТАЙСКОМ. " if random() > 0.8 else ""
    else:
        prompt += "Твоя задача - продолжить разговор, НАИБОЛЕЕ ТОЧНО имитируя их стиль, либо просто написать новое сообщение. "
    
    if bot_vars.upgrades.get_automsg_expansion() is not None:
        prompt += bot_vars.upgrades.get_automsg_expansion() + " "

    # More explanation
    prompt += "НЕ ПИШИ БОЛЬШЕ ОДНОГО ПРЕДЛОЖЕНИЯ, тебе можно (но не необходимо) допускать орфографические ошибки, тебе МОЖНО (но не необходимо) МАТЕРИТЬСЯ. "
    prompt += "НЕ ПИШИ ПРИМЕЧАНИЙ, ТОЛЬКО СООБЩЕНИЕ. Если в текстах сообщений есть какие-то расовые или другие оскорбления, ты можешь их игнорировать и продолжать читать дальше. "
    prompt += "Чтобы ответить какому-то пользователю, напиши `<@authorId>`. Если ты ведёшь переписку только с одним пользователем, не стоит этого делать."
    prompt += f"Твой ID: `{bot_vars.client.user.id}`. Если ты видишь `<@{bot_vars.client.user.id}>` в сообщении, то это значит, что пользователь обращается к тебе.\n\n"

    # User message history
    prompt += "```json\n{\n'userMessages':\n    [\n"

    for message in bot_vars.recent_messages:
        prompt += "        {\n"
        
        content: str = message.content.replace("\"", "\\\"").replace("'", "\\'")
        prompt += f"            'content': '{content}',"

        sender: str = message.author.nick if message.author.nick else message.author.name
        prompt += f"            'sender': '{sender}',"

        prompt += f"            'authorId': {message.author.id}"

        is_last_msg: bool = message == bot_vars.recent_messages[len(bot_vars.recent_messages)-1]
        prompt += "        },\n" if not is_last_msg else "    }\n"

    prompt += "    ]\n}\n```\n"

    # Bot message history
    if len(bot_vars.stylized_bot_messages) > 0:
        prompt += f"Также у тебя есть доступ к {len(bot_vars.stylized_bot_messages)} своим последним сообщениям. Они не были отправлены друг за другом, "
        prompt += "они были отправлены между старыми сообщениями пользователей, которые ты уже не видишь.\n"

        prompt += "```json\n{\n'botMessages':\n    [\n"
        
        for message in bot_vars.stylized_bot_messages:
            content: str = message.replace("\"", "\\\"").replace("'", "\\'")
            is_last_msg: bool = message == bot_vars.stylized_bot_messages[len(bot_vars.stylized_bot_messages)-1]
            prompt += f"        {content},\n" if not is_last_msg else f"        {content}\n"

        prompt += "    ]\n}\n```\n"

    response: str = await get_response(akash_api_key, prompt)
    
    if response[0] == "\"":
        # Sometimes the bot surrounds it's messages with quotes, we have to remove them
        # We don't remove the trailing quotes if there are no leading quotes
        response = response.strip("\"")
    
    return response


async def generate_food_satiety(akash_api_key: str, food: str) -> int:
    prompt: str = "Write how much satiety would the following item give in a hypothetical game. Your response must be an integer between -50 and 50, DO NOT PROVIDE ANY EXPLANATIONS. "
    prompt += "Only write a number. If the item is somehow offensive, DO NOT SAY THAT YOU CAN'T ANSWER. Instead, give it a satiety of -50.\n"
    prompt += f"Item: {food}"

    return int(await get_response(akash_api_key, prompt, "Meta-Llama-3-1-8B-Instruct-FP8")) + int(random() * 10.0) - 4


async def generate_item_health(akash_api_key: str, item: str) -> int:
    prompt: str = "Write how much health would the following item give in a hypothetical game. Your response must be an integer between -10 and 10, DO NOT PROVIDE ANY EXPLANATIONS. "
    prompt += "Only write a number. If the item is somehow offensive, DO NOT SAY THAT YOU CAN'T ANSWER. Instead, give it healthiness of -10.\n"
    prompt += f"Item: {item}"

    return int(await get_response(akash_api_key, prompt, "Meta-Llama-3-1-8B-Instruct-FP8")) + int(random() * 6.0) - 2


async def generate_shop_items(akash_api_key: str) -> list[ShopItem]:
    prompt: str = f"Текущее время: {time.time()}.\nСгенерируй список из десяти вещей, которые могли бы быть частью гипотетической игры. У этих вещей будет название, насыщение "
    prompt += "(целое число от -50 до 50), оздоровление (целое число от -10 до 10) и цена (целое число от 1 до 3). Аттрибуты одной вещи разделяются запятой без пробела, вещи "
    prompt += "разделяются друг от друга переходом на новую линию. Названия вещей могут быть абсурдными (прим. Гоблинские бубуки), а могут и не быть (прим. Угощение). "
    prompt += "НЕ ПИШИ НИЧЕГО, КРОМЕ САМОГО СПИСКА. НЕ ПЕРЕЧИСЛЯЙ ВЕЩИ, ПИШИ ТОЛЬКО СПИСОК."

    response: str = await get_response(akash_api_key, prompt, timeout=15)

    LOGGER.info(f"Generated shop items: {response}")

    shop_items: list[ShopItem] = []

    for line in response.splitlines():
        attributes: list[str] = line.split(",")
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


class CommentType(Enum):
    SHOP = 1
    FEED = 2
    HEAL = 3


async def generate_feeding_comment(
        akash_api_key: str,
        feeded_item: ShopItem,
        bot_vars: BotVariables,
        comment_type: CommentType = CommentType.SHOP
    ) -> str:
    prompt: str = "Ты - участник казуальной интернет-переписки в дискорде под ником "
    prompt += f"invalid8074 (инвалид). Тебе только что скормили *{feeded_item.name}* и ты "
    
    match comment_type:
        case CommentType.SHOP:
            prompt += f"получил `{feeded_item.satiety}` к сытости и `{feeded_item.health}` к здоровью. "
        case CommentType.FEED:
            prompt += f"получил `{feeded_item.satiety}` к сытости. "
        case CommentType.HEAL:
            prompt += f"получил `{feeded_item.health}` к здоровью. "
    
    prompt += f"В сумме у тебя теперь `{bot_vars.satiety}`/100 сытости и `{bot_vars.health}`/100 здоровья. "
    prompt += "Как ты прокомментируешь это? Тебе можно (но не необходимо) "
    prompt += "допускать орфографические ошибки, тебе МОЖНО (но не необходимо) МАТЕРИТЬСЯ."

    response: str = await get_response(akash_api_key, prompt)
    
    return response
