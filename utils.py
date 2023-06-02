import datetime
import random

from pony.orm import db_session, select
from vkwave.api import API
from vkwave.bots import PhotoUploader
from vkwave.client import AIOHTTPClient

from media_managers import ImageManager, GreetingManager, TikTokManager
from models import Greeting, UserBot
from config import USER_NONE_ANSWER, MEM_MINIMUM_QUANTITY, TOKEN, HELP_MESSAGE


class BaseManager:

    def __init__(self):
        self.image_manager = ImageManager()
        self.greeting_manager = GreetingManager()
        self.tiktok_manager = TikTokManager()
        self.api = API(clients=AIOHTTPClient(), tokens=TOKEN)
        self.uploader = PhotoUploader(self.api.get_context())

    async def send_image(self, user_id, photo):
        await self.api.get_context().messages.send(user_id=user_id, attachment=photo,
                                                   random_id=random.choice(range(2 ** 20)))

    async def send_message(self, user_id, message):
        if isinstance(user_id, int):
            user_id = [user_id]
        await self.api.get_context().messages.send(user_ids=user_id, message=message,
                                                   random_id=random.choice(range(2 ** 20)))

    @db_session
    def get_admin_list(self):
        return select(user for user in UserBot if user.status == 'admin')


class Get(BaseManager):

    # TODO переписать
    @staticmethod
    async def help():
        return HELP_MESSAGE

    async def greeting(self, user_id):
        with db_session:
            user = UserBot.get(user_id=user_id)
            if not user:
                return USER_NONE_ANSWER

            return self.greeting_manager.get_random()

    @db_session
    async def image(self, user_id):
        user = UserBot.get(user_id=user_id)
        if user:
            mem_link, mem_count = ImageManager().create_image_from_db_model()
            photo = await self.uploader.get_attachment_from_link(peer_id=user_id,
                                                                 link=mem_link)
            await self.send_image(user_id, photo)

            await self.mem_count_check(mem_count)
        else:
            return USER_NONE_ANSWER

    # TODO расширить его для поздравлений и тик-токов и вынести в BaseManager
    async def mem_count_check(self, count):
        if count > MEM_MINIMUM_QUANTITY:
            return
        user_id = [admin.user_id for admin in self.get_admin_list()]
        message = f'В базе осталось всего {count} мема, пора добавить новых!'
        await self.send_message(user_id=user_id, message=message)


class Add(BaseManager):

    @db_session
    async def greeting(self, text: list):
        if not text:
            return 'Поздравление пустое!'

        greeting = Greeting(text=' '.join(text), is_active=True)
        return 'Поздравление успешно добавлено!' if greeting else 'Что-то пошло не так!'

    def tt(self, text: str, user):
        # TODO реализовать tik-tok
        pass

    @db_session
    async def image(self, user_id, event_attachments):
        user = UserBot.get(user_id=user_id)
        if user and user.status == 'admin':
            # get photos from message
            attachments = [attachment.photo.sizes[-1] for attachment in event_attachments]
            # send confirm message if image load to db
            if self.image_manager.images_model_create(attachments):
                return 'Фото успешно загружены'

        return 'Что-то пошло не так. Возможно эти фото уже были загружены вами!'


class CommandManager:

    def __init__(self):
        self.add = Add()
        self.get = Get()

    @db_session
    async def ripple(self, text: list, user_id):
        user = UserBot.get(user_id=user_id)
        if not user:
            return USER_NONE_ANSWER

        if not text or text[0] == ' time':
            return f"Время рассылки {user.ripple_time.strftime('%H:%M')}"

        first_element = text[0]
        if len(text) == 1 and first_element in ('on', 'off'):
            user.ripple_status = True if first_element == 'on' else False
            return f'Статус рассылки изменен на {user.ripple_status}'
        elif len(text) == 2 and first_element == 'time':
            hour, minute = list(map(int, text[1].split(':')))

            user.ripple_time = datetime.datetime(year=1, month=1, day=1, hour=hour, minute=minute)
            return f"Время рассылки успешно изменено на {user.ripple_time.strftime('%H:%M')}"

        return 'Что-то пошло не так!'

# TODO разобраться почему функции не возвращают ответ пользователю
