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
    UNKNOWN = "UNKNOWN"
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
        return cls.UNKNOWN


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
    summary: str = Field(default="", min_length=0, max_length=512)
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
        import hashlib
        from datetime import datetime, timezone
        errors = {}
        error_lines = []
        # 0. text/body: хотя бы одно обязательно, второе заполняется из первого
        text = data.get('text')
        body = data.get('body')
        if (not text or text == '') and (not body or body == ''):
            return None, {'error': 'Either text or body must be provided', 'fields': {'text': ['Field required'], 'body': ['Field required']}}
        if not text or text == '':
            data['text'] = body
        if not body or body == '':
            data['body'] = text
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()
        # sha256: если явно передан и невалиден — ошибка, иначе всегда пересчитывается по text
        if 'sha256' in data.keys():
            sha256 = data.get('sha256', None)
            print(f"[BaseChunkFlatFields.validate_and_fill] sha256: {sha256}")
            if sha256 is not None and sha256 != '':
                if not re.fullmatch(r"[0-9a-fA-F]{64}", str(sha256)):
                    return None, {'error': 'sha256 must be a 64-character hex string', 'fields': {'sha256': ['Invalid sha256']}}
        # sha256 всегда пересчитывается по text
        if data.get('text'):
            data['sha256'] = hashlib.sha256(data['text'].encode('utf-8')).hexdigest()
        for name, field in BaseChunkFlatFields.model_fields.items():
            val = data.get(name, None)
            is_required = field.is_required()
            base_type = field.annotation
            if hasattr(base_type, 'default_value'):
                if not is_required and (val is None or val == ""):
                    data[name] = base_type.default_value()
                elif val is not None and val != "":
                    try:
                        base_type(val)
                    except Exception:
                        errors.setdefault(name, []).append(f'Invalid {name}')
                        error_lines.append(f'{name}: Invalid {name}')
            elif not is_required and (val is None or val == ""):
                if field.default is not None:
                    data[name] = field.default
                elif hasattr(field, 'default_factory') and field.default_factory is not None:
                    data[name] = field.default_factory()
        # Автозаполнение числовых полей (start, end) если None -> 0
        for int_field in ['start', 'end']:
            if int_field in data and data[int_field] is None:
                data[int_field] = 0
        try:
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
        from pydantic import ValidationError
        import hashlib
        from datetime import datetime, timezone
        errors = {}
        error_lines = []
        text = data.get('text')
        body = data.get('body')
        if (not text or text == '') and (not body or body == ''):
            errors.setdefault('text', []).append('Field required')
            errors.setdefault('body', []).append('Field required')
            error_lines.append('Either text or body must be provided')
        if not text or text == '':
            data['text'] = body
        if not body or body == '':
            data['body'] = text
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()
        # sha256: если явно передан и невалиден — ошибка, иначе всегда пересчитывается по text
        if 'sha256' in data.keys():
            sha256 = data.get('sha256', None)
            print(f"[SemanticChunk.validate_and_fill] sha256: {sha256}")
            if sha256 is not None and sha256 != '':
                if not re.fullmatch(r"[0-9a-fA-F]{64}", str(sha256)):
                    errors.setdefault('sha256', []).append('Invalid sha256')
                    error_lines.append('sha256 must be a 64-character hex string')
        # sha256 всегда пересчитывается по text
        if data.get('text'):
            data['sha256'] = hashlib.sha256(data['text'].encode('utf-8')).hexdigest()
        # tags: строгая валидация
        tags = data.get('tags', [])
        if tags is None:
            tags = []
        if not isinstance(tags, list):
            errors.setdefault('tags', []).append('Input should be a valid list')
            error_lines.append('tags must be a list')
        else:
            for tag in tags:
                if not isinstance(tag, str) or not tag or len(tag) > 32:
                    errors.setdefault('tags', []).append(f"Invalid tag: '{tag}'")
                    error_lines.append(f"Invalid tag: '{tag}'")
        # links: если невалидные — ошибка
        links = data.get('links', [])
        if links is None:
            links = []
        if not isinstance(links, list):
            errors.setdefault('links', []).append('Input should be a valid list')
            error_lines.append('links must be a list')
        else:
            for l in links:
                if not isinstance(l, str) or not re.match(r'^(parent|related):[0-9a-fA-F\-]{36}$', l):
                    errors.setdefault('links', []).append(f'Invalid link: {l}')
                    error_lines.append(f'Invalid link: {l}')
        # end < start: ошибка
        start = data.get('start', None)
        end = data.get('end', None)
        if start is not None and end is not None and isinstance(start, int) and isinstance(end, int):
            if end < start:
                errors.setdefault('end', []).append('end must be >= start')
                error_lines.append('end must be >= start')
        # source_lines: если невалидные — ошибка
        source_lines = data.get('source_lines', None)
        if source_lines is not None:
            if not (isinstance(source_lines, list) and len(source_lines) == 2 and all(isinstance(x, int) for x in source_lines)):
                errors.setdefault('source_lines', []).append('source_lines must be a list of two integers [start, end]')
                error_lines.append('source_lines must be a list of two integers [start, end]')
        # source_lines_start/source_lines_end: автозаполнение по логике диапазона строк исходного текста (как в FlatSemanticChunk)
        start = data.get('start', 0) or 0
        text = data.get('text', '') or ''
        # source_lines_start
        if 'source_lines_start' in data:
            if data['source_lines_start'] is None or data['source_lines_start'] < 0:
                data['source_lines_start'] = max(0, start)
            elif data['source_lines_start'] < start:
                data['source_lines_start'] = start
        else:
            data['source_lines_start'] = max(0, start)
        # source_lines_end
        if 'source_lines_end' not in data or data['source_lines_end'] in (None, 0):
            n_lines = text.count('\n')
            if text and not text.endswith('\n'):
                n_lines += 1
            data['source_lines_end'] = data['source_lines_start'] + n_lines
        elif data['source_lines_end'] < data['source_lines_start']:
            data['source_lines_end'] = data['source_lines_start']
        elif ('end' in data and data['end'] is not None and data['source_lines_end'] < data['end']):
            data['source_lines_end'] = data['end']
        for name, field in SemanticChunk.model_fields.items():
            val = data.get(name, None)
            is_required = field.is_required()
            base_type = field.annotation
            if hasattr(base_type, 'default_value'):
                if not is_required and (val is None or val == ""):
                    data[name] = base_type.default_value()
                elif val is not None and val != "":
                    try:
                        base_type(val)
                    except Exception:
                        errors.setdefault(name, []).append(f'Invalid {name}')
                        error_lines.append(f'{name}: Invalid {name}')
            elif not is_required and (val is None or val == ""):
                if field.default is not None:
                    data[name] = field.default
                elif hasattr(field, 'default_factory') and field.default_factory is not None:
                    data[name] = field.default_factory()
        if error_lines:
            error_text = '; '.join(error_lines)
            return None, {'error': error_text, 'fields': errors}
        try:
            obj = SemanticChunk(**data)
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
            return None, {'error': f"Validation error(s): {error_text}", 'fields': field_errors}
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
            elif min_len == 0:
                if val is None:
                    data[name] = ''
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
    summary: Optional[str] = Field(default="", min_length=0, max_length=512)

    @staticmethod
    def validate_and_fill(data: dict) -> tuple[Optional["FlatSemanticChunk"], Optional[dict]]:
        from pydantic import ValidationError
        import hashlib
        from datetime import datetime, timezone
        text = data.get('text')
        body = data.get('body')
        if (not text or text == '') and (not body or body == ''):
            return None, {'error': 'Either text or body must be provided', 'fields': {'text': ['Field required'], 'body': ['Field required']}}
        if not text or text == '':
            data['text'] = body
        if not body or body == '':
            data['body'] = text
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()
        if data.get('text'):
            if not data.get('sha256'):
                data['sha256'] = hashlib.sha256(data['text'].encode('utf-8')).hexdigest()
        if data.get('body'):
            if not data.get('sha256'):
                data['sha256'] = hashlib.sha256(data['body'].encode('utf-8')).hexdigest()
        # end < start: ошибка
        start = data.get('start', None)
        end = data.get('end', None)
        if start is not None and end is not None and isinstance(start, int) and isinstance(end, int):
            if end < start:
                return None, {'error': 'end must be >= start', 'fields': {'end': ['end must be >= start']}}
        # link_parent/link_related: если невалидный UUID — ошибка
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
        for link_field in ['link_parent', 'link_related']:
            val = data.get(link_field, None)
            if val is not None and val != '':
                if not isinstance(val, str) or not uuid_pattern.match(val):
                    return None, {'error': f'Invalid {link_field} UUID', 'fields': {link_field: ['Invalid UUID']}}
        # sha256: если явно передан и невалиден — ошибка
        sha256 = data.get('sha256', None)
        if sha256 is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", str(sha256)):
            return None, {'error': 'sha256 must be a 64-character hex string', 'fields': {'sha256': ['Invalid sha256']}}
        # если была ошибка — return сразу
        # tags: строгая валидация — только строка или список строк, каждый тег <=32, пустые игнорировать
        tags = data.get('tags', None)
        if tags is None:
            tags_str = ''
        elif isinstance(tags, list):
            filtered = [str(t).strip() for t in tags if str(t).strip()]
            for tag in filtered:
                if not isinstance(tag, str) or len(tag) > 32:
                    return None, {'error': f"Invalid tag: '{tag}'", 'fields': {'tags': [f"Invalid tag: '{tag}'"]}}
            tags_str = ','.join(filtered)
        elif isinstance(tags, str):
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            for tag in tag_list:
                if len(tag) > 32:
                    return None, {'error': f"Invalid tag: '{tag}'", 'fields': {'tags': [f"Invalid tag: '{tag}'"]}}
            tags_str = ','.join(tag_list)
        else:
            return None, {'error': 'tags must be a string or list', 'fields': {'tags': ['Input should be a valid string or list of strings']}}
        data['tags'] = tags_str
        # source_lines_start/source_lines_end: если не переданы, но есть start/end — подставлять их значения, иначе 0
        if 'source_lines_start' not in data or data['source_lines_start'] is None:
            data['source_lines_start'] = data.get('start', 0)
        if 'source_lines_end' not in data or data['source_lines_end'] is None:
            data['source_lines_end'] = data.get('end', 0)
        # block_meta: если отсутствует — автозаполнить пустым dict
        if 'block_meta' not in data or data['block_meta'] is None:
            data['block_meta'] = {}
        # Формирование error_message для нескольких ошибок
        errors = {}
        error_lines = []
        for name, field in FlatSemanticChunk.model_fields.items():
            val = data.get(name, None)
            is_required = field.is_required()
            base_type = field.annotation
            if hasattr(base_type, 'default_value'):
                if not is_required and (val is None or val == ""):
                    data[name] = base_type.default_value()
                elif val is not None and val != "":
                    try:
                        base_type(val)
                    except Exception:
                        errors.setdefault(name, []).append(f'Invalid {name}')
                        error_lines.append(f'{name}: Invalid {name}')
            elif not is_required and (val is None or val == ""):
                if field.default is not None:
                    data[name] = field.default
                elif hasattr(field, 'default_factory') and field.default_factory is not None:
                    data[name] = field.default_factory()
        try:
            obj = FlatSemanticChunk(**data)
            if errors:
                error_text = '; '.join(error_lines) if error_lines else 'Validation error(s)'
                return None, {'error': error_text, 'fields': errors}
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
            return None, {'error': f"Validation error(s): {error_text}", 'fields': field_errors}
        except Exception as e:
            return None, {'error': str(e), 'fields': {}}

    @classmethod
    def from_semantic_chunk(cls, chunk: SemanticChunk) -> 'FlatSemanticChunk':
        data = chunk.model_dump()
        tags = ','.join([t for t in chunk.tags if t.strip()]) if chunk.tags else ''
        if tags is None or tags == []:
            tags = ''
        link_parent = None
        link_related = None
        for link in getattr(chunk, 'links', []) or []:
            if link.startswith('parent:'):
                link_parent = link.split(':', 1)[1]
            elif link.startswith('related:'):
                link_related = link.split(':', 1)[1]
        source_lines_start = chunk.source_lines[0] if chunk.source_lines and len(chunk.source_lines) > 0 else 0
        source_lines_end = chunk.source_lines[1] if chunk.source_lines and len(chunk.source_lines) > 1 else 0
        # block_meta: всегда dict, не None
        block_meta = getattr(chunk, 'block_meta', None)
        if block_meta is None:
            block_meta = {}
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
            'block_meta': block_meta,
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