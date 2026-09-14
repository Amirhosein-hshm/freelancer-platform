from enum import Enum


class FormFieldType(Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    FILE = "file"
    JSON = "json"


class FormTemplateStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
