"""
Progress Tracker & Daily Lesson Generator for German Learning Assistant
Tracks user progress and generates personalized daily lessons
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import our config and agents
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import CACHE_CONFIG, CEFR_LEVELS
from agents.orchestrator import GermanLearningOrchestrator


class ProgressTracker:
    """
    Tracks user progress and generates personalized daily lessons
    """
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.progress_file = CACHE_CONFIG["user_progress_file"]
        self.orchestrator = GermanLearningOrchestrator()
        
        # Ensure progress file exists
        self._initialize_progress_file()
    
    def _initialize_progress_file(self):
        """Initialize progress file if it doesn't exist"""
        if not self.progress_file.exists():
            initial_progress = {
                "user_id": self.user_id,
                "created_at": datetime.now().isoformat(),
                "current_level": "A1",
                "target_level": "B2",
                "learning_streak": 0,
                "total_sessions": 0,
                "lessons_completed": [],
                "weak_areas": {
                    "grammar": [],
                    "vocabulary": [],
                    "conversation": []
                },
                "strong_areas": {
                    "grammar": [],
                    "vocabulary": [],
                    "conversation": []
                },
                "vocabulary_learned": {},
                "grammar_patterns_mastered": [],
                "conversation_topics_practiced": [],
                "daily_goals": {
                    "target_minutes": 15,
                    "target_exercises": 3,
                    "target_new_words": 5
                },
                "last_lesson_date": None,
                "progress_history": []
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(initial_progress, f, indent=2, ensure_ascii=False)
    
    def load_progress(self) -> Dict[str, Any]:
        """Load user progress from file"""
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading progress: {e}")
            self._initialize_progress_file()
            return self.load_progress()
    
    def save_progress(self, progress: Dict[str, Any]):
        """Save user progress to file"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    async def track_lesson_completion(self, lesson_result: Dict[str, Any]):
        """
        Track completion of a lesson and update progress
        """
        progress = self.load_progress()
        
        # Update basic stats
        progress["total_sessions"] += 1
        progress["last_lesson_date"] = datetime.now().isoformat()
        
        # Update learning streak
        if self._is_consecutive_day(progress.get("last_lesson_date")):
            progress["learning_streak"] += 1
        else:
            progress["learning_streak"] = 1
        
        # Analyze lesson results for progress tracking
        lesson_data = {
            "date": datetime.now().isoformat(),
            "lesson_type": lesson_result.get("lesson_type", "comprehensive"),
            "level": lesson_result.get("user_level", progress["current_level"]),
            "topics_covered": [],
            "words_learned": [],
            "grammar_points": [],
            "performance_score": 0.8  # Would be calculated based on user interaction
        }
        
        # Extract learning insights from lesson
        if "comprehensive_lesson" in lesson_result:
            lesson = lesson_result["comprehensive_lesson"]
            
            # Track vocabulary progress
            vocab_insights = lesson.get("vocabulary_insights", {})
            for word, analysis in vocab_insights.items():
                progress["vocabulary_learned"][word] = {
                    "learned_date": datetime.now().isoformat(),
                    "level": analysis.get("level", "unknown"),
                    "is_compound": analysis.get("is_compound", False),
                    "mastery_level": "introduced"
                }
                lesson_data["words_learned"].append(word)
            
            # Track grammar progress
            grammar_insights = lesson.get("grammar_insights", {})
            if grammar_insights.get("main_structures"):
                grammar_point = grammar_insights["main_structures"]
                if grammar_point not in progress["grammar_patterns_mastered"]:
                    progress["grammar_patterns_mastered"].append(grammar_point)
                lesson_data["grammar_points"].append(grammar_point)
            
            # Identify weak areas for future focus
            learning_plan = lesson.get("learning_plan", [])
            for step in learning_plan:
                if "grammar" in step.lower():
                    if step not in progress["weak_areas"]["grammar"]:
                        progress["weak_areas"]["grammar"].append(step)
                elif "vocabulary" in step.lower() or "word" in step.lower():
                    if step not in progress["weak_areas"]["vocabulary"]:
                        progress["weak_areas"]["vocabulary"].append(step)
                elif "conversation" in step.lower():
                    if step not in progress["weak_areas"]["conversation"]:
                        progress["weak_areas"]["conversation"].append(step)
        
        # Add lesson to history
        progress["lessons_completed"].append(lesson_data)
        progress["progress_history"].append({
            "date": datetime.now().isoformat(),
            "level": progress["current_level"],
            "streak": progress["learning_streak"],
            "total_words": len(progress["vocabulary_learned"]),
            "total_grammar": len(progress["grammar_patterns_mastered"])
        })
        
        # Check for level progression
        await self._check_level_progression(progress)
        
        self.save_progress(progress)
        return progress
    
    def _is_consecutive_day(self, last_date: Optional[str]) -> bool:
        """Check if today is consecutive to the last lesson date"""
        if not last_date:
            return False
        
        try:
            last_lesson = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
            yesterday = datetime.now() - timedelta(days=1)
            return last_lesson.date() >= yesterday.date()
        except:
            return False
    
    async def _check_level_progression(self, progress: Dict[str, Any]):
        """Check if user should progress to next level"""
        current_level = progress["current_level"]
        current_index = CEFR_LEVELS.index(current_level)
        
        # Simple progression criteria (can be made more sophisticated)
        vocab_count = len(progress["vocabulary_learned"])
        grammar_count = len(progress["grammar_patterns_mastered"])
        session_count = progress["total_sessions"]
        
        # Level progression thresholds
        progression_thresholds = {
            "A1": {"vocab": 50, "grammar": 10, "sessions": 20},
            "A2": {"vocab": 100, "grammar": 20, "sessions": 40},
            "B1": {"vocab": 200, "grammar": 30, "sessions": 60},
            "B2": {"vocab": 400, "grammar": 40, "sessions": 80},
            "C1": {"vocab": 600, "grammar": 50, "sessions": 100}
        }
        
        threshold = progression_thresholds.get(current_level, {})
        
        if (vocab_count >= threshold.get("vocab", 999) and 
            grammar_count >= threshold.get("grammar", 999) and 
            session_count >= threshold.get("sessions", 999) and
            current_index < len(CEFR_LEVELS) - 1):
            
            # Promote to next level
            new_level = CEFR_LEVELS[current_index + 1]
            progress["current_level"] = new_level
            
            print(f"🎉 Congratulations! You've progressed from {current_level} to {new_level}!")
    
    async def generate_daily_lesson(self) -> Dict[str, Any]:
        """
        Generate a personalized daily lesson based on user progress
        """
        progress = self.load_progress()
        
        # Determine lesson focus based on weak areas and progress
        lesson_focus = self._determine_lesson_focus(progress)
        
        # Generate lesson content based on focus
        lesson_content = await self._create_lesson_content(progress, lesson_focus)
        
        # Create daily lesson structure
        daily_lesson = {
            "date": datetime.now().isoformat(),
            "user_level": progress["current_level"],
            "target_level": progress["target_level"],
            "lesson_number": progress["total_sessions"] + 1,
            "estimated_duration": f"{progress['daily_goals']['target_minutes']} minutes",
            "focus_areas": lesson_focus,
            "lesson_content": lesson_content,
            "daily_goals": progress["daily_goals"],
            "progress_stats": {
                "current_streak": progress["learning_streak"],
                "words_learned": len(progress["vocabulary_learned"]),
                "grammar_patterns": len(progress["grammar_patterns_mastered"]),
                "completion_rate": self._calculate_completion_rate(progress)
            },
            "motivation_message": self._generate_motivation_message(progress)
        }
        
        return daily_lesson
    
    def _determine_lesson_focus(self, progress: Dict[str, Any]) -> List[str]:
        """Determine what the lesson should focus on based on progress"""
        focus_areas = []
        
        # Check weak areas that need attention
        grammar_weak = len(progress["weak_areas"]["grammar"])
        vocab_weak = len(progress["weak_areas"]["vocabulary"])
        conversation_weak = len(progress["weak_areas"]["conversation"])
        
        # Prioritize based on weakness and recency
        if grammar_weak > 0:
            focus_areas.append("grammar")
        if vocab_weak > 0:
            focus_areas.append("vocabulary")
        if conversation_weak > 0 or progress["total_sessions"] % 3 == 0:
            focus_areas.append("conversation")
        
        # Ensure at least one focus area
        if not focus_areas:
            focus_areas = ["comprehensive"]
        
        return focus_areas
    
    async def _create_lesson_content(self, progress: Dict[str, Any], focus_areas: List[str]) -> Dict[str, Any]:
        """Create lesson content based on focus areas"""
        
        # Select practice sentences based on user level and weak areas
        practice_sentences = self._get_practice_sentences(
            progress["current_level"], 
            focus_areas
        )
        
        lesson_content = {
            "warm_up": {
                "type": "vocabulary_review",
                "content": list(progress["vocabulary_learned"].keys())[-5:],  # Last 5 words learned
                "instruction": "Review these words you've learned recently"
            },
            "main_exercises": [],
            "practice_conversations": [],
            "reflection": {
                "questions": [
                    "What was the most challenging part of today's lesson?",
                    "Which new word or grammar point will you use this week?",
                    "How confident do you feel about today's topics (1-10)?"
                ]
            }
        }
        
        # Create exercises based on focus areas
        for area in focus_areas:
            if area == "grammar":
                lesson_content["main_exercises"].append({
                    "type": "grammar_analysis",
                    "sentence": practice_sentences["grammar"],
                    "focus": "Analyze the grammar structure of this sentence"
                })
            elif area == "vocabulary":
                lesson_content["main_exercises"].append({
                    "type": "vocabulary_building",
                    "word": practice_sentences["vocabulary"],
                    "focus": "Break down this compound word and find related words"
                })
            elif area == "conversation":
                lesson_content["practice_conversations"].append({
                    "type": "conversation_practice",
                    "scenario": practice_sentences["conversation"],
                    "focus": "Practice this conversation scenario"
                })
        
        return lesson_content
    
    def _get_practice_sentences(self, level: str, focus_areas: List[str]) -> Dict[str, str]:
        """Get practice sentences appropriate for user level and focus"""
        
        sentences_by_level = {
            "A1": {
                "grammar": "Das ist mein Haus.",
                "vocabulary": "Schulbuch",
                "conversation": "Hallo, wie heißt du?"
            },
            "A2": {
                "grammar": "Ich habe gestern ein Buch gelesen.",
                "vocabulary": "Arbeitgeber",
                "conversation": "Können Sie mir helfen?"
            },
            "B1": {
                "grammar": "Wenn ich Zeit hätte, würde ich nach Deutschland reisen.",
                "vocabulary": "Umweltschutz",
                "conversation": "Was denkst du über dieses Thema?"
            },
            "B2": {
                "grammar": "Nachdem er die Prüfung bestanden hatte, feierte er mit Freunden.",
                "vocabulary": "Verantwortungsbewusstsein",
                "conversation": "Könnten wir über die Vor- und Nachteile diskutieren?"
            },
            "C1": {
                "grammar": "Trotz der schwierigen Umstände gelang es ihm, sein Ziel zu erreichen.",
                "vocabulary": "Auseinandersetzung",
                "conversation": "Wie beurteilen Sie die gesellschaftlichen Auswirkungen?"
            },
            "C2": {
                "grammar": "Inwieweit die Hypothese zutrifft, bleibt abzuwarten.",
                "vocabulary": "Unverhältnismäßigkeit",
                "conversation": "Welche Implikationen ergeben sich aus dieser Analyse?"
            }
        }
        
        return sentences_by_level.get(level, sentences_by_level["A1"])
    
    def _calculate_completion_rate(self, progress: Dict[str, Any]) -> float:
        """Calculate lesson completion rate"""
        total_sessions = progress["total_sessions"]
        if total_sessions == 0:
            return 0.0
        
        # Simple completion rate based on consistency
        streak = progress["learning_streak"]
        return min(1.0, (streak / 7) * 0.8 + 0.2)  # 20% base + up to 80% for streak
    
    def _generate_motivation_message(self, progress: Dict[str, Any]) -> str:
        """Generate a motivational message based on progress"""
        streak = progress["learning_streak"]
        level = progress["current_level"]
        words_count = len(progress["vocabulary_learned"])
        
        if streak >= 7:
            return f"🔥 Amazing! {streak} day streak! You're mastering {level} level German!"
        elif streak >= 3:
            return f"👏 Great consistency! {streak} days in a row. Keep it up!"
        elif words_count >= 50:
            return f"📚 Impressive vocabulary! You've learned {words_count} German words!"
        else:
            return f"🌟 Every step counts! You're building your German skills at {level} level."


# Test function
async def test_progress_tracker():
    """Test the progress tracking and daily lesson generation"""
    print("🧪 Testing Progress Tracker & Daily Lesson Generator...")
    
    tracker = ProgressTracker("test_user")
    
    try:
        # Test progress loading
        progress = tracker.load_progress()
        print(f"✅ Progress loaded: Level {progress['current_level']}")
        
        # Simulate a lesson completion
        mock_lesson = {
            "success": True,
            "comprehensive_lesson": {
                "user_level": "A1",
                "vocabulary_insights": {
                    "Fahrzeug": {"level": "B1", "is_compound": True}
                },
                "grammar_insights": {
                    "main_structures": "Modal verbs with infinitives"
                },
                "learning_plan": [
                    "Practice modal verb conjugations",
                    "Learn more compound words with 'zeug'"
                ]
            },
            "lesson_type": "comprehensive"
        }
        
        updated_progress = await tracker.track_lesson_completion(mock_lesson)
        print(f"✅ Lesson tracked: Streak = {updated_progress['learning_streak']}")
        
        # Generate daily lesson
        daily_lesson = await tracker.generate_daily_lesson()
        print(f"✅ Daily lesson generated:")
        print(f"   📊 Level: {daily_lesson['user_level']}")
        print(f"   🎯 Focus: {', '.join(daily_lesson['focus_areas'])}")
        print(f"   ⏱️  Duration: {daily_lesson['estimated_duration']}")
        print(f"   💪 Motivation: {daily_lesson['motivation_message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_progress_tracker())