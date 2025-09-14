"""
Vocabulary Builder Agent - German Vocabulary Analysis
Specialized agent for German compound words, word families, and vocabulary building
"""

import json
import requests
from typing import Dict, Any, List, Optional
import asyncio
import aiohttp

# Import our config
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_config


class VocabularyBuilderAgent:
    """
    Specialized agent for German vocabulary analysis using Wiktionary API
    Focuses on: compound words, word families, etymology, level progression
    """
    
    def __init__(self):
        self.wiktionary_config = get_api_config("wiktionary")
        self.base_url = self.wiktionary_config["base_url"]
        self.user_agent = self.wiktionary_config["user_agent"]
        
        # Session for making requests
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            headers = {"User-Agent": self.user_agent}
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def _fetch_wiktionary_data(self, word: str, language: str = "de") -> Optional[Dict]:
        """
        Fetch word data from Wiktionary API
        """
        try:
            session = await self._get_session()
            url = f"{self.base_url}/page/definition/{word}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Look for German definitions
                    if language in data:
                        return data[language]
                    return data
                else:
                    return None
                    
        except Exception as e:
            print(f"Wiktionary API error: {e}")
            return None
    
    def _analyze_compound_word(self, word: str) -> Dict[str, Any]:
        """
        Analyze German compound words by breaking them down
        Uses common German word patterns and roots
        """
        # Common German compound patterns and word parts
        common_prefixes = ["un", "vor", "nach", "über", "unter", "aus", "ein", "ab", "an", "auf"]
        common_suffixes = ["heit", "keit", "ung", "lich", "bar", "los", "voll", "isch"]
        
        # Known compound words (examples)
        known_compounds = {
            "fahrzeug": ["fahr", "zeug"],  # drive + tool
            "hausarbeit": ["haus", "arbeit"],  # house + work
            "zeitschrift": ["zeit", "schrift"],  # time + writing
            "krankenhaus": ["kranken", "haus"]  # sick + house
        }
        
        # Basic compound word analysis
        compound_analysis = {
            "original_word": word,
            "is_compound": False,
            "components": [],
            "estimated_components": [],
            "word_length": len(word),
            "complexity": "simple"
        }
        
        word_lower = word.lower()
        
        # Check known compounds first
        if word_lower in known_compounds:
            compound_analysis["is_compound"] = True
            compound_analysis["complexity"] = "compound"
            compound_analysis["components"] = known_compounds[word_lower]
            for i, part in enumerate(known_compounds[word_lower]):
                compound_analysis["estimated_components"].append({
                    "part": part,
                    "type": "root",
                    "meaning": f"word part {i+1}: '{part}'"
                })
        
        # Heuristic: if word is longer than 8 characters, likely compound
        elif len(word) > 8:
            compound_analysis["is_compound"] = True
            compound_analysis["complexity"] = "compound"
            
            # Try to identify common patterns
            for prefix in common_prefixes:
                if word_lower.startswith(prefix):
                    compound_analysis["estimated_components"].append({
                        "part": prefix,
                        "type": "prefix",
                        "meaning": f"prefix '{prefix}'"
                    })
                    break
            
            for suffix in common_suffixes:
                if word_lower.endswith(suffix):
                    compound_analysis["estimated_components"].append({
                        "part": suffix,
                        "type": "suffix", 
                        "meaning": f"suffix '{suffix}'"
                    })
                    break
        
        return compound_analysis
    
    def _determine_cefr_level(self, word: str, frequency_rank: Optional[int] = None) -> str:
        """
        Estimate CEFR level for a German word based on length and complexity
        """
        word_len = len(word)
        
        # Simple heuristic based on word characteristics
        if word_len <= 4:
            return "A1"
        elif word_len <= 6:
            return "A2"
        elif word_len <= 8:
            return "B1"
        elif word_len <= 12:
            return "B2"
        elif word_len <= 16:
            return "C1"
        else:
            return "C2"
    
    async def analyze_vocabulary(self, word: str, level: str = "A1") -> Dict[str, Any]:
        """
        Comprehensive vocabulary analysis for a German word
        
        Args:
            word: German word to analyze
            level: Current learner's CEFR level
            
        Returns:
            Dictionary with detailed vocabulary analysis
        """
        try:
            # Get Wiktionary data
            wiktionary_data = await self._fetch_wiktionary_data(word)
            
            # Analyze compound structure
            compound_analysis = self._analyze_compound_word(word)
            
            # Determine estimated level
            estimated_level = self._determine_cefr_level(word)
            
            # Build comprehensive analysis
            vocabulary_analysis = {
                "word": word,
                "learner_level": level,
                "estimated_word_level": estimated_level,
                "compound_analysis": compound_analysis,
                "definitions": [],
                "word_family": [],
                "learning_tips": [],
                "difficulty_assessment": "unknown"
            }
            
            # Process Wiktionary data if available
            if wiktionary_data:
                # Extract definitions (simplified)
                if isinstance(wiktionary_data, list):
                    for definition_group in wiktionary_data:
                        if "definitions" in definition_group:
                            for definition in definition_group["definitions"]:
                                vocabulary_analysis["definitions"].append({
                                    "definition": definition.get("definition", ""),
                                    "part_of_speech": definition_group.get("partOfSpeech", "")
                                })
            
            # Add learning tips based on level
            vocabulary_analysis["learning_tips"] = self._generate_learning_tips(
                word, level, compound_analysis
            )
            
            # Assess difficulty relative to learner level
            vocabulary_analysis["difficulty_assessment"] = self._assess_difficulty(
                estimated_level, level
            )
            
            return {
                "success": True,
                "analysis": vocabulary_analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Vocabulary analysis failed: {str(e)}",
                "word": word
            }
    
    def _generate_learning_tips(self, word: str, learner_level: str, compound_analysis: Dict) -> List[str]:
        """Generate level-appropriate learning tips"""
        tips = []
        
        if compound_analysis["is_compound"]:
            tips.append("This is a compound word - try to break it into smaller parts")
            if compound_analysis["estimated_components"]:
                parts = [comp["part"] for comp in compound_analysis["estimated_components"]]
                tips.append(f"Look for these word parts: {', '.join(parts)}")
        
        if learner_level in ["A1", "A2"]:
            tips.append("Focus on the basic meaning first, don't worry about all the nuances")
            if len(word) > 8:
                tips.append("This word might be challenging at your level - learn the simpler parts first")
        
        elif learner_level in ["B1", "B2"]:
            tips.append("Try to use this word in different sentence contexts")
            if compound_analysis["is_compound"]:
                tips.append("Practice creating your own compound words with these parts")
        
        else:  # C1, C2
            tips.append("Explore the etymology and subtle meaning differences")
            tips.append("Look for related words in the same word family")
        
        return tips
    
    def _assess_difficulty(self, word_level: str, learner_level: str) -> str:
        """Assess word difficulty relative to learner level"""
        levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        
        try:
            word_idx = levels.index(word_level)
            learner_idx = levels.index(learner_level)
            
            if word_idx <= learner_idx:
                return "appropriate"
            elif word_idx == learner_idx + 1:
                return "challenging"
            else:
                return "advanced"
        except ValueError:
            return "unknown"
    
    async def close(self):
        """Clean up the session"""
        if self.session:
            await self.session.close()


# Test function
async def test_vocabulary_builder():
    """Test the Vocabulary Builder Agent"""
    print("🧪 Testing Vocabulary Builder Agent...")
    
    agent = VocabularyBuilderAgent()
    
    try:
        # Test with a simple German word
        test_word = "Fahrzeug"  # Vehicle (compound word)
        print(f"📝 Analyzing word: '{test_word}'")
        
        result = await agent.analyze_vocabulary(test_word, "B1")
        
        if result["success"]:
            print("✅ Vocabulary analysis successful!")
            analysis = result["analysis"]
            
            print(f"📊 Estimated level: {analysis['estimated_word_level']}")
            print(f"🔧 Is compound: {analysis['compound_analysis']['is_compound']}")
            print(f"💡 Learning tips: {len(analysis['learning_tips'])}")
            print(f"📈 Difficulty: {analysis['difficulty_assessment']}")
            
            if analysis["learning_tips"]:
                print(f"💡 First tip: {analysis['learning_tips'][0]}")
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        
        await agent.close()
        return result["success"]
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        await agent.close()
        return False


if __name__ == "__main__":
    asyncio.run(test_vocabulary_builder())