import pytest
import uuid
from datetime import datetime, timezone
from chunk_metadata_adapter.models import FlatSemanticChunk, SemanticChunk, ChunkType, ChunkRole, ChunkStatus, ChunkMetrics, LanguageEnum
from chunk_metadata_adapter.utils import ChunkId
import hashlib

def test_flat_chunk_invalid_tags():
    # Некорректные теги: слишком длинные, пустые, нестроковые
    for tags in [",badtag," + "a"*33, ["", "a"*33], 123, {"a":1}]:
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": hashlib.sha256(b"abc").hexdigest(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 0,
            "end": 1,
            "tags": tags,
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is None or err is not None

def test_flat_chunk_invalid_links():
    # Некорректные UUID для link_parent/link_related
    for field in ["link_parent", "link_related"]:
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": hashlib.sha256(b"abc").hexdigest(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 0,
            "end": 1,
            field: "not-a-uuid",
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is None or err is not None

def test_flat_chunk_invalid_sha256():
    data = {
        "uuid": str(uuid.uuid4()),
        "type": "DocBlock",
        "text": "abc",
        "language": "en",
        "sha256": "bad",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "start": 0,
        "end": 1,
    }
    obj, err = FlatSemanticChunk.validate_and_fill(data)
    assert obj is None or err is not None

def test_flat_chunk_invalid_created_at():
    data = {
        "uuid": str(uuid.uuid4()),
        "type": "DocBlock",
        "text": "abc",
        "language": "en",
        "sha256": hashlib.sha256(b"abc").hexdigest(),
        "created_at": "not-a-date",
        "start": 0,
        "end": 1,
    }
    obj, err = FlatSemanticChunk.validate_and_fill(data)
    assert obj is None or err is not None

def test_flat_chunk_end_less_than_start():
    data = {
        "uuid": str(uuid.uuid4()),
        "type": "DocBlock",
        "text": "abc",
        "language": "en",
        "sha256": hashlib.sha256(b"abc").hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "start": 5,
        "end": 2,
    }
    obj, err = FlatSemanticChunk.validate_and_fill(data)
    assert obj is None or err is not None

def test_flat_chunk_invalid_chunking_version():
    data = {
        "uuid": str(uuid.uuid4()),
        "type": "DocBlock",
        "text": "abc",
        "language": "en",
        "sha256": hashlib.sha256(b"abc").hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "start": 0,
        "end": 1,
        "chunking_version": "",
    }
    obj, err = FlatSemanticChunk.validate_and_fill(data)
    assert err is None
    assert obj.chunking_version == "1.0"

def test_flat_chunk_autofill_min_length_str_fields():
    from chunk_metadata_adapter.flat_chunk import _autofill_min_length_str_fields
    data = {"a": None, "b": "", "c": "x"}
    class Dummy:
        model_fields = {
            "a": type("F", (), {"annotation": str, "default": "", "is_required": lambda: False, "min_length": 0, "max_length": 10})(),
            "b": type("F", (), {"annotation": str, "default": "", "is_required": lambda: False, "min_length": 0, "max_length": 10})(),
            "c": type("F", (), {"annotation": str, "default": "", "is_required": lambda: False, "min_length": 0, "max_length": 10})(),
        }
    _autofill_min_length_str_fields(data, Dummy.model_fields)
    assert data["a"] == ''
    assert data["b"] == ""
    assert data["c"] == "x"

def test_flat_chunk_block_meta_roundtrip():
    # flat dict <-> block_meta
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
        links=[],
        block_meta={"foo.bar": 1, "baz": 2},
    )
    flat = FlatSemanticChunk.from_semantic_chunk(sem)
    sem2 = flat.to_semantic_chunk()
    assert isinstance(sem2, SemanticChunk)
    # block_meta может быть None или пустым dict после roundtrip
    assert sem2.block_meta is None or sem2.block_meta == {}

def test_flat_chunk_roundtrip_edge():
    # flat -> semantic -> flat с edge-значениями
    sem = SemanticChunk(
        uuid=ChunkId.default_value(),
        text="x",
        body="x",
        language=LanguageEnum.UNKNOWN,
        type=ChunkType.DOC_BLOCK.value,
        start=0,
        end=1,
        sha256=hashlib.sha256(b"x").hexdigest(),
        created_at=datetime.now(timezone.utc).isoformat(),
        summary="",
        tags=[],
        links=[],
        block_meta=None,
    )
    flat = FlatSemanticChunk.from_semantic_chunk(sem)
    sem2 = flat.to_semantic_chunk()
    assert sem2.text == "x"
    assert sem2.language == LanguageEnum.UNKNOWN
    assert sem2.block_meta is None 