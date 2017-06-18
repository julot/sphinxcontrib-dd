import os

from sphinxcontrib.dd.yaml import load


def get_yaml_path():
    path = os.path.dirname(os.path.realpath(__file__))
    return os.path.abspath(os.path.join(path, '..'))


def test():
    spec = load(path=os.path.join(get_yaml_path(), 'example.yml'))

    plain = load(path=os.path.join(get_yaml_path(), 'example-plain.yml'))

    assert spec['definitions']['Identity'] == plain['definitions']['Identity']
    assert spec['definitions']['Common'] == plain['definitions']['Common']
    assert spec['definitions']['User'] == plain['definitions']['User']
    assert spec['definitions']['Role'] == plain['definitions']['Role']
    assert spec['definitions']['UserRole'] == plain['definitions']['UserRole']
    assert spec == plain
