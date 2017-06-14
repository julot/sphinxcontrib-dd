from docutils import nodes
# from docutils.statemachine import ViewList
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive as BaseDirective
from recommonmark.parser import CommonMarkParser

from . import yaml


def string_list(argument):
    if ',' in argument:
        entries = argument.split(',')
    else:
        entries = argument.split()
    return [entry.strip() for entry in entries]


class Parser(CommonMarkParser):

    def setup_parse(self, inputstring, document):
        """Initial parse setup.  Call at start of `self.parse()`."""
        self.inputstring = inputstring
        self.document = document
        # document.reporter.attach_observer(document.note_parse_message)

    def finish_parse(self):
        """Finalize parse details.  Call at end of `self.parse()`."""
        # self.document.reporter.detach_observer(
        #     self.document.note_parse_message)
        pass


class Directive(BaseDirective):

    required_arguments = 1  # Path to yml file
    optional_arguments = 1  # Path to yml definition file
    final_argument_whitespace = True
    has_content = False

    option_spec = {
        'widths': directives.positive_int_list,
        'headers': string_list,
        'columns': string_list,
    }

    def run(self):
        env = self.state.document.settings.env
        app = env.app
        config = app.config

        widths = self.options.get(
            'widths',
            getattr(config, 'data_dictionary_{0}'.format('widths')),
        )

        headers = self.options.get(
            'headers',
            getattr(config, 'data_dictionary_{0}'.format('headers')),
        )

        columns = self.options.get(
            'columns',
            getattr(config, 'data_dictionary_{0}'.format('columns')),
        )

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

        spec = yaml.load(path=path, definition_path=def_path)

        data = []

        for name, entity in spec['tables'].items():
            data.append(self.create_section(name=name))
            data.extend(self.generate_description(entity=entity))
            table = self.create_table(
                entity=entity,
                columns=columns,
                headers=headers,
                widths=widths,
            )
            data.append(table)

        return data

    @staticmethod
    def parse_string(text):
        if not text:
            return []

        element = nodes.paragraph()
        # self.state.nested_parse(ViewList(str(text).splitlines()), 0, element)
        parser = Parser()
        parser.parse(str(text), element)
        return element.children

    def generate_description(self, entity):
        name = entity.get('name', None)
        if name:
            paragraph = nodes.paragraph(text='Name: ')
            paragraph.extend([nodes.literal(text=entity['name'])])
            yield paragraph

        description = entity.get('description', None)
        if description:
            for each in self.parse_string(description):
                yield each

    def create_table(self, entity, columns=None, headers=None, widths=None):
        group = self.create_group(widths)
        group.append(self.create_header(data=headers))
        group.append(self.create_body(entity=entity, columns=columns))

        table = nodes.table(classes=['data-dictionary'])
        table.append(group)
        return table

    @staticmethod
    def create_group(widths):
        group = nodes.tgroup(cols=len(widths))

        group.extend(
            nodes.colspec(colwidth=width) for width in widths
        )

        return group

    def create_header(self, data):
        head = nodes.thead()
        head.append(self.create_row(data))
        return head

    def create_row(self, data):
        row = nodes.row()
        for datum in data:
            row.append(nodes.entry(datum, *self.parse_string(text=datum)))
        return row

    def create_body(self, entity, columns):
        body = nodes.tbody()
        for k, v in entity['columns']['properties'].items():
            data = []
            for column in columns:
                if column == 'name':
                    data.append(k)
                    continue

                data.append(v.get(column, ''))
            body.append(self.create_row(data=data))

        return body

    @staticmethod
    def create_section(name):
        section = nodes.section(ids=[name])
        section.append(nodes.title(text=name))
        return section


def setup(app):
    app.add_config_value(
        'data_dictionary_{0}'.format('widths'),
        [1, 1, 1, 4],
        'env',
    )
    app.add_config_value(
        'data_dictionary_{0}'.format('headers'),
        ['Name', 'Type', 'Length', 'Description'],
        'env',
    )
    app.add_config_value(
        'data_dictionary_{0}'.format('columns'),
        ['name', 'type', 'maxLength', 'description'],
        'env',
    )

    app.add_directive('data-dictionary', Directive)
