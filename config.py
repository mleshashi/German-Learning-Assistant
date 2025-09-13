"""
German Learning Assistant Configuration
Using only free resources and APIs
"""

import os
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("⚠️  Falling back to system environment variables")

# Project Structure
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DB_PATH = DATA_DIR / "chroma_db"
AUDIO_CACHE_DIR = PROJECT_ROOT / "audio_cache"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DB_PATH.mkdir(exist_ok=True)
AUDIO_CACHE_DIR.mkdir(exist_ok=True)

# Free API Configuration
FREE_APIS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama3-8b-8192",  # Free tier model
        "api_key": os.getenv("GROQ_API_KEY", ""),
        "max_tokens": 1024
    },
    "wiktionary": {
        "base_url": "https://en.wiktionary.org/api/rest_v1",
        "user_agent": "GermanLearningBot/1.0"
    },
    "tts": {
        "service": "edge-tts",  # Free Microsoft Edge TTS
        "voice": "de-DE-KatjaNeural",
        "rate": "+0%",
        "pitch": "+0Hz"
    }
}

# German Learning Levels
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

# Agent Configuration
AGENTS = {
    "grammar_master": {
        "name": "Grammar Master",
        "role": "German grammar expert specializing in articles, cases, and verb conjugations",
        "expertise": ["der/die/das", "nominativ/akkusativ/dativ/genitiv", "verb_conjugation"]
    },
    "vocabulary_builder": {
        "name": "Vocabulary Builder", 
        "role": "German vocabulary expert for compound words and word families",
        "expertise": ["compound_words", "word_families", "etymology", "level_progression"]
    },
    "conversation_practice": {
        "name": "Conversation Partner",
        "role": "German conversation partner with cultural context",
        "expertise": ["dialogue", "cultural_context", "pronunciation", "real_world_usage"]
    }
}

# Cache Configuration
CACHE_CONFIG = {
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "vocab_cache_file": DATA_DIR / "vocab_cache.json",
    "user_progress_file": DATA_DIR / "user_progress.json",
    "ttl": 3600  # 1 hour cache TTL
}

def get_api_config(service: str) -> Dict[str, Any]:
    """Get configuration for a specific service"""
    return FREE_APIS.get(service, {})

def validate_config() -> bool:
    """Validate that required configuration is present"""
    if not FREE_APIS["groq"]["api_key"]:
        print("⚠️  Warning: GROQ_API_KEY environment variable not set")
        return False
    return True