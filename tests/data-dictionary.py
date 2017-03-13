from sphinxcontrib.dd import data_dictionary


def test_string_list():
    l = data_dictionary.string_list('')
    assert l == []

    l = data_dictionary.string_list('Name Type Length')
    assert l == ['Name', 'Type', 'Length']

    l = data_dictionary.string_list('Name, Type, Max Length')
    assert l == ['Name', 'Type', 'Max Length']
