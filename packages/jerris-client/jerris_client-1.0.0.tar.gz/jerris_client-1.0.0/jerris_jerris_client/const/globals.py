TYPE_BOOLEAN = "boolean"
TYPE_FLOAT = "float"
TYPE_INTEGER = "integer"
TYPE_LIST = "list"
TYPE_STRING = "string"
TYPE_NULL = None

SOFT_LIMIT_WIDTH = 1216
SOFT_LIMIT_HEIGHT = 768
HARD_LIMIT_WIDTH = 2000
HARD_LIMIT_HEIGHT = 2000

TYPES_EMPTY = {
    TYPE_BOOLEAN: False,
    TYPE_FLOAT: 0.0,
    TYPE_INTEGER: 0,
    TYPE_LIST: [],
    TYPE_STRING: "",
}

TYPES_MAPPING = {
    "boolean": bool,
    "integer": int,
    "float": float,
    "string": str,
    "list": list,
}

TYPE_FORMAT_HEIC = "heic"
TYPE_FORMAT_JPEG = "jpg"
TYPE_FORMAT_PNG = "png"
TYPE_FORMAT_WEBP = "webp"

SUPPORTED_IMAGES_FORMATS = {
    TYPE_FORMAT_HEIC: {"mime": ["image/heic", "image/heif"]},
    TYPE_FORMAT_JPEG: {
        "mime": ["image/jpeg"],
    },
    TYPE_FORMAT_PNG: {
        "mime": ["image/png"],
    },
    TYPE_FORMAT_WEBP: {
        "mime": ["image/webp"],
    },
}

MAX_FILE_SIZE_MB = 10
