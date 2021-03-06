import unittest
from unittest import mock

import oh_behave
from oh_behave import reader

test_string ='{\n' \
'    "type": "Actor",\n' \
'    "id": "actor_01",\n' \
'    "name": "Billy Bob",\n' \
'    "rootnode": [\n' \
'        {\n' \
'            "type": "NodeSequence",\n' \
'            "id": "sequence_01",\n' \
'            "childnodes": [\n' \
'                {\n' \
'                    "type": "NodeLeafIterative",\n' \
'                    "id": "sequence_01",\n' \
'                    "execs": 5\n' \
'                },\n' \
'                {\n' \
'                    "type": "NodeLeafIterative",\n' \
'                    "id": "sequence_02",\n' \
'                    "execs": 5\n' \
'                }\n' \
'            ]\n' \
'        }\n' \
'    ]\n' \
'}'

def mock_classname_match_table():
    mock_table = {}
    for name, baseclass in reader.classname_match_table_default.items():
        mock_table[name] = mock.Mock(spec=baseclass)
    return mock_table

class TestObjectEntry(unittest.TestCase):
    """Tests ObjectEntry class"""
    def setUp(self):
        self.min_params = {'id':'fake', 'type':'faketype'}

    def test__init__default_parameters(self):
        """Tests that non-required parameters are given correct defaults"""
        entry = reader.ObjectEntry(self.min_params)
        self.assertIs(None, entry.rootnode)
        self.assertEqual([], entry.childnodes)
        self.assertIs(None, entry.decoratee)

    def test__init__gets_parameters(self):
        """__init__ grabs the parameters shown below"""
        root = 'node01'
        childnodes = ['node02', 'node03']
        decoratee='decoratednode'
        data = {'id':'mock',
                'type':'Fake',
                'rootnode':root,
                'childnodes':childnodes,
                'decoratee':decoratee
               }

        entry = reader.ObjectEntry(data)

        self.assertEqual(entry.rootnode, root)
        self.assertEqual(entry.childnodes, childnodes)
        self.assertEqual(entry.decoratee, decoratee)

    def test__init__no_classtype(self):
        """__init__ throws MissingParameterException if classtype not specifed"""
        with self.assertRaises(reader.MissingFieldException):
            params = self.min_params
            del params['type']
            reader.ObjectEntry(params)


class TestDataParser(unittest.TestCase):
    """Tests data parser class"""

    def setUp(self):
        self.table = mock_classname_match_table()
        self.parser = reader.DataParser(classname_match_table=self.table)

    def test__parse_object_string_dictionary(self):
        """Parse simple json representation of actor and add it to correct list"""
        input_string = '{\n' \
            '        "type": "Actor",\n' \
            '        "id": "actor_01",\n' \
            '        "name": "Billy Bob"\n' \
            '}'
        with mock.patch('oh_behave.reader.ObjectEntry', autospec=True) as mock_entry:
            self.parser._parse_object_string(input_string)
            mock_entry.assert_called_with({'type': 'Actor', 'id':'actor_01', 'name': 'Billy Bob'})
            self.assertIn(mock_entry.return_value, self.parser._entries)

    # This may be more of an integration test
    def test_link_objects(self):
        """Parse simple json representation of node and add it to correct list"""
        input_string1 = '{\n' \
            '    "id": "guy_node",\n' \
            '    "type": "NodeSelector"\n' \
            '}'
        input_string2 = '{\n' \
            '    "id": "actor01",\n' \
            '    "type": "Actor",\n' \
            '    "name": "Guy Mann",\n' \
            '    "rootnode": "guy_node"\n' \
            '}'
        self.parser._parse_object_string(input_string1)
        self.parser._parse_object_string(input_string2)
