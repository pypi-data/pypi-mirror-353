from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
import pydantic
from chunk_metadata_adapter.models import BaseChunkMetadata, ChunkStatus, ChunkMetrics, FeedbackMetrics, SemanticChunk, BlockType, ChunkType, ChunkRole, _autofill_min_length_str_fields, LanguageEnum
import uuid
from chunk_metadata_adapter.utils import (
    semantic_to_flat_value, dict_prop_to_flat_dict, flat_dict_to_dict_prop, 
    list_to_str, str_to_list, get_empty_value_for_type, is_empty_value, 
    get_base_type, get_valid_default_for_type, ChunkId, EnumBase, autofill_enum_field
)

class FlatSemanticChunk(BaseChunkMetadata):
    """
    Flat representation of the semantic chunk with all fields in a flat structure.
    Strict field validation for all fields.

    Fields:
    - uuid: Optional[ChunkId]
    - source_id: Optional[ChunkId]
    - project: Optional[str]
    - task_id: Optional[ChunkId]
    - subtask_id: Optional[ChunkId]
    - unit_id: Optional[ChunkId]
    - type: str
    - role: Optional[str]
    - language: LanguageEnum
    - body: Optional[str]
    - text: str
    - summary: Optional[str]
    - ordinal: Optional[int]
    - sha256: str
    - created_at: str
    - status: str
    - source_path: Optional[str]
    - source_lines_start: Optional[int]
    - source_lines_end: Optional[int]
    - tags: Optional[str]  # comma-separated, corresponds to List[str] in SemanticChunk
    - link_related: Optional[ChunkId]  # corresponds to links: List[str] in SemanticChunk
    - link_parent: Optional[ChunkId]   # corresponds to links: List[str] in SemanticChunk
    - quality_score: Optional[float]
    - coverage: Optional[float]
    - cohesion: Optional[float]
    - boundary_prev: Optional[float]
    - boundary_next: Optional[float]
    - used_in_generation: bool
    - feedback_accepted: int
    - feedback_rejected: int
    - start: Optional[int]
    - end: Optional[int]
    - category: Optional[str]
    - title: Optional[str]
    - year: Optional[int]
    - is_public: Optional[bool]
    - source: Optional[str]
    - block_type: Optional[BlockType]
    - chunking_version: Optional[str]  # [added] Version of the chunking algorithm or pipeline
    - metrics: Optional[ChunkMetrics]  # [added] Full metrics object for compatibility
    - block_id: Optional[ChunkId]  # [added] UUIDv4 of the source block, corresponds to block_id in SemanticChunk

    Notes:
    - tags: comma-separated string, corresponds to List[str] in SemanticChunk
    - source_lines_start/source_lines_end: correspond to source_lines: List[int] in SemanticChunk
    - link_parent/link_related: correspond to links: List[str] in SemanticChunk
    - metrics: for compatibility, but main metrics fields are flat
    """
    uuid: Optional[ChunkId] = Field(default=None)
    source_id: Optional[ChunkId] = Field(default=None)
    project: Optional[str] = Field(default=None, min_length=0, max_length=128)
    task_id: Optional[ChunkId] = Field(default=None, description="Task identifier (UUIDv4)")
    subtask_id: Optional[ChunkId] = Field(default=None, description="Subtask identifier (UUIDv4)")
    unit_id: Optional[ChunkId] = Field(default=None, description="Processing unit identifier (UUIDv4)")
    type: str = Field(..., min_length=3, max_length=32)
    role: Optional[str] = Field(default=None, min_length=0, max_length=32)
    language: LanguageEnum = Field(default=LanguageEnum.default_value(), description="Language code (enum)")
    body: Optional[str] = Field(default=None, min_length=0, max_length=10000)
    text: str = Field(..., min_length=1, max_length=10000)
    summary: Optional[str] = Field(default=None, min_length=0, max_length=512)
    ordinal: Optional[int] = Field(default=None, ge=0)
    sha256: str = Field(..., min_length=64, max_length=64, pattern=r"^[0-9a-fA-F]{64}$")
    created_at: str = Field(...)
    status: str = Field(default=ChunkStatus.NEW.value, min_length=2, max_length=32)
    source_path: Optional[str] = Field(default=None, min_length=0, max_length=512)
    source_lines_start: Optional[int] = Field(default=None, ge=0)
    source_lines_end: Optional[int] = Field(default=None, ge=0)
    tags: Optional[str] = Field(default=None, max_length=1024)
    link_related: Optional[ChunkId] = Field(default=None)
    link_parent: Optional[ChunkId] = Field(default=None)
    quality_score: Optional[float] = Field(default=None, ge=0, le=1)
    coverage: Optional[float] = Field(default=None, ge=0, le=1)
    cohesion: Optional[float] = Field(default=None, ge=0, le=1)
    boundary_prev: Optional[float] = Field(default=None, ge=0, le=1)
    boundary_next: Optional[float] = Field(default=None, ge=0, le=1)
    used_in_generation: bool = False
    feedback_accepted: int = Field(default=0, ge=0)
    feedback_rejected: int = Field(default=0, ge=0)
    start: Optional[int] = Field(default=None, ge=0)
    end: Optional[int] = Field(default=None, ge=0)
    category: Optional[str] = Field(default=None, max_length=64)
    title: Optional[str] = Field(default=None, max_length=256)
    year: Optional[int] = Field(default=None, ge=0, le=2100)
    is_public: Optional[bool] = Field(default=None)
    source: Optional[str] = Field(default=None, max_length=64)
    block_type: Optional[BlockType] = Field(default=None, description="Тип исходного блока (BlockType: 'paragraph', 'message', 'section', 'other').")
    chunking_version: Optional[str] = Field(default="1.0", min_length=1, max_length=32)
    metrics: Optional[ChunkMetrics] = Field(default=None)
    block_id: Optional[ChunkId] = Field(default=None)

    @field_validator('uuid', 'source_id', 'link_related', 'link_parent')
    @classmethod
    def validate_uuid_fields(cls, v: Optional[str], info) -> Optional[str]:
        from chunk_metadata_adapter.utils import ChunkId
        import re, uuid
        UUID4_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
        if v is None:
            return v
        if v == ChunkId.empty_uuid4():
            return v
        if not UUID4_PATTERN.match(v):
            try:
                uuid_obj = uuid.UUID(v, version=4)
                if str(uuid_obj) != v.lower():
                    raise ValueError(f"{info.field_name} UUID version or format doesn't match")
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid UUID4 format for {info.field_name}: {v}")
        return v

    @field_validator('created_at')
    @classmethod
    def validate_created_at(cls, v: str) -> str:
        import re
        ISO8601_PATTERN = re.compile(r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$')
        if not ISO8601_PATTERN.match(v):
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    raise ValueError("Missing timezone information")
                return dt.isoformat()
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid ISO8601 format with timezone: {v}")
        return v

    @field_validator('sha256')
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        import re
        if not re.fullmatch(r"[0-9a-fA-F]{64}", v):
            raise ValueError(f"sha256 must be a 64-character hex string, got: {v}")
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        tags = [tag.strip() for tag in v.split(",") if tag.strip()]
        for tag in tags:
            if not tag or len(tag) < 1 or len(tag) > 32:
                raise ValueError(f"Each tag must be 1-32 chars, got: '{tag}'")
        return v

    @field_validator('end')
    @classmethod
    def validate_end_ge_start(cls, v: Optional[int], values) -> Optional[int]:
        start = values.data.get('start') if hasattr(values, 'data') else values.get('start')
        if v is not None and start is not None and v < start:
            raise ValueError(f"end ({v}) must be >= start ({start})")
        return v

    def validate(self) -> None:
        self.__class__.model_validate(self)

    @staticmethod
    def validate_and_fill(data: dict) -> tuple[Optional["FlatSemanticChunk"], Optional[dict]]:
        from pydantic import ValidationError
        import enum
        # 1. Автозаполнение Enum-полей
        enum_fields = {
            'type': ChunkType,
            'role': ChunkRole,
            'status': ChunkStatus,
            'block_type': BlockType,
            'language': LanguageEnum,
        }
        print(f"FlatSemanticChunk.validate_and_fill data={data}")
        for name, enum_cls in enum_fields.items():
            if name in data:
                data[name] = autofill_enum_field(data.get(name), enum_cls, allow_none=True)
                print(f"FlatSemanticChunk.validate_and_fill data[{name}]: {data[name]}")
        # 2. Автозаполнение строковых полей с min_length > 0 (кроме Enum)
        for name, field in FlatSemanticChunk.model_fields.items():
            base_type = get_base_type(field.annotation)
            val = data.get(name, None)
            # Enum
            if isinstance(base_type, type) and issubclass(base_type, EnumBase):
                data[name] = autofill_enum_field(val, base_type, allow_none=True)
            # str
            elif base_type is str:
                if name == "tags":
                    if val is None or (isinstance(val, (list, tuple)) and len(val) == 0):
                        data[name] = ""
                    elif isinstance(val, (list, tuple)):
                        data[name] = ",".join([str(t).strip() for t in val if str(t).strip()])
                    elif isinstance(val, str):
                        data[name] = val
                    else:
                        raise ValueError(f"FlatSemanticChunk.validate_and_fill: tags must be a string, list, or None")
                else:
                    val = "" if val is None else val
                    if name == "chunking_version" and val.strip() == "":
                        data[name] = "1.0"
                    else:
                        if type(val) is list or type(val) is tuple:
                            if len(val) == 0:
                                data[name] = ""
                            else:
                                raise ValueError(f"FlatSemanticChunk.validate_and_fill: {name} must be a string or empty list/tuple")
                        elif type(val) is str:
                            min_len = getattr(field, 'min_length', 0)
                            strip_val = val.strip()
                            if len(strip_val) == 0 and min_len > 0:
                                data[name] = "x" * min_len
                            elif min_len > len(val):
                                raise ValueError(f"FlatSemanticChunk.validate_and_fill: {name} must be at least {min_len} chars long")
                        else:
                            raise ValueError(f"FlatSemanticChunk.validate_and_fill: {name} must be a string")
            # int/float
            elif base_type in (int, float):
                if val is None or val == "":
                    min_v = getattr(field, 'ge', None)
                    max_v = getattr(field, 'le', None)
                    if min_v is not None:
                        data[name] = min_v
                    elif max_v is not None:
                        data[name] = max_v
                    else:
                        data[name] = 0 if base_type is int else 0.0
            # bool
            elif base_type is bool:
                if val is None:
                    data[name] = False
            # UUID/ChunkId
            elif base_type is ChunkId:
                if is_empty_value(val):
                    data[name] = ChunkId.default_value()
            # pydantic.BaseModel
            elif isinstance(base_type, type) and issubclass(base_type, pydantic.BaseModel):
                if is_empty_value(val):
                    data[name] = base_type()
            # list
            elif base_type is list:
                min_len = getattr(field, 'min_length', 0)
                if val is None and min_len > 0:
                    data[name] = [None] * min_len
            # dict, tuple
            elif base_type in (dict, tuple):
                if val is None:
                    data[name] = base_type()
            # Остальные
            elif is_empty_value(val):
                data[name] = get_empty_value_for_type(base_type)
                print(f"FlatSemanticChunk.validate_and_fill Empty value for {base_type} is {name }={data[name]}")
        try:
            # Финальный цикл автозаполнения строковых полей с min_length > 0 (включая chunking_version)
            for name, field in FlatSemanticChunk.model_fields.items():
                base_type = get_base_type(field.annotation)
                val = data.get(name, None)
                if base_type is str:
                    min_len = getattr(field, 'min_length', 0)
                    if min_len > 0:
                        if val is None or not isinstance(val, str) or len(val) < min_len:
                            if name == "chunking_version":
                                data[name] = "1.0"
                            elif name == "status":
                                data[name] = "new"
                            else:
                                data[name] = "x" * min_len
                        elif val == "":
                            if name == "chunking_version":
                                data[name] = "1.0"
                            else:
                                data[name] = "x" * min_len
            # 2. Валидируем через Pydantic
            print(f"data: {data}")
            obj = FlatSemanticChunk(**data)
            print(f"obj: {obj}")
            return obj, None
        except ValidationError as e:
            field_errors = {}
            error_lines = []
            for err in e.errors():
                loc = err.get('loc')
                msg = err.get('msg')
                if loc:
                    field = loc[0]
                    field_errors.setdefault(field, []).append(msg)
                    error_lines.append(f"{field}: {msg}")
            error_text = "; ".join(error_lines)
            print(f"FlatSemanticChunk.validate_and_fill Validation error(s):")
            print({'error': f"Validation error(s): {error_text}", 'fields': field_errors})
            return None, {'error': f"Validation error(s): {error_text}", 'fields': field_errors}
        except Exception as e:
            return None, {'error': str(e), 'fields': {}}

    def validate_metadata(self) -> None:
        if self.chunk_format != "flat":
            raise ValueError(f"Invalid chunk_format for FlatSemanticChunk: {self.chunk_format}")
        if self.tags is not None and not isinstance(self.tags, str):
            raise ValueError("tags must be a string for flat metadata")
        self.validate()

    @classmethod
    def from_semantic_chunk(cls, chunk: SemanticChunk) -> 'FlatSemanticChunk':
        import uuid
        # Универсальный способ получить dict
        if hasattr(chunk, 'model_dump'):
            data = chunk.model_dump()
        elif hasattr(chunk, '__dict__'):
            data = dict(vars(chunk))
        else:
            raise TypeError("from_semantic_chunk: input must be a pydantic model or have __dict__")
        # UUID-поля: автозаполнение только валидным UUIDv4
        uuid_fields = ['uuid', 'source_id', 'task_id', 'subtask_id', 'unit_id', 'block_id']
        for f in uuid_fields:
            val = data.get(f, None)
            if not val or not isinstance(val, str):
                data[f] = ChunkId.default_value()
            else:
                try:
                    uuid_obj = uuid.UUID(val, version=4)
                    data[f] = str(uuid_obj)
                except Exception:
                    data[f] = ChunkId.default_value()
        # language: Enum
        lang = getattr(chunk, 'language', None)
        if isinstance(lang, str):
            try:
                lang = LanguageEnum(lang)
            except Exception:
                lang = LanguageEnum.default_value()
        elif not isinstance(lang, LanguageEnum):
            lang = LanguageEnum.default_value()
        data['language'] = lang
        # Списки -> строки
        tags = list_to_str(getattr(chunk, 'tags', [])) if getattr(chunk, 'tags', None) else ''
        # links -> link_parent/link_related
        link_parent = None
        link_related = None
        for link in getattr(chunk, 'links', []) or []:
            if link.startswith('parent:'):
                link_parent = link.split(':', 1)[1]
            elif link.startswith('related:'):
                link_related = link.split(':', 1)[1]
        # source_lines_start/source_lines_end
        if getattr(chunk, 'source_lines', None):
            data['source_lines_start'] = chunk.source_lines[0]
            data['source_lines_end'] = chunk.source_lines[1]
        else:
            data['source_lines_start'] = None
            data['source_lines_end'] = None
        # block_meta (dict) -> flat dict
        if hasattr(chunk, 'block_meta') and chunk.block_meta is not None:
            flat_block_meta = dict_prop_to_flat_dict(chunk.block_meta)
            data.update(flat_block_meta)
        # Автозаполнение обязательных строковых полей с min_length > 0 (type, text, sha256, created_at)
        required_str_fields = {
            'type': 'xxx',
            'text': 'x',
            'sha256': 'a'*64,
            'created_at': '1970-01-01T00:00:00+00:00',
        }
        for k, v in required_str_fields.items():
            if not data.get(k):
                data[k] = v
        # Автозаполнение строковых полей с min_length > 0 (кроме tags)
        data = _autofill_min_length_str_fields(data, cls.model_fields)
        return cls(**{
            **{k: v for k, v in data.items() if k in cls.model_fields},
            'tags': tags,
            'link_parent': link_parent,
            'link_related': link_related,
            'chunking_version': data.get('chunking_version', '1.0'),
        })

    def to_semantic_chunk(self) -> SemanticChunk:
        from chunk_metadata_adapter.utils import str_to_list, flat_dict_to_dict_prop
        data = self.model_dump()
        # language: Enum
        lang = self.language
        if isinstance(lang, str):
            try:
                lang = LanguageEnum(lang)
            except Exception:
                lang = LanguageEnum.default_value()
        elif not isinstance(lang, LanguageEnum):
            lang = LanguageEnum.default_value()
        data['language'] = lang
        # Строки -> списки
        tags = str_to_list(self.tags) if self.tags else []
        # link_parent/link_related -> links
        links = []
        if self.link_parent:
            links.append(f'parent:{self.link_parent}')
        if self.link_related:
            links.append(f'related:{self.link_related}')
        # source_lines_start/source_lines_end -> source_lines
        if self.source_lines_start is not None and self.source_lines_end is not None:
            data['source_lines'] = [self.source_lines_start, self.source_lines_end]
        else:
            data['source_lines'] = None
        # flat dict -> block_meta (dict)
        block_meta_keys = [k for k in data if '.' in k]
        if block_meta_keys:
            flat_block_meta = {k: data[k] for k in block_meta_keys}
            data['block_meta'] = flat_dict_to_dict_prop(flat_block_meta)
            for k in block_meta_keys:
                del data[k]
        # block_id: гарантировать UUIDv4 через ChunkId.default_value()
        block_id = data.get('block_id', None)
        if not block_id or not isinstance(block_id, str):
            data['block_id'] = ChunkId.default_value()
        else:
            try:
                uuid_obj = uuid.UUID(block_id, version=4)
                data['block_id'] = str(uuid_obj)
            except Exception:
                data['block_id'] = ChunkId.default_value()
        # Автозаполнение строковых полей с min_length > 0 (кроме tags)
        data = _autofill_min_length_str_fields(data, SemanticChunk.model_fields)
        # Валидация и автозаполнение SemanticChunk
        obj, err = SemanticChunk.validate_and_fill({
            **{k: v for k, v in data.items() if k in SemanticChunk.model_fields},
            'tags': tags,
            'links': links,
            'source_lines': data['source_lines'],
            'block_meta': data.get('block_meta', None),
        })
        if err is not None:
            raise ValueError(f"SemanticChunk validation error: {err}")
        return obj 

def _autofill_min_length_str_fields(data, model_fields):
    for name, field in model_fields.items():
        base_type = get_base_type(field.annotation)
        if base_type is str and name != 'tags':
            min_len = getattr(field, 'min_length', 0)
            val = data.get(name, None)
            if name == 'chunking_version':
                if val is None or val == '':
                    data[name] = '1.0'
            elif name == 'status':
                if val is None or val == '':
                    data[name] = 'new'
            elif min_len > 0:
                if val is None or val == '' or (isinstance(val, str) and len(val) < min_len):
                    fill = val if isinstance(val, str) else ''
                    data[name] = (fill + 'x' * min_len)[:min_len]
            elif min_len == 0:
                if val is None:
                    data[name] = ''
    return data 