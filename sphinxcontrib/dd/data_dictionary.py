from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive as BaseDirective

from sphinxcontrib.dd import yaml


class Directive(BaseDirective):

    required_arguments = 1  # Path to yml file
    final_argument_whitespace = True
    has_content = False

    option_spec = {
        'encoding': directives.encoding,
        'class': directives.class_option,
    }

    def run(self):
        env = self.state.document.settings.env
        # app = env.app
        # config = app.config

        # FIXME: Change this to options to specify header label
        headers = ['Name', 'Type', 'Length', 'Description']

        # FIXME: Change to options to specify the data to fetch
        columns = ['name', 'type', 'maxLength', 'description']

        rel_path, path = env.relfn2path(directives.path(self.arguments[0]))

        # Add the file as a dependency to the current document.
        # That means the document will be rebuilt if the file is changed.
        env.note_dependency(rel_path)

        spec = yaml.load(path)

        data = []

        for name, entity in spec['entities'].items():
            data.append(create_section(name=name))
            data.extend(generate_description(entity=entity))
            table = create_table(
                entity=entity,
                columns=columns,
                headers=headers,
            )
            data.append(table)

        return data


def create_section(name):
    # FIXME: Make this into h+1 (h1-h6) depending on the context

    paragraph = nodes.paragraph()
    strong = nodes.strong(text=name)
    paragraph.append(strong)

    return paragraph


def generate_description(entity):
    name = entity.get('name', None)
    if name:
        paragraph = nodes.paragraph(text='Name: ')
        paragraph.extend([nodes.literal(text=entity['name'])])
        yield paragraph

    # FIXME: Description may contains markdown/reST(?) syntax
    # http://www.sphinx-doc.org/en/stable/extdev/markupapi.html#parsing-directive-content-as-rest
    description = entity.get('description', None)
    if description:
        yield nodes.paragraph(text=description)


def create_row(data):
    row = nodes.row()
    for datum in data:
        row.append(nodes.entry(datum, nodes.paragraph(text=datum)))
    return row


def create_header(data):
    head = nodes.thead()
    head.append(create_row(data))
    return head


def create_body(entity, columns):
    body = nodes.tbody()
    for k, v in entity['columns']['properties'].items():
        data = []
        for column in columns:
            if column == 'name':
                data.append(k)
                continue

            data.append(v.get(column, ''))
        body.append(create_row(data=data))

    return body


def create_group(columns):
    group = nodes.tgroup(cols=columns)

    col_widths = [100 // columns] * columns
    group.extend(
        nodes.colspec(colwidth=col_width) for col_width in col_widths
    )

    return group


def create_table(entity, columns=None, headers=None, widths=None):
    # TODO: Add widths options directive
    _ = widths

    group = create_group(columns=len(headers))
    group.append(create_header(data=headers))
    group.append(create_body(entity=entity, columns=columns))

    table = nodes.table()
    table.append(group)
    return table
