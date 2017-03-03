from . import data_dictionary


def setup(app):
    app.add_directive('data-dictionary', data_dictionary.Directive)
