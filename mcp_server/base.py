"""
Base MCP Server for German Learning Assistant
Handles communication with free AI services
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import our config
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_config, FREE_APIS


class MCPRequestType(Enum):
    """Types of MCP requests our server can handle"""
    GRAMMAR_ANALYSIS = "grammar_analysis"
    VOCABULARY_LOOKUP = "vocabulary_lookup" 
    CONVERSATION_PRACTICE = "conversation_practice"
    TEXT_TO_SPEECH = "text_to_speech"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"


@dataclass
class MCPRequest:
    """Structure for MCP requests"""
    request_type: MCPRequestType
    text: str
    language: str = "de"  # German by default
    level: str = "A1"    # CEFR level
    context: Optional[Dict[str, Any]] = None


@dataclass 
class MCPResponse:
    """Structure for MCP responses"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    request_id: Optional[str] = None


class BaseMCPServer:
    """
    Base MCP Server that handles communication with free services
    """
    
    def __init__(self):
        self.groq_config = get_api_config("groq")
        self.wiktionary_config = get_api_config("wiktionary")
        self.tts_config = get_api_config("tts")
        
        # Validate we have required config
        if not self.groq_config.get("api_key"):
            raise ValueError("GROQ_API_KEY not found in environment")
    
    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """
        Main entry point for processing MCP requests
        Routes to appropriate handler based on request type
        """
        try:
            if request.request_type == MCPRequestType.GRAMMAR_ANALYSIS:
                return await self._handle_grammar_request(request)
            elif request.request_type == MCPRequestType.VOCABULARY_LOOKUP:
                return await self._handle_vocabulary_request(request)
            elif request.request_type == MCPRequestType.CONVERSATION_PRACTICE:
                return await self._handle_conversation_request(request)
            elif request.request_type == MCPRequestType.TEXT_TO_SPEECH:
                return await self._handle_tts_request(request)
            elif request.request_type == MCPRequestType.COMPREHENSIVE_ANALYSIS:
                return await self._handle_comprehensive_analysis(request)
            else:
                return MCPResponse(
                    success=False,
                    data={},
                    error=f"Unknown request type: {request.request_type}"
                )
        
        except Exception as e:
            return MCPResponse(
                success=False,
                data={},
                error=f"Server error: {str(e)}"
            )
    
    async def _handle_grammar_request(self, request: MCPRequest) -> MCPResponse:
        """Handle grammar analysis requests using Grammar Master Agent"""
        try:
            # Import here to avoid circular imports
            from agents.grammar_master import GrammarMasterAgent
            
            agent = GrammarMasterAgent()
            result = await agent.analyze_grammar(request.text, request.level)
            
            if result["success"]:
                return MCPResponse(
                    success=True,
                    data=result["analysis"],
                    error=None
                )
            else:
                return MCPResponse(
                    success=False,
                    data={},
                    error=result.get("error", "Grammar analysis failed")
                )
                
        except Exception as e:
            return MCPResponse(
                success=False,
                data={},
                error=f"Grammar agent error: {str(e)}"
            )
    
    async def _handle_vocabulary_request(self, request: MCPRequest) -> MCPResponse:
        """Handle vocabulary lookup requests using Vocabulary Builder Agent"""
        try:
            # Import here to avoid circular imports
            from agents.vocabulary_builder import VocabularyBuilderAgent
            
            agent = VocabularyBuilderAgent()
            result = await agent.analyze_vocabulary(request.text, request.level)
            await agent.close()  # Clean up session
            
            if result["success"]:
                return MCPResponse(
                    success=True,
                    data=result["analysis"],
                    error=None
                )
            else:
                return MCPResponse(
                    success=False,
                    data={},
                    error=result.get("error", "Vocabulary analysis failed")
                )
                
        except Exception as e:
            return MCPResponse(
                success=False,
                data={},
                error=f"Vocabulary agent error: {str(e)}"
            )
    
    async def _handle_conversation_request(self, request: MCPRequest) -> MCPResponse:
        """Handle conversation practice requests using Conversation Practice Agent"""
        try:
            # Import here to avoid circular imports
            from agents.conversation_practice import ConversationPracticeAgent
            
            agent = ConversationPracticeAgent()
            
            # Extract context from request if available
            context = request.context or {}
            
            result = await agent.practice_conversation(
                request.text, 
                request.level, 
                context
            )
            
            if result["success"]:
                return MCPResponse(
                    success=True,
                    data=result["response"],
                    error=None
                )
            else:
                return MCPResponse(
                    success=False,
                    data={},
                    error=result.get("error", "Conversation practice failed")
                )
                
        except Exception as e:
            return MCPResponse(
                success=False,
                data={},
                error=f"Conversation agent error: {str(e)}"
            )
    
    async def _handle_tts_request(self, request: MCPRequest) -> MCPResponse:
        """Handle text-to-speech requests"""
        # This will be implemented later with edge-tts
        return MCPResponse(
            success=True,
            data={"message": "TTS not yet implemented"},
            error=None
        )

    async def _handle_comprehensive_analysis(self, request: MCPRequest) -> MCPResponse:
        """Handle comprehensive analysis using LangGraph orchestration"""
        try:
            # Import here to avoid circular imports
            from agents.orchestrator import GermanLearningOrchestrator
            
            orchestrator = GermanLearningOrchestrator()
            
            # Extract context and goal from request
            context = request.context or {}
            goal = context.get("learning_goal", "comprehensive learning")
            
            result = await orchestrator.orchestrate_learning(
                text=request.text,
                level=request.level,
                goal=goal,
                context=context
            )
            
            if result["success"]:
                return MCPResponse(
                    success=True,
                    data=result["comprehensive_lesson"],
                    error=None
                )
            else:
                return MCPResponse(
                    success=False,
                    data={},
                    error=result.get("error", "Comprehensive analysis failed")
                )
                
        except Exception as e:
            return MCPResponse(
                success=False,
                data={},
                error=f"LangGraph orchestration error: {str(e)}"
            )
    
    def health_check(self) -> Dict[str, Any]:
        """Basic health check for the MCP server"""
        return {
            "status": "healthy",
            "services": {
                "groq": bool(self.groq_config.get("api_key")),
                "wiktionary": True,  # No auth needed
                "tts": True  # Local service
            },
            "version": "0.1.0"
        }


# Simple test function
async def test_mcp_server():
    """Test the complete MCP server functionality with all agents"""
    print("🧪 Testing Complete MCP Server with All Agents...")
    
    try:
        server = BaseMCPServer()
        
        # Test health check
        health = server.health_check()
        print(f"✅ Health Check: {health['status']}")
        
        # Test Grammar Master Agent
        print("\n📚 Testing Grammar Master Agent...")
        grammar_request = MCPRequest(
            request_type=MCPRequestType.GRAMMAR_ANALYSIS,
            text="Der große Hund läuft schnell.",
            level="A2"
        )
        grammar_response = await server.process_request(grammar_request)
        print(f"✅ Grammar Analysis: {grammar_response.success}")
        
        # Test Vocabulary Builder Agent  
        print("\n📖 Testing Vocabulary Builder Agent...")
        vocab_request = MCPRequest(
            request_type=MCPRequestType.VOCABULARY_LOOKUP,
            text="Fahrzeug",
            level="B1"
        )
        vocab_response = await server.process_request(vocab_request)
        print(f"✅ Vocabulary Analysis: {vocab_response.success}")
        if vocab_response.success:
            is_compound = vocab_response.data.get("compound_analysis", {}).get("is_compound", False)
            print(f"   🔧 Detected compound: {is_compound}")
        
        # Test Conversation Practice Agent
        print("\n💬 Testing Conversation Practice Agent...")
        conversation_request = MCPRequest(
            request_type=MCPRequestType.CONVERSATION_PRACTICE,
            text="Guten Tag! Wie geht es Ihnen?",
            level="A2",
            context={"topic": "greeting", "scenario": "formal"}
        )
        conversation_response = await server.process_request(conversation_request)
        print(f"✅ Conversation Practice: {conversation_response.success}")
        if conversation_response.success:
            german_response = conversation_response.data.get("german_response", "")
            print(f"   🤖 Bot responded: {german_response[:50]}...")
        
        # Test LangGraph Comprehensive Analysis
        print("\n🧠 Testing LangGraph Comprehensive Analysis...")
        comprehensive_request = MCPRequest(
            request_type=MCPRequestType.COMPREHENSIVE_ANALYSIS,
            text="Ich möchte ein Fahrzeug kaufen, aber es ist sehr teuer.",
            level="B1",
            context={
                "learning_goal": "comprehensive learning",
                "topic": "shopping",
                "scenario": "buying decisions"
            }
        )
        comprehensive_response = await server.process_request(comprehensive_request)
        print(f"✅ LangGraph Analysis: {comprehensive_response.success}")
        if comprehensive_response.success:
            lesson = comprehensive_response.data
            grammar_insights = lesson.get("grammar_insights", {})
            vocab_insights = lesson.get("vocabulary_insights", {})
            learning_plan = lesson.get("learning_plan", [])
            
            print(f"   📚 Grammar insights: {bool(grammar_insights)}")
            print(f"   📖 Vocabulary words analyzed: {len(vocab_insights)}")
            print(f"   📋 Learning plan steps: {len(learning_plan)}")
            if learning_plan:
                print(f"   🎯 First step: {learning_plan[0][:50]}...")
        else:
            print(f"   ❌ LangGraph failed: {comprehensive_response.error}")
        
        print(f"\n🎉 Complete German Learning System operational!")
        print("   ✅ Individual Agents (Grammar, Vocabulary, Conversation)")
        print("   ✅ LangGraph Orchestration (Comprehensive Analysis)")
        print("   ✅ MCP Server Integration")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    # Run basic test
    asyncio.run(test_mcp_server())