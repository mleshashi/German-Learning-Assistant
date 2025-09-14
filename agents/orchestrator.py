"""
LangGraph Orchestrator for German Learning Assistant
Coordinates multiple agents for comprehensive German learning
"""

import json
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Import our agents
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from agents.grammar_master import GrammarMasterAgent
from agents.vocabulary_builder import VocabularyBuilderAgent  
from agents.conversation_practice import ConversationPracticeAgent


class GermanLearningState(TypedDict):
    """
    Shared state between all agents in the workflow
    """
    # Input
    original_text: str
    user_level: str
    learning_goal: str
    context: Dict[str, Any]
    
    # Agent Results
    grammar_analysis: Optional[Dict[str, Any]]
    vocabulary_analysis: Optional[Dict[str, Any]] 
    conversation_response: Optional[Dict[str, Any]]
    
    # Workflow Control
    needs_grammar_analysis: bool
    needs_vocabulary_analysis: bool
    needs_conversation_practice: bool
    complex_words_found: List[str]
    
    # Final Output
    comprehensive_lesson: Optional[Dict[str, Any]]
    next_agent: Optional[str]
    workflow_complete: bool


class GermanLearningOrchestrator:
    """
    LangGraph orchestrator that coordinates all German learning agents
    """
    
    def __init__(self):
        # Initialize agents
        self.grammar_agent = GrammarMasterAgent()
        self.vocab_agent = VocabularyBuilderAgent()
        self.conversation_agent = ConversationPracticeAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for German learning
        """
        workflow = StateGraph(GermanLearningState)
        
        # Add agent nodes
        workflow.add_node("analyzer", self._analyze_input)
        workflow.add_node("grammar_master", self._grammar_analysis)
        workflow.add_node("vocabulary_builder", self._vocabulary_analysis)
        workflow.add_node("conversation_partner", self._conversation_practice)
        workflow.add_node("synthesizer", self._synthesize_lesson)
        
        # Define the workflow edges
        workflow.set_entry_point("analyzer")
        
        # Analyzer decides which agents to call
        workflow.add_conditional_edges(
            "analyzer",
            self._route_from_analyzer,
            {
                "grammar": "grammar_master",
                "vocabulary": "vocabulary_builder", 
                "conversation": "conversation_partner",
                "synthesize": "synthesizer"
            }
        )
        
        # Grammar master can trigger vocabulary analysis
        workflow.add_conditional_edges(
            "grammar_master",
            self._route_from_grammar,
            {
                "vocabulary": "vocabulary_builder",
                "conversation": "conversation_partner", 
                "synthesize": "synthesizer"
            }
        )
        
        # Vocabulary builder leads to conversation or synthesis
        workflow.add_conditional_edges(
            "vocabulary_builder",
            self._route_from_vocabulary,
            {
                "conversation": "conversation_partner",
                "synthesize": "synthesizer"
            }
        )
        
        # Conversation practice leads to synthesis
        workflow.add_edge("conversation_partner", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile()
    
    async def _analyze_input(self, state: GermanLearningState) -> GermanLearningState:
        """
        Analyze input and determine which agents are needed
        """
        text = state["original_text"]
        level = state["user_level"]
        goal = state["learning_goal"]
        
        # Determine what analysis is needed based on input and goal
        state["needs_grammar_analysis"] = True  # Always analyze grammar
        
        # Check for complex words (> 6 chars or compound words)
        words = text.split()
        complex_words = [w for w in words if len(w) > 6 or any(char.isupper() for char in w[1:])]
        state["complex_words_found"] = complex_words
        state["needs_vocabulary_analysis"] = len(complex_words) > 0
        
        # Conversation practice based on learning goal
        conversation_goals = ["conversation", "speaking", "practice", "dialogue"]
        state["needs_conversation_practice"] = any(goal_word in goal.lower() for goal_word in conversation_goals)
        
        print(f"🔍 Analysis Plan:")
        print(f"   Grammar: {state['needs_grammar_analysis']}")
        print(f"   Vocabulary: {state['needs_vocabulary_analysis']} (found {len(complex_words)} complex words)")
        print(f"   Conversation: {state['needs_conversation_practice']}")
        
        return state
    
    async def _grammar_analysis(self, state: GermanLearningState) -> GermanLearningState:
        """
        Perform grammar analysis using Grammar Master Agent
        """
        print("📚 Running Grammar Analysis...")
        
        result = await self.grammar_agent.analyze_grammar(
            state["original_text"], 
            state["user_level"]
        )
        
        if result["success"]:
            state["grammar_analysis"] = result["analysis"]
            
            # Check if grammar analysis found additional complex words
            analysis = result["analysis"]
            if "nouns" in analysis:
                grammar_complex_words = [noun["word"] for noun in analysis["nouns"] if len(noun["word"]) > 6]
                state["complex_words_found"].extend(grammar_complex_words)
                state["complex_words_found"] = list(set(state["complex_words_found"]))  # Remove duplicates
                
                if grammar_complex_words:
                    state["needs_vocabulary_analysis"] = True
                    print(f"   ➕ Found additional complex words: {grammar_complex_words}")
            
            print(f"   ✅ Grammar analysis complete")
        else:
            print(f"   ❌ Grammar analysis failed: {result.get('error', 'Unknown error')}")
            state["grammar_analysis"] = {"error": result.get("error")}
        
        return state
    
    async def _vocabulary_analysis(self, state: GermanLearningState) -> GermanLearningState:
        """
        Perform vocabulary analysis using Vocabulary Builder Agent
        """
        print("📖 Running Vocabulary Analysis...")
        
        vocab_results = {}
        
        # Analyze each complex word found
        for word in state["complex_words_found"]:
            print(f"   🔍 Analyzing word: {word}")
            result = await self.vocab_agent.analyze_vocabulary(word, state["user_level"])
            
            if result["success"]:
                vocab_results[word] = result["analysis"]
                print(f"   ✅ {word}: {result['analysis']['estimated_word_level']}")
            else:
                vocab_results[word] = {"error": result.get("error")}
                print(f"   ❌ {word}: Failed")
        
        await self.vocab_agent.close()  # Clean up session
        
        state["vocabulary_analysis"] = vocab_results
        print(f"   📊 Vocabulary analysis complete for {len(vocab_results)} words")
        
        return state
    
    async def _conversation_practice(self, state: GermanLearningState) -> GermanLearningState:
        """
        Generate conversation practice using Conversation Practice Agent
        """
        print("💬 Running Conversation Practice...")
        
        # Build context from previous analyses
        context = state["context"].copy()
        
        # Add insights from grammar analysis
        if state["grammar_analysis"]:
            context["grammar_focus"] = state["grammar_analysis"].get("level_appropriate_tip", "")
        
        # Add insights from vocabulary analysis
        if state["vocabulary_analysis"]:
            context["vocabulary_focus"] = list(state["vocabulary_analysis"].keys())
        
        result = await self.conversation_agent.practice_conversation(
            state["original_text"],
            state["user_level"], 
            context
        )
        
        if result["success"]:
            state["conversation_response"] = result["response"]
            print(f"   ✅ Conversation practice generated")
        else:
            print(f"   ❌ Conversation practice failed: {result.get('error', 'Unknown error')}")
            state["conversation_response"] = {"error": result.get("error")}
        
        return state
    
    async def _synthesize_lesson(self, state: GermanLearningState) -> GermanLearningState:
        """
        Synthesize all agent outputs into a comprehensive lesson
        """
        print("🎯 Synthesizing Comprehensive Lesson...")
        
        lesson = {
            "original_input": state["original_text"],
            "user_level": state["user_level"],
            "learning_goal": state["learning_goal"],
            "timestamp": "now",
            
            "grammar_insights": {},
            "vocabulary_insights": {},
            "conversation_practice": {},
            
            "learning_plan": [],
            "difficulty_assessment": "unknown",
            "next_steps": [],
            "estimated_study_time": "10-15 minutes"
        }
        
        # Synthesize grammar insights
        if state["grammar_analysis"] and "error" not in state["grammar_analysis"]:
            lesson["grammar_insights"] = {
                "main_structures": state["grammar_analysis"].get("cases_explanation", ""),
                "learning_tip": state["grammar_analysis"].get("level_appropriate_tip", ""),
                "common_mistakes": state["grammar_analysis"].get("common_mistakes", [])
            }
        
        # Synthesize vocabulary insights
        if state["vocabulary_analysis"]:
            vocab_summary = {}
            for word, analysis in state["vocabulary_analysis"].items():
                if "error" not in analysis:
                    vocab_summary[word] = {
                        "level": analysis.get("estimated_word_level", "unknown"),
                        "is_compound": analysis.get("compound_analysis", {}).get("is_compound", False),
                        "difficulty": analysis.get("difficulty_assessment", "unknown")
                    }
            lesson["vocabulary_insights"] = vocab_summary
        
        # Add conversation practice
        if state["conversation_response"] and "error" not in state["conversation_response"]:
            lesson["conversation_practice"] = {
                "suggested_response": state["conversation_response"].get("german_response", ""),
                "translation": state["conversation_response"].get("english_translation", ""),
                "cultural_note": state["conversation_response"].get("cultural_note", ""),
                "conversation_tips": state["conversation_response"].get("conversation_tips", [])
            }
        
        # Generate learning plan
        lesson["learning_plan"] = self._create_learning_plan(state)
        
        state["comprehensive_lesson"] = lesson
        state["workflow_complete"] = True
        
        print(f"   ✅ Comprehensive lesson created")
        print(f"   📋 Learning plan has {len(lesson['learning_plan'])} steps")
        
        return state
    
    def _create_learning_plan(self, state: GermanLearningState) -> List[str]:
        """Create a personalized learning plan based on analysis results"""
        plan = []
        
        # Grammar-based recommendations
        if state["grammar_analysis"]:
            plan.append("Review the grammatical structures identified in your text")
            if state["grammar_analysis"].get("common_mistakes"):
                plan.append("Practice avoiding the common grammar mistakes highlighted")
        
        # Vocabulary-based recommendations
        if state["vocabulary_analysis"]:
            compound_words = [word for word, analysis in state["vocabulary_analysis"].items() 
                            if analysis.get("compound_analysis", {}).get("is_compound", False)]
            if compound_words:
                plan.append(f"Practice breaking down compound words: {', '.join(compound_words)}")
        
        # Conversation-based recommendations
        if state["conversation_response"]:
            plan.append("Practice the conversation scenario with the suggested responses")
            if state["conversation_response"].get("conversation_tips"):
                plan.append("Apply the conversation tips in your next German conversation")
        
        return plan
    
    # Routing functions for conditional edges
    def _route_from_analyzer(self, state: GermanLearningState) -> str:
        """Route from analyzer to first needed agent"""
        if state["needs_grammar_analysis"]:
            return "grammar"
        elif state["needs_vocabulary_analysis"]:
            return "vocabulary"
        elif state["needs_conversation_practice"]:
            return "conversation"
        else:
            return "synthesize"
    
    def _route_from_grammar(self, state: GermanLearningState) -> str:
        """Route from grammar master to next agent"""
        if state["needs_vocabulary_analysis"]:
            return "vocabulary"
        elif state["needs_conversation_practice"]:
            return "conversation"
        else:
            return "synthesize"
    
    def _route_from_vocabulary(self, state: GermanLearningState) -> str:
        """Route from vocabulary builder to next agent"""
        if state["needs_conversation_practice"]:
            return "conversation"
        else:
            return "synthesize"
    
    async def orchestrate_learning(
        self, 
        text: str, 
        level: str = "A1", 
        goal: str = "general learning",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main orchestration method - coordinates all agents for comprehensive learning
        
        Args:
            text: German text to analyze
            level: CEFR level (A1-C2)
            goal: Learning goal (grammar, vocabulary, conversation, etc.)
            context: Additional context
            
        Returns:
            Comprehensive learning analysis from all agents
        """
        try:
            print(f"🚀 Starting LangGraph Orchestration for: '{text}'")
            print(f"   📊 Level: {level}, Goal: {goal}")
            
            # Initialize state
            initial_state = GermanLearningState(
                original_text=text,
                user_level=level,
                learning_goal=goal,
                context=context or {},
                
                grammar_analysis=None,
                vocabulary_analysis=None,
                conversation_response=None,
                
                needs_grammar_analysis=False,
                needs_vocabulary_analysis=False,
                needs_conversation_practice=False,
                complex_words_found=[],
                
                comprehensive_lesson=None,
                next_agent=None,
                workflow_complete=False
            )
            
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": True,
                "comprehensive_lesson": final_state["comprehensive_lesson"],
                "workflow_state": final_state
            }
            
        except Exception as e:
            print(f"❌ Orchestration failed: {e}")
            return {
                "success": False,
                "error": f"Orchestration failed: {str(e)}",
                "original_text": text
            }


# Test function
async def test_langgraph_orchestrator():
    """Test the LangGraph orchestration with a complex German sentence"""
    print("🧪 Testing LangGraph German Learning Orchestrator...")
    
    orchestrator = GermanLearningOrchestrator()
    
    try:
        # Test with a sentence that needs all three agents
        test_sentence = "Ich möchte ein Fahrzeug kaufen, aber es ist sehr teuer."
        
        result = await orchestrator.orchestrate_learning(
            text=test_sentence,
            level="B1", 
            goal="comprehensive learning",
            context={"topic": "shopping", "scenario": "buying decisions"}
        )
        
        if result["success"]:
            print("\n🎉 LangGraph Orchestration Successful!")
            lesson = result["comprehensive_lesson"]
            
            print(f"📚 Grammar Insights: {bool(lesson.get('grammar_insights'))}")
            print(f"📖 Vocabulary Insights: {len(lesson.get('vocabulary_insights', {}))}")
            print(f"💬 Conversation Practice: {bool(lesson.get('conversation_practice'))}")
            print(f"📋 Learning Plan Steps: {len(lesson.get('learning_plan', []))}")
            
            if lesson.get("learning_plan"):
                print(f"🎯 First learning step: {lesson['learning_plan'][0]}")
            
            return True
        else:
            print(f"❌ Orchestration failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_langgraph_orchestrator())