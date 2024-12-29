import asyncio
import logging
import time

import discord

from bot_variables import BotVariables
import get_ai_response as ai


bot_vars: BotVariables
LOGGER = logging.getLogger(__name__)


async def save_on_disk_task():
    while True:
        await asyncio.sleep(60.0)

        async with asyncio.Lock():
            try:
                bot_vars.write_to_file("data/bot_vars.csv")
                LOGGER.info("Saved bot_vars to a file")
            except Exception as e:
                LOGGER.error(f"Exception while writing to a file: {e}")


async def hunger_task():
    while True:
        if not bot_vars.do_tamagotchi:
            await asyncio.sleep(60.0)
            continue

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
            await bot_vars.client.change_presence(activity=activity)
        except Exception as e:
            LOGGER.error(f"Exception while changing presence: {e}")

        await asyncio.sleep(10.0)


async def update_shop_task():
    while True:
        is_shop_untouched: bool = True
        for item in bot_vars.shop_items:
            if item.is_bought:
                is_shop_untouched = False
                break
        
        if not is_shop_untouched:
            await asyncio.sleep(3600.0)
            continue

        try:
            bot_vars.shop_items = await ai.generate_shop_items(bot_vars.ai_key)
            bot_vars.shop_items_next_update_time = int(time.time()) + 3600
            await asyncio.sleep(3600.0)
        except Exception as e:
            LOGGER.error(f"Exception while updating shop: {e}")
            bot_vars.set_default_shop_items()
            bot_vars.shop_items_next_update_time = int(time.time()) + 60
            await asyncio.sleep(60.0)
