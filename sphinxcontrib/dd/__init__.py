from docutils.nodes import SkipNode

from . import data_dictionary
from . import database_diagram


def skip(self, node):
    _ = self
    _ = node
    raise SkipNode


def setup(app):
    app.setup_extension('sphinx.ext.graphviz')

    app.add_directive('data-dictionary', data_dictionary.Directive)

    for option in database_diagram.Directive.option_spec:
        config = 'database_diagram_{0}'.format(option.replace('-', '_'))
        app.add_config_value(config, None, 'env')

    app.add_node(
        database_diagram.Node,
        html=(database_diagram.visit_html, skip),
        latex=(database_diagram.visit_latex, skip),
        text=(skip, skip),
        man=(skip, skip),
        texinfo=(skip, skip),
    )

    app.add_directive('database-diagram', database_diagram.Directive)
