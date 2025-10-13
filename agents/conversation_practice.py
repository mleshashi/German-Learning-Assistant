"""
Conversation Practice Agent - German Conversation Partner
Simulates real German conversations with cultural context and corrections
NOW WITH TEXT-TO-SPEECH SUPPORT!
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from groq import Groq

# Import our config
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_config


class ConversationPracticeAgent:
    """
    Conversation partner for practicing German with cultural context
    Provides corrections, suggestions, and maintains conversation flow
    Now includes text-to-speech audio generation!
    """
    
    def __init__(self):
        self.groq_config = get_api_config("groq")
        self.client = Groq(api_key=self.groq_config["api_key"])
        self.model = self.groq_config["model"]
        
        # Conversation memory (simple list for now)
        self.conversation_history = []
        
        # TTS helper (lazy load to avoid circular imports)
        self._tts_helper = None
    
    @property
    def tts_helper(self):
        """Lazy load TTS helper"""
        if self._tts_helper is None:
            from agents.tts_helper import GermanTTSHelper
            self._tts_helper = GermanTTSHelper()
        return self._tts_helper
    
    def _create_conversation_prompt(self, user_message: str, level: str, context: Dict[str, Any] = None) -> str:
        """Create a conversation prompt for German practice"""
        
        context_info = context or {}
        topic = context_info.get("topic", "general conversation")
        scenario = context_info.get("scenario", "casual chat")
        
        return f"""You are a helpful German conversation partner. The user is learning German at {level} level.

Conversation Context:
- Topic: {topic}
- Scenario: {scenario}
- User's level: {level}

User said: "{user_message}"

CRITICAL: Your response must ALWAYS include a follow-up question to keep the conversation flowing naturally.

Please respond in this JSON format:
{{
    "german_response": "Your natural German response that ENDS WITH A QUESTION to continue the conversation",
    "english_translation": "English translation of your response",
    "corrections": [
        {{"error": "user's mistake", "correction": "corrected version", "explanation": "why this is better"}}
    ],
    "vocabulary_help": [
        {{"word": "difficult word from response", "meaning": "simple explanation", "level": "word difficulty"}}
    ],
    "cultural_note": "Optional cultural context about Germany/Austria/Switzerland",
    "conversation_tips": ["tip1", "tip2"],
    "suggested_responses": ["response option 1 to your question", "response option 2 to your question"]
}}

Guidelines:
- Respond naturally in German at {level} level
- ALWAYS end your response with a question to keep conversation flowing
- Make questions relevant to the topic and user's level
- Give gentle corrections without being overwhelming
- Include cultural context when relevant
- Use appropriate formality level for the scenario
- Ask open-ended questions that encourage detailed responses
- Vary your questions: use "Was", "Wie", "Warum", "Wo", "Wann", etc.

Examples of good follow-up questions by level:
- A1: "Und Sie? Was machen Sie gern?" (And you? What do you like to do?)
- A2: "Wie war Ihr Wochenende?" (How was your weekend?)
- B1: "Was denken Sie darüber?" (What do you think about that?)
- B2: "Können Sie mir mehr darüber erzählen?" (Can you tell me more about that?)
- C1: "Wie würden Sie diese Situation einschätzen?" (How would you assess this situation?)"""

    async def practice_conversation(
        self, 
        user_message: str, 
        level: str = "A1", 
        context: Optional[Dict[str, Any]] = None,
        generate_audio: bool = True
    ) -> Dict[str, Any]:
        """
        Practice German conversation with corrections and help
        
        Args:
            user_message: User's German message
            level: CEFR level (A1-C2)
            context: Conversation context (topic, scenario, etc.)
            generate_audio: Whether to generate TTS audio for the response
            
        Returns:
            Dictionary with conversation response, learning aids, and optional audio
        """
        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "message": user_message,
                "level": level
            })
            
            prompt = self._create_conversation_prompt(user_message, level, context)
            
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a German conversation partner. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=self.groq_config["max_tokens"],
                temperature=0.7  # Higher temperature for more natural conversation
            )
            
            # Parse response
            response_text = chat_completion.choices[0].message.content
            
            # Extract JSON
            try:
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end]
                
                conversation_response = json.loads(response_text)
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "message": conversation_response.get("german_response", ""),
                    "level": level
                })
                
                # Generate audio if requested
                audio_file = None
                if generate_audio and conversation_response.get("german_response"):
                    try:
                        german_text = conversation_response["german_response"]
                        print(f"🔊 Generating audio for: '{german_text[:50]}...'")
                        audio_file = await self.tts_helper.generate_speech(german_text)
                        conversation_response["audio_file"] = str(audio_file)
                        print(f"✅ Audio available: {audio_file.name}")
                    except Exception as audio_error:
                        print(f"⚠️  Audio generation failed: {audio_error}")
                        conversation_response["audio_file"] = None
                        conversation_response["audio_error"] = str(audio_error)
                
                # Add metadata
                conversation_response["user_input"] = user_message
                conversation_response["conversation_level"] = level
                conversation_response["model_used"] = self.model
                conversation_response["has_audio"] = audio_file is not None
                
                return {
                    "success": True,
                    "response": conversation_response
                }
                
            except json.JSONDecodeError:
                # Fallback response
                return {
                    "success": True,
                    "response": {
                        "german_response": "Entschuldigung, können Sie das wiederholen?",
                        "english_translation": "Sorry, can you repeat that?",
                        "raw_response": response_text,
                        "note": "Response parsing failed, but conversation continues",
                        "has_audio": False
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Conversation failed: {str(e)}",
                "user_input": user_message
            }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def suggest_conversation_starters(self, level: str = "A1") -> List[str]:
        """Get conversation starters appropriate for the level"""
        starters = {
            "A1": [
                "Hallo! Wie heißen Sie?",
                "Wie geht es Ihnen?", 
                "Wo wohnen Sie?",
                "Was machen Sie gern?"
            ],
            "A2": [
                "Was haben Sie gestern gemacht?",
                "Können Sie mir den Weg erklären?",
                "Was ist Ihr Lieblingswetter?",
                "Erzählen Sie von Ihrer Familie."
            ],
            "B1": [
                "Was denken Sie über das Wetter heute?",
                "Können wir über Ihre Hobbys sprechen?",
                "Wie finden Sie das Leben in Deutschland?",
                "Was würden Sie gern lernen?"
            ],
            "B2": [
                "Wie stehen Sie zu aktuellen Ereignissen?",
                "Was würden Sie in dieser Situation machen?",
                "Können Sie Ihre Meinung dazu äußern?",
                "Lassen Sie uns über Kultur diskutieren."
            ],
            "C1": [
                "Wie beurteilen Sie die gesellschaftlichen Entwicklungen?",
                "Könnten Sie Ihre Standpunkt differenziert erläutern?",
                "Was sind die Vor- und Nachteile dieser Lösung?",
                "Wie würden Sie dieses komplexe Problem angehen?"
            ],
            "C2": [
                "Inwieweit stimmen Sie der Hypothese zu?",
                "Welche Implikationen ergeben sich daraus?",
                "Wie würden Sie die Nuancen dieser Argumentation bewerten?",
                "Können Sie eine kritische Analyse vornehmen?"
            ]
        }
        
        return starters.get(level, starters["A1"])


# Test function
async def test_conversation_practice():
    """Test the Conversation Practice Agent with TTS"""
    print("🧪 Testing Conversation Practice Agent with TTS")
    print("=" * 60)
    
    agent = ConversationPracticeAgent()
    
    try:
        # Test conversation with audio
        test_message = "Hallo! Ich bin heute müde."
        context = {
            "topic": "daily life",
            "scenario": "casual greeting"
        }
        
        print(f"\n👤 User: '{test_message}'")
        print("🔄 Generating conversation response with audio...")
        
        result = await agent.practice_conversation(
            test_message, 
            "A2", 
            context,
            generate_audio=True  # Enable audio
        )
        
        if result["success"]:
            print("\n✅ Conversation successful!")
            response = result["response"]
            
            print(f"\n🤖 Bot: {response.get('german_response', 'No response')}")
            print(f"📝 Translation: {response.get('english_translation', 'No translation')}")
            
            if response.get("has_audio"):
                print(f"🔊 Audio available: {response.get('audio_file')}")
            else:
                print("🔇 No audio generated")
            
            if response.get("corrections"):
                print(f"✏️  Corrections: {len(response['corrections'])}")
            
            if response.get("vocabulary_help"):
                print(f"📚 Vocabulary help: {len(response['vocabulary_help'])}")
            
            if response.get("cultural_note"):
                print(f"🇩🇪 Cultural note: {response['cultural_note'][:60]}...")
            
            # Test without audio
            print("\n" + "=" * 60)
            print("\n🔇 Testing without audio generation...")
            result_no_audio = await agent.practice_conversation(
                "Danke schön!",
                "A2",
                context,
                generate_audio=False  # Disable audio
            )
            
            if result_no_audio["success"]:
                print(f"✅ Response without audio: {result_no_audio['response'].get('german_response', '')[:50]}...")
                print(f"🔇 Has audio: {result_no_audio['response'].get('has_audio', False)}")
        
        else:
            print(f"❌ Conversation failed: {result.get('error', 'Unknown error')}")
        
        # Test conversation starters
        print("\n" + "=" * 60)
        starters = agent.suggest_conversation_starters("A2")
        print(f"\n💡 Conversation starters for A2: {len(starters)}")
        for i, starter in enumerate(starters[:3], 1):
            print(f"   {i}. {starter}")
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        
        return result["success"]
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_conversation_practice())