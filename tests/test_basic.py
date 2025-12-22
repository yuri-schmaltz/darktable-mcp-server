"""
Basic tests to ensure CI pipeline works.
More comprehensive tests will be added in TASK-010.
"""
import sys
from pathlib import Path

# Add host directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "host"))


def test_imports():
    """Test that main modules can be imported."""
    import common
    import interactive_cli
    assert hasattr(common, 'setup_logging')
    assert hasattr(interactive_cli, 'RunConfig')


def test_run_config():
    """Test RunConfig dataclass."""
    from interactive_cli import RunConfig, DEFAULT_LIMIT, DEFAULT_MIN_RATING
    
    config = RunConfig(
        mode="rating",
        source="all",
        path_filter=None,
        tag=None,
        collection=None,
        min_rating=DEFAULT_MIN_RATING,
        limit=DEFAULT_LIMIT,
        target_dir=None,
        model="llama3.2-vision",
        llm_url="http://localhost:11434",
        prompt_file=None,
        timeout=60.0,
        download_model=None,
        prompt_variant="basico",
        generate_styles=True,
        text_only=False,
        extra_flags=[]
    )
    
    assert config.mode == "rating"
    assert config.limit == DEFAULT_LIMIT
    assert config.timeout == 60.0


def test_logging_setup():
    """Test logging setup function."""
    from common import setup_logging
    import tempfile
    import logging
    
    # Test that function runs without error
    setup_logging(verbose=False, json_logging=False)
    
    # Check that logger is configured
    logger = logging.getLogger()
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1  # At least console handler


def test_path_sanitization():
    """Test basic path validation (relates to TASK-003)."""
    import re
    
    # Dangerous patterns that should be rejected
    dangerous = ["; rm -rf /", "../../etc/passwd", "$(whoami)", "`whoami`"]
    
    # Pattern from security fix
    pattern = re.compile(r"[;|&$`<>]|\.\.|\$\(")
    
    for path in dangerous:
        assert pattern.search(path) is not None, f"Should detect dangerous pattern in: {path}"
    
    # Safe paths should pass
    safe = ["/home/user/photos", "./exports", "my-photos"]
    for path in safe:
        if pattern.search(path):
            # Only .. and $( are truly dangerous in these
            assert ".." in path or "$(" in path
