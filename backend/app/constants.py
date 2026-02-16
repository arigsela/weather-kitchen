"""
Application constants: weather types, categories, limits, error codes.
"""

# Weather Types (10 types as per PRD)
WEATHER_TYPES = [
    "sunny",
    "cloudy",
    "rainy",
    "snowy",
    "windy",
    "stormy",
    "hazy",
    "foggy",
    "hot",
    "cold",
]

# Recipe Categories (4 types as per PRD)
RECIPE_CATEGORIES = [
    "breakfast",
    "lunch",
    "dinner",
    "snack",
]

# Limits
RECIPE_NAME_MAX_LENGTH = 100
RECIPE_EMOJI_MAX_LENGTH = 2
RECIPE_WHY_MAX_LENGTH = 500
RECIPE_TIP_MAX_LENGTH = 500
RECIPE_SERVES_MIN = 1
RECIPE_SERVES_MAX = 20
RECIPE_INGREDIENT_MAX_LENGTH = 200
RECIPE_STEP_MAX_LENGTH = 500
RECIPE_TAG_MAX_LENGTH = 50
RECIPE_TAGS_MAX_COUNT = 20

USER_NAME_MAX_LENGTH = 50
USER_EMOJI_MAX_LENGTH = 2
FAMILY_NAME_MAX_LENGTH = 100
FAMILY_SIZE_MIN = 1
FAMILY_SIZE_MAX = 20

PARENT_EMAIL_MAX_LENGTH = 254
ADMIN_PIN_MIN_DIGITS = 4
ADMIN_PIN_MAX_DIGITS = 6

INGREDIENT_TAG_MAX_LENGTH = 50
INGREDIENT_TAGS_MAX_COUNT = 100

PAGINATION_DEFAULT_LIMIT = 20
PAGINATION_MAX_LIMIT = 100

# Soft Delete Grace Period
SOFT_DELETE_GRACE_PERIOD_DAYS = 30

# Audit Log Retention
AUDIT_LOG_RETENTION_DAYS = 90

# Error Codes (used in ErrorResponse)
ERROR_CODES = {
    "VALIDATION_ERROR": "Validation failed",
    "AUTHENTICATION_REQUIRED": "Authentication required",
    "INSUFFICIENT_PERMISSIONS": "Insufficient permissions",
    "RESOURCE_NOT_FOUND": "Resource not found",
    "RESOURCE_ALREADY_EXISTS": "Resource already exists",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded",
    "INVALID_REQUEST": "Invalid request",
    "DATABASE_ERROR": "Database error",
    "INTERNAL_SERVER_ERROR": "Internal server error",
    "SERVICE_UNAVAILABLE": "Service unavailable",
    "CONSENT_REQUIRED": "Parental consent required",
    "PIN_LOCKOUT": "PIN locked due to too many failed attempts",
    "INVALID_PIN": "Invalid PIN",
    "INVALID_TOKEN": "Invalid or expired token",
    "TOKEN_ROTATED": "Token has been rotated, please use the new token",
}

# HTTP Status Codes
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_CONFLICT = 409
STATUS_LOCKED = 423  # Used for PIN lockout
STATUS_UNPROCESSABLE_ENTITY = 422
STATUS_RATE_LIMITED = 429
STATUS_INTERNAL_ERROR = 500
STATUS_SERVICE_UNAVAILABLE = 503
