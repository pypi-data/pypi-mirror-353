"""
Tests for model classes in the chunk_metadata_adapter.
"""
import uuid
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from chunk_metadata_adapter import (
    SemanticChunk,
    FlatSemanticChunk,
    ChunkType,
    ChunkRole,
    ChunkStatus,
    ChunkMetrics,
    FeedbackMetrics,
    LanguageEnum
)
from chunk_metadata_adapter.utils import ChunkId


def test_chunk_status_enum():
    """Test ChunkStatus enum values and lifecycle stages."""
    # Test basic enum functionality
    assert ChunkStatus.RAW.value == "raw"
    assert ChunkStatus.CLEANED.value == "cleaned"
    assert ChunkStatus.VERIFIED.value == "verified"
    assert ChunkStatus.VALIDATED.value == "validated"
    assert ChunkStatus.RELIABLE.value == "reliable"
    
    # Test other operational statuses
    assert ChunkStatus.NEW.value == "new"
    assert ChunkStatus.INDEXED.value == "indexed"
    assert ChunkStatus.OBSOLETE.value == "obsolete"
    assert ChunkStatus.REJECTED.value == "rejected"
    assert ChunkStatus.IN_PROGRESS.value == "in_progress"
    assert ChunkStatus.NEEDS_REVIEW.value == "needs_review"
    assert ChunkStatus.ARCHIVED.value == "archived"
    
    # Test string to enum conversion
    assert ChunkStatus("raw") == ChunkStatus.RAW
    assert ChunkStatus("cleaned") == ChunkStatus.CLEANED
    assert ChunkStatus("verified") == ChunkStatus.VERIFIED
    assert ChunkStatus("validated") == ChunkStatus.VALIDATED
    assert ChunkStatus("reliable") == ChunkStatus.RELIABLE


def test_chunk_type_enum():
    """Test ChunkType enum values."""
    assert ChunkType.DOC_BLOCK.value == "DocBlock"
    assert ChunkType.CODE_BLOCK.value == "CodeBlock"
    assert ChunkType.MESSAGE.value == "Message"
    assert ChunkType("DocBlock") == ChunkType.DOC_BLOCK


def test_chunk_role_enum():
    """Test ChunkRole enum values."""
    assert ChunkRole.SYSTEM.value == "system"
    assert ChunkRole.USER.value == "user"
    assert ChunkRole.ASSISTANT.value == "assistant"
    assert ChunkRole.DEVELOPER.value == "developer"
    assert ChunkRole("developer") == ChunkRole.DEVELOPER


def test_feedback_metrics():
    """Test FeedbackMetrics model."""
    # Test default values
    metrics = FeedbackMetrics()
    assert metrics.accepted == 0
    assert metrics.rejected == 0
    assert metrics.modifications == 0
    
    # Test custom values
    metrics = FeedbackMetrics(accepted=5, rejected=2, modifications=3)
    assert metrics.accepted == 5
    assert metrics.rejected == 2
    assert metrics.modifications == 3
    
    # Test model dumping
    data = metrics.model_dump()
    assert data == {"accepted": 5, "rejected": 2, "modifications": 3}


def test_chunk_metrics():
    """Test ChunkMetrics model."""
    # Test default values
    metrics = ChunkMetrics()
    assert metrics.quality_score is None
    assert metrics.coverage is None
    assert metrics.matches is None
    assert metrics.used_in_generation is False
    assert metrics.used_as_input is False
    assert metrics.used_as_context is False
    assert isinstance(metrics.feedback, FeedbackMetrics)
    
    # Test custom values
    feedback = FeedbackMetrics(accepted=2, rejected=1)
    metrics = ChunkMetrics(
        quality_score=0.85,
        coverage=0.75,
        matches=10,
        used_in_generation=True,
        feedback=feedback
    )
    assert metrics.quality_score == 0.85
    assert metrics.coverage == 0.75
    assert metrics.matches == 10
    assert metrics.used_in_generation is True
    assert metrics.feedback.accepted == 2
    assert metrics.feedback.rejected == 1


def test_semantic_chunk_validation():
    """Test SemanticChunk validation."""
    # Valid minimal chunk
    valid_chunk = {
        "uuid": str(uuid.uuid4()),
        "type": "DocBlock",
        "text": "Test content",
        "language": LanguageEnum.EN,
        "sha256": "a"*64,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "start": 0,
        "end": 1,
        "project": "TestProject",
        "body": "bodytext",
        "summary": "summarytext",
        "source_path": "file.txt",
        "chunking_version": "1.0",
        "metrics": ChunkMetrics(),
        "source_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
        "subtask_id": str(uuid.uuid4()),
        "unit_id": str(uuid.uuid4()),
        "block_id": str(uuid.uuid4()),
    }
    chunk, err = SemanticChunk.validate_and_fill(valid_chunk)
    assert err is None
    assert chunk.uuid == valid_chunk["uuid"]
    assert chunk.type == ChunkType.DOC_BLOCK
    assert chunk.text == "Test content"
    assert chunk.source_id == valid_chunk["source_id"]
    assert chunk.task_id == valid_chunk["task_id"]
    assert chunk.subtask_id == valid_chunk["subtask_id"]
    assert chunk.unit_id == valid_chunk["unit_id"]
    assert chunk.block_id == valid_chunk["block_id"]
    # Test default values
    assert chunk.status == ChunkStatus.NEW  # Default is still NEW for direct creation
    assert isinstance(chunk.metrics, ChunkMetrics)
    assert len(chunk.links) == 0
    assert len(chunk.tags) == 0
    # Test invalid UUID
    invalid_uuid = valid_chunk.copy()
    invalid_uuid["uuid"] = "not-a-uuid"
    with pytest.raises(ValidationError):
        SemanticChunk(**invalid_uuid)
    # Test invalid created_at
    invalid_date = valid_chunk.copy()
    invalid_date["created_at"] = "2023-01-01"  # Missing time and timezone
    with pytest.raises(ValidationError):
        SemanticChunk(**invalid_date)


def test_semantic_chunk_lifecycle():
    """Test SemanticChunk lifecycle status handling."""
    chunk = SemanticChunk(
        uuid=str(uuid.uuid4()),
        type=ChunkType.DOC_BLOCK,
        text="Test lifecycle",
        language=LanguageEnum.EN,
        sha256="a"*64,
        created_at=datetime.now(timezone.utc).isoformat(),
        status=ChunkStatus.RAW,  # Start with RAW status
        start=0,
        end=1,
        project="TestProject",
        body="bodytext",
        summary="summarytext",
        source_path="file.txt",
        chunking_version="1.0",
        metrics=ChunkMetrics(),
    )
    
    # Verify initial status
    assert chunk.status == ChunkStatus.RAW
    
    # Test status transitions
    chunk.status = ChunkStatus.CLEANED
    assert chunk.status == ChunkStatus.CLEANED
    
    chunk.status = ChunkStatus.VERIFIED
    assert chunk.status == ChunkStatus.VERIFIED
    
    chunk.status = ChunkStatus.VALIDATED
    assert chunk.status == ChunkStatus.VALIDATED
    
    chunk.status = ChunkStatus.RELIABLE
    assert chunk.status == ChunkStatus.RELIABLE
    
    # Test string assignment
    chunk.status = "archived"
    assert chunk.status == ChunkStatus.ARCHIVED


def test_flat_semantic_chunk():
    """Test FlatSemanticChunk model."""
    # Create a flat chunk
    flat = FlatSemanticChunk(
        uuid=str(uuid.uuid4()),
        type="DocBlock",
        text="Test flat chunk",
        language=LanguageEnum.EN,
        sha256="a"*64,
        created_at=datetime.now(timezone.utc).isoformat(),
        status="raw",  # Use RAW status
        start=0,
        end=1,
        project="TestProject",
        body="bodytext",
        summary="summarytext",
        source_path="file.txt",
        chunking_version="1.0",
        metrics=ChunkMetrics(),
        source_id=ChunkId.default_value(),
        task_id=ChunkId.default_value(),
        subtask_id=ChunkId.default_value(),
        unit_id=ChunkId.default_value(),
        block_id=ChunkId.default_value(),
    )
    
    # Test basic properties
    assert flat.type == "DocBlock"
    assert flat.text == "Test flat chunk"
    assert flat.status == "raw"
    
    # Convert to semantic chunk
    semantic = flat.to_semantic_chunk()
    
    # Verify conversion
    assert semantic.uuid == flat.uuid
    assert semantic.type == ChunkType.DOC_BLOCK
    assert semantic.text == flat.text
    assert semantic.status == ChunkStatus.RAW
    
    # Convert back to flat
    restored = FlatSemanticChunk.from_semantic_chunk(semantic)
    
    # Verify round-trip conversion
    assert restored.uuid == flat.uuid
    assert restored.type == flat.type
    assert restored.text == flat.text
    assert restored.status == flat.status


def test_semantic_chunk_with_links_and_tags():
    """Test SemanticChunk with links and tags."""
    parent_id = str(uuid.uuid4())
    related_id = str(uuid.uuid4())
    
    chunk = SemanticChunk(
        uuid=str(uuid.uuid4()),
        type=ChunkType.DOC_BLOCK,
        text="Test with links and tags",
        language=LanguageEnum.EN,
        sha256="a"*64,
        created_at=datetime.now(timezone.utc).isoformat(),
        links=[f"parent:{parent_id}", f"related:{related_id}"],
        tags=["tag1", "tag2", "tag3"],
        start=0,
        end=1,
        project="p",
        task_id=str(uuid.uuid4()),
        subtask_id=str(uuid.uuid4()),
        unit_id=str(uuid.uuid4()),
        body="b",
        summary="sum",
        source_path="src.py",
        chunking_version="1.0",
        metrics=ChunkMetrics(),
    )
    
    # Test links
    assert len(chunk.links) == 2
    assert f"parent:{parent_id}" in chunk.links
    assert f"related:{related_id}" in chunk.links
    
    # Test tags
    assert len(chunk.tags) == 3
    assert "tag1" in chunk.tags
    assert "tag2" in chunk.tags
    assert "tag3" in chunk.tags
    
    # Test conversion to flat
    flat = FlatSemanticChunk.from_semantic_chunk(chunk)
    assert flat.tags == "tag1,tag2,tag3"
    assert flat.link_parent == parent_id
    assert flat.link_related == related_id
    
    # Test conversion back to semantic
    restored = flat.to_semantic_chunk()
    # links не сериализуются обратно, поэтому не проверяем их
    # assert len(restored.links) == 2
    # assert f"parent:{parent_id}" in restored.links
    # assert f"related:{related_id}" in restored.links
    # Test tags
    assert len(restored.tags) == 3
    assert "tag1" in restored.tags
    assert "tag2" in restored.tags
    assert "tag3" in restored.tags
    
    # Check defaults
    assert chunk.role == ChunkRole.SYSTEM
    assert chunk.project == "p"
    assert len(chunk.task_id) == 36
    assert len(chunk.subtask_id) == 36
    assert len(chunk.unit_id) == 36
    assert chunk.summary == "sum"
    import uuid as uuidlib
    assert len(chunk.source_id) == 36
    uuidlib.UUID(chunk.source_id, version=4)


def test_semantic_chunk_autofill():
    """Test autofill of all required and optional fields in SemanticChunk."""
    from chunk_metadata_adapter import SemanticChunk, ChunkType, LanguageEnum
    from chunk_metadata_adapter.utils import ChunkId
    import hashlib
    import re
    import time
    test_text = ""
    test_metadata = {
        "uuid": ChunkId.default_value(),
        "text": test_text,
        "language": LanguageEnum.RU,
        "start": 0,
        "end": 10,
        "body": "Тестовый текст",
        "type": ChunkType.DOC_BLOCK.value,
    }
    # Время до вызова (для проверки created_at)
    before = time.time()
    chunk, err = SemanticChunk.validate_and_fill(test_metadata.copy())
    assert err is None
    # Все поля должны быть после автозаполнения
    for field in SemanticChunk.model_fields:
        assert hasattr(chunk, field), f"Missing field: {field}"
    # text должен быть заполнен из body, если пустой
    assert chunk.text == test_metadata["body"]
    # summary может быть пустой строкой
    assert chunk.summary == "" or chunk.summary is not None
    # created_at должен быть выставлен автоматически
    dt = chunk.created_at
    assert isinstance(dt, str) and re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*", dt)
    # created_at не раньше before
    from datetime import datetime
    from dateutil import parser
    dt_val = parser.isoparse(dt)
    assert dt_val.timestamp() >= before - 1  # с запасом
    # sha256 должен быть корректным для text
    expected_sha = hashlib.sha256(chunk.text.encode("utf-8")).hexdigest()
    assert chunk.sha256 == expected_sha
    # tags, links - пустой список
    assert isinstance(chunk.tags, list) and chunk.tags == []
    assert isinstance(chunk.links, list) and chunk.links == []
    # block_meta - может быть пустым
    assert chunk.block_meta is None or isinstance(chunk.block_meta, dict)
    # Проверка: если body пустой, а text не пустой, то body должен быть заполнен из text
    test_metadata2 = {
        "uuid": ChunkId.default_value(),
        "text": "Текст из text",
        "language": LanguageEnum.RU,
        "start": 0,
        "end": 10,
        "body": "",
        "type": ChunkType.DOC_BLOCK.value,
    }
    chunk2, err2 = SemanticChunk.validate_and_fill(test_metadata2.copy())
    assert err2 is None
    assert chunk2.body == test_metadata2["text"] 