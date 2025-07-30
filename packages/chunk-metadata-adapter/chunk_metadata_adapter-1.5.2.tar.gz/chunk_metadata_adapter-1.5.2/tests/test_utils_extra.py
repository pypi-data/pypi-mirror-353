import pytest
from chunk_metadata_adapter import utils
import enum
from chunk_metadata_adapter.utils import dict_prop_to_flat_dict, flat_dict_to_dict_prop, str_to_list, list_to_str

class DummyField:
    def __init__(self, name, annotation, min_length=None, max_length=None, ge=None, le=None, decimal_places=None, pattern=None):
        self.name = name
        self.annotation = annotation
        self.min_length = min_length
        self.max_length = max_length
        self.ge = ge
        self.le = le
        self.decimal_places = decimal_places
        self.pattern = pattern

# --- coerce_value_with_modifiers ---
def test_coerce_str_min_max():
    f = DummyField('s', str, min_length=3, max_length=5)
    assert utils.coerce_value_with_modifiers('a', f) == 'axx'
    assert utils.coerce_value_with_modifiers('abcdef', f) == 'abcde'
    assert utils.coerce_value_with_modifiers(None, f) is None

def test_coerce_int_float_ge_le():
    f = DummyField('i', int, ge=10, le=20)
    assert utils.coerce_value_with_modifiers(5, f) == 10
    assert utils.coerce_value_with_modifiers(25, f) == 20
    f2 = DummyField('f', float, ge=0.5, le=1.5, decimal_places=2)
    assert utils.coerce_value_with_modifiers(0.1, f2) == 0.5
    assert utils.coerce_value_with_modifiers(2.0, f2) == 1.5
    assert utils.coerce_value_with_modifiers(1.2345, f2) == 1.23

def test_coerce_bool():
    f = DummyField('b', bool)
    assert utils.coerce_value_with_modifiers(True, f) is True
    assert utils.coerce_value_with_modifiers('yes', f) is True
    assert utils.coerce_value_with_modifiers('no', f) is False
    assert utils.coerce_value_with_modifiers(0, f) is False

def test_coerce_list_min_max():
    f = DummyField('l', list, min_length=2, max_length=3)
    assert utils.coerce_value_with_modifiers([1], f) == [1, None]
    assert utils.coerce_value_with_modifiers([1,2,3,4], f) == [1,2,3]
    assert utils.coerce_value_with_modifiers('a,b', f) == ['a','b']
    assert utils.coerce_value_with_modifiers(None, f) == []

def test_coerce_chunkid():
    class DummyChunkId(str):
        pass
    f = DummyField('cid', utils.ChunkId)
    assert utils.coerce_value_with_modifiers(None, f) is None
    assert utils.coerce_value_with_modifiers(utils.ChunkId.empty_uuid4(), f) is None
    val = str(utils.ChunkId.empty_uuid4())
    assert utils.coerce_value_with_modifiers(val, f) is None
    assert utils.coerce_value_with_modifiers('123', f) == '123'

# --- semantic_to_flat_value ---
def test_semantic_to_flat_str():
    f = DummyField('s', str, min_length=3, max_length=5)
    assert utils.semantic_to_flat_value('a', f, 's') == 'axx'
    assert utils.semantic_to_flat_value('abcdef', f, 's') == 'abcde'
    assert utils.semantic_to_flat_value(None, f, 's') == 'xxx'

def test_semantic_to_flat_int_float():
    f = DummyField('i', int, ge=10, le=20)
    assert utils.semantic_to_flat_value(5, f, 'i') == 10
    assert utils.semantic_to_flat_value(25, f, 'i') == 20
    f2 = DummyField('f', float, ge=0.5, le=1.5, decimal_places=2)
    assert utils.semantic_to_flat_value(0.1, f2, 'f') == 0.5
    assert utils.semantic_to_flat_value(2.0, f2, 'f') == 1.5
    assert utils.semantic_to_flat_value(1.2345, f2, 'f') == 1.23

def test_semantic_to_flat_bool():
    f = DummyField('b', bool)
    assert utils.semantic_to_flat_value(True, f, 'b') is True
    assert utils.semantic_to_flat_value(None, f, 'b') is False

def test_semantic_to_flat_list():
    f = DummyField('l', list, min_length=2, max_length=3)
    assert utils.semantic_to_flat_value([1], f, 'l') == '1,None'
    assert utils.semantic_to_flat_value([1,2,3,4], f, 'l') == '1,2,3'
    assert utils.semantic_to_flat_value(None, f, 'l') == 'None,None'

def test_semantic_to_flat_dict():
    f = DummyField('d', dict)
    d = {'a': 1, 'b': 2}
    assert utils.semantic_to_flat_value(d, f, 'd') == 'd.a=1,d.b=2'
    assert utils.semantic_to_flat_value(None, f, 'd') == ''

def test_semantic_to_flat_object_passthrough():
    class DummyModel:
        pass
    f = DummyField('m', object)
    m = DummyModel()
    assert utils.semantic_to_flat_value(m, f, 'm') is m

# --- autofill_enum_field ---
class Color(enum.Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    @classmethod
    def default_value(cls):
        return cls.RED

def test_autofill_enum_field():
    assert utils.autofill_enum_field(None, Color) is None
    assert utils.autofill_enum_field('', Color) is None
    assert utils.autofill_enum_field('red', Color) == 'red'
    assert utils.autofill_enum_field('notacolor', Color) == 'red'
    assert utils.autofill_enum_field(Color.GREEN, Color) == 'green'
    assert utils.autofill_enum_field('blue', Color) == 'blue'

# --- str_to_list / list_to_str ---
def test_str_to_list():
    assert utils.str_to_list('a,b,c') == ['a','b','c']
    assert utils.str_to_list('') == []
    assert utils.str_to_list(None) == []
    # If value is a list, returns its copy
    assert utils.str_to_list(['a','b']) == ['a','b']
    with pytest.raises(ValueError):
        utils.str_to_list(123)

def test_list_to_str():
    assert utils.list_to_str(['a','b','c']) == 'a,b,c'
    assert utils.list_to_str([]) == ''
    assert utils.list_to_str(None) == ''
    with pytest.raises(ValueError):
        utils.list_to_str('abc')
    with pytest.raises(ValueError):
        utils.list_to_str([1,2])

# --- dict_prop_to_flat_dict / flat_dict_to_dict_prop ---
def test_dict_prop_to_flat_dict():
    d = {'a': 'x', 'b': ['y','z'], 'c': {'d': 'e'}}
    flat = utils.dict_prop_to_flat_dict(d)
    assert flat['a'] == 'x'
    # List is returned as is
    assert flat['b'] == ['y','z']
    assert flat['c.d'] == 'e'
    with pytest.raises(ValueError):
        utils.dict_prop_to_flat_dict(123)

def test_flat_dict_to_dict_prop():
    flat = {'a': 'x', 'b': 'y,z', 'c.d': 'e'}
    d = utils.flat_dict_to_dict_prop(flat)
    assert d['a'] == 'x'
    assert d['b'] == 'y,z'
    assert d['c']['d'] == 'e'
    with pytest.raises(ValueError):
        utils.flat_dict_to_dict_prop(123)

# --- autofill_min_length_str_fields ---
def test_autofill_min_length_str_fields():
    fields = {
        'a': DummyField('a', str, min_length=3),
        'b': DummyField('b', str, min_length=0),
        'c': DummyField('c', str, min_length=2),
    }
    data = {'a': '', 'b': None, 'c': 'x'}
    utils.autofill_min_length_str_fields(data, fields)
    assert data['a'] == 'xxx'
    assert data['b'] == ''
    assert data['c'] == 'xx'

def test_dict_to_flat_and_back_simple():
    d = {'a': 'x', 'b': {'c': 'y'}, 'd': [1,2], 'e': 42}
    flat = dict_prop_to_flat_dict(d)
    # 'a' and 'e' are simple keys
    assert flat['a'] == 'x'
    assert flat['e'] == 42
    # 'b' is nested dict
    assert flat['b.c'] == 'y'
    # 'd' is a list, should be as is
    assert flat['d'] == [1,2]
    # Back conversion
    restored = flat_dict_to_dict_prop(flat)
    assert restored['a'] == 'x'
    assert restored['e'] == 42
    assert restored['b']['c'] == 'y'
    assert restored['d'] == [1,2]

def test_flat_dict_to_dict_prop_edge_cases():
    # Key with no dot
    flat = {'foo': 'bar'}
    d = flat_dict_to_dict_prop(flat)
    assert d['foo'] == 'bar'
    # Key with one dot
    flat = {'x.y': 1}
    d = flat_dict_to_dict_prop(flat)
    assert d['x']['y'] == 1
    # Key with more than one dot
    flat = {'a.b.c': 2}
    with pytest.raises(ValueError):
        flat_dict_to_dict_prop(flat)

def test_dict_prop_to_flat_dict_edge_cases():
    # Nested dict
    d = {'a': {'b': {'c': 1}}}
    flat = utils.dict_prop_to_flat_dict(d)
    # Only one level of nesting is flattened
    assert 'a.b' in flat
    assert isinstance(flat['a.b'], dict)
    # List as value
    d = {'lst': [1,2,3]}
    flat = utils.dict_prop_to_flat_dict(d)
    assert flat['lst'] == [1,2,3]
    # None as value
    d = {'n': None}
    flat = utils.dict_prop_to_flat_dict(d)
    assert flat['n'] is None

def test_semantic_flat_roundtrip():
    # Simulate semantic dict with dict/list fields
    semantic = {
        'uuid': 'u1',
        'meta': {'author': 'vasya', 'year': 2024},
        'tags': ['a', 'b', 'c'],
        'score': 0.9,
        'empty': {},
        'none': None
    }
    flat = utils.dict_prop_to_flat_dict(semantic)
    # meta.author and meta.year become flat keys
    assert flat['meta.author'] == 'vasya'
    assert flat['meta.year'] == 2024
    # tags is a list, should be as is
    assert flat['tags'] == ['a','b','c'] or flat['tags'] == ['a', 'b', 'c']
    # uuid, score
    assert flat['uuid'] == 'u1'
    assert flat['score'] == 0.9
    # 'empty' is not present, 'none' is present and is None
    assert 'empty' not in flat
    assert 'none' in flat and flat['none'] is None
    # Back conversion
    restored = utils.flat_dict_to_dict_prop(flat)
    assert restored['meta']['author'] == 'vasya'
    assert restored['meta']['year'] == 2024
    assert restored['tags'] == ['a','b','c'] or restored['tags'] == ['a', 'b', 'c']
    assert restored['uuid'] == 'u1'
    assert restored['score'] == 0.9
    # 'empty' is not present, 'none' is present and is None
    assert 'empty' not in restored
    assert 'none' in restored and restored['none'] is None

def test_metadata_dict_semantic_flat_semantic():
    # Initial semantic dict with non-empty metadata
    semantic = {
        'uuid': 'u2',
        'meta': {
            'author': 'petya',
            'year': 2023,
            'info': {'lang': 'ru', 'pages': 100}
        },
        'tags': ['x', 'y'],
        'score': 1.0
    }
    # Flatten
    flat = dict_prop_to_flat_dict(semantic)
    # meta.author and meta.year become flat keys
    assert flat['meta.author'] == 'petya'
    assert flat['meta.year'] == 2023
    # meta.info is a nested dict, so flat['meta.info'] is itself a dict
    assert isinstance(flat['meta.info'], dict)
    assert flat['meta.info']['lang'] == 'ru'
    assert flat['meta.info']['pages'] == 100
    # tags is a list
    assert flat['tags'] == ['x','y']
    assert flat['uuid'] == 'u2'
    assert flat['score'] == 1.0
    # Back conversion
    restored = flat_dict_to_dict_prop(flat)
    assert restored['meta']['author'] == 'petya'
    assert restored['meta']['year'] == 2023
    assert restored['meta']['info']['lang'] == 'ru'
    assert restored['meta']['info']['pages'] == 100
    assert restored['tags'] == ['x','y']
    assert restored['uuid'] == 'u2'
    assert restored['score'] == 1.0 