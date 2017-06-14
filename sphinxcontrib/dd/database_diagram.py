import re

from collections import OrderedDict
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive as BaseDirective
from sphinx.ext.graphviz import render_dot_html, render_dot_latex

from . import yaml


def serialize(dictionary):
    """
    Turn dictionary into argument like string.

    """

    data = []
    for key, value in dictionary.items():
        data.append('{0}="{1}"'.format(key, value))
    return ', '.join(data)


class Graph(object):

    def __init__(self, spec, graph, node, edge=None, root=None):
        self.spec = spec
        self.graph = graph
        self.node = node
        self.edge = edge or {}
        self.root = root or {}

    def dot(self):
        data = [
            'graph [{0}]'.format(serialize(self.graph)),
            'node [{0}]'.format(serialize(self.node)),
            'edge [{0}]'.format(serialize(self.edge)),
        ]

        for entity, spec in self.spec['tables'].items():
            data.append(Entity(entity, spec).dot())

        for relationship in self.spec.get('relationships', {}):
            data.append(Relationship(relationship).dot())

        for key, value in self.root.items():
            if key == 'samerank':
                template = '{{rank="same"; {0};}}'
                groups = [v.strip() for v in value.split(',')]
                for group in groups:
                    entities = ['"{0}"'.format(v) for v in group.split()]
                    data.append(template.format('; '.join(entities)))

        return 'digraph DatabaseDiagram {{\n{0}\n}}'.format(';\n'.join(data))


class Entity(object):

    def __init__(self, name, spec):
        self.name = name
        self.spec = spec

    def dot(self):
        labels = [
            '<table border="0">',
            '<tr>',
            '<td><b>{0}</b></td>'.format(self.name),
            '</tr>',

            '<hr />',

            '<tr>',
            '<td align="left">',
            '<table border="0" cellspacing="0">',
        ]

        for name, spec in self.spec['columns']['properties'].items():
            labels.append(Property(name, spec).dot())

        labels += [
            '</table>',
            '</td>',
            '</tr>',
            '</table>',
        ]

        return '"{name}" [label=<{label}>]'.format(
            name=self.name,
            label=''.join(labels),
        )


class Property(object):

    def __init__(self, name, spec):
        self.name = name
        self.spec = spec

    @property
    def type(self):
        kind = self.spec.get('type', '')
        if not kind:
            return ''

        length = self.spec.get('maxLength', '')
        if not length:
            return kind

        return '{kind}({length})'.format(kind=kind, length=length)

    def dot(self):
        data = [
            '<tr>',
            '<td align="left">{0}</td>'.format(self.name),
            '<td>&nbsp;&nbsp;&nbsp;&nbsp;</td>',
            '<td align="right">{0}</td>'.format(self.type),
            '</tr>',
        ]
        return ''.join(data)


class Relationship(object):

    pattern = re.compile(r'^(.*) ([>|0]{1,2})?--([0|<]{1,2}) (.*)$')
    arrows = {
        '0': 'odot',
        '|': 'tee',
        '>': 'crow',
        '<': 'crow',
    }

    def __init__(self, spec):
        self.spec = spec

    def dot(self):
        matches = self.pattern.match(self.spec)
        if not matches:
            return ''

        heads = []
        for index, arrow in enumerate(matches.group(3)[::-1]):
            if index == 0 and arrow == '|':
                heads.append('none')
            heads.append(self.arrows[arrow])

        tails = []
        for index, arrow in enumerate(matches.group(2)):
            if index == 0 and arrow == '|':
                tails.append('none')
            tails.append(self.arrows[arrow])

        options = OrderedDict(
            dir='both',
            arrowhead=''.join(heads),
            arrowtail=''.join(tails),
        )

        # if matches.group(1) == 'Test1' and matches.group(4) == 'Test5':
        #     options['minlen'] = 2

        node = '"{0}" -> "{1}" [{2}]'.format(
            matches.group(1),
            matches.group(4),
            serialize(options),
        )

        return node


class Node(nodes.General, nodes.Element):
    pass


class Directive(BaseDirective):

    required_arguments = 1  # Path to yml file
    optional_arguments = 1  # Path to yml definition file
    final_argument_whitespace = True
    has_content = False
    option_spec = {
        'graph-fontname': directives.unchanged,
        'graph-fontsize': directives.unchanged,
        'graph-label': directives.unchanged,
        'graph-labeljust': directives.unchanged,
        'graph-labelloc': directives.unchanged,
        'graph-margin': directives.unchanged,
        'graph-nodesep': directives.unchanged,
        'graph-ranksep': directives.unchanged,

        'node-fontname': directives.unchanged,
        'node-fontsize': directives.unchanged,
        'node-shape': directives.unchanged,
        'node-style': directives.unchanged,

        'root-samerank': directives.unchanged,
    }

    # Values to be excluded from database_diagram_ config
    private_options = ['root-samerank']

    def run(self):
        env = self.state.document.settings.env
        app = env.app
        config = app.config

        rel_path, path = env.relfn2path(directives.path(self.arguments[0]))

        def_rel_path = ''
        def_path = ''
        try:
            def_rel_path, def_path = env.relfn2path(
                directives.path(self.arguments[1])
            )
        except IndexError:
            pass

        # Add the file as a dependency to the current document.
        # That means the document will be rebuilt if the file is changed.
        env.note_dependency(rel_path)
        if def_rel_path:
            env.note_dependency(def_rel_path)

        node = Node()
        node['spec'] = yaml.load(path=path, definition_path=def_path)

        node['graph'] = {
            'margin': 0,
            'nodesep': .75,
            'ranksep': .75,
            'rankdir': 'LR',
        }
        node['node'] = {
            'shape': 'box',
            'style': 'rounded',
            'margin': 0,
        }
        node['edge'] = {}
        node['root'] = {}

        for option in self.option_spec:
            group, attr = option.split('-')
            value = self.options.get(
                option,
                getattr(
                    config,
                    'database_diagram_{0}'.format(option.replace('-', '_')),
                    None,
                ),
            )
            if value:
                node[group][attr] = value

        return [node]


def visit_html(self, node):
    graph = Graph(
        spec=node['spec'],
        graph=node['graph'],
        node=node['node'],
        edge=node['edge'],
        root=node['root'],
    )
    render_dot_html(
        self=self,
        node=node,
        code=graph.dot(),
        options={},
        prefix='db-diagram',
        imgcls='db-diagram',
        alt='Database Diagram',
    )
    raise nodes.SkipNode


def visit_latex(self, node):
    graph = Graph(
        spec=node['spec'],
        graph=node['graph'],
        node=node['node'],
        edge=node['edge'],
        root=node['root'],
    )
    render_dot_latex(
        self=self,
        node=node,
        code=graph.dot(),
        options={},
        prefix='db-diagram',
    )
    raise nodes.SkipNode


def skip(self, node):
    _ = self
    _ = node
    raise nodes.SkipNode


def setup(app):
    app.setup_extension('sphinx.ext.graphviz')

    for option in Directive.option_spec:
        if option in Directive.private_options:
            continue

        config = 'database_diagram_{0}'.format(option.replace('-', '_'))
        app.add_config_value(config, None, 'env')

    app.add_node(
        Node,
        html=(visit_html, skip),
        latex=(visit_latex, skip),
        text=(skip, skip),
        man=(skip, skip),
        texinfo=(skip, skip),
    )

    app.add_directive('database-diagram', Directive)
