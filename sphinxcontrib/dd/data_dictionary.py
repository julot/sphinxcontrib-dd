import io

from docutils import nodes
from docutils.parsers.rst import directives
from yaml import load as load_yaml
from sphinx.util.compat import Directive as BaseDirective

from . import yaml


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

        rel_path, path = env.relfn2path(directives.path(self.arguments[0]))

        # Add OpenAPI spec as a dependency to the current document.
        # That means the document will be rebuilt if the spec is changed.
        env.note_dependency(rel_path)

        # Read the spec using encoding passed to the directive or fallback to
        # the one specified in Sphinx's config.
        encoding = self.options.get('encoding', env.config.source_encoding)
        with io.open(path, 'rt', encoding=encoding) as stream:
            spec = load_yaml(stream, yaml.Loader)
        spec = yaml.resolve_refs('file://%s' % path, spec)

        data = []

        for name, entity in spec['entities'].items():
            data.extend(self.create_section(name=name))
            data.extend(self.create_description(entity=entity))
            data.extend(self.create_table(entity=entity))

        return data

    @staticmethod
    def create_section(name):
        # FIXME: Make this into h+1 (h1-h6) depending on the context

        # section = nodes.section(names=[name])
        # title = nodes.title(text=name)
        # section += title
        # tables.append(section)

        paragraph = nodes.paragraph()
        strong = nodes.strong(text=name)
        paragraph.append(strong)

        return [paragraph]

    @staticmethod
    def create_description(entity):
        name = entity.get('name', None)
        if name:
            paragraph = nodes.paragraph(text='Name: ')
            paragraph.extend([nodes.literal(text=entity['name'])])
            yield paragraph

        description = entity.get('description', None)
        if description:
            yield nodes.paragraph(text=description)

    @staticmethod
    def create_table(entity):
        # FIXME: Change this to directive options named headers
        headers = ['Name', 'Type', 'Description']

        # TODO: Add directive options name columns to specify the data to fetch
        # TODO: Add widths options directive

        table = nodes.table()

        max_cols = len(headers)
        col_widths = [100 // max_cols] * max_cols

        group = nodes.tgroup(cols=max_cols)
        group.extend(
            nodes.colspec(colwidth=col_width) for col_width in col_widths
        )
        table.append(group)

        # Add header
        head = nodes.thead()
        group.append(head)
        row = nodes.row()
        for header in headers:
            row.append(nodes.entry(header, nodes.paragraph(text=header)))
        head.append(row)

        body = nodes.tbody()
        group.append(body)
        for k, v in entity['columns']['properties'].items():
            data = (
                k,
                v.get('type', ''),
                v.get('description', ''),
            )

            row = nodes.row()
            for datum in data:
                row.append(nodes.entry(datum, nodes.paragraph(text=datum)))
            body.append(row)

        return [table]
