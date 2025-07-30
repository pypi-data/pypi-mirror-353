import uuid
import pytest
from datetime import datetime, timezone
from chunk_metadata_adapter.models import SemanticChunk, BaseChunkFlatFields, ChunkType, LanguageEnum, ChunkStatus, ChunkMetrics, FeedbackMetrics
from chunk_metadata_adapter.utils import ChunkId
import hashlib


def test_semantic_chunk_autofill_text_body():
    # text пустой, body заполнен
    data = {
        "uuid": ChunkId.default_value(),
        "text": "",
        "body": "bodytext",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    assert chunk.text == "bodytext"
    assert chunk.body == "bodytext"
    # body пустой, text заполнен
    data2 = data.copy()
    data2["text"] = "text"
    data2["body"] = ""
    chunk2, err2 = SemanticChunk.validate_and_fill(data2.copy())
    assert err2 is None
    assert chunk2.body == "text"
    assert chunk2.text == "text"

def test_semantic_chunk_autofill_summary():
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    assert chunk.summary == ""

def test_semantic_chunk_autofill_created_at():
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
    }
    before = datetime.now(timezone.utc).timestamp()
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    from dateutil import parser
    dt_val = parser.isoparse(chunk.created_at)
    assert dt_val.timestamp() >= before

def test_semantic_chunk_autofill_sha256():
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    assert chunk.sha256 == hashlib.sha256("abc".encode()).hexdigest()

def test_semantic_chunk_autofill_tags():
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    assert chunk.tags == []

def test_semantic_chunk_autofill_links():
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    assert chunk.links == []

def test_semantic_chunk_autofill_block_meta():
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    assert chunk.block_meta is None

def test_semantic_chunk_autofill_all_defaults():
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
    }
    before = datetime.now(timezone.utc).timestamp()
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    assert chunk.summary == ""
    from dateutil import parser
    dt_val = parser.isoparse(chunk.created_at)
    assert dt_val.timestamp() >= before
    assert chunk.sha256 == hashlib.sha256(data["text"].encode()).hexdigest()
    assert chunk.tags == []
    assert chunk.links == []
    assert chunk.block_meta is None

def test_semantic_chunk_validate_and_fill_errors():
    # Нет type
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "language": LanguageEnum.EN,
        "start": 0,
        "end": 1,
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert chunk is None
    assert err is not None
    assert "type" in err["fields"]
    # Некорректный uuid
    data2 = data.copy()
    data2["type"] = ChunkType.DOC_BLOCK.value
    data2["uuid"] = "bad"
    chunk2, err2 = SemanticChunk.validate_and_fill(data2.copy())
    assert chunk2 is None
    assert err2 is not None
    assert "uuid" in err2["fields"]
    # end < start
    data3 = data2.copy()
    data3["uuid"] = str(uuid.uuid4())
    data3["end"] = -1
    chunk3, err3 = SemanticChunk.validate_and_fill(data3.copy())
    assert chunk3 is None
    assert err3 is not None
    assert "end" in err3["fields"]

def test_semantic_chunk_to_dict_and_roundtrip():
    data = {
        "uuid": str(uuid.uuid4()),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
        "summary": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256("abc".encode()).hexdigest(),
        "tags": ["tag1", "tag2"],
        "links": ["parent:" + str(uuid.uuid4())],
        "block_meta": {"meta": 1},
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    d = chunk.to_dict()
    assert d["language"] == LanguageEnum.EN.value
    assert d["tags"] == ["tag1", "tag2"] or d["tags"] == "tag1,tag2"
    # roundtrip
    chunk2, err2 = SemanticChunk.validate_and_fill(d)
    assert err2 is None
    assert chunk2.text == chunk.text
    assert chunk2.body == chunk.body
    assert chunk2.language == chunk.language
    assert chunk2.type == chunk.type
    assert chunk2.tags == chunk.tags
    assert chunk2.links == chunk.links
    assert chunk2.block_meta == chunk.block_meta

def test_basechunkflatfields_to_dict_and_autofill():
    data = {
        "uuid": ChunkId.default_value(),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
        "summary": "",
        "sha256": hashlib.sha256("abc".encode()).hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    obj, err = BaseChunkFlatFields.validate_and_fill(data.copy())
    assert err is None
    d = obj.to_dict()
    assert d["language"] == LanguageEnum.EN.value
    # Проверка автозаполнения всех неуказанных полей
    for field in BaseChunkFlatFields.model_fields:
        assert hasattr(obj, field)

# Edge: tags/links как строки, пустые, None
@pytest.mark.parametrize("tags,links", [
    (None, []),
    ([], []),
])
def test_semantic_chunk_tags_links_variants(tags, links):
    data = {
        "uuid": str(uuid.uuid4()),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
        "tags": tags,
        "links": links,
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    assert isinstance(chunk.tags, list)
    assert isinstance(chunk.links, list)

# Проверка, что sha256 всегда пересчитывается
def test_semantic_chunk_sha256_always_recalculated():
    data = {
        "uuid": str(uuid.uuid4()),
        "text": "abc",
        "body": "abc",
        "language": LanguageEnum.EN,
        "type": ChunkType.DOC_BLOCK.value,
        "start": 0,
        "end": 1,
    }
    chunk, err = SemanticChunk.validate_and_fill(data.copy())
    assert err is None
    assert chunk.sha256 == hashlib.sha256(data["text"].encode()).hexdigest() 

    data2 = chunk.to_dict()
    data2["text"] = "another text"
    data2["body"] = "another text" 
    data2["sha256"] = None
    chunk2, err2 = SemanticChunk.validate_and_fill(data2.copy())
    assert err2 is None
    assert chunk2.sha256 == hashlib.sha256(data2["text"].encode()).hexdigest()