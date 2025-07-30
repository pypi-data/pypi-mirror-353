import pytest
import uuid
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkRole, ChunkStatus, SemanticChunk, FlatSemanticChunk

def valid_uuid():
    return str(uuid.uuid4())

def test_flat_metadata_all_none():
    builder = ChunkMetadataBuilder(project="xx", unit_id="xx")
    data = builder.build_flat_metadata(
        text="xx",
        source_id=valid_uuid(),
        ordinal=0,
        type=ChunkType.DOC_BLOCK,
        language="xx"
    )
    # Все опциональные поля должны быть None или дефолт
    assert data["summary"] is None
    assert data["tags"] is None
    assert data["role"] is None
    assert data["task_id"] is None
    assert data["subtask_id"] is None
    assert data["link_parent"] is None
    assert data["link_related"] is None
    assert data["category"] is None
    assert data["title"] is None
    assert data["year"] is None
    assert data["is_public"] is None
    assert data["source"] is None

def test_flat_metadata_enum_and_str():
    builder = ChunkMetadataBuilder(project="xx", unit_id="xx")
    data1 = builder.build_flat_metadata(
        text="xx",
        source_id=valid_uuid(),
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language="xx",
        role=ChunkRole.USER,
        status=ChunkStatus.NEW
    )
    data2 = builder.build_flat_metadata(
        text="xx",
        source_id=valid_uuid(),
        ordinal=1,
        type="DocBlock",
        language="xx",
        role="user",
        status="new"
    )
    assert data1["type"] == data2["type"] == "DocBlock"
    assert data1["role"] == data2["role"] == "user"
    assert data1["status"] == data2["status"] == "new"

def test_flat_metadata_invalid_coverage():
    builder = ChunkMetadataBuilder(project="xx", unit_id="xx")
    with pytest.raises(ValueError):
        builder.build_flat_metadata(
            text="test text",
            source_id=str(uuid.uuid4()),
            ordinal=1,
            type=ChunkType.DOC_BLOCK,
            language="ru",
            coverage="not_a_number"
        )

def test_semantic_chunk_invalid_links():
    builder = ChunkMetadataBuilder(project="xx", unit_id="xx")
    with pytest.raises(ValueError):
        builder.build_semantic_chunk(
            text="xx",
            language="xx",
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=valid_uuid(),
            links=["not_a_link"]
        )
    with pytest.raises(ValueError):
        builder.build_semantic_chunk(
            text="xx",
            language="xx",
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=valid_uuid(),
            links=["parent:not-a-uuid"]
        )

def test_semantic_chunk_invalid_enum():
    builder = ChunkMetadataBuilder(project="xx", unit_id="xx")
    with pytest.raises(ValueError):
        builder.build_semantic_chunk(
            text="xx",
            language="xx",
            chunk_type="notatype",
            source_id=valid_uuid()
        )
    with pytest.raises(ValueError):
        builder.build_semantic_chunk(
            text="xx",
            language="xx",
            chunk_type=ChunkType.DOC_BLOCK,
            role="notarole",
            source_id=valid_uuid()
        )
    with pytest.raises(ValueError):
        builder.build_semantic_chunk(
            text="xx",
            language="xx",
            chunk_type=ChunkType.DOC_BLOCK,
            status="notastatus",
            source_id=valid_uuid()
        )

def test_semantic_chunk_tags_links_none():
    builder = ChunkMetadataBuilder(project="xx", unit_id="xx")
    with pytest.raises(Exception):
        builder.build_semantic_chunk(
            text="xx",
            language="xx",
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=valid_uuid(),
            tags=["tag1"],
            links=["parent:" + valid_uuid()]
        )

def test_semantic_chunk_tags_links_empty():
    builder = ChunkMetadataBuilder(project="xx", unit_id="xx")
    with pytest.raises(Exception):
        builder.build_semantic_chunk(
            text="xx",
            language="xx",
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=valid_uuid(),
            tags=["tag1"],
            links=["parent:" + valid_uuid()]
        )

def test_semantic_chunk_invalid_source_id():
    builder = ChunkMetadataBuilder(project="xx", unit_id="xx")
    with pytest.raises(ValueError):
        builder.build_semantic_chunk(
            text="xx",
            language="xx",
            chunk_type=ChunkType.DOC_BLOCK,
            source_id="not-a-uuid"
        )

def test_semantic_chunk_business_fields_extreme():
    builder = ChunkMetadataBuilder(project="xx", unit_id="xx")
    with pytest.raises(Exception):
        builder.build_semantic_chunk(
            text="xx",
            language="xx",
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=valid_uuid(),
            category="x"*64,
            title="y"*256,
            year=2100,
            is_public=True,
            source="z"*64,
            tags=["tag1"],
            links=["parent:" + valid_uuid()]
        )

def test_flat_to_semantic_and_back_edge():
    builder = ChunkMetadataBuilder(project="xx", unit_id=str(uuid.uuid4()))
    flat = builder.build_flat_metadata(
        text="xx",
        source_id=valid_uuid(),
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language="xx",
        category="cat",
        title="title",
        year=2022,
        is_public=False,
        source="user",
        tags="tag1,tag2"
    )
    with pytest.raises(Exception):
        builder.flat_to_semantic(flat) 