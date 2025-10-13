"""
Text-to-Speech Helper for German Learning Assistant
Generates German audio using Microsoft Edge TTS (free)
No caching - generates fresh audio each time
"""

import edge_tts
import asyncio
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime

# Import our config
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import get_api_config, AUDIO_CACHE_DIR


class GermanTTSHelper:
    """
    Helper class for generating German text-to-speech audio
    Uses edge-tts (Microsoft Edge TTS) - completely free
    Generates fresh audio each time (no caching)
    """
    
    def __init__(self):
        self.tts_config = get_api_config("tts")
        self.voice = self.tts_config["voice"]
        self.rate = self.tts_config["rate"]
        self.pitch = self.tts_config["pitch"]
        self.audio_dir = AUDIO_CACHE_DIR
        
        # Ensure audio directory exists
        self.audio_dir.mkdir(exist_ok=True)
    
    def _get_audio_filename(self, text: str) -> Path:
        """
        Generate a unique filename for audio
        Uses timestamp + hash to ensure uniqueness
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return self.audio_dir / f"de_{timestamp}_{text_hash}.mp3"
    
    async def generate_speech(
        self, 
        text: str, 
        voice: Optional[str] = None
    ) -> Path:
        """
        Generate speech audio for German text
        
        Args:
            text: German text to convert to speech
            voice: Voice to use (default: de-DE-KatjaNeural)
            
        Returns:
            Path to the generated MP3 file
        """
        voice_to_use = voice or self.voice
        audio_file = self._get_audio_filename(text)
        
        print(f"🎤 Generating speech: '{text[:50]}...'")
        
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_to_use,
                rate=self.rate,
                pitch=self.pitch
            )
            
            await communicate.save(str(audio_file))
            print(f"✅ Audio saved: {audio_file.name}")
            return audio_file
            
        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            raise
    
    async def generate_multiple(
        self,
        texts: list,
        voice: Optional[str] = None
    ) -> list:
        """
        Generate speech for multiple texts efficiently
        
        Args:
            texts: List of German texts
            voice: Voice to use
            
        Returns:
            List of paths to generated MP3 files
        """
        tasks = [self.generate_speech(text, voice) for text in texts]
        return await asyncio.gather(*tasks)
    
    def cleanup_old_audio(self, max_files: int = 50):
        """
        Clean up old audio files, keeping only the most recent ones
        
        Args:
            max_files: Maximum number of audio files to keep
        """
        audio_files = sorted(
            self.audio_dir.glob("*.mp3"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if len(audio_files) > max_files:
            files_to_delete = audio_files[max_files:]
            for audio_file in files_to_delete:
                audio_file.unlink()
            print(f"🗑️  Cleaned up {len(files_to_delete)} old audio files")
    
    def clear_all_audio(self):
        """Clear all audio files"""
        count = 0
        for audio_file in self.audio_dir.glob("*.mp3"):
            audio_file.unlink()
            count += 1
        print(f"🗑️  Cleared {count} audio files")
    
    def get_audio_stats(self) -> dict:
        """Get audio directory statistics"""
        files = list(self.audio_dir.glob("*.mp3"))
        total_size = sum(f.stat().st_size for f in files)
        
        return {
            "file_count": len(files),
            "total_size_mb": total_size / (1024 * 1024),
            "total_size_kb": total_size / 1024
        }
    
    def get_available_voices(self) -> dict:
        """Get information about available German voices"""
        return {
            "female_standard": {
                "voice": "de-DE-KatjaNeural",
                "description": "Female German voice (Standard German)",
                "region": "Germany",
                "style": "Friendly, clear, natural"
            },
            "male_standard": {
                "voice": "de-DE-ConradNeural",
                "description": "Male German voice (Standard German)",
                "region": "Germany",
                "style": "Professional, clear, authoritative"
            },
            "female_austria": {
                "voice": "de-AT-IngridNeural",
                "description": "Female Austrian German voice",
                "region": "Austria",
                "style": "Austrian accent, friendly"
            },
            "male_austria": {
                "voice": "de-AT-JonasNeural",
                "description": "Male Austrian German voice",
                "region": "Austria",
                "style": "Austrian accent, professional"
            },
            "female_swiss": {
                "voice": "de-CH-LeniNeural",
                "description": "Female Swiss German voice",
                "region": "Switzerland",
                "style": "Swiss accent, warm"
            },
            "male_swiss": {
                "voice": "de-CH-JanNeural",
                "description": "Male Swiss German voice",
                "region": "Switzerland",
                "style": "Swiss accent, clear"
            }
        }


# Test function
async def test_tts():
    """Test the TTS helper"""
    print("🧪 Testing German TTS Helper (No Caching)")
    print("=" * 60)
    
    tts = GermanTTSHelper()
    
    try:
        # Test 1: Basic speech generation
        print("\n📝 Test 1: Basic Speech Generation")
        test_text = "Guten Tag! Wie geht es Ihnen heute?"
        print(f"Text: '{test_text}'")
        
        audio_file = await tts.generate_speech(test_text)
        file_size = audio_file.stat().st_size / 1024
        print(f"✅ Audio generated: {audio_file.name}")
        print(f"📊 File size: {file_size:.2f} KB")
        
        # Test 2: Generate same text again (should create new file)
        print("\n🔄 Test 2: Generate Same Text Again (No Cache)")
        audio_file2 = await tts.generate_speech(test_text)
        print(f"✅ New file created: {audio_file.name != audio_file2.name}")
        print(f"   File 1: {audio_file.name}")
        print(f"   File 2: {audio_file2.name}")
        
        # Test 3: Multiple texts
        print("\n📚 Test 3: Multiple Texts Generation")
        multiple_texts = [
            "Eins, zwei, drei",
            "Ich lerne Deutsch",
            "Das ist sehr interessant"
        ]
        audio_files = await tts.generate_multiple(multiple_texts)
        print(f"✅ Generated {len(audio_files)} audio files")
        
        # Test 4: Available voices
        print("\n🎤 Test 4: Available German Voices")
        voices = tts.get_available_voices()
        for key, info in voices.items():
            print(f"  • {info['description']}: {info['voice']}")
        
        # Test 5: Audio statistics
        print("\n📊 Test 5: Audio Statistics")
        stats = tts.get_audio_stats()
        print(f"✅ Audio files: {stats['file_count']}")
        print(f"✅ Total size: {stats['total_size_mb']:.2f} MB ({stats['total_size_kb']:.2f} KB)")
        
        # Test 6: Cleanup
        print("\n🗑️  Test 6: Cleanup Old Files")
        tts.cleanup_old_audio(max_files=3)
        stats_after = tts.get_audio_stats()
        print(f"✅ Files after cleanup: {stats_after['file_count']}")
        
        print("\n" + "=" * 60)
        print("🎉 All TTS tests passed successfully!")
        print(f"🔊 You can play the audio files in: {tts.audio_dir}")
        print("💡 Audio files are NOT cached - fresh generation each time")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_tts())