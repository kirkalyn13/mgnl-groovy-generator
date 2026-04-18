# Server
HOST = "0.0.0.0"
PORT = 8000
ALLOWED_ORIGINS = ["http://localhost:5173", "https://mgnl-groovy-generator-app.vercel.app"]

# Ollama
REQUEST_TIMEOUT = 120.0

# Qdrant
TOP_K_SIMILARITY = 3
DEFAULT_DOCS_PATH = "./data"
EXTENSIONS = [".groovy"]

# Query Settings
MAX_RETRIES = 3
UNWANTED_RESPONSE_KEYWORDS = [".save"]
EDIT_KEYWORDS = ["edit", "change", "modify", "update", "delete", "remove", "drop"]
GROOVY_REQUEST_KEYWORDS = ["groovy", "script", "magnolia", "cms", "generate", "create", "write"]
GROOVY_KEYWORDS = ["def", "import", "class", "void", "return", "println"]