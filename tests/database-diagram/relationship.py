from sphinxcontrib.dd.database_diagram import Relationship


def test():
    relations = {
        'E1 |--| E2': (
            '"E1" -> "E2" '
            '[dir="both", arrowhead="nonetee", arrowtail="nonetee"]'
        ),
        'E1 ||--|| E2': (
            '"E1" -> "E2" '
            '[dir="both", arrowhead="noneteetee", arrowtail="noneteetee"]'
        ),
        'E1 |0--0| E2': (
            '"E1" -> "E2" '
            '[dir="both", arrowhead="noneteeodot", arrowtail="noneteeodot"]'
        ),
        'E1 >--< E2': (
            '"E1" -> "E2" '
            '[dir="both", arrowhead="crow", arrowtail="crow"]'
        ),
        'E1 >0--0< E2': (
            '"E1" -> "E2" '
            '[dir="both", arrowhead="crowodot", arrowtail="crowodot"]'
        ),
        'E1 >|--|< E2': (
            '"E1" -> "E2" '
            '[dir="both", arrowhead="crowtee", arrowtail="crowtee"]'
        ),
    }

    for relation, dot in relations.items():
        assert Relationship(relation).dot() == dot
