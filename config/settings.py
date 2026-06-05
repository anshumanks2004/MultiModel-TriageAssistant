"""Application-wide constants and configuration."""

# Ollama API
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TEXT_MODEL = "llama3"
OLLAMA_VISION_MODEL = "llava"
OLLAMA_TIMEOUT = 120  # seconds
OLLAMA_RETRY_ATTEMPTS = 2

# Severity levels
SEVERITY_LOW = "Low"
SEVERITY_MEDIUM = "Medium"
SEVERITY_HIGH = "High"

# Severity to color mapping (used by UI)
SEVERITY_COLORS = {
    SEVERITY_LOW: "#1E8449",
    SEVERITY_MEDIUM: "#D4AC0D",
    SEVERITY_HIGH: "#C0392B",
}

# Consultation urgency levels
URGENCY_ROUTINE = "Routine (within 1-2 weeks)"
URGENCY_SOON = "Soon (within 2-3 days)"
URGENCY_URGENT = "Urgent (within 24 hours)"
URGENCY_EMERGENCY = "EMERGENCY – Seek care immediately"

# Input validation limits
MAX_SYMPTOM_TEXT_LENGTH = 2000
MIN_SYMPTOM_TEXT_LENGTH = 10
MAX_REPORT_FILE_SIZE_MB = 20
MAX_IMAGE_FILE_SIZE_MB = 10

# Emergency level thresholds (score-based)
EMERGENCY_SCORE_CRITICAL = 60   # Immediate 911 / life-threatening
EMERGENCY_SCORE_HIGH = 30       # Urgent – go to ER now
EMERGENCY_SCORE_MODERATE = 10   # Concerning – seek care today

# Legacy flat keyword list kept for backward compatibility with any
# callers that still import it. The engine now uses the structured
# rule-set defined in core/emergency_detector.py.
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "can't breathe", "cannot breathe",
    "difficulty breathing", "stopped breathing", "not breathing",
    "heavy bleeding", "uncontrollable bleeding", "unconscious",
    "unresponsive", "seizure", "convulsion", "stroke", "severe chest",
    "crushing chest", "choking", "anaphylaxis", "passing out",
    "fainted", "overdose", "suicide", "self harm",
]
