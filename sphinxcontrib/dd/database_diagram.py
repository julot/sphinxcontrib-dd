from docutils import nodes
from sphinx.util.compat import Directive as BaseDirective
from sphinx.ext.graphviz import render_dot_html, render_dot_latex


sample = '''
digraph DatabaseDiagram {

    graph [
        /* label="Test"
        labelloc="t",
        labeljust="c", */
        charset="UTF-8",
        rankdir="TB",
        margin=0,
        ratio=auto,
        nodesep=.5,
        ranksep=1,
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


class Node(nodes.General, nodes.Element):

    pass


class Directive(BaseDirective):

    required_arguments = 1  # Path to yml file
    final_argument_whitespace = True
    has_content = False

    def run(self):
        return [Node()]


def visit_html(self, node):
    render_dot_html(
        self=self,
        node=node,
        code=sample,
        options={},
        prefix='db-diagram',
        imgcls='db-diagram',
        alt='Database Diagram',
    )
    raise nodes.SkipNode


def visit_latex(self, node):
    render_dot_latex(
        self=self,
        node=node,
        code=sample,
        options={},
        prefix='db-diagram',
    )
    raise nodes.SkipNode
