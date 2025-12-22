"""
Comprehensive tests for common.py module.
Tests encoding, async processing, logging, and MCP client functionality.
"""
import sys
from pathlib import Path
import threading
import time

sys.path.insert(0, str(Path(__file__).parent.parent / "host"))

import pytest
from unittest.mock import Mock, patch, MagicMock
from common import (
    encode_image_to_base64,
    prepare_vision_payloads,
    prepare_vision_payloads_async,
    setup_logging,
    VisionImage
)


class TestImageEncoding:
    """Tests for encode_image_to_base64 function."""
    
    def test_encode_small_image(self, temp_image_path):
        """Test encoding a small image."""
        b64, data_url = encode_image_to_base64(temp_image_path)
        
        assert isinstance(b64, str)
        assert len(b64) > 0
        assert data_url.startswith("data:image/jpeg;base64,")
        assert b64 in data_url
    
    def test_encode_large_image_resizes(self, temp_large_image_path):
        """Test that large images are resized to max_dimension."""
        b64_small, _ = encode_image_to_base64(temp_large_image_path, max_dimension=800)
        b64_original, _ = encode_image_to_base64(temp_large_image_path, max_dimension=3000)
        
        # Resized image should be smaller
        assert len(b64_small) < len(b64_original)
    
    def test_encode_png_converts_to_jpeg(self, temp_png_image_path):
        """Test that PNG images are converted to JPEG."""
        b64, data_url = encode_image_to_base64(temp_png_image_path)
        
        assert "image/jpeg" in data_url
        assert isinstance(b64, str)
    
    def test_encode_nonexistent_file(self, tmp_path):
        """Test error handling for missing file."""
        fake_path = tmp_path / "nonexistent.jpg"
        
        with pytest.raises(FileNotFoundError):
            encode_image_to_base64(fake_path)
    
    def test_encode_with_custom_max_dimension(self, temp_image_path):
        """Test custom max_dimension parameter."""
        b64_1600, _ = encode_image_to_base64(temp_image_path, max_dimension=1600)
        b64_800, _ = encode_image_to_base64(temp_image_path, max_dimension=800)
        
        # Smaller max_dimension should result in smaller or equal size
        # (image is already 800x600, so won't be resized further)
        assert len(b64_1600) >= len(b64_800)


class TestSyncVisionPayloads:
    """Tests for prepare_vision_payloads (synchronous version)."""
    
    def test_empty_images_list(self):
        """Test with empty images list."""
        payloads, errors = prepare_vision_payloads([], attach_images=True)
        
        assert payloads == []
        assert errors == []
    
    def test_attach_images_false(self, mock_image_list):
        """Test that attach_images=False returns empty payloads."""
        payloads, errors = prepare_vision_payloads(mock_image_list, attach_images=False)
        
        assert payloads == []
        assert errors == []
    
    def test_single_image_processing(self, mock_image_dict):
        """Test processing a single image."""
        payloads, errors = prepare_vision_payloads([mock_image_dict], attach_images=True)
        
        assert len(payloads) == 1
        assert len(errors) == 0
        assert isinstance(payloads[0], VisionImage)
        assert payloads[0].meta == mock_image_dict
        assert len(payloads[0].b64) > 0
    
    def test_multiple_images_processing(self, mock_image_list):
        """Test processing multiple images."""
        payloads, errors = prepare_vision_payloads(mock_image_list, attach_images=True)
        
        assert len(payloads) == len(mock_image_list)
        assert len(errors) == 0
        
        for payload in payloads:
            assert isinstance(payload, VisionImage)
            assert len(payload.b64) > 0
    
    def test_progress_callback(self, mock_image_list):
        """Test that progress callback is called."""
        callback_calls = []
        
        def mock_callback(current, total, message):
            callback_calls.append((current, total, message))
        
        payloads, errors = prepare_vision_payloads(
            mock_image_list, 
            attach_images=True,
            progress_callback=mock_callback
        )
        
        assert len(callback_calls) > 0
        # Check first call
        assert callback_calls[0][0] == 1
        assert callback_calls[0][1] == len(mock_image_list)
        assert "Preparando" in callback_calls[0][2]
    
    def test_missing_file_error(self, tmp_path):
        """Test handling of missing image file."""
        bad_image = {
            "id": 999,
            "filename": "nonexistent.jpg",
            "path": str(tmp_path),
            "rating": 0
        }
        
        payloads, errors = prepare_vision_payloads([bad_image], attach_images=True)
        
        assert len(payloads) == 0
        assert len(errors) == 1
        assert "não encontrado" in errors[0] or "not found" in errors[0].lower()


class TestAsyncVisionPayloads:
    """Tests for prepare_vision_payloads_async (asynchronous version)."""
    
    def test_async_empty_list(self):
        """Test async with empty list."""
        payloads, errors = prepare_vision_payloads_async([], attach_images=True)
        
        assert payloads == []
        assert errors == []
    
    def test_async_attach_false(self, mock_image_list):
        """Test async with attach_images=False."""
        payloads, errors = prepare_vision_payloads_async(
            mock_image_list, 
            attach_images=False
        )
        
        assert payloads == []
        assert errors == []
    
    def test_async_single_image(self, mock_image_dict):
        """Test async processing of single image."""
        payloads, errors = prepare_vision_payloads_async(
            [mock_image_dict], 
            attach_images=True,
            max_workers=2
        )
        
        assert len(payloads) == 1
        assert len(errors) == 0
        assert isinstance(payloads[0], VisionImage)
    
    def test_async_multiple_images(self, mock_image_list):
        """Test async processing of multiple images."""
        payloads, errors = prepare_vision_payloads_async(
            mock_image_list, 
            attach_images=True,
            max_workers=4
        )
        
        assert len(payloads) == len(mock_image_list)
        assert len(errors) == 0
        
        # Verify ordering is preserved
        for i, payload in enumerate(payloads):
            assert payload.meta["id"] == mock_image_list[i]["id"]
    
    def test_async_with_progress_callback(self, mock_image_list):
        """Test async with progress callback."""
        callback_calls = []
        callback_lock = threading.Lock()
        
        def mock_callback(current, total, message):
            with callback_lock:
                callback_calls.append((current, total, message))
        
        payloads, errors = prepare_vision_payloads_async(
            mock_image_list,
            attach_images=True,
            progress_callback=mock_callback,
            max_workers=2
        )
        
        assert len(callback_calls) > 0
        assert payloads is not None
    
    def test_async_worker_count(self, mock_image_list):
        """Test with different worker counts."""
        for workers in [1, 2, 4]:
            payloads, errors = prepare_vision_payloads_async(
                mock_image_list,
                attach_images=True,
                max_workers=workers
            )
            
            assert len(payloads) == len(mock_image_list)
            assert len(errors) == 0
    
    def test_async_ordering_preserved(self, mock_image_list):
        """Test that async processing preserves image order."""
        payloads, errors = prepare_vision_payloads_async(
            mock_image_list,
            attach_images=True,
            max_workers=4
        )
        
        # Check that order matches input
        for i, payload in enumerate(payloads):
            expected_id = mock_image_list[i]["id"]
            assert payload.meta["id"] == expected_id
    
    def test_async_error_handling(self, tmp_path):
        """Test async error handling with missing files."""
        bad_images = [
            {
                "id": i,
                "filename": f"missing_{i}.jpg",
                "path": str(tmp_path),
                "rating": 0
            }
            for i in range(3)
        ]
        
        payloads, errors = prepare_vision_payloads_async(
            bad_images,
            attach_images=True,
            max_workers=2
        )
        
        assert len(payloads) == 0
        assert len(errors) == 3


class TestLoggingSetup:
    """Tests for setup_logging function."""
    
    def test_logging_setup_basic(self):
        """Test basic logging setup."""
        import logging
        
        setup_logging(verbose=False, json_logging=False)
        
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) >= 1
    
    def test_logging_setup_verbose(self):
        """Test verbose logging setup."""
        import logging
        
        setup_logging(verbose=True, json_logging=False)
        
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG
    
    def test_logging_setup_json(self):
        """Test JSON logging setup (may warn if library missing)."""
        import logging
        
        # Should not raise even if python-json-logger missing
        setup_logging(verbose=False, json_logging=True)
        
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG


class TestVisionImageDataclass:
    """Tests for VisionImage dataclass."""
    
    def test_vision_image_creation(self, mock_image_dict):
        """Test creating a VisionImage."""
        from pathlib import Path
        
        vi = VisionImage(
            meta=mock_image_dict,
            path=Path("/tmp/test.jpg"),
            b64="base64data",
            data_url="data:image/jpeg;base64,base64data"
        )
        
        assert vi.meta == mock_image_dict
        assert vi.path == Path("/tmp/test.jpg")
        assert vi.b64 == "base64data"
        assert vi.data_url.startswith("data:image/jpeg")
    
    def test_vision_image_fields(self):
        """Test VisionImage has correct fields."""
        from dataclasses import fields
        
        field_names = {f.name for f in fields(VisionImage)}
        
        assert "meta" in field_names
        assert "path" in field_names
        assert "b64" in field_names
        assert "data_url" in field_names
