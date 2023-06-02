import random
import re

from pony.orm import db_session, select
from vkwave.api import API
from vkwave.bots import PhotoUploader, DocUploader
from vkwave.client import AIOHTTPClient

from media_managers import ImageManager, TikTokManager, GreetingManager
from models import UserBot
from config import USER_NONE_ANSWER, MEM_MINIMUM_QUANTITY, TOKEN


class BaseManager:
    """
    Класс базового менеджера
    """
    def __init__(self):
        self.image_manager = ImageManager()
        self.tiktok_manager = TikTokManager()
        self.greeting_manager = GreetingManager()
        self.api = API(clients=AIOHTTPClient(), tokens=TOKEN)
        self.uploader = PhotoUploader(self.api.get_context())

    async def send_image(self, user_id, photo):
        """
        Метод отправки изображения
        :param user_id: id пользователя
        :param photo: файл фото
        """
        await self.api.get_context().messages.send(user_id=user_id, attachment=photo,
                                                   random_id=random.choice(range(2 ** 20)))

    async def send_document(self, peer_id, link):
        """
        Метод отправки документа
        :param peer_id: id чата
        :param link: ссылка на документ
        """
        doc = await DocUploader(self.api.get_context()).get_attachment_from_link(
            peer_id=peer_id,
            link=link,
            title="aboba")
        await self.api.get_context().messages.send(user_id=1234, attachment=doc,
                                                   random_id=random.choice(range(2 ** 20)))

    async def send_message(self, user_id, message):
        """
        Метод отправки сообщения
        :param user_id: id пользователя
        :param message: текст сообщения
        """
        if isinstance(user_id, int):
            user_id = [user_id]
        await self.api.get_context().messages.send(user_ids=user_id, message=message,
                                                   random_id=random.choice(range(2 ** 20)))

    @db_session
    def get_admin_list(self):
        """
        Метод получения списка пользователей-админов.
        :return: список пользователей админов
        """
        return select(user for user in UserBot if user.status == 'admin')

    async def count_check(self, count, type):
        """
        Метод проверки количества объектов в бд и отправки сообщения администраторам, если их количество меньше
        допустимого.
        :param count: количество объектов.
        :param type: тип объекта.
        :return: сообщение
        """
        if count > MEM_MINIMUM_QUANTITY:
            return
        user_id = [admin.user_id for admin in self.get_admin_list()]
        message = f'В базе осталось всего {count} {type}, пора добавить новых!'
        await self.send_message(user_id=user_id, message=message)

    @staticmethod
    def get_link_from_message(text):
        """
        Метод получения ссылки из текста
        :param text: текст
        :return: ссылка
        """
        return re.findall("(?P<url>https?://[^\s]+)", text)


class Get(BaseManager):
    """
    Класс менеджера получения объектов из бд.
    """
    @staticmethod
    async def help(user_id):
        """
        Метод отправки пользователю сообщения с help текстом.
        :param user_id: id пользователя.
        :return: сообщение пользователю.
        """
        with db_session():
            user = UserBot.get(user_id=user_id)
            if user:
                text = "Привет!&#9995; \nЯ - бот, который был создан, чтобы тебе не было скучно, пока все твои друзья заняты!&#128526; \nУ нас с " \
                    "тобой день рождения в один день, и я очень надеюсь, что мы поладим!&#128546;\nЯ ещё совсем маленький и мало " \
                    "что умею делать, но в скором времени у меня будут появляться всё больше возможностей. \n&#129303;\nА пока ты в " \
                    "любой момент можешь попросить у меня мем, для этого просто напиши мне сообщение с текстом 'мем' или " \
                    "тик-ток, для этого напиши 'тик-ток', если хочешь получить пожелание просто напиши 'пожелание'.&#128149;"

                if user.status == "admin":
                    return text + "\n1) Для того, чтобы загрузить мем в базу напиши loadmem или memload и прикрепи нужные фото(" \
                           "можно сразу несколько). \n2) Для того, чтобы загрузить тик-ток в базу напиши loadtt или " \
                           "ttload и вставь ссылки, разделяя пробелами(если их несколько). \n3) Для того, чтобы загрузить " \
                           "пожелание в базу напиши loadgr или grload и текст пожелания"
                else:
                    return text

    async def image(self, user_id):
        """
        Метод получения изображения из бд и отправки его пользователю.
        :param user_id: id пользователя.
        :return: сообщение пользователю.
        """
        with db_session():
            user = UserBot.get(user_id=user_id)
            if user:
                mem_link, mem_count = self.image_manager.create_object_from_db_model()
                if not mem_link:
                    return "Произошла ошибка!"

                photo = await self.uploader.get_attachment_from_link(peer_id=user_id, link=mem_link)
                await self.send_image(user_id, photo)
                await self.count_check(mem_count, 'мема')
            else:
                return USER_NONE_ANSWER

    async def tt(self, user_id):
        """
        Метод получения тик тока из бд и отправки его пользователю.
        :param user_id: id пользователя.
        :return: сообщение пользователю.
        """
        with db_session():
            user = UserBot.get(user_id=user_id)
            if user:
                tt_link, tt_count = self.tiktok_manager.create_object_from_db_model()
                if not tt_link:
                    return "Произошла ошибка!"

                await self.send_message(user_id, tt_link)
                await self.count_check(tt_count, 'тик токов')
            else:
                return USER_NONE_ANSWER

    async def greeting(self, user_id):
        """
        Метод получения пожелания из бд и отправки его пользователю.
        :param user_id: id пользователя.
        :return: сообщение пользователю.
        """
        with db_session():
            user = UserBot.get(user_id=user_id)
            if user:
                gr_link, gr_count = self.greeting_manager.create_object_from_db_model()
                if not gr_link:
                    return "Произошла ошибка!"

                await self.send_message(user_id, gr_link)
                await self.count_check(gr_count, 'пожеланий')
            else:
                return USER_NONE_ANSWER


class Add(BaseManager):
    """
    Класс менеджера добавления объектов в бд.
    """
    async def image(self, user_id, event_attachments):
        """
        Метод добавления изображения в бд.
        :param user_id: id пользователя.
        :param event_attachments: вложение.
        :return: сообщение администратору.
        """
        with db_session():
            user = UserBot.get(user_id=user_id)
            if user and user.status == 'admin':
                # get photos from message
                attachments = [attachment.photo.sizes[-1] for attachment in event_attachments]
                # send confirm message if image load to db
                image_models = self.image_manager.image_models_create(attachments)
                if image_models:
                    if all(model is not None for model in image_models):
                        return 'Все фото успешно загружены'
                    elif all(model is None for model in image_models):
                        return 'Ни одно фото не было загружено!'
                    else:
                        return 'Одно или несколько фото не было загружено!'

            return 'Что-то пошло не так. Возможно эти фото уже были загружены вами!'

    async def tt(self, text, user_id):
        """
        Метод добавления тик тока в бд.
        :param text: текст, содержащий ссылку на тик ток.
        :param user_id: id пользователя.
        :return: сообщение администратору.
        """
        with db_session():
            user = UserBot.get(user_id=user_id)
            if user and user.status == 'admin':
                links = self.get_link_from_message(text)
                tt_models = self.tiktok_manager.tt_models_create(links)
                if tt_models:
                    if all(tt is not None for tt in tt_models):
                        return 'Все тик-токи были успешно добавлены!'
                    elif all(tt is None for tt in tt_models):
                        return 'Ни один тик-ток не был добавлен!'
                    else:
                        return 'Один или несколько тик-токов не был добавлен!'

            return 'Что-то пошло не так!'

    async def greeting(self, text, user_id):
        """
        Метод добавления пожелания в бд.
        :param text: текст пожления.
        :param user_id: id пользователя.
        :return: сообщение администратору.
        """
        with db_session():
            user = UserBot.get(user_id=user_id)
            if user and user.status == 'admin':
                greeting = self.greeting_manager.greeting_model_create(text)
                if greeting:
                    return 'Поздравление успешно добавлено!'

            return 'Что-то пошло не так!'


class CommandManager:
    """
    Менеджер команд.
    """
    def __init__(self):
        self.add = Add()
        self.get = Get()
