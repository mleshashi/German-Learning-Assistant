"""
Grammar Master Agent - German Grammar Analysis
Specialized agent for analyzing German articles, cases, and verb conjugations
"""

import json
from typing import Dict, Any, List
from groq import Groq

# Import our config
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_config


class GrammarMasterAgent:
    """
    Specialized agent for German grammar analysis using Groq's free LLM
    Focuses on: der/die/das, cases (Nominativ/Akkusativ/Dativ/Genitiv), verb conjugations
    """
    
    def __init__(self):
        self.groq_config = get_api_config("groq")
        self.client = Groq(api_key=self.groq_config["api_key"])
        self.model = self.groq_config["model"]
    
    def _create_grammar_prompt(self, text: str, level: str = "A1") -> str:
        """Create a specialized prompt for German grammar analysis"""
        return f"""You are a German grammar expert. Analyze this German text and provide educational explanations suitable for {level} level learners.

Text to analyze: "{text}"

Please provide analysis in this JSON format:
{{
    "articles": [
        {{"word": "der", "type": "definite", "case": "nominativ", "gender": "masculine", "explanation": "..."}}
    ],
    "nouns": [
        {{"word": "Hund", "gender": "masculine", "case": "nominativ", "plural": "Hunde", "explanation": "..."}}
    ],
    "verbs": [
        {{"word": "ist", "infinitive": "sein", "tense": "präsens", "person": "3rd singular", "explanation": "..."}}
    ],
    "adjectives": [
        {{"word": "groß", "declension": "predicative", "explanation": "..."}}
    ],
    "cases_explanation": "Brief explanation of the cases used in this sentence",
    "level_appropriate_tip": "One helpful tip for {level} learners",
    "common_mistakes": ["Mistake 1", "Mistake 2"]
}}

Focus on practical learning points. Explain WHY the grammar works this way, not just WHAT it is."""

    async def analyze_grammar(self, text: str, level: str = "A1") -> Dict[str, Any]:
        """
        Analyze German grammar in the given text
        
        Args:
            text: German text to analyze
            level: CEFR level (A1, A2, B1, B2, C1, C2)
            
        Returns:
            Dictionary with detailed grammar analysis
        """
        try:
            prompt = self._create_grammar_prompt(text, level)
            
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful German grammar teacher. Always respond with valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=self.groq_config["max_tokens"],
                temperature=0.3  # Lower temperature for more consistent grammar analysis
            )
            
            # Parse the response
            response_text = chat_completion.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Sometimes the model wraps JSON in markdown
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end]
                
                grammar_analysis = json.loads(response_text)
                
                # Add metadata
                grammar_analysis["source_text"] = text
                grammar_analysis["analysis_level"] = level
                grammar_analysis["model_used"] = self.model
                
                return {
                    "success": True,
                    "analysis": grammar_analysis
                }
                
            except json.JSONDecodeError:
                # Fallback: return raw text if JSON parsing fails
                return {
                    "success": True,
                    "analysis": {
                        "raw_response": response_text,
                        "source_text": text,
                        "analysis_level": level,
                        "note": "Grammar analysis provided but not in structured format"
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Grammar analysis failed: {str(e)}",
                "source_text": text
            }
    
    def get_case_explanation(self, case_name: str) -> str:
        """Get explanation for German cases"""
        cases = {
            "nominativ": "The subject of the sentence - who or what is doing the action",
            "akkusativ": "The direct object - who or what receives the action", 
            "dativ": "The indirect object - to whom or for whom something is done",
            "genitiv": "Shows possession or relationship - whose or of what"
        }
        return cases.get(case_name.lower(), "Unknown case")
    
    def get_article_table(self, gender: str) -> Dict[str, str]:
        """Get article declension table for a specific gender"""
        tables = {
            "masculine": {
                "nominativ": "der", "akkusativ": "den", 
                "dativ": "dem", "genitiv": "des"
            },
            "feminine": {
                "nominativ": "die", "akkusativ": "die",
                "dativ": "der", "genitiv": "der" 
            },
            "neuter": {
                "nominativ": "das", "akkusativ": "das",
                "dativ": "dem", "genitiv": "des"
            },
            "plural": {
                "nominativ": "die", "akkusativ": "die",
                "dativ": "den", "genitiv": "der"
            }
        }
        return tables.get(gender.lower(), {})


# Test function
async def test_grammar_master():
    """Test the Grammar Master Agent"""
    print("🧪 Testing Grammar Master Agent...")
    
    try:
        agent = GrammarMasterAgent()
        
        # Test with a simple German sentence
        test_sentence = "Der große Hund ist braun."
        print(f"📝 Analyzing: '{test_sentence}'")
        
        result = await agent.analyze_grammar(test_sentence, "A1")
        
        if result["success"]:
            print("✅ Grammar analysis successful!")
            analysis = result["analysis"]
            
            # Print key findings
            if "articles" in analysis:
                print(f"📚 Articles found: {len(analysis['articles'])}")
            if "level_appropriate_tip" in analysis:
                print(f"💡 Learning tip: {analysis['level_appropriate_tip']}")
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            
        return result["success"]
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_grammar_master())