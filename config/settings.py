# Server
HOST = "0.0.0.0"
PORT = 8000

# Ollama
REQUEST_TIMEOUT = 120.0

# Qdrant
TOP_K_SIMILARITY = 3

# Query Settings
UNWANTED_RESPONSE_KEYWORDS = [".save"]
MAX_RETRIES = 3
EDIT_KEYWORDS = ["edit", "change", "modify", "update", "delete", "remove", "drop"]
GROOVY_REQUEST_KEYWORDS = ["groovy", "script", "magnolia", "cms", "generate", "create", "write"]
GROOVY_KEYWORDS = ["def", "import", "class", "void", "return", "println"]