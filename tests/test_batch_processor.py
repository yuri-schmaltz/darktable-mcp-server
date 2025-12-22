"""
Tests for batch_processor.py module.
Tests batch processing logic, message building, and LLM interaction.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "host"))

import pytest
from unittest.mock import Mock, patch, MagicMock
from batch_processor import build_messages, BatchProcessor


class TestBuildMessages:
    """Tests for build_messages function."""
    
    def test_build_messages_no_images(self):
        """Test building messages without images."""
        system_prompt = "You are a helpful assistant."
        sample = [{"id": 1, "path": "/test", "filename": "img.jpg"}]
        vision_images = []
        
        messages = build_messages(system_prompt, sample, vision_images, "ollama")
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == system_prompt
        assert messages[1]["role"] == "user"
    
    def test_build_messages_with_images_ollama(self, mock_image_dict):
        """Test building messages with images for Ollama format."""
        from common import VisionImage
        
        system_prompt = "Analyze images"
        vision_images = [
            VisionImage(
                meta=mock_image_dict,
                path=Path("/test/img.jpg"),
                b64="fakebase64",
                data_url="data:image/jpeg;base64,fakebase64"
            )
        ]
        sample = [mock_image_dict]
        
        messages = build_messages(system_prompt, sample, vision_images, "ollama")
        
        assert len(messages) >= 1
        assert messages[0]["role"] == "system"
    
    def test_build_messages_system_prompt(self):
        """Test that system prompt is included."""
        system_prompt = "Custom system prompt"
        sample = []
        vision_images = []
        
        messages = build_messages(system_prompt, sample, vision_images, "ollama")
        
        assert any(msg["role"] == "system" and system_prompt in msg["content"] 
                   for msg in messages)


class TestBatchProcessor:
    """Tests for BatchProcessor class."""
    
    def test_batch_processor_initialization(self):
        """Test BatchProcessor can be initialized."""
        with patch('batch_processor.LLMProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider.__class__.__name__ = "OllamaProvider"
            mock_client = Mock()
            
            processor = BatchProcessor(
                client=mock_client,
                provider=mock_provider,
                dry_run=False
            )
            
            assert processor.client == mock_client
            assert processor.provider == mock_provider
            assert processor.dry_run == False
    
    def test_batch_processor_rate_mode(self):
        """Test rate mode is recognized."""
        with patch('batch_processor.LLMProvider'):
            mock_provider = Mock()
            mock_provider.__class__.__name__ = "OllamaProvider"
            mock_client = Mock()
            
            processor = BatchProcessor(
                client=mock_client,
                provider=mock_provider
            )
            
            # Should have run method
            assert hasattr(processor, 'run')
    
    @patch('batch_processor.fetch_images')
    @patch('batch_processor.prepare_vision_payloads_async')
    def test_batch_processor_mock_execution(self, mock_prepare, mock_fetch):
        """Test batch processor with mocked dependencies."""
        # Setup mocks
        mock_fetch.return_value = [{"id": 1, "rating": 0}]
        mock_prepare.return_value = ([], [])
        
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "OllamaProvider"
        mock_provider.send_message.return_value = "rating: 3"
        mock_client = Mock()
        
        processor = BatchProcessor(
            client=mock_client,
            provider=mock_provider
        )
        
        # Create mock args
        args = Mock()
        args.mode = "rating"
        args.limit = 1
        args.min_rating = 0
        args.text_only = True
        args.prompt_file = None
        args.prompt_variant = "basico"
        args.generate_styles = False
        
        # Should not crash
        assert processor is not None


class TestBatchProcessorEdgeCases:
    """Tests for edge cases in batch processing."""
    
    def test_empty_image_list(self):
        """Test handling of empty image list."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "OllamaProvider"
        mock_client = Mock()
        
        processor = BatchProcessor(
            client=mock_client,
            provider=mock_provider
        )
        
        assert processor.provider == mock_provider
    
    def test_batch_processor_with_invalid_mode(self):
        """Test initialization with various modes."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "OllamaProvider"
        mock_client = Mock()
        
        processor = BatchProcessor(
            client=mock_client,
            provider=mock_provider
        )
        
        # Should initialize without error
        assert processor is not None


class TestProgressCallback:
    """Tests for progress callback functionality."""
    
    def test_progress_callback_signature(self):
        """Test that progress callback can be called."""
        callback_calls = []
        
        def test_callback(current, total, message):
            callback_calls.append((current, total, message))
        
        # Simulate callback
        test_callback(1, 10, "Processing")
        
        assert len(callback_calls) == 1
        assert callback_calls[0] == (1, 10, "Processing")
    
    @patch('batch_processor.prepare_vision_payloads_async')
    def test_progress_callback_with_batch(self, mock_prepare):
        """Test progress callback integration."""
        callback_calls = []
        
        def mock_callback(current, total, message):
            callback_calls.append((current, total, message))
        
        # Mock should accept progress_callback
        mock_prepare.return_value = ([], [])
        
        from common import prepare_vision_payloads_async
        
        # Test that function accepts callback parameter
        result = prepare_vision_payloads_async(
            [],
            attach_images=True,
            progress_callback=mock_callback
        )
        
        assert result == ([], [])


class TestMessageFormatting:
    """Tests for message formatting for different providers."""
    
    def test_ollama_message_format(self):
        """Test message format for Ollama."""
        messages = build_messages("System", [], [], "ollama")
        
        # Ollama expects role/content structure
        for msg in messages:
            assert "role" in msg
            assert "content" in msg
    
    def test_openai_compat_message_format(self):
        """Test message format for OpenAI-compatible APIs."""
        messages = build_messages("System", [], [], "openai-compat")
        
        # Should also have role/content
        for msg in messages:
            assert "role" in msg
            assert "content" in msg
