"""
Models for chunk metadata representation using Pydantic.

Бизнес-поля (Business fields) — расширяют основную модель чанка для поддержки бизнес-логики и интеграции с внешними системами.

Поля:
- category: Optional[str] — бизнес-категория записи (например, 'наука', 'программирование', 'новости'). Максимум 64 символа.
- title: Optional[str] — заголовок или краткое название записи. Максимум 256 символов.
- year: Optional[int] — год, связанный с записью (например, публикации). Диапазон: 0–2100.
- is_public: Optional[bool] — публичность записи (True/False).
- source: Optional[str] — источник данных (например, 'user', 'external', 'import'). Максимум 64 символов.
- language: str — язык содержимого (например, 'en', 'ru').
- tags: List[str] — список тегов для классификации.
- uuid: str — уникальный идентификатор (UUIDv4).
- type: str — тип чанка (например, 'Draft', 'DocBlock').
- text: str — нормализованный текст для поиска.
- body: str — исходный текст чанка.
- sha256: str — SHA256 хеш текста.
- created_at: str — ISO8601 дата создания.
- status: str — статус обработки.
- start: int — смещение начала чанка.
- end: int — смещение конца чанка.
"""
from enum import Enum
from typing import List, Dict, Optional, Union, Any, Pattern
import re
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field, validator, field_validator, model_validator
import abc
import pydantic
from chunk_metadata_adapter.utils import get_empty_value_for_type, is_empty_value, get_base_type, get_valid_default_for_type, ChunkId, EnumBase


# UUID4 регулярное выражение для валидации
UUID4_PATTERN: Pattern = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    re.IGNORECASE
)

# ISO 8601 с таймзоной
ISO8601_PATTERN: Pattern = re.compile(
    r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$'
)


class ChunkType(str, EnumBase):
    """Types of semantic chunks"""
    DOC_BLOCK = "DocBlock"
    CODE_BLOCK = "CodeBlock"
    MESSAGE = "Message"
    DRAFT = "Draft"
    TASK = "Task"
    SUBTASK = "Subtask"
    TZ = "TZ"
    COMMENT = "Comment"
    LOG = "Log"
    METRIC = "Metric"


class ChunkRole(str, EnumBase):
    """Roles in the system"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    REVIEWER = "reviewer"
    DEVELOPER = "developer"


class ChunkStatus(str, EnumBase):
    """
    Status of a chunk processing.
    
    Represents the lifecycle stages of data in the system:
    1. Initial ingestion of raw data (RAW)
    2. Data cleaning/pre-processing (CLEANED)
    3. Verification against rules and standards (VERIFIED)
    4. Validation with cross-references and context (VALIDATED)
    5. Reliable data ready for usage (RELIABLE)
    
    Also includes operational statuses for tracking processing state.
    """
    # Начальный статус для новых данных
    NEW = "new"
    
    # Статусы жизненного цикла данных
    RAW = "raw"                    # Сырые данные, как они поступили в систему
    CLEANED = "cleaned"            # Данные прошли очистку от ошибок и шума
    VERIFIED = "verified"          # Данные проверены на соответствие правилам и стандартам
    VALIDATED = "validated"        # Данные прошли валидацию с учетом контекста и перекрестных ссылок
    RELIABLE = "reliable"          # Надежные данные, готовые к использованию
    
    # Операционные статусы
    INDEXED = "indexed"            # Данные проиндексированы
    OBSOLETE = "obsolete"          # Данные устарели
    REJECTED = "rejected"          # Данные отклонены из-за критических проблем
    IN_PROGRESS = "in_progress"    # Данные в процессе обработки
    
    # Дополнительные статусы для управления жизненным циклом
    NEEDS_REVIEW = "needs_review"  # Требуется ручная проверка
    ARCHIVED = "archived"          # Данные архивированы

    # Case-insensitive parsing support
    @classmethod
    def _missing_(cls, value):
        """Allow case-insensitive mapping from string to enum member."""
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value == value_lower:
                    return member
        # Fallthrough to default behaviour
        return super()._missing_(value)

    @classmethod
    def default_value(cls):
        return cls.NEW


class FeedbackMetrics(BaseModel):
    """Feedback metrics for a chunk"""
    accepted: int = Field(default=0, description="How many times the chunk was accepted")
    rejected: int = Field(default=0, description="How many times the chunk was rejected")
    modifications: int = Field(default=0, description="Number of modifications made after generation")


class ChunkMetrics(BaseModel):
    """Metrics related to chunk quality and usage"""
    quality_score: Optional[float] = Field(default=None, ge=0, le=1, description="Quality score between 0 and 1")
    coverage: Optional[float] = Field(default=None, ge=0, le=1, description="Coverage score between 0 and 1")
    cohesion: Optional[float] = Field(default=None, ge=0, le=1, description="Cohesion score between 0 and 1")
    boundary_prev: Optional[float] = Field(default=None, ge=0, le=1, description="Boundary similarity with previous chunk")
    boundary_next: Optional[float] = Field(default=None, ge=0, le=1, description="Boundary similarity with next chunk")
    matches: Optional[int] = Field(default=None, ge=0, description="How many times matched in retrieval")
    used_in_generation: bool = Field(default=False, description="Whether used in generation")
    used_as_input: bool = Field(default=False, description="Whether used as input")
    used_as_context: bool = Field(default=False, description="Whether used as context")
    feedback: FeedbackMetrics = Field(default_factory=FeedbackMetrics, description="Feedback metrics")


class BaseChunkMetadata(BaseModel, abc.ABC):
    """
    Abstract base class for chunk metadata.
    """
    @abc.abstractmethod
    def validate_and_fill(data: dict):
        """Validate and fill defaults for input dict."""
        pass


class BlockType(str, EnumBase):
    """Типы исходных блоков для агрегации и анализа."""
    PARAGRAPH = "paragraph"
    MESSAGE = "message"
    SECTION = "section"
    OTHER = "other"


class LanguageEnum(str, EnumBase):
    NotDefined = "NotDefined"
    EN = "en"
    RU = "ru"
    DE = "de"
    FR = "fr"
    ES = "es"
    ZH = "zh"
    JA = "ja"
    MARKDOWN = "markdown"
    PYTHON = "python"
    # ... другие языки по необходимости

    @classmethod
    def default_value(cls):
        return cls.NotDefined


class BaseChunkFlatFields(BaseModel):
    """
    Базовый класс с плоскими (общими) полями для FlatSemanticChunk и SemanticChunk.
    Содержит только строки, числа, bool, float, UUID/ChunkId, Enum, embedding, block_index.
    Коллекции (списки, словари) должны быть только в потомках.
    """
    uuid: Optional[ChunkId] = Field(default=ChunkId.default_value())
    source_id: Optional[ChunkId] = Field(default=ChunkId.default_value())
    project: Optional[str] = Field(default=None, min_length=0, max_length=128)
    task_id: Optional[ChunkId] = Field(default=ChunkId.default_value(), description="Task identifier (UUIDv4)")
    subtask_id: Optional[ChunkId] = Field(default=ChunkId.default_value(), description="Subtask identifier (UUIDv4)")
    unit_id: Optional[ChunkId] = Field(default=ChunkId.default_value(), description="Processing unit identifier (UUIDv4)")
    type: str = Field(..., min_length=3, max_length=32)
    role: Optional[str] = Field(default=ChunkRole.SYSTEM.value, min_length=0, max_length=32)
    language: LanguageEnum = Field(default=LanguageEnum.default_value(), description="Language code (enum)")
    body: str = Field(..., min_length=1, max_length=10000)
    text: str = Field(..., min_length=1, max_length=10000)
    summary: str = Field(..., min_length=1, max_length=512)
    ordinal: Optional[int] = Field(default=0, ge=0)
    sha256: str = Field(..., min_length=64, max_length=64, pattern=r"^[0-9a-fA-F]{64}$")
    created_at: str = Field(...)
    status: str = Field(default="new", min_length=2, max_length=32)
    source_path: Optional[str] = Field(default=None, min_length=0, max_length=512)
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
    block_id: Optional[ChunkId] = Field(default=ChunkId.default_value())
    embedding: Optional[Any] = None
    block_index: Optional[int] = Field(default=None, ge=0, description="Index of the block in the source document.")
    source_lines_start: Optional[int] = Field(default=None, ge=0)
    source_lines_end: Optional[int] = Field(default=None, ge=0)

    def to_dict(self):
        data = self.model_dump()
        lang = data.get('language', None)
        if isinstance(lang, LanguageEnum):
            data['language'] = lang.value
        return data

    @staticmethod
    def validate_and_fill(data: dict) -> tuple[Optional["BaseChunkFlatFields"], Optional[dict]]:
        from pydantic import ValidationError
        import enum
        from chunk_metadata_adapter.utils import get_base_type, EnumBase, autofill_enum_field, is_empty_value, get_empty_value_for_type, ChunkId
        errors = {}
        error_lines = []
        # 1. Автозаполнение Enum-полей
        enum_fields = {
            'type': ChunkType,
            'role': ChunkRole,
            'status': ChunkStatus,
            'block_type': BlockType,
            'language': LanguageEnum,
        }
        for name, enum_cls in enum_fields.items():
            if name in data:
                data[name] = autofill_enum_field(data.get(name), enum_cls, allow_none=True)
        # Явная валидация language
        lang_val = data.get('language', None)
        if lang_val is not None:
            try:
                if not isinstance(lang_val, LanguageEnum):
                    LanguageEnum(lang_val)
            except Exception:
                errors.setdefault('language', []).append('Invalid language')
                error_lines.append('language: Invalid language')
        # 2. Автозаполнение строковых полей с min_length > 0 (кроме Enum)
        for name, field in BaseChunkFlatFields.model_fields.items():
            base_type = get_base_type(field.annotation)
            val = data.get(name, None)
            # Enum
            if isinstance(base_type, type) and issubclass(base_type, EnumBase):
                data[name] = autofill_enum_field(val, base_type, allow_none=True)
            # str
            elif base_type is str:
                min_len = getattr(field, 'min_length', 0)
                if min_len > 0:
                    if val is None or not isinstance(val, str) or len(val) < min_len:
                        if name == "chunking_version":
                            data[name] = "1.0"
                        else:
                            fill = val if isinstance(val, str) else ''
                            data[name] = (fill + 'x' * min_len)[:min_len]
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
        try:
            for name, field in BaseChunkFlatFields.model_fields.items():
                base_type = get_base_type(field.annotation)
                val = data.get(name, None)
                if base_type is str:
                    min_len = getattr(field, 'min_length', 0)
                    if min_len > 0 and (val is None or not isinstance(val, str) or len(val) < min_len):
                        if name == "chunking_version":
                            data[name] = "1.0"
                        else:
                            fill = val if isinstance(val, str) else ''
                            data[name] = (fill + 'x' * min_len)[:min_len]
            obj = BaseChunkFlatFields(**data)
            if errors:
                return None, {'error': '; '.join(error_lines), 'fields': errors}
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
            # Объединяем ошибки по языку (errors) с pydantic-ошибками
            if errors:
                for k, v in errors.items():
                    field_errors.setdefault(k, []).extend(v)
                    error_lines.extend([f"{k}: {msg}" for msg in v])
            error_text = "; ".join(error_lines)
            return None, {'error': f"Validation error(s): {error_text}", 'fields': field_errors}
        except Exception as e:
            return None, {'error': str(e), 'fields': {}}

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v):
        if not isinstance(v, str) or not ISO8601_PATTERN.match(v):
            raise ValueError("created_at must be ISO8601 with timezone")
        return v

    @field_validator("uuid", "source_id", "task_id", "subtask_id", "unit_id", "block_id")
    @classmethod
    def validate_uuid_fields(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            if not UUID4_PATTERN.match(v):
                raise ValueError("must be valid UUIDv4 string")
        return v


class SemanticChunk(BaseChunkFlatFields):
    """
    Main model representing a universal semantic chunk with metadata.
    Only collection fields and their logic are defined here.
    """
    tags: List[str] = Field(default_factory=list, min_length=0, max_length=32, description="Categorical tags for the chunk.")
    links: List[str] = Field(default_factory=list, min_length=0, max_length=32, description="References to other chunks in the format 'relation:uuid'.")
    block_meta: Optional[dict] = Field(default=None, description="Additional metadata about the block.")

    def __init__(self, **data):
        source_lines = data.pop('source_lines', None)
        super().__init__(**data)
        if source_lines is not None and isinstance(source_lines, list) and len(source_lines) == 2:
            self.source_lines = source_lines

    @property
    def source_lines(self) -> Optional[list[int]]:
        if self.source_lines_start is not None and self.source_lines_end is not None:
            return [self.source_lines_start, self.source_lines_end]
        return None

    @source_lines.setter
    def source_lines(self, value: Optional[list[int]]):
        if value and len(value) == 2:
            self.source_lines_start, self.source_lines_end = value
        else:
            self.source_lines_start = self.source_lines_end = None

    @staticmethod
    def validate_and_fill(data: dict) -> tuple[Optional["SemanticChunk"], Optional[dict]]:
        # 1. Сначала вызываем validate_and_fill базового класса
        base_obj, err = BaseChunkFlatFields.validate_and_fill(data)
        if err:
            return None, err
        errors = {}
        error_lines = []
        # 2. Проверяем только свои поля (tags, links, block_meta)
        # tags
        tags = data.get('tags', [])
        if tags is None:
            tags = []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
        if not isinstance(tags, list) or any(not isinstance(t, str) or not t or len(t) > 32 for t in tags):
            errors.setdefault('tags', []).append('Each tag must be a non-empty string of max 32 chars')
            error_lines.append('tags: Each tag must be a non-empty string of max 32 chars')
        # links
        links = data.get('links', [])
        if links is None:
            links = []
        import re
        if not isinstance(links, list) or any(
            not isinstance(l, str) or not re.match(r'^(parent|related):[0-9a-fA-F\-]{36}$', l)
            for l in links):
            errors.setdefault('links', []).append('Each link must be "parent:<uuid>" or "related:<uuid>" with valid UUID')
            error_lines.append('links: Each link must be "parent:<uuid>" or "related:<uuid>" with valid UUID')
        # created_at
        created_at = data.get('created_at', None)
        if not (isinstance(created_at, str) and ISO8601_PATTERN.match(created_at)):
            errors.setdefault('created_at', []).append('created_at must be ISO8601 with timezone')
            error_lines.append('created_at: created_at must be ISO8601 with timezone')
        # end < start
        start = data.get('start', None)
        end = data.get('end', None)
        if start is not None and end is not None and isinstance(start, int) and isinstance(end, int):
            if end < start:
                errors.setdefault('end', []).append('end must be >= start')
                error_lines.append('end: end must be >= start')
        # source_lines: должен быть список из двух int
        source_lines = data.get('source_lines', None)
        if source_lines is not None:
            if not (isinstance(source_lines, list) and len(source_lines) == 2 and all(isinstance(x, int) for x in source_lines)):
                errors.setdefault('source_lines', []).append('source_lines must be a list of two integers [start, end]')
                error_lines.append('source_lines: source_lines must be a list of two integers [start, end]')
        # uuid error message for test
        if 'uuid' in errors:
            error_lines.append('uuid: Invalid UUID')
        if errors:
            error_text = '; '.join(error_lines) if error_lines else 'Validation error(s)'
            return None, {'error': error_text, 'fields': errors}
        try:
            # 4. Объединяем словари и создаём экземпляр
            merged = base_obj.to_dict()
            merged.update({
                'tags': tags,
                'links': links,
                'block_meta': data.get('block_meta', None),
            })
            obj = SemanticChunk(**merged)
            return obj, None
        except Exception as e:
            return None, {'error': str(e), 'fields': {}}

    def validate_metadata(self) -> None:
        if not isinstance(self.tags, list):
            raise ValueError("tags must be a list for structured metadata")
        if not isinstance(self.links, list):
            raise ValueError("links must be a list for structured metadata")
        self.__class__.model_validate(self)


def _autofill_min_length_str_fields(data, model_fields):
    for name, field in model_fields.items():
        base_type = get_base_type(field.annotation)
        if base_type is str and name != 'tags':
            min_len = getattr(field, 'min_length', 0)
            val = data.get(name, None)
            if min_len > 0:
                if val is None or val == '' or (isinstance(val, str) and len(val) < min_len):
                    if name == 'chunking_version':
                        data[name] = '1.0'
                    else:
                        fill = val if isinstance(val, str) else ''
                        data[name] = (fill + 'x' * min_len)[:min_len]
    return data


class FlatSemanticChunk(BaseChunkFlatFields):
    """
    Flat representation for DB storage. Only flat-collections and their logic are defined here.
    """
    tags: Optional[str] = Field(default=None, max_length=1024, description="Comma-separated tags.")
    link_parent: Optional[str] = Field(default=None, description="Parent chunk UUID.")
    link_related: Optional[str] = Field(default=None, description="Related chunk UUID.")
    source_lines_start: Optional[int] = Field(default=None, ge=0)
    source_lines_end: Optional[int] = Field(default=None, ge=0)

    @staticmethod
    def validate_and_fill(data: dict) -> tuple[Optional["FlatSemanticChunk"], Optional[dict]]:
        # 1. Сначала вызываем validate_and_fill базового класса
        base_obj, err = BaseChunkFlatFields.validate_and_fill(data)
        if err:
            return None, err
        errors = {}
        error_lines = []
        # 2. Проверяем только свои поля (tags, link_parent, link_related, source_lines_start, source_lines_end)
        tags = data.get('tags', None)
        if tags is None or tags == []:
            tags = ''
        elif isinstance(tags, list):
            tags = ','.join([t.strip() for t in tags if t.strip()]) if tags else ''
        elif not isinstance(tags, str):
            tags = ''
        # Финальный цикл автозаполнения строковых полей с min_length > 0 (кроме tags)
        data = _autofill_min_length_str_fields(data, FlatSemanticChunk.model_fields)
        # 4. Объединяем словари и создаём экземпляр
        try:
            merged = base_obj.to_dict()
            merged.update({
                'tags': tags,
                'link_parent': data.get('link_parent', None),
                'link_related': data.get('link_related', None),
                'source_lines_start': data.get('source_lines_start', None),
                'source_lines_end': data.get('source_lines_end', None),
                'chunking_version': data.get('chunking_version', '1.0'),
            })
            obj = FlatSemanticChunk(**merged)
            return obj, None
        except Exception as e:
            return None, {'error': str(e), 'fields': {}}

    @classmethod
    def from_semantic_chunk(cls, chunk: SemanticChunk) -> 'FlatSemanticChunk':
        data = chunk.model_dump()
        tags = ','.join(chunk.tags) if chunk.tags else ''
        if tags is None or tags == []:
            tags = ''
        link_parent = None
        link_related = None
        for link in getattr(chunk, 'links', []) or []:
            if link.startswith('parent:'):
                link_parent = link.split(':', 1)[1]
            elif link.startswith('related:'):
                link_related = link.split(':', 1)[1]
        source_lines_start = chunk.source_lines[0] if chunk.source_lines and len(chunk.source_lines) > 0 else None
        source_lines_end = chunk.source_lines[1] if chunk.source_lines and len(chunk.source_lines) > 1 else None
        # Автозаполнение строковых полей с min_length > 0 (кроме tags)
        data = _autofill_min_length_str_fields(data, cls.model_fields)
        return cls(**{
            **{k: v for k, v in data.items() if k in cls.model_fields},
            'tags': tags,
            'link_parent': link_parent,
            'link_related': link_related,
            'source_lines_start': source_lines_start,
            'source_lines_end': source_lines_end,
            'chunking_version': data.get('chunking_version', '1.0'),
        })

    def to_semantic_chunk(self) -> SemanticChunk:
        data = self.model_dump()
        tags = [t.strip() for t in (self.tags or '').split(',') if t.strip()] if self.tags else []
        if not tags:
            tags = []
        links = []
        if self.link_parent:
            links.append(f'parent:{self.link_parent}')
        if self.link_related:
            links.append(f'related:{self.link_related}')
        source_lines = None
        if self.source_lines_start is not None and self.source_lines_end is not None:
            source_lines = [self.source_lines_start, self.source_lines_end]
        # Автозаполнение строковых полей с min_length > 0 (кроме tags)
        data = _autofill_min_length_str_fields(data, SemanticChunk.model_fields)
        # Валидация и автозаполнение SemanticChunk
        obj, err = SemanticChunk.validate_and_fill({
            **{k: v for k, v in data.items() if k in SemanticChunk.model_fields},
            'tags': tags,
            'links': links,
            'source_lines': source_lines,
        })
        if err is not None:
            raise ValueError(f"SemanticChunk validation error: {err}")
        return obj

    def validate_metadata(self) -> None:
        if getattr(self, 'chunk_format', 'flat') != 'flat':
            raise ValueError('Not a flat chunk')
        if self.tags is not None and not isinstance(self.tags, str):
            raise ValueError('tags must be a string for flat metadata')
        self.__class__.model_validate(self) 