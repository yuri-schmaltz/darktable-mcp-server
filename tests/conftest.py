"""
Test fixtures for image testing.
Provides utility functions and mock images for test suite.
"""
import io
import base64
from pathlib import Path
from PIL import Image
import tempfile
import pytest


@pytest.fixture
def temp_image_path(tmp_path):
    """Create a temporary test image."""
    img_path = tmp_path / "test_image.jpg"
    img = Image.new('RGB', (800, 600), color=(73, 109, 137))
    img.save(img_path, 'JPEG')
    return img_path


@pytest.fixture
def temp_large_image_path(tmp_path):
    """Create a temporary large test image (>1600px)."""
    img_path = tmp_path / "large_image.jpg"
    img = Image.new('RGB', (2400, 1800), color=(200, 100, 50))
    img.save(img_path, 'JPEG')
    return img_path


@pytest.fixture
def temp_png_image_path(tmp_path):
    """Create a temporary PNG test image with alpha."""
    img_path = tmp_path / "test_image.png"
    img = Image.new('RGBA', (640, 480), color=(100, 150, 200, 128))
    img.save(img_path, 'PNG')
    return img_path


@pytest.fixture
def mock_image_dict(temp_image_path):
    """Create a mock image dictionary as returned by Darktable."""
    return {
        "id": 123,
        "filename": temp_image_path.name,
        "path": str(temp_image_path.parent),
        "rating": 3,
        "colorlabels": ["red", "blue"],
        "width": 800,
        "height": 600
    }


@pytest.fixture
def mock_image_list(tmp_path):
    """Create a list of mock images for batch testing."""
    images = []
    for i in range(5):
        img_path = tmp_path / f"img_{i}.jpg"
        img = Image.new('RGB', (640, 480), color=(i*50, i*40, i*30))
        img.save(img_path, 'JPEG')
        
        images.append({
            "id": 100 + i,
            "filename": img_path.name,
            "path": str(tmp_path),
            "rating": i % 5,
            "colorlabels": ["red"] if i % 2 == 0 else []
        })
    
    return images


def create_test_base64_image():
    """Create a small base64-encoded test image."""
    img = Image.new('RGB', (100, 100), color=(255, 0, 0))
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    b64 = base64.b64encode(buffer.getvalue()).decode('ascii')
    return b64, f"data:image/jpeg;base64,{b64}"
