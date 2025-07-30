import pytest
import uuid
from datetime import datetime, timezone
from chunk_metadata_adapter.models import FlatSemanticChunk, SemanticChunk, ChunkType, ChunkRole, ChunkStatus, ChunkMetrics, LanguageEnum
from chunk_metadata_adapter.utils import ChunkId
import hashlib

def test_flat_chunk_tags_edge_cases():
    # tags: None, пустой список, строка, список с пустыми элементами
    for tags_in, expected in [
        (None, ''),
        ([], ''),
        ('tag1,tag2', 'tag1,tag2'),
        (['tag1', '', 'tag2'], 'tag1,tag2'),
        (['', ''], ''),
    ]:
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": hashlib.sha256(b"abc").hexdigest(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 0,
            "end": 1,
            "tags": tags_in,
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert err is None
        assert obj.tags == expected

def test_flat_chunk_link_parent_related():
    # Проверка преобразования links <-> link_parent/link_related
    sem = SemanticChunk(
        uuid=ChunkId.default_value(),
        text="abc",
        body="abc",
        language=LanguageEnum.EN,
        type=ChunkType.DOC_BLOCK.value,
        start=0,
        end=1,
        sha256=hashlib.sha256(b"abc").hexdigest(),
        created_at=datetime.now(timezone.utc).isoformat(),
        summary="",
        tags=["t1"],
        links=[f"parent:{ChunkId.default_value()}", f"related:{ChunkId.default_value()}"],
    )
    flat = FlatSemanticChunk.from_semantic_chunk(sem)
    assert isinstance(flat, FlatSemanticChunk)
    # to_semantic_chunk обратно
    sem2 = flat.to_semantic_chunk()
    assert isinstance(sem2, SemanticChunk)
    assert set([l.split(':')[0] for l in sem2.links]) <= {"parent", "related"}

def test_flat_chunk_source_lines():
    # source_lines_start/source_lines_end <-> source_lines
    sem = SemanticChunk(
        uuid=ChunkId.default_value(),
        text="abc",
        body="abc",
        language=LanguageEnum.EN,
        type=ChunkType.DOC_BLOCK.value,
        start=0,
        end=1,
        sha256=hashlib.sha256(b"abc").hexdigest(),
        created_at=datetime.now(timezone.utc).isoformat(),
        summary="",
        tags=[],
        links=[],
    )
    sem.source_lines = [10, 20]
    flat = FlatSemanticChunk.from_semantic_chunk(sem)
    assert flat.source_lines_start == 10
    assert flat.source_lines_end == 20
    sem2 = flat.to_semantic_chunk()
    assert sem2.source_lines == [10, 20]

def test_flat_chunk_validate_metadata():
    data = {
        "uuid": ChunkId.default_value(),
        "type": "DocBlock",
        "text": "abc",
        "language": "en",
        "sha256": hashlib.sha256(b"abc").hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "start": 0,
        "end": 1,
    }
    flat, err = FlatSemanticChunk.validate_and_fill(data)
    assert err is None
    flat.validate_metadata()
    # Некорректный формат
    data2 = data.copy()
    data2["tags"] = ["not-a-string"]
    flat2, err2 = FlatSemanticChunk.validate_and_fill(data2)
    assert err2 is None
    flat2.tags = ["not-a-string"]
    with pytest.raises(ValueError):
        flat2.validate_metadata()

def test_flat_chunk_long_strings():
    # Проверка длинных строк
    long_text = "a" * 10000
    data = {
        "uuid": str(uuid.uuid4()),
        "type": "DocBlock",
        "text": long_text,
        "language": "en",
        "sha256": hashlib.sha256(long_text.encode()).hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "start": 0,
        "end": 1,
    }
    obj, err = FlatSemanticChunk.validate_and_fill(data)
    assert err is None
    assert obj.text == long_text

def test_flat_chunk_invalid_uuid():
    # Не валидный uuid
    data = {
        "uuid": "bad",
        "type": "DocBlock",
        "text": "abc",
        "language": "en",
        "sha256": hashlib.sha256(b"abc").hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "start": 0,
        "end": 1,
    }
    obj, err = FlatSemanticChunk.validate_and_fill(data)
    assert obj is None
    assert err is not None
    assert "uuid" in err["fields"]

def test_flat_chunk_empty_and_none_fields():
    # Пустые и None значения для необязательных полей
    data = {
        "uuid": str(uuid.uuid4()),
        "type": "DocBlock",
        "text": "abc",
        "language": "en",
        "sha256": hashlib.sha256(b"abc").hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "start": 0,
        "end": 1,
        "tags": None,
        "link_parent": None,
        "link_related": None,
        "source_lines_start": None,
        "source_lines_end": None,
    }
    obj, err = FlatSemanticChunk.validate_and_fill(data)
    assert err is None
    assert obj.tags == ''
    assert obj.link_parent is None
    assert obj.link_related is None
    assert obj.source_lines_start == 0
    assert obj.source_lines_end == 1 