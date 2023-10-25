import os

SECRET_KEY = 'dadjwbfjbwbfbw'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_2563_exam:12345678@std-mysql.ist.mospolytech.ru/std_2563_exam'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

USER_ROLE = 1
MODERATOR_ROLE = 2
ADMINISTRATOR_ROLE = 3

BOOKS_ON_INDEX_PAGE = 3


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
