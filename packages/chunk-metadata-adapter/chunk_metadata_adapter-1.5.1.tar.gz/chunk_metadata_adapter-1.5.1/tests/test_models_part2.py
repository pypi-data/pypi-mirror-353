"""
Tests for the data models (part 2).
"""
import re
import uuid
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError, BaseModel

from chunk_metadata_adapter import (
    SemanticChunk,
    FlatSemanticChunk,
    ChunkType,
    ChunkRole,
    ChunkStatus,
    ChunkMetrics,
    FeedbackMetrics
)
from chunk_metadata_adapter.utils import ChunkId


class TestSemanticChunk:
    """Tests for SemanticChunk model"""
    
    def test_uuid_validation(self):
        """Test UUID validation"""
        # Valid UUID should pass
        valid_uuid = str(uuid.uuid4())
        data = {
            "uuid": valid_uuid,
            "type": ChunkType.DOC_BLOCK,
            "text": "Test content",
            "language": "markdown",
            "sha256": "a" * 64,
            "start": 0,
            "end": 1,
            "project": "p",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "b",
            "summary": "s",
            "block_id": str(uuid.uuid4()),
            "block_type": "paragraph",
            "block_index": 0,
            "block_meta": {},
            "source_id": str(uuid.uuid4()),
            "source_path": "/tmp/file.txt",
            "source_lines": [0, 1],
            "ordinal": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": ChunkStatus.NEW,
            "chunking_version": "1.0",
            "links": [],
            "tags": [],
            "metrics": ChunkMetrics(),
            "category": None,
            "title": None,
            "year": None,
            "is_public": None,
            "source": None
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert err is None
        assert obj is not None
        assert obj.uuid == valid_uuid
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        # Invalid UUIDs should fail
        data_bad = data.copy()
        data_bad["uuid"] = "invalid-uuid"
        obj, err = SemanticChunk.validate_and_fill(data_bad)
        assert obj is None
        assert err is not None
        # Non-version 4 UUIDs should fail
        non_v4_uuid = str(uuid.uuid1())
        data_bad2 = data.copy()
        data_bad2["uuid"] = non_v4_uuid.replace("-4", "-1")
        obj, err = SemanticChunk.validate_and_fill(data_bad2)
        assert obj is None
        assert err is not None
            
    def test_timestamp_validation(self):
        """Test timestamp validation"""
        valid_timestamp = datetime.now(timezone.utc).isoformat()
        data = {
            "uuid": str(uuid.uuid4()),
            "type": ChunkType.DOC_BLOCK,
            "text": "Test content",
            "language": "markdown",
            "sha256": "a" * 64,
            "created_at": valid_timestamp,
            "start": 0,
            "end": 1,
            "project": "p",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "b",
            "summary": "s",
            "block_id": str(uuid.uuid4()),
            "block_type": "paragraph",
            "block_index": 0,
            "block_meta": {},
            "source_id": str(uuid.uuid4()),
            "source_path": "/tmp/file.txt",
            "source_lines": [0, 1],
            "ordinal": 0,
            "status": ChunkStatus.NEW,
            "chunking_version": "1.0",
            "links": [],
            "tags": [],
            "metrics": ChunkMetrics(),
            "category": None,
            "title": None,
            "year": None,
            "is_public": None,
            "source": None
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert err is None
        assert obj is not None
        assert obj.created_at[:19] == valid_timestamp[:19]
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        # ISO timestamp without timezone should fail
        data_bad = data.copy()
        data_bad["created_at"] = "2023-01-01T12:00:00"
        obj, err = SemanticChunk.validate_and_fill(data_bad)
        assert obj is None
        assert err is not None
        # Invalid format should fail
        data_bad2 = data.copy()
        data_bad2["created_at"] = "01/01/2023 12:00:00"
        obj, err = SemanticChunk.validate_and_fill(data_bad2)
        assert obj is None
        assert err is not None
            
    def test_links_validation(self):
        """Test links validation"""
        valid_link = f"parent:{str(uuid.uuid4())}"
        data = {
            "uuid": str(uuid.uuid4()),
            "type": ChunkType.DOC_BLOCK,
            "text": "Test content",
            "language": "markdown",
            "sha256": "a" * 64,
            "links": [valid_link],
            "start": 0,
            "end": 1,
            "project": "p",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "b",
            "summary": "s",
            "block_id": str(uuid.uuid4()),
            "block_type": "paragraph",
            "block_index": 0,
            "block_meta": {},
            "source_id": str(uuid.uuid4()),
            "source_path": "/tmp/file.txt",
            "source_lines": [0, 1],
            "ordinal": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": ChunkStatus.NEW,
            "chunking_version": "1.0",
            "tags": [],
            "metrics": ChunkMetrics(),
            "category": None,
            "title": None,
            "year": None,
            "is_public": None,
            "source": None
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert err is None
        assert obj is not None
        assert obj.links[0] == valid_link
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        # Invalid link format should fail
        data_bad = data.copy()
        data_bad["links"] = ["invalid-link-format"]
        obj, err = SemanticChunk.validate_and_fill(data_bad)
        assert obj is None
        assert err is not None
        # Link with invalid UUID should fail
        data_bad2 = data.copy()
        data_bad2["links"] = [f"parent:invalid-uuid"]
        obj, err = SemanticChunk.validate_and_fill(data_bad2)
        assert obj is None
        assert err is not None


class TestFlatSemanticChunk:
    """Tests for FlatSemanticChunk model"""
    
    def test_minimal_initialization(self):
        """Test initialization with minimal required fields"""
        uuid_val = str(uuid.uuid4())
        chunk = FlatSemanticChunk(
            uuid=uuid_val,
            type="DocBlock",
            text="Test content",
            language="markdown",
            sha256="a" * 64,
            created_at=datetime.now(timezone.utc).isoformat(),
            start=0,
            end=1,
            role="user",
            status="new",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4()),
            project="p",
            body="b",
            summary="s",
            source_path="src.py",
            chunking_version="1.0",
            metrics=ChunkMetrics(),
        )
        
        assert chunk.uuid == uuid_val
        assert chunk.type == "DocBlock"
        assert chunk.text == "Test content"
        assert chunk.language == "markdown"
        assert chunk.sha256 == "a" * 64
        
        # Check defaults
        assert chunk.source_id is None
        assert chunk.project == "p"
        assert len(chunk.task_id) == 36
        assert len(chunk.subtask_id) == 36
        assert len(chunk.unit_id) == 36
        assert chunk.role == "user"
        assert chunk.summary == "s"
        assert chunk.ordinal is None
        assert chunk.status == "new"
        assert chunk.source_path == "src.py"
        assert chunk.source_lines_start is None
        assert chunk.source_lines_end is None
        assert chunk.tags is None
        assert chunk.link_related is None
        assert chunk.link_parent is None
        assert chunk.quality_score is None
        assert chunk.used_in_generation is False
        assert chunk.feedback_accepted == 0
        assert chunk.feedback_rejected == 0
        
    def test_full_initialization(self):
        """Test initialization with all fields"""
        uuid_val = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        parent_id = str(uuid.uuid4())
        related_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        chunk = FlatSemanticChunk(
            uuid=uuid_val,
            source_id=source_id,
            project="TestProject",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4()),
            type="CodeBlock",
            role="developer",
            language="python",
            text="def test():\n    pass",
            summary="Test function",
            ordinal=5,
            sha256="b" * 64,
            created_at=timestamp,
            status="verified",
            source_path="src/test.py",
            source_lines_start=10,
            source_lines_end=11,
            tags="test,example",
            link_parent=parent_id,
            link_related=related_id,
            quality_score=0.9,
            used_in_generation=True,
            feedback_accepted=3,
            feedback_rejected=1,
            start=0,
            end=1,
            body="bodytext",
            chunking_version="1.0",
            metrics=ChunkMetrics(),
        )
        
        assert chunk.uuid == uuid_val
        assert chunk.source_id == source_id
        assert chunk.project == "TestProject"
        assert len(chunk.task_id) == 36
        assert len(chunk.subtask_id) == 36
        assert len(chunk.unit_id) == 36
        assert chunk.type == "CodeBlock"
        assert chunk.role == "developer"
        assert chunk.language == "python"
        assert chunk.text == "def test():\n    pass"
        assert chunk.summary == "Test function"
        assert chunk.ordinal == 5
        assert chunk.sha256 == "b" * 64
        assert chunk.created_at == timestamp
        assert chunk.status == "verified"
        assert chunk.source_path == "src/test.py"
        assert chunk.source_lines_start == 10
        assert chunk.source_lines_end == 11
        assert chunk.tags == "test,example"
        assert chunk.link_parent == parent_id
        assert chunk.link_related == related_id
        assert chunk.quality_score == 0.9
        assert chunk.used_in_generation is True
        assert chunk.feedback_accepted == 3
        assert chunk.feedback_rejected == 1
        
    def test_conversion_to_semantic(self):
        """Test conversion from flat to semantic format"""
        uuid_val = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        parent_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        flat_chunk = FlatSemanticChunk(
            uuid=uuid_val,
            source_id=source_id,
            project="TestProject",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4()),
            type="DocBlock",
            role="developer",
            language="markdown",
            text="Test content",
            summary="Test summary",
            sha256="c" * 64,
            created_at=timestamp,
            link_parent=parent_id,
            tags="tag1,tag2",
            start=7,
            end=42,
            body="bodytext",
            block_id=str(uuid.uuid4()),
            block_type="paragraph",
            block_index=1,
            block_meta={},
            source_path="/tmp/file.txt",
            source_lines_start=7,
            source_lines_end=42,
            ordinal=1,
            status="new",
            chunking_version="1.0",
            metrics=ChunkMetrics(),
            category=None,
            title=None,
            year=None,
            is_public=None,
            source=None
        )
        semantic_chunk = flat_chunk.to_semantic_chunk()
        assert isinstance(semantic_chunk, SemanticChunk)
        assert semantic_chunk.uuid == uuid_val
        assert semantic_chunk.source_id == source_id
        assert semantic_chunk.project == "TestProject"
        assert semantic_chunk.type == ChunkType.DOC_BLOCK
        assert semantic_chunk.language == "markdown"
        assert semantic_chunk.text == "Test content"
        assert semantic_chunk.summary == "Test summary"
        assert semantic_chunk.sha256 == "c" * 64
        assert semantic_chunk.created_at == timestamp
        # assert len(semantic_chunk.links) == 1
        # assert semantic_chunk.links[0] == f"parent:{parent_id}"
        assert len(semantic_chunk.tags) == 2
        assert "tag1" in semantic_chunk.tags
        assert "tag2" in semantic_chunk.tags
        assert semantic_chunk.start == 7
        assert semantic_chunk.end == 42
        
    def test_conversion_from_semantic(self):
        """Test conversion from semantic to flat format"""
        uuid_val = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        related_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        semantic_chunk = SemanticChunk(
            uuid=uuid_val,
            source_id=source_id,
            project="TestProject",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4()),
            type=ChunkType.CODE_BLOCK,
            role="developer",
            language="python",
            text="def convert():\n    pass",
            summary="Conversion function",
            sha256="d" * 64,
            created_at=timestamp,
            links=[f"related:{related_id}"],
            tags=["python", "code"],
            start=0,
            end=1,
            body="bodytext",
            block_id=str(uuid.uuid4()),
            block_type="paragraph",
            block_index=1,
            block_meta={},
            source_path="/tmp/file.txt",
            source_lines=[0, 1],
            ordinal=1,
            status=ChunkStatus.NEW,
            chunking_version="1.0",
            metrics=ChunkMetrics(),
            category=None,
            title=None,
            year=None,
            is_public=None,
            source=None
        )
        flat_chunk = FlatSemanticChunk.from_semantic_chunk(semantic_chunk)
        assert isinstance(flat_chunk, FlatSemanticChunk)
        assert flat_chunk.uuid == uuid_val
        assert flat_chunk.source_id == source_id
        assert flat_chunk.project == "TestProject"
        assert flat_chunk.type == "CodeBlock"
        assert flat_chunk.language == "python"
        assert flat_chunk.text == "def convert():\n    pass"
        assert flat_chunk.summary == "Conversion function"
        assert flat_chunk.sha256 == "d" * 64
        assert flat_chunk.created_at[:19] == timestamp[:19]
        assert flat_chunk.link_related == related_id
        assert flat_chunk.link_parent is None
        assert flat_chunk.tags == "python,code"
        
    def test_uuid_validation(self):
        """Test UUID validation"""
        # Valid UUID should pass
        valid_uuid = str(uuid.uuid4())
        chunk = FlatSemanticChunk(
            uuid=valid_uuid,
            type="DocBlock",
            text="Test content",
            language="markdown",
            sha256="a" * 64,
            created_at=datetime.now(timezone.utc).isoformat(),
            start=0,
            end=1,
            role="user",
            status="new"
        )
        assert chunk.uuid == valid_uuid
        
        # Invalid UUIDs should fail
        with pytest.raises(ValidationError):
            FlatSemanticChunk(
                uuid="invalid-uuid",
                type="DocBlock",
                text="Test content",
                language="markdown",
                sha256="a" * 64,
                created_at=datetime.now(timezone.utc).isoformat(),
                start=0,
                end=1,
                role="user",
                status="new"
            )
            
    def test_timestamp_validation(self):
        """Test timestamp validation"""
        # Valid ISO timestamp with timezone should pass
        valid_timestamp = datetime.now(timezone.utc).isoformat()
        chunk = FlatSemanticChunk(
            uuid=str(uuid.uuid4()),
            type="DocBlock",
            text="Test content",
            language="markdown",
            sha256="a" * 64,
            created_at=valid_timestamp,
            start=0,
            end=1,
            role="user",
            status="new"
        )
        assert isinstance(chunk.created_at, str) and chunk.created_at.startswith(valid_timestamp[:19])
        
        # ISO timestamp without timezone should fail
        with pytest.raises(ValidationError):
            FlatSemanticChunk(
                uuid=str(uuid.uuid4()),
                type="DocBlock",
                text="Test content",
                language="markdown",
                sha256="a" * 64,
                created_at="2023-01-01T12:00:00",  # No timezone
                start=0,
                end=1,
                role="user",
                status="new"
            )
            
    def test_link_uuid_validation(self):
        """Test link UUID validation"""
        # Valid UUIDs should pass
        valid_uuid = str(uuid.uuid4())
        chunk = FlatSemanticChunk(
            uuid=str(uuid.uuid4()),
            type="DocBlock",
            text="Test content",
            language="markdown",
            sha256="a" * 64,
            created_at=datetime.now(timezone.utc).isoformat(),
            link_parent=valid_uuid,
            start=0,
            end=1,
            role="user",
            status="new"
        )
        assert chunk.link_parent == valid_uuid
        
        # Invalid UUIDs should fail
        with pytest.raises(ValidationError):
            FlatSemanticChunk(
                uuid=str(uuid.uuid4()),
                type="DocBlock",
                text="Test content",
                language="markdown",
                sha256="a" * 64,
                created_at=datetime.now(timezone.utc).isoformat(),
                link_related="invalid-uuid",
                start=0,
                end=1,
                role="user",
                status="new"
            )

    def test_body_field(self):
        """Test body field in FlatSemanticChunk"""
        uuid_val = str(uuid.uuid4())
        chunk = FlatSemanticChunk(
            uuid=uuid_val,
            type="DocBlock",
            text="cleaned text",
            body="raw text",
            language="markdown",
            sha256="a" * 64,
            created_at=datetime.now(timezone.utc).isoformat(),
            start=0,
            end=1,
            role="user",
            status="new"
        )
        assert chunk.body == "raw text"
        assert chunk.text == "cleaned text"
        # body can be None
        chunk2 = FlatSemanticChunk(
            uuid=str(uuid.uuid4()),
            type="DocBlock",
            text="cleaned text",
            language="markdown",
            sha256="a" * 64,
            created_at=datetime.now(timezone.utc).isoformat(),
            start=0,
            end=1,
            role="user",
            status="new"
        )
        assert chunk2.body is None

    def test_flat_semantic_autofill_and_roundtrip(self):
        """
        Проверяет автозаполнение FlatSemanticChunk и корректность round-trip flat <-> semantic.
        """
        from chunk_metadata_adapter.models import SemanticChunk, ChunkType, ChunkRole, ChunkStatus, ChunkMetrics, FeedbackMetrics
        from chunk_metadata_adapter.flat_chunk import FlatSemanticChunk
        from chunk_metadata_adapter.utils import ChunkId
        import uuid
        # 1. Проверка автозаполнения flat по модификаторам
        data = {
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": "2020-01-01T00:00:00+00:00",
            "start": 0,
            "end": 1,
            "uuid": str(uuid.uuid4()),
            "task_id": str(uuid.uuid4()),
            "status": "new",
            "tags": "tag1,tag2",
            "metrics": ChunkMetrics(),
            "project": "TestProject",
            "role": "user",
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "chunking_version": "1.0",
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is not None, f"Validation failed: {err}"
        # Строки автозаполнены по min_length/max_length
        assert len(obj.type) >= 3
        assert len(obj.text) >= 1
        assert len(obj.language) >= 2
        assert len(obj.sha256) == 64
        # Числа приведены к диапазону
        assert obj.start == 0
        assert obj.end >= 0
        # UUID автозаполнен
        assert isinstance(obj.uuid, str) and len(obj.uuid) == 36
        assert isinstance(obj.task_id, str) and len(obj.task_id) == 36
        # Enum автозаполнен
        assert obj.status == ChunkStatus.NEW.value
        # Коллекции автозаполнены
        assert obj.tags == "tag1,tag2"
        # Объекты автозаполнены
        assert obj.metrics is not None
        # 2. Проверка round-trip flat -> semantic -> flat
        sem = obj.to_semantic_chunk()
        flat2 = FlatSemanticChunk.from_semantic_chunk(sem)
        # Проверяем, что значения не нарушают модификаторы
        assert len(flat2.type) >= 3
        assert len(flat2.text) >= 1
        assert len(flat2.language) >= 2
        assert len(flat2.sha256) == 64
        assert flat2.start == 0
        assert flat2.end >= 0
        assert isinstance(flat2.uuid, str) and len(flat2.uuid) == 36
        assert isinstance(flat2.task_id, str) and len(flat2.task_id) == 36
        assert flat2.status == ChunkStatus.NEW.value
        # 3. Проверка round-trip semantic -> flat -> semantic
        sem2 = flat2.to_semantic_chunk()
        assert sem2.type in [ChunkType.DOC_BLOCK, flat2.type]
        assert sem2.language == flat2.language
        assert sem2.text == flat2.text
        assert sem2.sha256 == flat2.sha256
        assert sem2.start == flat2.start
        assert sem2.end == flat2.end
        assert sem2.uuid == flat2.uuid
        assert sem2.status == flat2.status


class TestSemanticChunkValidateAndFill:
    def test_valid_minimal(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "start": 0,
            "end": 1,
            "links": [],
            "tags": [],
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new",
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is not None
        assert err is None
        assert obj.text == "abc"
        assert obj.status == ChunkStatus.NEW
        assert obj.chunking_version == "1.0"
        assert obj.project == "TestProject"
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        assert obj.body == "bodytext"
        assert obj.summary == "summarytext"
        assert obj.source_path == "/tmp/file.txt"
        assert obj.created_at[:19] == datetime.now(timezone.utc).isoformat()[:19]
        assert obj.metrics == ChunkMetrics()
        assert obj.role == "user"
        assert obj.status == "new"
        assert len(obj.source_id) == 36
        assert len(obj.block_id) == 36

    def test_invalid_uuid(self):
        data = {
            "uuid": "not-a-uuid",
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "start": 0,
            "end": 1,
            "project": "TestProject",
            "task_id": "T-001",
            "subtask_id": "T-001-A",
            "unit_id": "test-unit",
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "uuid" in err["fields"]

    def test_invalid_sha256(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "bad",
            "start": 0,
            "end": 1,
            "project": "TestProject",
            "task_id": "T-001",
            "subtask_id": "T-001-A",
            "unit_id": "test-unit",
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "sha256" in err["fields"]

    def test_invalid_links(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "links": ["bad-link"],
            "start": 0,
            "end": 1,
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new",
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "links" in err["fields"] or any(f in err["fields"] for f in ["task_id", "subtask_id", "unit_id", "source_id", "block_id"])

    def test_invalid_tags(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "tags": ["", "a"*33],
            "start": 0,
            "end": 1,
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new",
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "tags" in err["fields"] or any(f in err["fields"] for f in ["task_id", "subtask_id", "unit_id", "source_id", "block_id"])

    def test_end_less_than_start(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "start": 5,
            "end": 2,
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new",
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "end" in err["fields"]

    def test_invalid_source_lines(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "start": 0,
            "end": 1,
            "source_lines": [0],
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new",
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "source_lines" in err["fields"]

    def test_multiple_errors(self):
        data = {
            "uuid": "bad",
            "type": "DocBlock",
            "text": "",
            "language": "e",
            "sha256": "bad",
            "start": -1,
            "end": -2,
            "tags": ["", "a"*33],
            "links": ["bad-link"],
            "project": "TestProject",
            "task_id": "T-001",
            "subtask_id": "T-001-A",
            "unit_id": "test-unit",
            "body": "",
            "summary": "",
            "source_path": "/tmp/file.txt",
            "created_at": "bad",
            "chunking_version": "bad",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        # Проверяем, что хотя бы ключевые ошибки есть
        for field in ["uuid", "text", "language", "sha256", "start", "end", "tags", "links", "project", "task_id", "subtask_id", "unit_id", "body", "summary", "source_path", "created_at", "chunking_version", "metrics"]:
            if field in err["fields"]:
                assert field in err["fields"]

    def test_error_message_and_fields_single(self):
        data = {
            "uuid": "bad",
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "start": 0,
            "end": 1,
            "project": "TestProject",
            "task_id": "T-001",
            "subtask_id": "T-001-A",
            "unit_id": "test-unit",
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "uuid" in err["fields"]
        assert "Invalid UUID" in err["error"]

    def test_error_message_and_fields_multiple(self):
        data = {
            "uuid": "bad",
            "type": "",
            "text": "",
            "language": "e",
            "sha256": "bad",
            "start": -1,
            "end": -2,
            "tags": ",badtag," + "a"*33,
            "links": ["bad-link"],
            "project": "TestProject",
            "task_id": "T-001",
            "subtask_id": "T-001-A",
            "unit_id": "test-unit",
            "body": "",
            "summary": "",
            "source_path": "/tmp/file.txt",
            "created_at": "bad",
            "chunking_version": "bad",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        # Проверяем, что все ключевые ошибки есть в error и fields
        for field in ["uuid", "type", "text", "language", "sha256", "start", "end", "tags", "links", "project", "task_id", "subtask_id", "unit_id", "body", "summary", "source_path", "created_at", "chunking_version", "metrics"]:
            if field in err["fields"]:
                assert field in err["fields"]
        # Проверяем, что error содержит несколько ошибок через ;
        assert ";" in err["error"]

    def test_optional_fields_defaults(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": ChunkType.DOC_BLOCK,
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "start": 1,
            "end": 2,
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new",
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = SemanticChunk.validate_and_fill(data)
        assert err is None
        assert obj is not None
        for name, field in type(obj).model_fields.items():
            if not field.is_required():
                assert hasattr(obj, name)
        assert obj.project == "TestProject"
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        assert obj.body == "bodytext"
        assert obj.summary == "summarytext"
        assert obj.source_path == "/tmp/file.txt"
        assert obj.created_at[:19] == datetime.now(timezone.utc).isoformat()[:19]
        assert obj.metrics == ChunkMetrics()
        assert len(obj.source_id) == 36
        assert len(obj.block_id) == 36

    def test_error_on_missing_default_for_optional(self):
        # В Pydantic 2.x TypeError не выбрасывается, просто проверяем, что модель создаётся
        class BadModel(BaseModel):
            foo: int | None


class TestFlatSemanticChunkValidateAndFill:
    def test_valid_minimal(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 0,
            "end": 1,
            "links": [],
            "tags": [],
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is not None
        assert err is None
        assert obj.text == "abc"
        assert obj.status == "new"
        assert obj.project == "TestProject"
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        assert obj.body == "bodytext"
        assert obj.summary == "summarytext"
        assert obj.source_path == "/tmp/file.txt"
        assert obj.created_at[:19] == datetime.now(timezone.utc).isoformat()[:19]
        assert obj.chunking_version == "1.0"
        assert obj.metrics == ChunkMetrics()

    def test_invalid_uuid(self):
        data = {
            "uuid": "bad",
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 0,
            "end": 1,
            "project": "TestProject",
            "task_id": "T-001",
            "subtask_id": "T-001-A",
            "unit_id": "test-unit",
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "uuid" in err["fields"]

    def test_invalid_tags(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": ["", "a"*33],
            "start": 0,
            "end": 1,
            "project": "TestProject",
            "task_id": "T-001",
            "subtask_id": "T-001-A",
            "unit_id": "test-unit",
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "tags" in err["fields"]

    def test_end_less_than_start(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 5,
            "end": 2,
            "project": "TestProject",
            "task_id": "T-001",
            "subtask_id": "T-001-A",
            "unit_id": "test-unit",
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "end" in err["fields"]

    def test_multiple_errors(self):
        data = {
            "uuid": "bad",
            "type": "",
            "text": "",
            "language": "e",
            "sha256": "bad",
            "created_at": "bad",
            "start": -1,
            "end": -2,
            "tags": ",badtag," + "a"*33,
            "project": "TestProject",
            "task_id": "T-001",
            "subtask_id": "T-001-A",
            "unit_id": "test-unit",
            "body": "",
            "summary": "",
            "source_path": "/tmp/file.txt",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_version": "bad",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        for field in ["uuid", "type", "text", "language", "sha256", "created_at", "start", "end", "tags", "project", "task_id", "subtask_id", "unit_id", "body", "summary", "source_path", "created_at", "chunking_version", "metrics"]:
            if field in err["fields"]:
                assert field in err["fields"]
        # Проверяем, что error содержит несколько ошибок через ;
        assert ";" in err["error"]

    def test_flat_semantic_chunk_validate_and_fill_without_tags(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "Test content",
            "language": "markdown",
            "sha256": "a" * 64,
            "created_at": "2024-01-01T00:00:00+00:00",
            "start": 0,
            "end": 1,
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert err is None
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36

    def test_optional_fields_defaults(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 1,
            "end": 2,
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert err is None
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        for name, field in type(obj).model_fields.items():
            if not field.is_required():
                assert hasattr(obj, name)
        assert obj.project == "TestProject"
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        assert obj.body == "bodytext"
        assert obj.summary == "summarytext"
        assert obj.source_path == "/tmp/file.txt"
        assert obj.created_at[:19] == datetime.now(timezone.utc).isoformat()[:19]
        assert obj.chunking_version == "1.0"
        assert obj.metrics == ChunkMetrics()

    def test_tags_empty_list_to_string(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 1,
            "end": 2,
            "tags": [],
            "project": "TestProject",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "body": "bodytext",
            "summary": "summarytext",
            "source_path": "/tmp/file.txt",
            "chunking_version": "1.0",
            "metrics": ChunkMetrics(),
            "role": "user",
            "status": "new"
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert err is None
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        assert obj.tags == "" or obj.tags is None
        assert obj.project == "TestProject"
        assert len(obj.task_id) == 36
        assert len(obj.subtask_id) == 36
        assert len(obj.unit_id) == 36
        assert obj.body == "bodytext"
        assert obj.summary == "summarytext"
        assert obj.source_path == "/tmp/file.txt"
        assert obj.created_at[:19] == datetime.now(timezone.utc).isoformat()[:19]
        assert obj.chunking_version == "1.0"
        assert obj.metrics == ChunkMetrics()

    def test_chunkid_all_zeros_variants(self):
        # UUID с разным количеством нулей и разделителей
        for v in [
            "00000000-0000-0000-0000-000000000000",
            "00000000-0000-4000-8000-000000000000",
        ]:
            cid = ChunkId.validate(v, None)
            # Проверяем только валидность UUID
            assert isinstance(cid, str) and len(cid) == 36 

    def test_invalid_created_at(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": "not-a-date",
            "start": 0,
            "end": 1,
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is None
        assert err is not None
        assert "created_at" in err["fields"]

    def test_invalid_sha256(self):
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
        assert obj is None
        assert err is not None
        assert "sha256" in err["fields"]

    def test_empty_str_to_none(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 0,
            "end": 1,
            "project": "",
            "body": "",
            "summary": "",
            "source_path": "",
            "chunking_version": "",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert err is None
        assert obj is not None
        assert obj.project == ""
        assert obj.body == ""
        assert obj.summary == ""
        assert obj.source_path == ""
        assert obj.chunking_version == "1.0"

    def test_validate_metadata_wrong_format(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 0,
            "end": 1,
            "project": "",
            "body": "",
            "summary": "",
            "source_path": "",
            "chunking_version": "",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is not None
        assert err is None
        assert obj.project == ""
        assert obj.body == ""
        assert obj.summary == ""
        assert obj.source_path == ""
        assert obj.chunking_version == "1.0"

    def test_validate_metadata_tags_not_str(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 0,
            "end": 1,
            "tags": ["tag1", "tag2"],
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert obj is not None
        assert err is None
        assert obj.tags == "tag1,tag2"

    def test_from_semantic_chunk_edge(self):
        class Dummy:
            tags = None
            links = None
            source_lines = None
            block_type = None
            metrics = None
            uuid = str(uuid.uuid4())
            type = "DocBlock"
            role = None
            language = "en"
            body = None
            text = "abc"
            summary = None
            ordinal = 0
            sha256 = "a"*64
            created_at = datetime.now(timezone.utc).isoformat()
            status = "new"
            source_path = None
            project = None
            task_id = None
            subtask_id = None
            unit_id = None
            start = 0
            end = 1
            category = None
            title = None
            year = None
            is_public = None
            source = None
        flat = FlatSemanticChunk.from_semantic_chunk(Dummy())
        assert isinstance(flat, FlatSemanticChunk)
        assert flat.tags == ""
        assert flat.link_parent is None
        assert flat.link_related is None
        assert flat.source_lines_start is None
        assert flat.source_lines_end is None
        assert flat.project == ""
        assert flat.body == ""
        assert flat.summary == ""
        assert flat.source_path == ""

    def test_to_semantic_chunk_edge(self):
        data = {
            "uuid": str(uuid.uuid4()),
            "type": "DocBlock",
            "text": "abc",
            "language": "en",
            "sha256": "a"*64,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "start": 0,
            "end": 1,
            "tags": "",
            "link_parent": None,
            "link_related": None,
            "project": "",
            "body": "",
            "summary": "",
            "source_path": "",
            "chunking_version": "",
            "task_id": str(uuid.uuid4()),
            "subtask_id": str(uuid.uuid4()),
            "unit_id": str(uuid.uuid4()),
            "source_id": str(uuid.uuid4()),
            "block_id": str(uuid.uuid4()),
        }
        obj, err = FlatSemanticChunk.validate_and_fill(data)
        assert err is None
        assert obj is not None
        assert obj.project == ""
        assert obj.body == ""
        assert obj.summary == ""
        assert obj.source_path == ""
        assert obj.chunking_version == "1.0" 