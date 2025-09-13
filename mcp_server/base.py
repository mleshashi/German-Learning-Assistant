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
        """Handle grammar analysis requests"""
        # This will be implemented by the Grammar Master Agent
        return MCPResponse(
            success=True,
            data={"message": "Grammar analysis not yet implemented"},
            error=None
        )
    
    async def _handle_vocabulary_request(self, request: MCPRequest) -> MCPResponse:
        """Handle vocabulary lookup requests"""
        # This will be implemented by the Vocabulary Builder Agent
        return MCPResponse(
            success=True,
            data={"message": "Vocabulary lookup not yet implemented"},
            error=None
        )
    
    async def _handle_conversation_request(self, request: MCPRequest) -> MCPResponse:
        """Handle conversation practice requests"""
        # This will be implemented by the Conversation Practice Agent
        return MCPResponse(
            success=True,
            data={"message": "Conversation practice not yet implemented"},
            error=None
        )
    
    async def _handle_tts_request(self, request: MCPRequest) -> MCPResponse:
        """Handle text-to-speech requests"""
        # This will be implemented later with edge-tts
        return MCPResponse(
            success=True,
            data={"message": "TTS not yet implemented"},
            error=None
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
    """Test the basic MCP server functionality"""
    print("🧪 Testing Basic MCP Server...")
    
    try:
        server = BaseMCPServer()
        
        # Test health check
        health = server.health_check()
        print(f"✅ Health Check: {health}")
        
        # Test a basic request
        test_request = MCPRequest(
            request_type=MCPRequestType.GRAMMAR_ANALYSIS,
            text="Der Hund ist groß",
            level="A1"
        )
        
        response = await server.process_request(test_request)
        print(f"✅ Test Request: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    # Run basic test
    asyncio.run(test_mcp_server())