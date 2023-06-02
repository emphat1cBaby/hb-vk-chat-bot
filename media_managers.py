import random
from pony.orm import db_session, select, commit
from models import *


class MediaManager:
    """
    Базовый класс медиа менеджера.
    """

    model = None  # модель бд, с которой работает менеджер
    attr_name = None  # название атрибута, который возвращает метод создания объекта из записи дб
    __model_fields = []  # поля модели бд (заполняется автоматически)

    def __init__(self):
        if any(attr is None for attr in [self.model, self.attr_name]):
            raise Exception("Обязательные атрибуты класса не заполнены!")

        self.__model_fields = db.entities.get(self.model.__name__)._columns_

    @db_session
    def active_false(self, object):
        """
        Метод деактивации объекта.
        :param object: объект из бд.
        """
        object.is_active = False
        commit()

    @db_session
    def get_random_objects_from_db(self):
        """
        Метод получения случайного объекта из бд.
        :return: объект, количество активных объектов оставшихся в базе.
        """
        objects = self.get_free_objects_from_db()
        if not objects:
            return None, 0

        return random.choice(objects), len(objects) - 1

    @db_session
    def get_free_objects_from_db(self):
        """
        Метод получения списка активных объектов из бд.
        :return: список активных объектов из бд.
        """
        if not self.model:
            return False

        return list(select(photo for photo in self.model if photo.is_active))

    @db_session
    def create_object_from_db_model(self):
        """
        Метод создания объекта из записи дб.
        :return: объект, количество объектов, которые остались в базе.
        """

        if self.attr_name is None:
            return None, 0

        object, objects_count = self.get_random_objects_from_db()
        if object is None:
            return None, 0

        self.active_false(object)
        return getattr(object, self.attr_name), objects_count

    @db_session
    def create_model(self, data: dict):
        """
        Метод создания записи в бд.
        :param data: данные для записи.
        :return: объект созданной записи.
        """
        if not data or data.keys() != self.__model_fields:
            return None

        return self.model(**data)


class ImageManager(MediaManager):
    """
    Класс менеджер изображений.
    """
    model = PhotoMem
    attr_name = "link"

    @db_session
    def image_models_create(self, images_data):
        """
        Метод создания новой записи изображения в бд.
        :param images_data: список изображений.
        :return: список записей изображений.
        """
        return [self.create_model({"link": image.link, "width": image.width, "height": image.height, "is_active": True})
                for image in images_data]


class TikTokManager(MediaManager):
    """
    Класс менеджер тик токов.
    """
    model = TikTok
    attr_name = "link"

    @db_session
    def tt_models_create(self, tt_data):
        """
        Метод создания новой записи видео в дб.
        :param tt_data: список видео.
        :return: список моделей видео из бд.
        """

        if tt_data:
            return [self.create_model({"link": tt, "is_active": True}) for tt in tt_data]


class GreetingManager(MediaManager):
    """
    Класс менеджер пожеланий.
    """
    model = Greeting
    attr_name = "text"

    @db_session
    def greeting_model_create(self, text):
        """
        Метод создания записи пожелания в бд.
        :param text: текст пожелания.
        :return: запись бд.
        """
        return self.create_model({"text": text, "is_active": True})
