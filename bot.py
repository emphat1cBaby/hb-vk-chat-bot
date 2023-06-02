import asyncio

from vkwave.api import API
from vkwave.bots.utils.uploaders import PhotoUploader
from vkwave.client import AIOHTTPClient
from vkwave.bots import SimpleBotEvent, SimpleLongPollBot
from utils import ImageManager, CommandManager
import os

try:
    from config import TOKEN, GROUP_ID, MEM_MINIMUM_QUANTITY, USER_NONE_ANSWER
except Exception:
    TOKEN = str(os.environ.get('TOKEN'))
    GROUP_ID = int(os.environ.get('GROUP_ID'))

GLOBAL_PREFIXES = ('/', '!', '', '@ulyana ')

# bot init
bot = SimpleLongPollBot(tokens=TOKEN, group_id=GROUP_ID)
# init api
api = API(clients=AIOHTTPClient(), tokens=TOKEN)
uploader = PhotoUploader(api.get_context())
# init image manager
image_manager = ImageManager()
# init command_manager
command_manager = CommandManager()


@bot.message_handler(bot.command_filter(commands=('h', 'help', 'помощь', 'привет'),
                                        prefixes=GLOBAL_PREFIXES))
async def help_command(event: SimpleBotEvent) -> str:
    help_text = await command_manager.get.help()
    return help_text


@bot.message_handler(bot.command_filter(commands=('loadmem', 'memload'),
                                        prefixes=GLOBAL_PREFIXES))
async def get_photos(event: SimpleBotEvent):
    message = await command_manager.add.image(event.user_id, event.attachments)
    return message


@bot.message_handler(bot.command_filter(commands=('mem', 'm', 'мем', 'картинка'),
                                        prefixes=GLOBAL_PREFIXES))
async def mem(event: SimpleBotEvent):
    return await command_manager.get.image(event.user_id)


@bot.message_handler(bot.command_filter(commands=('ripple', 'рассылка'),
                                        prefixes=GLOBAL_PREFIXES))
async def ripple(event: SimpleBotEvent):
    message = await command_manager.ripple(event.text.split()[1:], event.user_id)
    return message


@bot.message_handler(bot.command_filter(commands=('greeting', 'поздравление', 'пожелание'),
                                        prefixes=GLOBAL_PREFIXES))
async def load_greeting(event: SimpleBotEvent):
    if len(event.text.split()) == 1:
        message = await command_manager.get.greeting(event.user_id)
    else:
        message = await command_manager.add.greeting(event.text.split()[1:])
    return message


# run bot
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run())

    loop.run_forever()
