import random
from pony.orm import db_session, select, commit
from models import PhotoMem, Greeting, TikTokMovies


class MediaManager:

    @db_session
    def active_false(self, obj):
        obj.is_active = False
        commit()


class ImageManager(MediaManager):

    @db_session
    def get_random_image_from_db(self):
        photos = self.get_free_images_from_db()

        return random.choice(photos), len(photos) - 1

    @db_session
    def get_free_images_from_db(self):
        return list(select(photo for photo in PhotoMem if photo.is_active))

    @db_session
    def images_model_create(self, images_data):
        return [PhotoMem(link=image.url, width=image.width, height=image.height, is_active=True)
                for image in images_data]

    @db_session
    def create_image_from_db_model(self):
        model, images_count = self.get_random_image_from_db()
        self.active_false(model)

        return model.link, images_count


class TikTokManager(MediaManager):

    @db_session
    def get_random_tt_from_db(self):
        tts = self.get_free_tt_from_db()
        return random.choice(tts), len(tts) - 1

    @db_session
    def get_free_tt_from_db(self):
        return list(select(tt for tt in TikTokMovies if tt.is_active))

    @db_session
    def tt_model_create(self, tt_data):
        if tt_data:
            return [TikTokMovies(link=tt, is_active=True) for tt in tt_data]

    @db_session
    def create_tt_from_db_model(self):
        model, tt_count = self.get_random_tt_from_db()
        self.active_false(model)

        return model.link, tt_count


class GreetingManager(MediaManager):

    @staticmethod
    def add(text: str):
        return Greeting(text=text, is_active=True)

    def get_random(self):
        greeting = random.choice(self.get_greetings_list())

        self.active_false(greeting.id)
        return greeting

    @staticmethod
    def get_greetings_list():
        with db_session:
            greetings = select(greeting for greeting in Greeting if greeting.is_active)
            return list(greetings)
