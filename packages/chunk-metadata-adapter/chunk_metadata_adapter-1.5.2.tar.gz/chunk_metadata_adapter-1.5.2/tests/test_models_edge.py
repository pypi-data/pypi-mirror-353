import pytest
import uuid
from datetime import datetime, timezone
from chunk_metadata_adapter.models import (
    SemanticChunk, BaseChunkFlatFields, ChunkType, ChunkRole, ChunkStatus, ChunkMetrics, FeedbackMetrics, LanguageEnum
)
from chunk_metadata_adapter.utils import ChunkId
import hashlib


def test_uuid_field_validator():
    # Валидный UUID
    valid = str(uuid.uuid4())
    assert BaseChunkFlatFields.validate_uuid_fields(valid) == valid
    # Не валидный UUID
    with pytest.raises(ValueError):
        BaseChunkFlatFields.validate_uuid_fields("bad-uuid")

def test_created_at_field_validator():
    # Валидный ISO8601
    now = datetime.now(timezone.utc).isoformat()
    assert BaseChunkFlatFields.validate_created_at(now) == now
    # Не валидный
    with pytest.raises(ValueError):
        BaseChunkFlatFields.validate_created_at("2020-01-01 00:00:00")

def test_to_dict_and_autofill_min_length():
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
        "sha256": hashlib.sha256("abc".encode()).hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": "",
    }
    obj, err = BaseChunkFlatFields.validate_and_fill(data.copy())
    assert err is None
    d = obj.to_dict()
    assert d["language"] == LanguageEnum.EN.value
    # Проверка автозаполнения min_length=0
    assert d["summary"] == ""

def test_source_lines_property_and_setter():
    chunk = SemanticChunk(
        uuid=ChunkId.default_value(),
        text="abc",
        body="abc",
        language=LanguageEnum.EN,
        type=ChunkType.DOC_BLOCK.value,
        start=0,
        end=1,
        sha256=hashlib.sha256("abc".encode()).hexdigest(),
        created_at=datetime.now(timezone.utc).isoformat(),
        summary="",
    )
    # setter
    chunk.source_lines = [1, 2]
    assert chunk.source_lines == [1, 2]
    # setter None
    chunk.source_lines = None
    assert chunk.source_lines is None

def test_autofill_min_length_str_fields():
    from chunk_metadata_adapter.models import _autofill_min_length_str_fields
    data = {"a": None, "b": "", "c": "x"}
    class Dummy:
        model_fields = {
            "a": type("F", (), {"annotation": str, "default": "", "is_required": lambda: False, "min_length": 0, "max_length": 10})(),
            "b": type("F", (), {"annotation": str, "default": "", "is_required": lambda: False, "min_length": 0, "max_length": 10})(),
            "c": type("F", (), {"annotation": str, "default": "", "is_required": lambda: False, "min_length": 0, "max_length": 10})(),
        }
    _autofill_min_length_str_fields(data, Dummy.model_fields)
    # Функция теперь всегда заменяет None на '' если поле не обязательно
    assert data["a"] == ''
    assert data["b"] == ""
    assert data["c"] == "x"

def test_semantic_chunk_validate_metadata():
    chunk = SemanticChunk(
        uuid=ChunkId.default_value(),
        text="abc",
        body="abc",
        language=LanguageEnum.EN,
        type=ChunkType.DOC_BLOCK.value,
        start=0,
        end=1,
        sha256=hashlib.sha256("abc".encode()).hexdigest(),
        created_at=datetime.now(timezone.utc).isoformat(),
        summary="",
    )
    # Не должно выбрасывать
    chunk.validate_metadata()

def test_semantic_chunk_tags_links_block_meta():
    chunk, err = SemanticChunk.validate_and_fill({
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
        "sha256": hashlib.sha256("abc".encode()).hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    assert err is None
    assert chunk.tags == []
    assert chunk.links == []
    assert chunk.block_meta is None

def test_semantic_chunk_block_meta_autofill():
    # block_meta не передан
    chunk, err = SemanticChunk.validate_and_fill({
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
        "sha256": hashlib.sha256("abc".encode()).hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    assert err is None
    assert chunk.block_meta is None

def test_semantic_chunk_language_enum_default():
    chunk, err = SemanticChunk.validate_and_fill({
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
        "sha256": hashlib.sha256("abc".encode()).hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    assert err is None
    assert chunk.language == LanguageEnum.UNKNOWN 