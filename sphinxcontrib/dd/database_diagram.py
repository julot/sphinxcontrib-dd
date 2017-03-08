from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive as BaseDirective
from sphinx.ext.graphviz import render_dot_html, render_dot_latex

from sphinxcontrib.dd import yaml


class Graph(object):

    def __init__(self, spec, graph, node, edge):
        self.spec = spec
        self.graph = graph
        self.node = node
        self.edge = edge

    def dot(self):
        return sample


class Node(nodes.General, nodes.Element):
    pass


class Directive(BaseDirective):

    required_arguments = 1  # Path to yml file
    final_argument_whitespace = True
    has_content = False
    option_spec = {
        'graph-fontname': directives.unchanged,
        'graph-fontsize': directives.unchanged,
        'graph-label': directives.unchanged,

        'node-fontname': directives.unchanged,
        'node-fontsize': directives.unchanged,
    }

    def run(self):
        env = self.state.document.settings.env
        app = env.app
        config = app.config

        rel_path, path = env.relfn2path(directives.path(self.arguments[0]))

        # Add the file as a dependency to the current document.
        # That means the document will be rebuilt if the file is changed.
        env.note_dependency(rel_path)

        node = Node()
        node['spec'] = yaml.load(path)
        
        node['graph'] = {'margin': 0, 'nodesep': .5, 'ranksep': 1}
        node['node'] = {'shape': 'solid', 'style': 'rounded', 'margin': 0}
        node['edge'] = {'name': 'edge'}

        for option in self.option_spec:
            group, attr = option.split('-')
            value = self.options.get(
                group,
                getattr(config, 'database_diagram_%s' % option, ''),
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
    )
    render_dot_latex(
        self=self,
        node=node,
        code=graph.dot(),
        options={},
        prefix='db-diagram',
    )
    raise nodes.SkipNode


sample = '''
digraph DatabaseDiagram {

    graph [
        label="Database Diagram",
        labelloc="t",
        labeljust="c",
        charset="UTF-8",
        rankdir="TB",
        margin=0,
        ratio=auto,
        nodesep=.5,
        ranksep="1",
        fontsize=18,
        fontname="Calibri",
    ];

    node [
        shape="solid",
        style="rounded",
        layout=dot,
        margin=0,
        fontname="Calibri",
        fontsize=12,
    ];

    "f o o" [
        label=<
            <table border="0">
                <tr>
                    <td><b>Foo</b></td>
                </tr>
                <hr />
                <tr>
                    <td align="left"><table border="0" cellspacing="0">
                        <tr>
                            <td align="left">id</td>
                            <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
                            <td align="right">integer</td>
                        </tr>
                        <tr>
                            <td align="left">name</td>
                            <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
                            <td align="right">varchar(255)</td>
                        </tr>
                    </table></td>
                </tr>
            </table>
        >,
    ];

    bar [
        label=<
            <table border="0">
                <tr>
                    <td><b>Bar</b></td>
                </tr>
                <hr />
                <tr>
                    <td align="left"><table border="0" cellspacing="0">
                        <tr>
                            <td align="left">id</td>
                            <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
                            <td align="right">integer</td>
                        </tr>
                        <tr>
                            <td align="left">name</td>
                            <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
                            <td align="right">varchar(255)</td>
                        </tr>
                    </table></td>
                </tr>
            </table>
        >,
    ];

    "f o o" -> bar [dir=both, arrowhead=crowodot, arrowtail=noneteetee];

}
'''
