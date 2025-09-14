"""
Conversation Practice Agent - German Conversation Partner
Simulates real German conversations with cultural context and corrections
"""

import json
from typing import Dict, Any, List, Optional
from groq import Groq

# Import our config
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_config


class ConversationPracticeAgent:
    """
    Conversation partner for practicing German with cultural context
    Provides corrections, suggestions, and maintains conversation flow
    """
    
    def __init__(self):
        self.groq_config = get_api_config("groq")
        self.client = Groq(api_key=self.groq_config["api_key"])
        self.model = self.groq_config["model"]
        
        # Conversation memory (simple list for now)
        self.conversation_history = []
    
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

Please respond in this JSON format:
{{
    "german_response": "Your natural German response to continue the conversation",
    "english_translation": "English translation of your response",
    "corrections": [
        {{"error": "user's mistake", "correction": "corrected version", "explanation": "why this is better"}}
    ],
    "vocabulary_help": [
        {{"word": "difficult word from response", "meaning": "simple explanation", "level": "word difficulty"}}
    ],
    "cultural_note": "Optional cultural context about Germany/Austria/Switzerland",
    "conversation_tips": ["tip1", "tip2"],
    "suggested_responses": ["response option 1", "response option 2"]
}}

Guidelines:
- Respond naturally in German at {level} level
- Give gentle corrections without being overwhelming
- Include cultural context when relevant
- Keep the conversation flowing naturally
- Use appropriate formality level for the scenario"""

    async def practice_conversation(
        self, 
        user_message: str, 
        level: str = "A1", 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Practice German conversation with corrections and help
        
        Args:
            user_message: User's German message
            level: CEFR level (A1-C2)
            context: Conversation context (topic, scenario, etc.)
            
        Returns:
            Dictionary with conversation response and learning aids
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
                
                # Add metadata
                conversation_response["user_input"] = user_message
                conversation_response["conversation_level"] = level
                conversation_response["model_used"] = self.model
                
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
                        "note": "Response parsing failed, but conversation continues"
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
    """Test the Conversation Practice Agent"""
    print("🧪 Testing Conversation Practice Agent...")
    
    agent = ConversationPracticeAgent()
    
    try:
        # Test conversation
        test_message = "Hallo! Ich bin müde heute."
        context = {
            "topic": "daily life",
            "scenario": "casual greeting"
        }
        
        print(f"👤 User: '{test_message}'")
        
        result = await agent.practice_conversation(test_message, "A2", context)
        
        if result["success"]:
            print("✅ Conversation successful!")
            response = result["response"]
            
            print(f"🤖 Bot: {response.get('german_response', 'No response')}")
            print(f"📝 Translation: {response.get('english_translation', 'No translation')}")
            
            if response.get("corrections"):
                print(f"✏️  Corrections: {len(response['corrections'])}")
            
            if response.get("vocabulary_help"):
                print(f"📚 Vocabulary help: {len(response['vocabulary_help'])}")
            
            if response.get("cultural_note"):
                print(f"🇩🇪 Cultural note: {response['cultural_note'][:50]}...")
        
        else:
            print(f"❌ Conversation failed: {result.get('error', 'Unknown error')}")
        
        # Test conversation starters
        starters = agent.suggest_conversation_starters("A2")
        print(f"💡 Conversation starters for A2: {len(starters)}")
        
        return result["success"]
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_conversation_practice())