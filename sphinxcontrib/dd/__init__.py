from . import data_dictionary
from . import database_diagram


def setup(app):
    data_dictionary.setup(app=app)
    database_diagram.setup(app=app)
