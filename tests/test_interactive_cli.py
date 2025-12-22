"""
Additional tests for interactive_cli.py module.
Tests configuration parsing and command-line argument handling.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "host"))

import pytest
from unittest.mock import Mock, patch
from interactive_cli import RunConfig, DEFAULT_LIMIT, DEFAULT_MIN_RATING


class TestRunConfig:
    """Tests for RunConfig dataclass."""
    
    def test_run_config_defaults(self):
        """Test RunConfig with default values."""
        config = RunConfig(
            mode="rating",
            source="all"
        )
        
        assert config.mode == "rating"
        assert config.source == "all"
        assert config.min_rating == DEFAULT_MIN_RATING
        assert config.limit == DEFAULT_LIMIT
        assert config.dry_run == True  # Default
        assert config.only_raw == False
    
    def test_run_config_all_fields(self):
        """Test RunConfig with all fields specified."""
        config = RunConfig(
            mode="tagging",
            source="path",
            path_contains="/photos/2024",
            tag="vacation",
            collection="My Collection",
            min_rating=3,
            only_raw=True,
            dry_run=False,
            limit=50,
            model="llama3.2-vision:latest",
            llm_url="http://localhost:11434",
            target_dir="/exports",
            prompt_file=Path("/tmp/prompt.md"),
            prompt_variant="detalhado",
            timeout=120.0,
            download_model=None,
            generate_styles=True,
            text_only=False,
            extra_flags=["--verbose"]
        )
        
        assert config.mode == "tagging"
        assert config.source == "path"
        assert config.path_contains == "/photos/2024"
        assert config.tag == "vacation"
        assert config.min_rating == 3
        assert config.limit == 50
        assert config.timeout == 120.0
    
    def test_run_config_rating_mode(self):
        """Test RunConfig for rating mode."""
        config = RunConfig(
            mode="rating",
            source="collection",
            collection="Test Collection",
            min_rating=0
        )
        
        assert config.mode == "rating"
        assert config.collection == "Test Collection"
        assert config.min_rating == 0
    
    def test_run_config_tagging_mode(self):
        """Test RunConfig for tagging mode."""
        config = RunConfig(
            mode="tagging",
            source="tag",
            tag="landscape"
        )
        
        assert config.mode == "tagging"
        assert config.tag == "landscape"
    
    def test_run_config_treatment_mode(self):
        """Test RunConfig for treatment mode."""
        config = RunConfig(
            mode="tratamento",
            source="all",
            target_dir="/tmp/exports"
        )
        
        assert config.mode == "tratamento"
        assert config.target_dir == "/tmp/exports"
    
    def test_run_config_export_mode(self):
        """Test RunConfig for export mode."""
        config = RunConfig(
            mode="export",
            source="all",
            target_dir="/exports/batch",
            generate_styles=True
        )
        
        assert config.mode == "export"
        assert config.target_dir == "/exports/batch"
        assert config.generate_styles == True


class TestConstants:
    """Tests for module constants."""
    
    def test_default_limit(self):
        """Test DEFAULT_LIMIT constant."""
        assert DEFAULT_LIMIT > 0
        assert isinstance(DEFAULT_LIMIT, int)
    
    def test_default_min_rating(self):
        """Test DEFAULT_MIN_RATING constant."""
        assert DEFAULT_MIN_RATING >= -2  # Allow unrated (-2)
        assert DEFAULT_MIN_RATING <= 5
        assert isinstance(DEFAULT_MIN_RATING, int)
    
    def test_timeout_default(self):
        """Test default timeout in RunConfig."""
        config = RunConfig(mode="rating", source="all")
        assert hasattr(config, 'timeout')
        assert config.timeout >= 0


class TestPromptVariants:
    """Tests for prompt variant functionality."""
    
    def test_prompt_variant_basico(self):
        """Test basic prompt variant."""
        config = RunConfig(
            mode="rating",
            source="all",
            prompt_variant="basico"
        )
        
        assert config.prompt_variant == "basico"
    
    def test_prompt_variant_detalhado(self):
        """Test detailed prompt variant."""
        config = RunConfig(
            mode="rating",
            source="all",
            prompt_variant="detalhado"
        )
        
        assert config.prompt_variant == "detalhado"
    
    def test_custom_prompt_file(self):
        """Test custom prompt file."""
        custom_prompt = Path("/tmp/custom_prompt.md")
        config = RunConfig(
            mode="rating",
            source="all",
            prompt_file=custom_prompt
        )
        
        assert config.prompt_file == custom_prompt


class TestSourceOptions:
    """Tests for source options."""
    
    def test_source_all(self):
        """Test 'all' source."""
        config = RunConfig(mode="rating", source="all")
        assert config.source == "all"
    
    def test_source_path(self):
        """Test 'path' source with path filter."""
        config = RunConfig(
            mode="rating",
            source="path",
            path_contains="/photos"
        )
        
        assert config.source == "path"
        assert config.path_contains == "/photos"
    
    def test_source_tag(self):
        """Test 'tag' source with tag filter."""
        config = RunConfig(
            mode="rating",
            source="tag",
            tag="favorite"
        )
        
        assert config.source == "tag"
        assert config.tag == "favorite"
    
    def test_source_collection(self):
        """Test 'collection' source."""
        config = RunConfig(
            mode="rating",
            source="collection",
            collection="My Photos"
        )
        
        assert config.source == "collection"
        assert config.collection == "My Photos"


class TestFlags:
    """Tests for various flags."""
    
    def test_dry_run_flag(self):
        """Test dry_run flag."""
        config_dry = RunConfig(mode="rating", source="all", dry_run=True)
        config_real = RunConfig(mode="rating", source="all", dry_run=False)
        
        assert config_dry.dry_run == True
        assert config_real.dry_run == False
    
    def test_only_raw_flag(self):
        """Test only_raw flag."""
        config = RunConfig(mode="rating", source="all", only_raw=True)
        assert config.only_raw == True
    
    def test_text_only_flag(self):
        """Test text_only flag."""
        config = RunConfig(mode="rating", source="all", text_only=True)
        assert config.text_only == True
    
    def test_generate_styles_flag(self):
        """Test generate_styles flag."""
        config = RunConfig(mode="export", source="all", generate_styles=True)
        assert config.generate_styles == True


class TestExtraFlags:
    """Tests for extra_flags list."""
    
    def test_empty_extra_flags(self):
        """Test with no extra flags."""
        config = RunConfig(mode="rating", source="all")
        assert isinstance(config.extra_flags, list)
    
    def test_multiple_extra_flags(self):
        """Test with multiple extra flags."""
        flags = ["--verbose", "--debug", "--no-color"]
        config = RunConfig(mode="rating", source="all", extra_flags=flags)
        
        assert config.extra_flags == flags
        assert len(config.extra_flags) == 3
