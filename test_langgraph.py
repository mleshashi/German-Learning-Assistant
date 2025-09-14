#!/usr/bin/env python3
"""
Quick test for LangGraph integration
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agents.orchestrator import GermanLearningOrchestrator

async def test_complete_system():
    """Test the complete LangGraph system"""
    print("🧪 Testing Complete LangGraph German Learning System...")
    
    try:
        # Test LangGraph Orchestrator directly
        orchestrator = GermanLearningOrchestrator()
        
        test_sentence = "Ich möchte ein Fahrzeug kaufen, aber es ist sehr teuer."
        
        result = await orchestrator.orchestrate_learning(
            text=test_sentence,
            level="B1",
            goal="comprehensive learning",
            context={
                "topic": "shopping",
                "scenario": "buying decisions"
            }
        )
        
        if result["success"]:
            print("🎉 LangGraph System Working!")
            lesson = result["comprehensive_lesson"]
            
            print(f"📚 Grammar Insights: {bool(lesson.get('grammar_insights'))}")
            print(f"📖 Vocabulary Analysis: {len(lesson.get('vocabulary_insights', {}))}")
            print(f"💬 Conversation Practice: {bool(lesson.get('conversation_practice'))}")
            print(f"📋 Learning Plan: {len(lesson.get('learning_plan', []))} steps")
            
            # Show some results
            if lesson.get("learning_plan"):
                print(f"\n🎯 Learning Plan:")
                for i, step in enumerate(lesson["learning_plan"], 1):
                    print(f"   {i}. {step}")
            
            if lesson.get("vocabulary_insights"):
                print(f"\n📖 Vocabulary Analysis:")
                for word, analysis in lesson["vocabulary_insights"].items():
                    level = analysis.get("level", "unknown")
                    is_compound = analysis.get("is_compound", False)
                    print(f"   • {word}: {level} level {'(compound)' if is_compound else ''}")
            
            return True
        else:
            print(f"❌ LangGraph failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_system())
    if success:
        print("\n✅ LangGraph integration is working perfectly!")
        print("🚀 Ready to build UI or add more features!")
    else:
        print("\n❌ LangGraph integration needs debugging")