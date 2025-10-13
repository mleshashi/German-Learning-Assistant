"""
German Learning Assistant Configuration
Aligned with Goethe Institut Curriculum (A1-C2)
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
AUDIO_CACHE_DIR = PROJECT_ROOT / "audio_cache"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
AUDIO_CACHE_DIR.mkdir(exist_ok=True)

# Free API Configuration
FREE_APIS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant",  # Free tier model
        "api_key": os.getenv("GROQ_API_KEY", ""),
        "max_tokens": 1024
    },
    "wiktionary": {
        "base_url": "https://en.wiktionary.org/api/rest_v1",
        "user_agent": "GermanLearningBot/1.0"
    },
    "tts": {
        "service": "edge-tts",  # Free Microsoft Edge TTS
        "voice": "de-DE-KatjaNeural",  # Female German voice
        "voice_male": "de-DE-ConradNeural",  # Male German voice (alternative)
        "rate": "+0%",
        "pitch": "+0Hz"
    }
}

# German Learning Levels (CEFR)
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

# Agent Configuration - Aligned with Goethe Institut Syllabus
AGENTS = {
    "grammar_master": {
        "name": "Grammar Master",
        "role": "German grammar expert covering complete Goethe syllabus from A1 to C2",
        "expertise": [
            # Articles & Gender
            "articles_definite_indefinite",
            "gender_rules_der_die_das",
            "article_declension",
            "zero_article",
            
            # Cases (Core of German Grammar)
            "nominative_case",
            "accusative_case",
            "dative_case",
            "genitive_case",
            "case_prepositions",
            "two_way_prepositions",
            
            # Nouns
            "noun_declension",
            "plural_formation",
            "compound_nouns",
            "weak_nouns_n_declension",
            
            # Verbs - Basic
            "present_tense",
            "past_tense_prateritum",
            "perfect_tense",
            "future_tense",
            "verb_conjugation_regular",
            "verb_conjugation_irregular",
            
            # Verbs - Advanced
            "modal_verbs",
            "separable_verbs",
            "inseparable_verbs",
            "reflexive_verbs",
            "passive_voice",
            "subjunctive_konjunktiv_1",
            "subjunctive_konjunktiv_2",
            "imperative_mood",
            "infinitive_with_zu",
            
            # Adjectives
            "adjective_declension",
            "comparative_forms",
            "superlative_forms",
            "adjective_as_nouns",
            
            # Pronouns
            "personal_pronouns",
            "possessive_pronouns",
            "reflexive_pronouns",
            "relative_pronouns",
            "demonstrative_pronouns",
            "indefinite_pronouns",
            
            # Sentence Structure
            "word_order_main_clause",
            "word_order_questions",
            "subordinate_clauses",
            "relative_clauses",
            "conditional_clauses",
            "temporal_clauses",
            "causal_clauses",
            "final_clauses",
            "concessive_clauses",
            
            # Conjunctions
            "coordinating_conjunctions",
            "subordinating_conjunctions",
            "two_part_conjunctions",
            
            # Other Grammar Topics
            "negation_nicht_kein",
            "comparison_structures",
            "indirect_speech",
            "participial_constructions",
            "nominalization"
        ]
    },
    "vocabulary_builder": {
        "name": "Vocabulary Builder", 
        "role": "Vocabulary expert for all Goethe levels with thematic organization",
        "expertise": [
            # Word Formation
            "compound_words",
            "word_families",
            "prefixes_verbs",
            "suffixes_nouns_adjectives",
            "etymology",
            
            # Learning Strategies
            "level_progression_a1_c2",
            "frequency_analysis",
            "cognates_english_german",
            "false_friends",
            "mnemonics_techniques",
            
            # Thematic Vocabulary (Goethe Topics)
            "personal_information",
            "family_relationships",
            "housing_living",
            "daily_routine",
            "food_drink",
            "shopping_services",
            "travel_tourism",
            "health_body",
            "education_training",
            "work_profession",
            "free_time_hobbies",
            "media_communication",
            "weather_nature",
            "culture_society",
            "politics_economy",
            "science_technology",
            
            # Collocations & Usage
            "collocations",
            "idiomatic_expressions",
            "phrasal_verbs",
            "synonyms_antonyms",
            "register_formal_informal",
            
            # Specialized Vocabulary
            "academic_german",
            "business_german",
            "technical_vocabulary",
            "literary_vocabulary"
        ]
    },
    "conversation_practice": {
        "name": "Conversation Partner",
        "role": "Conversation practice aligned with Goethe communicative competencies",
        "expertise": [
            # Communication Skills (all levels)
            "greeting_farewell",
            "introducing_self_others",
            "asking_answering_questions",
            "expressing_opinions",
            "agreeing_disagreeing",
            "making_suggestions",
            "giving_instructions",
            "describing_people_places",
            "narrating_events",
            "expressing_feelings",
            "making_requests",
            "apologizing_thanking",
            
            # Situational Dialogues (Goethe Scenarios)
            "restaurant_ordering",
            "shopping_buying",
            "doctor_appointment",
            "bank_post_office",
            "hotel_accommodation",
            "directions_transportation",
            "job_interview",
            "official_appointments",
            "telephone_conversations",
            "social_gatherings",
            
            # Formality Levels
            "du_vs_sie",
            "formal_register",
            "informal_register",
            "academic_register",
            "professional_register",
            
            # Pronunciation & Phonetics
            "pronunciation_rules",
            "intonation_patterns",
            "stress_patterns",
            "regional_accents",
            "connected_speech",
            
            # Cultural Competence
            "german_culture",
            "austrian_culture",
            "swiss_culture",
            "cultural_norms",
            "social_etiquette",
            "regional_differences",
            "festivals_traditions",
            "business_culture",
            
            # Communication Strategies
            "clarification_strategies",
            "paraphrasing",
            "circumlocution",
            "error_correction",
            "self_correction",
            "communication_repair",
            "turn_taking",
            "active_listening"
        ]
    }
}

# Goethe Institut Syllabus by Level
GOETHE_SYLLABUS = {
    "A1": {
        "can_do": [
            "Understand and use familiar everyday expressions",
            "Introduce yourself and others",
            "Ask and answer questions about personal details",
            "Interact in a simple way"
        ],
        "grammar_focus": [
            "Present tense", "Basic word order", "Nominative and accusative cases",
            "Articles (der/die/das)", "Personal pronouns", "Possessive articles",
            "Modal verbs (können, müssen, wollen)", "Simple questions"
        ],
        "vocabulary_themes": [
            "Personal information", "Family", "Numbers", "Time",
            "Food and drink", "Shopping", "Hobbies", "Daily routine"
        ]
    },
    "A2": {
        "can_do": [
            "Understand sentences on familiar topics",
            "Communicate in simple routine tasks",
            "Describe background and environment",
            "Express immediate needs"
        ],
        "grammar_focus": [
            "Perfect tense", "Dative case", "Prepositions with cases",
            "Comparative and superlative", "Subordinate clauses (weil, dass)",
            "Reflexive verbs", "Separable verbs", "Imperative"
        ],
        "vocabulary_themes": [
            "Housing", "Health", "Weather", "Clothing",
            "Transportation", "Media", "Education", "Work"
        ]
    },
    "B1": {
        "can_do": [
            "Understand main points of clear standard input",
            "Deal with most travel situations",
            "Produce simple connected text",
            "Describe experiences, dreams, hopes"
        ],
        "grammar_focus": [
            "All tenses review", "Genitive case", "Relative clauses",
            "Passive voice", "Subjunctive II", "Indirect speech",
            "All types of subordinate clauses", "Adjective declension"
        ],
        "vocabulary_themes": [
            "Environment", "Technology", "Politics", "Culture",
            "Career and profession", "Society", "Emotions", "Arguments"
        ]
    },
    "B2": {
        "can_do": [
            "Understand complex texts on concrete and abstract topics",
            "Interact fluently with native speakers",
            "Produce clear detailed text",
            "Explain viewpoint on topical issues"
        ],
        "grammar_focus": [
            "Advanced subjunctive", "Participle constructions",
            "Nominalization", "Advanced passive forms",
            "Conjunctive adverbs", "Extended attributes"
        ],
        "vocabulary_themes": [
            "Abstract concepts", "Idiomatic expressions",
            "Academic language", "Business communication",
            "Literary texts", "Complex argumentation"
        ]
    },
    "C1": {
        "can_do": [
            "Understand wide range of demanding texts",
            "Express ideas fluently and spontaneously",
            "Use language flexibly for social, academic, professional purposes",
            "Produce clear, well-structured detailed text"
        ],
        "grammar_focus": [
            "Fine nuances of all grammar", "Stylistic variations",
            "Complex sentence structures", "Register switching",
            "Historical grammar forms"
        ],
        "vocabulary_themes": [
            "Specialized fields", "Nuanced expression",
            "Academic discourse", "Professional specialization",
            "Literary analysis", "Cultural criticism"
        ]
    },
    "C2": {
        "can_do": [
            "Understand virtually everything heard or read",
            "Summarize information from different sources",
            "Express yourself spontaneously, fluently, precisely",
            "Distinguish finer shades of meaning"
        ],
        "grammar_focus": [
            "Mastery of all grammar", "Stylistic refinement",
            "Regional variations", "Historical forms",
            "Near-native competence"
        ],
        "vocabulary_themes": [
            "Native-like expression", "Subtle distinctions",
            "Field-specific expertise", "Cultural references",
            "Literary sophistication", "Complete fluency"
        ]
    }
}

# User Progress Configuration
CACHE_CONFIG = {
    "user_progress_file": DATA_DIR / "user_progress.json",
    "vocab_cache_file": DATA_DIR / "vocab_cache.json"
}

def get_api_config(service: str) -> Dict[str, Any]:
    """Get configuration for a specific service"""
    return FREE_APIS.get(service, {})

def get_level_syllabus(level: str) -> Dict[str, Any]:
    """Get Goethe syllabus for a specific CEFR level"""
    return GOETHE_SYLLABUS.get(level, {})

def validate_config() -> bool:
    """Validate that required configuration is present"""
    if not FREE_APIS["groq"]["api_key"]:
        print("⚠️  Warning: GROQ_API_KEY environment variable not set")
        print("📝 Get your free API key at: https://console.groq.com/")
        return False
    return True